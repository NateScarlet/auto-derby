<template>
  <li class="group p-1">
    <div class="flex gap-2">
      <div class="w-24 flex-none">
        <div class="w-full text-center rounded" v-bind="levelAttrs">
          {{ value.lv }}
        </div>
        <div class="text-xs hidden group-hover:block text-center">
          {{ timeText }}
        </div>
      </div>
      <div class="flex-auto">
        <Component :is="itemClass.component" :value="value"></Component>
      </div>
      <span class="text-xs float-right">
        {{ lineno }}
      </span>
    </div>
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
        class: 'text-gray-500',
      };
    case LogLevel.INFO:
      return {
        class: 'bg-gray-200',
      };
    case LogLevel.WARN:
      return {
        class: 'bg-orange-500 text-white',
      };
    case LogLevel.ERROR:
      return {
        class: 'bg-red-500 text-white',
      };
    default:
      assertNever(props.value.lv);
      return {};
  }
});
</script>
