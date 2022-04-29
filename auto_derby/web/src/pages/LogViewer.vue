<template>
  <div>
    loadingCount: {{ loadingCount }} errors: {{ errors }}
    <ol ref="host">
      <li v-for="(i, index) in records" :key="index">
        {{ i }}
      </li>
    </ol>
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

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataLog>,
    required: true,
  },
});

const host = ref<HTMLOListElement>();
const records = reactive([] as LogRecord[]);

const loadingCount = ref(0);
const errors = reactive([] as string[]);
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
            errors.push(`line parsing failed: ${err}`);
          }
        },
      });
    } catch (err) {
      errors.push(`stream read failed: ${err}`);
    }
  }),
  { immediate: true }
);
</script>
