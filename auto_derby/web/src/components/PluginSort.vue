<template>
  <ol ref="listEl" class="space-y-2">
    <li
      v-for="{
        key,
        itemAttrs,
        copyButtonAttrs,
        deleteButtonAttrs,
        value,
      } in listData"
      :key="key"
      v-bind="itemAttrs"
      class="bg-white flex items-center p-1 rounded gap-1"
    >
      <svg
        class="drag-handle inline align-top fill-current h-6 cursor-grab"
        viewBox="0 0 24 24"
      >
        <path :d="mdiDragHorizontal"></path>
      </svg>
      <span class="text-lg flex-auto">
        {{ value }}
      </span>
      <button v-bind="deleteButtonAttrs">
        <svg
          class="inline align-top fill-current h-6 hover:bg-gray-200"
          viewBox="0 0 24 24"
        >
          <path :d="mdiDeleteOutline"></path>
        </svg>
      </button>
      <button v-bind="copyButtonAttrs">
        <svg
          class="inline align-top fill-current h-6 hover:bg-gray-200"
          viewBox="-2 -2 28 28"
        >
          <path :d="mdiContentCopy"></path>
        </svg>
      </button>
    </li>
    <template v-if="listData.length === 0">
      <div class="flex flex-center h-full inset-0">
        <p class="text-center text-lg">No plugins to sort</p>
      </div>
    </template>
  </ol>
</template>

<script setup lang="ts">
import usePropVModel from '@/composables/usePropVModel';
import useSortable from '@/composables/useSortable';
import { mdiDragHorizontal, mdiDeleteOutline, mdiContentCopy } from '@mdi/js';
import type { PropType } from 'vue';
import { triggerRef, computed, watch, ref } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array as PropType<string[]>,
    required: true,
  },
});

const emit = defineEmits<{
  (e: 'update:modelValue', v: string[]): void;
}>();

const localModelValue = usePropVModel({ emit }, props, 'modelValue');

const listEl = ref<HTMLOListElement>();

const { order, sortRef } = useSortable(
  listEl,
  computed(() => ({
    handle: '.drag-handle',
  }))
);

const version = ref(0);
const itemID = (v: string, index: number) => {
  return `${v}@${index}-v${version.value}`;
};
const listData = computed(() =>
  localModelValue.value.map((i, index) => {
    const key = itemID(i, index);
    return {
      key,
      value: i,
      itemAttrs: {
        'data-id': key,
      },
      copyButtonAttrs: {
        type: 'button' as const,
        onClick: () => {
          localModelValue.value.splice(index, 0, i);
          triggerRef(localModelValue);
        },
      },
      deleteButtonAttrs: {
        type: 'button' as const,
        onClick: () => {
          localModelValue.value.splice(index, 1);
          triggerRef(localModelValue);
        },
      },
    };
  })
);
watch(order, () => {
  sortRef(localModelValue, itemID);
  version.value += 1;
});
</script>
