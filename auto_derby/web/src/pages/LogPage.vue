<template>
  <div
    class="
      container
      max-w-2xl
      m-auto
      h-screen
      overflow-hidden
      flex flex-col
      gap-1
    "
  >
    <LogViewer
      class="flex-auto"
      :records="records"
      :paused="paused"
      :filter="logFilter"
    ></LogViewer>
    <div class="flex">
      <div class="space-x-2">
        <template
          v-for="{ key, level, count, inputAttrs } in levelListData"
          :key="key"
        >
          <label class="inline-flex flex-center">
            <input v-bind="inputAttrs" />
            <LogLevelWidget
              :value="level"
              class="w-16 inline-block text-center"
            ></LogLevelWidget>
            <span>({{ count }})</span>
          </label>
        </template>
      </div>
    </div>
    <div class="flex-none flex gap-1">
      <label class="flex flex-auto items-center">
        <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
          <path :d="mdiMagnify"></path>
        </svg>
        <input
          v-model="inputData.query"
          class="flex-auto rounded border-gray-300"
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
          class="
            bg-white
            flex-initial
            rounded
            border-gray-300
            h-10
            px-4
            disabled:text-gray-200 disabled:cursor-not-allowed
          "
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
import { mdiMagnify, mdiPause, mdiPlay } from '@mdi/js';
import type { PropType } from 'vue';
import { computed, watch, reactive, ref } from 'vue';
import LogViewer from '@/components/LogViewer/LogViewer.vue';
import app from '@/services';
import { isDevelopmentMode } from '@/settings';
import useStringArray from '@/composables/useStringArray';
import LogLevelWidget from '@/components/LogLevelWidget.vue';
import matchSearchKeys from '@/utils/matchSearchKeys';
import { sortBy } from 'lodash-es';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataLog>,
    required: true,
  },
});

const records = reactive([] as LogRecord[]);

const levelRecordCount = reactive(new Map<LogLevel, number>());

const pushRecord = async (v: LogRecord) => {
  levelRecordCount.set(v.lv, (levelRecordCount.get(v.lv) ?? 0) + 1);
  records.push(v);
};

const levelOrder = [
  LogLevel.ERROR,
  LogLevel.WARN,
  LogLevel.INFO,
  LogLevel.DEBUG,
];
const enabledLevels = ref([
  LogLevel.ERROR,
  LogLevel.WARN,
  LogLevel.INFO,
] as LogLevel[]);
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

const paused = ref(false);

const loadingCount = ref(0);
const inputData = reactive({
  query: '',
});
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
            app.message.error(`line parsing failed: ${err}`);
            if (isDevelopmentMode) {
              // eslint-disable-next-line no-console
              console.error({ err, line });
            }
          }
        },
      });
    } catch (err) {
      app.message.error(`stream read failed: ${err}`);
    }
    app.message.info('stream closed');
  }),
  { immediate: true }
);
</script>
