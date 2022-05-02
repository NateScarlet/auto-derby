<template>
  <span v-bind="levelAttrs">
    {{ value }}
  </span>
</template>

<script setup lang="ts">
import { LogLevel } from '@/log-record';
import assertNever from '@/utils/assertNever';
import type { PropType } from 'vue';
import { computed } from 'vue';

const props = defineProps({
  value: {
    type: String as PropType<LogLevel>,
    required: true,
  },
});

const levelAttrs = computed(() => {
  const { value } = props;
  switch (value) {
    case LogLevel.DEBUG:
      return {
        class: 'text-black border border-gray-400 bg-gray-200',
      };
    case LogLevel.INFO:
      return {
        class: 'bg-gray-300 text-black',
      };
    case LogLevel.WARN:
      return {
        class: 'bg-orange-500 text-white',
      };
    case LogLevel.ERROR:
      return {
        class: 'bg-red-500 text-white',
      };
    default:
      assertNever(value);
      return {};
  }
});
</script>
