<template>
  <li>
    <span>
      {{ value.ts }}
    </span>
    <Component :is="itemClass.component" :value="value"></Component>
  </li>
</template>
<script lang="ts">
import type { LogRecord } from '@/log-record';
import { RecordType } from '@/log-record';
import type { Component, PropType } from 'vue';
import { computed } from 'vue';
import ItemImageVue from '@/components/LogViewer/ItemImage.vue';
import ItemTextVue from '@/components/LogViewer/ItemText.vue';
import ItemDefaultVue from '@/components/LogViewer/ItemDefault.vue';

interface ItemClass {
  component: Component;
}

const itemClasses = new Map<RecordType, ItemClass>([
  [RecordType.IMAGE, { component: ItemImageVue }],
  [RecordType.TEXT, { component: ItemTextVue }],
]);
const defaultItemClass: ItemClass = { component: ItemDefaultVue };
</script>
<script setup lang="ts">
const props = defineProps({
  value: {
    type: Object as PropType<LogRecord>,
    required: true,
  },
});

const itemClass = computed(
  () => itemClasses.get(props.value.t) ?? defaultItemClass
);
</script>
