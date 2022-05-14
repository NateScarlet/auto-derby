<template>
  <div class="container max-w-2xl m-auto h-screen flex flex-col gap-1">
    <LogViewer
      v-model:end-index="endIndex"
      :paused="paused"
      class="flex-auto"
      :records="records"
      :filter="logFilter"
    ></LogViewer>
    <div class="flex item-center flex-wrap">
      <div class="space-x-2 flex items-center">
        <template
          v-for="{ key, level, count, inputAttrs } in levelListData"
          :key="key"
        >
          <label class="inline-flex flex-center">
            <input v-bind="inputAttrs" class="mx-1" />
            <LogLevelWidget
              :value="level"
              class="w-16 inline-block text-center"
            ></LogLevelWidget>
            <span class="text-sm">({{ count }})</span>
          </label>
        </template>
      </div>
      <span class="flex-auto"></span>
      <div class="flex-none flex items-center w-48">
        <input
          v-model.number="inputData.endLineno"
          :max="totalCount"
          :min="1"
          type="number"
          class="spin-button-none flex-auto w-0 text-center h-8 rounded border-gray-400"
          @focus="onEndLinenoInputFocus"
        />
        <button
          v-if="inputData.endLineno != totalCount"
          type="button"
          class="bg-white rounded border px-2 border-gray-400 hover:bg-gray-200 h-8"
          @click="inputData.endLineno = totalCount"
        >
          <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
            <path :d="mdiSkipNext"></path>
          </svg>
        </button>
      </div>
    </div>
    <div class="flex-none flex gap-1">
      <label class="flex flex-auto items-center">
        <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
          <path :d="mdiMagnify"></path>
        </svg>
        <input
          v-model="inputData.query"
          class="flex-auto rounded border-gray-400"
          type="search"
          placeholder="search"
        />
      </label>
      <Transition
        leave-from-class=""
        leave-active-class="transition duration-300 ease-in-out"
        leave-to-class="opacity-0 transform translate-x-full"
      >
        <button
          v-if="loadingCount > 0"
          type="button"
          class="bg-white flex-initial rounded h-10 px-4 disabled:text-gray-200 disabled:cursor-not-allowed border border-gray-400"
          :disabled="loadingCount === 0"
          @click="paused = !paused"
        >
          <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
            <path :d="paused ? mdiPlay : mdiPause"></path>
          </svg>
        </button>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import useCleanup from '@/composables/useCleanup';
import type { LogRecord } from '@/log-record';
import { LogLevel, searchKeys } from '@/log-record';
import type { PageDataLog } from '@/page-data';
import readLineStream from '@/utils/readLineStream';
import withLoading from '@/utils/withLoading';
import { mdiMagnify, mdiPause, mdiPlay, mdiSkipNext } from '@mdi/js';
import type { PropType } from 'vue';
import { toRef, computed, watch, reactive, ref } from 'vue';
import LogViewer from '@/components/LogViewer/LogViewer.vue';
import services from '@/services';
import { isDevelopmentMode } from '@/settings';
import useStringArray from '@/composables/useStringArray';
import LogLevelWidget from '@/components/LogLevelWidget.vue';
import matchSearchKeys from '@/utils/matchSearchKeys';
import { sortBy, throttle } from 'lodash-es';
import useStorage from '@/composables/useStorage';
import limitTextLength from '@/utils/limitTextLength';
import useTransform from '@/composables/useTransform';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataLog>,
    required: true,
  },
});

const records = reactive([] as LogRecord[]);
const loadingCount = ref(0);
const inputData = reactive({
  query: '',
  endLineno: 0,
});
const endIndex = useTransform(
  toRef(inputData, 'endLineno'),
  (i) => i - 1,
  (i) => i + 1
);
const levelRecordCount = reactive(new Map<LogLevel, number>());
const paused = ref(false);
const totalCount = ref(0);
const recordBuffer = [] as LogRecord[];
const flushRecords = throttle(
  () => {
    const b = recordBuffer.slice();
    recordBuffer.length = 0;
    totalCount.value += b.length;
    records.push(...b);
    b.forEach((v) => {
      levelRecordCount.set(v.lv, (levelRecordCount.get(v.lv) ?? 0) + 1);
    });

    inputData.endLineno = totalCount.value;
  },
  100,
  { trailing: true }
);
const pushRecord = async (v: LogRecord) => {
  recordBuffer.push(v);
  flushRecords();
};

const levelOrder = [
  LogLevel.ERROR,
  LogLevel.WARN,
  LogLevel.INFO,
  LogLevel.DEBUG,
];
const enabledLevels = useStorage(
  localStorage,
  '76fec8b7-5485-4ef5-ac6f-9f3a45cbc2a2',
  [LogLevel.ERROR, LogLevel.WARN, LogLevel.INFO] as LogLevel[]
);
const { toggle: toggleEnabledLevel } = useStringArray(enabledLevels);
const levelListData = computed(() =>
  sortBy(
    Array.from(levelRecordCount.entries()).map(([k, v]) => ({
      key: k,
      level: k,
      count: v,
      inputAttrs: {
        type: 'checkbox' as const,
        checked: enabledLevels.value.includes(k),
        onChange: () => {
          toggleEnabledLevel(k);
        },
      },
    })),
    (i) => levelOrder.indexOf(i.level)
  )
);

const logFilter = computed(() => {
  const { query } = inputData;
  const level = enabledLevels.value;
  return (v: LogRecord) => {
    if (!matchSearchKeys(query, searchKeys(v))) {
      return false;
    }
    if (!level.includes(v.lv)) {
      return false;
    }
    return true;
  };
});
const { addCleanup, cleanup } = useCleanup();
watch(
  () => props.pageData.streamURL,
  withLoading(loadingCount, async (url) => {
    cleanup();
    const abort = new AbortController();
    addCleanup(() => abort.abort());
    try {
      const { body } = await fetch(url, { signal: abort.signal });
      if (!body) {
        return;
      }

      await readLineStream({
        stream: body,
        onLine: async (line) => {
          try {
            await pushRecord(Object.freeze(JSON.parse(line)));
          } catch (err) {
            services.message.error(
              `line parsing failed: '${limitTextLength(line, 80)}': ${err}`
            );
            if (isDevelopmentMode) {
              // eslint-disable-next-line no-console
              console.error({ err, line });
            }
          }
        },
      });
    } catch (err) {
      services.message.error(`stream read failed: ${err}`);
    }
    flushRecords();
    paused.value = true;
    services.message.info('stream closed');
  }),
  { immediate: true }
);

const onEndLinenoInputFocus = (e: Event) => {
  const el = e.target;
  if (!(el instanceof HTMLInputElement)) {
    return;
  }
  el.select();
  paused.value = true;
};
</script>
