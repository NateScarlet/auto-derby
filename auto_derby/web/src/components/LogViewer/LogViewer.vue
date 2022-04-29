<template>
  <ol ref="el" class="max-h-screen p-4 overflow-auto space-y-2">
    <template v-for="(i, index) in records" :key="index">
      <ListItem
        class="bg-white rounded"
        :value="i"
        :lineno="index + 1"
      ></ListItem>
    </template>
  </ol>
</template>

<script setup lang="ts">
import type { LogRecord } from '@/log-record';
import type { PropType } from 'vue';
import { ref, toRef, watch } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';

const props = defineProps({
  records: {
    type: Array as PropType<LogRecord[]>,
    required: true,
  },
});
const records = toRef(props, 'records');
const el = ref<HTMLOListElement>();

watch(
  [el, records],
  ([el]) => {
    if (!el) {
      return;
    }
    el.scroll({
      top: el.scrollHeight,
    });
  },
  { deep: true }
);
</script>
