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
    ></LogViewer>
    <div class="flex-none flex gap-1">
      <label class="flex flex-auto items-center">
        <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
          <path :d="mdiMagnify"></path>
        </svg>
        <input
          class="flex-auto rounded border-gray-300"
          type="search"
          placeholder="TODO: search"
        />
      </label>
      <button
        type="button"
        class="
          bg-white
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
    </div>
  </div>
</template>

<script setup lang="ts">
import useCleanup from '@/composables/useCleanup';
import type { LogRecord } from '@/log-record';
import { RecordType } from '@/log-record';
import type { PageDataLog } from '@/page-data';
import readLineStream from '@/utils/readLineStream';
import withLoading from '@/utils/withLoading';
import { mdiMagnify, mdiPause, mdiPlay } from '@mdi/js';
import type { PropType } from 'vue';
import { watch, reactive, ref } from 'vue';
import LogViewer from '@/components/LogViewer/LogViewer.vue';
import app from '@/services';
import loadImage from '@/utils/loadImage';
import { isDevelopmentMode } from '@/settings';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataLog>,
    required: true,
  },
});

const records = reactive([] as LogRecord[]);

const pushRecord = async (v: LogRecord) => {
  if (v.t === RecordType.IMAGE) {
    try {
      await loadImage(v.url);
    } catch (err) {
      app.message.error(`load image failed: ${v.url}: ${err}`);
    }
  }
  records.push(v);
};

const paused = ref(false);

const loadingCount = ref(0);
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
