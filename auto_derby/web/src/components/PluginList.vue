<template>
  <div class="flex flex-col overflow-hidden">
    <ol
      class="space-y-2 p-1 flex-auto overflow-y-auto overflow-x-hidden relative"
    >
      <TransitionGroup
        move-class="transition-all duration-300 ease-in-out"
        enter-active-class="transition-all duration-500 ease-in-out"
        enter-from-class="opacity-0"
        leave-active-class="transition-all duration-500 ease-in-out absolute"
        leave-to-class="opacity-0"
        @before-leave="bakeElementSize"
      >
        <template v-for="{ itemAttrs, key } in listData" :key="key">
          <PluginListItem v-bind="itemAttrs"></PluginListItem>
        </template>
        <template v-if="listData.length === 0">
          <div class="flex flex-center h-full w-full">
            <p v-if="query">No matched plugin</p>
            <p v-else>No plugin</p>
          </div>
        </template>
      </TransitionGroup>
    </ol>
    <label class="flex flex-none items-center">
      <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
        <path :d="mdiMagnify"></path>
      </svg>
      <input
        v-model="query"
        class="flex-auto rounded border-gray-400 m-1"
        type="search"
        placeholder="search"
      />
    </label>
  </div>
</template>

<script setup lang="ts">
import usePropVModel from '@/composables/usePropVModel';
import useStringArray from '@/composables/useStringArray';
import type { Plugin } from '@/page-data';
import { mdiMagnify } from '@mdi/js';
import type { PropType } from 'vue';
import { ref, computed } from 'vue';
import PluginListItem from '@/components/PluginListItem.vue';
import matchSearchKeys from '@/utils/matchSearchKeys';
import bakeElementSize from '@/utils/bakeElementSize';

const props = defineProps({
  modelValue: {
    type: Array as PropType<string[]>,
    default: () => [],
  },
  items: {
    type: Array as PropType<Plugin[]>,
    required: true,
  },
});

const emit = defineEmits<{
  (e: 'update:modelValue', v: string[]): void;
}>();

const localModelValue = usePropVModel({ emit }, props, 'modelValue');

const { toggle } = useStringArray(localModelValue);

const query = ref('');

const listData = computed(() =>
  props.items
    .filter((i) => matchSearchKeys(query.value, [i.name, i.doc]))
    .map((i) => {
      const selected = localModelValue.value.includes(i.name);
      return {
        key: i.name,
        itemAttrs: {
          value: i,
          class: [
            'border border-2 cursor-pointer',
            selected ? 'border-theme-green' : 'border-gray-200',
          ],
          selected,
          'onUpdate:selected': () => {
            toggle(i.name);
          },
        },
      };
    })
);
</script>
