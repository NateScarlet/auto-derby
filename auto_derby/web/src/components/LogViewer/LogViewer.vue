<template>
  <ol>
    <template v-for="(i, index) in records" :key="index">
      <ListItem :value="i"></ListItem>
    </template>
  </ol>
</template>

<script setup lang="ts">
import type { LogRecord } from '@/log-record';
import type { PropType } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';

const props = defineProps({
  records: {
    type: Array as PropType<LogRecord[]>,
    required: true,
  },
});
const _ = props;
</script>
