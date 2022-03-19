<template>
  <div class="text-left">
    <p class="border-b border-gray-200">
      <span class="font-bold">{{ value.name }} </span>
      <span v-show="!idHidden" class="text-sm float-right">
        {{ value.id }}
      </span>
    </p>
    <p class="text-sm">
      <span class="bg-gray-200 rounded-lg px-1 mr-2">効果</span>
      <span class="font-bold">
        {{ value.description }}
      </span>
    </p>
  </div>
</template>

<script setup lang="ts">
import type { SingleModeItem } from '@/page-data';
import type { PropType } from 'vue';

const props = defineProps({
  value: {
    type: Object as PropType<SingleModeItem>,
    required: true,
  },
  idHidden: {
    type: Boolean,
  },
});
const _ = props;
</script>
