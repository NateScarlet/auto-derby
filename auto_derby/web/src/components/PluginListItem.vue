<template>
  <li
    class="bg-white rounded p-4 flex gap-2 items-center cursor-pointer"
    @click="localSelected = !localSelected"
  >
    <div class="flex-auto overflow-hidden space-y-1">
      <div class="text-lg font-bold">
        {{ displayName }}
      </div>
      <div
        v-if="value.doc"
        class="whitespace-pre-line border-t border-gray-200 font-serif"
      >
        {{ value.doc }}
      </div>
    </div>
    <div class="flex-none">
      <input
        v-model="localSelected"
        type="checkbox"
        class="h-6 w-6 rounded text-theme-green border-gray-400 checked:border-none ring-0"
      />
    </div>
  </li>
</template>

<script setup lang="ts">
import usePropVModel from '@/composables/usePropVModel';
import type { Plugin } from '@/page-data';
import { upperFirst } from 'lodash-es';
import type { PropType } from 'vue';
import { computed } from 'vue';

const props = defineProps({
  value: {
    type: Object as PropType<Plugin>,
    required: true,
  },
  selected: {
    type: Boolean,
  },
});
const emit = defineEmits<{
  (e: 'update:selected', v: boolean): void;
}>();

const displayName = computed(() => {
  return props.value.name.split('_').map(upperFirst).join(' ');
});

const localSelected = usePropVModel({ emit }, props, 'selected');
</script>
