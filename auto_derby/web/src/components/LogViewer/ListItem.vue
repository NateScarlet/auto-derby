<template>
  <li class="p-1 bg-white rounded border border-gray-300">
    <div class="space-x-1">
      <LogLevelWidget
        class="w-24 inline-block text-center"
        :value="value.lv"
      ></LogLevelWidget>
      <span>{{ value.source }}</span>
      <span class="text-sm float-right text-gray-400">
        <span>
          {{ timeText }}
        </span>
        <span class="dot mx-1"></span>
        <span>
          {{ lineno }}
        </span>
      </span>
    </div>
    <hr class="border-gray-300 my-1" />
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
import LogLevelWidget from '@/components/LogLevelWidget.vue';
</script>

<script setup lang="ts">
interface ItemClass {
  component: Component;
}

const itemClasses = new Map<RecordType, ItemClass>([
  [RecordType.IMAGE, { component: ItemImageVue }],
  [RecordType.TEXT, { component: ItemTextVue }],
]);
const defaultItemClass: ItemClass = { component: ItemDefaultVue };

const timeFormat = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'short',
  timeStyle: 'medium',
  hour12: false,
});
const secondFormat = new Intl.DateTimeFormat(undefined, {
  fractionalSecondDigits: 3,
});
const props = defineProps({
  value: {
    type: Object as PropType<LogRecord>,
    required: true,
  },
  lineno: {
    type: Number,
    required: true,
  },
});

const timeText = computed(() => {
  const t = new Date(props.value.ts);
  return `${timeFormat.format(t)}.${secondFormat.format(t)}`;
});
const itemClass = computed(
  () => itemClasses.get(props.value.t) ?? defaultItemClass
);
</script>
