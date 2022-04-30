<template>
  <li class="p-1 bg-white rounded border border-gray-300">
    <div class="space-x-1">
      <span class="w-24 inline-block text-center" v-bind="levelAttrs">
        {{ value.lv }}
      </span>
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
import { LogLevel, RecordType } from '@/log-record';
import type { Component, PropType } from 'vue';
import { computed } from 'vue';
import ItemImageVue from '@/components/LogViewer/ItemImage.vue';
import ItemTextVue from '@/components/LogViewer/ItemText.vue';
import ItemDefaultVue from '@/components/LogViewer/ItemDefault.vue';
import assertNever from '@/utils/assertNever';

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

const levelAttrs = computed(() => {
  switch (props.value.lv) {
    case LogLevel.DEBUG:
      return {
        class: 'text-gray-400 bg-gray-800',
      };
    case LogLevel.INFO:
      return {
        class: 'bg-gray-300',
      };
    case LogLevel.WARN:
      return {
        class: 'bg-orange-500 text-orange-800',
      };
    case LogLevel.ERROR:
      return {
        class: 'bg-red-500 text-red-800',
      };
    default:
      assertNever(props.value.lv);
      return {};
  }
});
</script>
