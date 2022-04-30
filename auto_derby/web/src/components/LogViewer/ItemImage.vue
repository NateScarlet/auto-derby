<template>
  <figure>
    <figcaption>{{ value.caption }}</figcaption>
    <hr class="mb-1 border-theme-text border-opacity-30" />
    <img :src="value.url" />
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
