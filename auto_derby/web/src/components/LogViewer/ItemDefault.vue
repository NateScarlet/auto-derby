<template>
  <div>unsupported item: {{ value }}</div>
</template>

<script setup lang="ts">
import type { LogRecord } from '@/log-record';
import type { PropType } from 'vue';

defineProps({
  value: {
    type: Object as PropType<LogRecord>,
    required: true,
  },
});
</script>
