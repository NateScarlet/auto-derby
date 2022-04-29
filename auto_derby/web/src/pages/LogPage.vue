<template>
  <div class="container m-auto">
    <LogViewer :records="records"></LogViewer>
    <div v-if="loadingCount === 0" class="text-center">log end</div>
  </div>
</template>

<script setup lang="ts">
import useCleanup from '@/composables/useCleanup';
import type { LogRecord } from '@/log-record';
import type { PageDataLog } from '@/page-data';
import readLineStream from '@/utils/readLineStream';
import withLoading from '@/utils/withLoading';
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
            records.push(Object.freeze(JSON.parse(line)));
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
