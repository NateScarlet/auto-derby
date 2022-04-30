<template>
  <figure>
    <img :src="value.url" />
    <figcaption>{{ value.caption }}</figcaption>
  </figure>
</template>

<script setup lang="ts">
import type { ImageRecord } from '@/log-record';
import type { PropType } from 'vue';

defineProps({
  value: {
    type: Object as PropType<ImageRecord>,
    required: true,
  },
});
</script>
