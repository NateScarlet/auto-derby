<template>
  <ol>
    <template v-for="{ itemAttrs, key } in listData" :key="key">
      <PluginListItem v-bind="itemAttrs"></PluginListItem>
    </template>
  </ol>
</template>

<script setup lang="ts">
import usePropVModel from '@/composables/usePropVModel';
import useStringArray from '@/composables/useStringArray';
import type { Plugin } from '@/page-data';
import type { PropType } from 'vue';
import { computed } from 'vue';

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

const listData = computed(() =>
  props.items.map((i) => {
    return {
      key: i.name,
      itemAttrs: {
        value: i,
        selected: localModelValue.value.includes(i.name),
        'onUpdate:selected': () => {
          toggle(i.name);
        },
      },
    };
  })
);
</script>
