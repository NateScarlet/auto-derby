<template>
  <div class="container m-auto">
    <div class="p-1">
      <button
        type="button"
        class="bg-white rounded px-4"
        @click="paused = !paused"
      >
        <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
          <path :d="paused ? mdiPlay : mdiPause"></path>
        </svg>
      </button>
    </div>
    <LogViewer :records="records"></LogViewer>
    <div v-if="loadingCount === 0" class="text-center">log end</div>
  </div>
</template>

<script setup lang="ts">
import useCleanup from '@/composables/useCleanup';
import type { LogRecord, TextRecord } from '@/log-record';
import type { PageDataLog } from '@/page-data';
import readLineStream from '@/utils/readLineStream';
import withLoading from '@/utils/withLoading';
import { mdiPause, mdiPlay } from '@mdi/js';
import type { PropType } from 'vue';
import { watch, reactive, ref } from 'vue';
import LogViewer from '@/components/LogViewer/LogViewer.vue';
import app from '@/services';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataLog>,
    required: true,
  },
});

const records = reactive([] as LogRecord[]);
const recordBuffer = [] as LogRecord[];

const paused = ref(false);
const flushRecordBuffer = () => {
  if (paused.value) {
    return;
  }
  records.push(...recordBuffer);
  recordBuffer.length = 0;
};
const pushRecord = (v: TextRecord) => {
  recordBuffer.push(v);
  flushRecordBuffer();
};
watch(paused, (paused) => {
  if (!paused) {
    flushRecordBuffer();
  }
});
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
        onLine: (line) => {
          try {
            pushRecord(Object.freeze(JSON.parse(line)));
          } catch (err) {
            app.message.error(`line parsing failed: ${err}`);
          }
        },
      });
    } catch (err) {
      app.message.error(`stream read failed: ${err}`);
    }
  }),
  { immediate: true }
);
</script>
