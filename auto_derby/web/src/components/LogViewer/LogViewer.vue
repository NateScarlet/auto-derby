<template>
  <TransitionGroup
    ref="el"
    class="max-h-screen p-4 overflow-y-auto overflow-x-hidden space-y-1"
    tag="ol"
    move-class="transition ease-in-out duration-300"
    enter-from-class="opacity-0 transform translate-x-8"
    enter-active-class="transition-all ease-in-out duration-500 relative"
    enter-to-class="opacity-100"
    level-to-class="opacity-0"
    appear
  >
    <template v-if="hasPrevious">
      <button
        type="button"
        class="w-full text-blue-500 underline"
        @click="onScrollToTop()"
      >
        load previous records
      </button>
    </template>
    <template v-for="{ value, key, index } in visibleRecords" :key="key">
      <ListItem
        :value="value"
        :lineno="index + 1"
        :data-index="index"
      ></ListItem>
    </template>
    <span v-if="hasNext">
      <button
        type="button"
        class="w-full text-blue-500 underline"
        @click="onScrollToBottom()"
      >
        load next records
      </button>
    </span>
    <div v-if="records.length === 0" class="flex flex-center h-full">
      <div class="text-center">
        <h1 class="text-2xl">Log Viewer</h1>
        <p>no record</p>
      </div>
    </div>
  </TransitionGroup>
</template>

<script setup lang="ts">
import type { LogRecord } from '@/log-record';
import type { PropType, TransitionGroup } from 'vue';
import { watch, watchEffect, computed, ref, toRef } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';
import computedWith from '@/utils/computedWith';
import useInfiniteScroll from '@/composables/useInfiniteScroll';
import usePause from '@/composables/usePause';

const props = defineProps({
  records: {
    type: Array as PropType<LogRecord[]>,
    required: true,
  },
  size: {
    type: Number,
    default: 100,
  },
  paused: {
    type: Boolean,
  },
});
const paused = toRef(props, 'paused');
const records = toRef(props, 'records');
const el = ref<
  InstanceType<typeof TransitionGroup> & { $el: HTMLOListElement }
>();
const topIndex = ref(0);

const scrollContainer = computed(() => el.value?.$el);
const totalCount = usePause(
  computedWith(
    () => props.records,
    () => {
      return props.records.length;
    },
    { deep: true }
  ),
  paused
);
const hasPrevious = computed(() => {
  return topIndex.value > 0;
});
const hasNext = computed(() => {
  return topIndex.value < totalCount.value - props.size;
});

const itemByIndex = (index: number) => {
  return scrollContainer.value?.querySelector(`[data-index="${index}"]`);
};

const onScrollToTop = () => {
  if (!hasPrevious.value) {
    return;
  }
  const topItem = itemByIndex(topIndex.value);
  topIndex.value -= Math.round(props.size / 2);
  topItem?.scrollIntoView();
};
const onScrollToBottom = () => {
  if (!hasNext.value) {
    return;
  }
  topIndex.value += Math.round(props.size / 2);
};

useInfiniteScroll(scrollContainer, {
  onScrollToTop,
  onScrollToBottom,
});

const visibleRecords = computedWith([totalCount, topIndex], () =>
  props.records
    .slice(topIndex.value, topIndex.value + props.size)
    .map((i, index) => ({
      value: i,
      key: topIndex.value + index,
      index: topIndex.value + index,
    }))
);
watchEffect(() => {
  if (!props.paused) {
    topIndex.value = Math.max(0, props.records.length - props.size);
  }
});

watch(
  [() => props.paused, scrollContainer, visibleRecords],
  ([paused, el]) => {
    if (paused || !el) {
      return;
    }

    setTimeout(() => {
      el.scroll({
        top: el.scrollHeight,
        behavior: 'smooth',
      });
    }, 500);
  },
  { deep: true }
);
</script>
