<template>
  <div>
    {{ value.msg }}
  </div>
</template>

<script setup lang="ts">
import type { TextRecord } from '@/log-record';
import type { PropType } from 'vue';

defineProps({
  value: {
    type: Object as PropType<TextRecord>,
    required: true,
  },
});
</script>
