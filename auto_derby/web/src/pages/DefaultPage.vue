<template>
  {{ pageData }}
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import type { PageData } from '@/page-data';
import pageData from '@/page-data';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageData>,
    required: true,
  },
});
const _ = props;
</script>
