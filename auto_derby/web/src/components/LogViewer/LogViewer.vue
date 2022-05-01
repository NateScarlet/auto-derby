<template>
  <TransitionGroup
    ref="el"
    class="max-h-screen overflow-y-auto overflow-x-hidden space-y-1"
    tag="ol"
    v-bind="transitionGroupAttrs"
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
        <p>waiting for record</p>
      </div>
    </div>
  </TransitionGroup>
</template>

<script setup lang="ts">
import type { LogRecord } from '@/log-record';
import type { PropType, TransitionGroup } from 'vue';
import { nextTick, watch, watchEffect, computed, ref, toRef } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';
import computedWith from '@/utils/computedWith';
import useInfiniteScroll from '@/composables/useInfiniteScroll';
import usePause from '@/composables/usePause';
import useTransform from '@/composables/useTransform';
import clamp from '@/utils/clamp';
import { throttle } from 'lodash-es';

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

const transitionGroupAttrs = computed(() => {
  if (props.paused) {
    return;
  }
  return {
    enterFromClass: 'opacity-0 transform translate-x-8',
    enterActiveClass: 'transition-all ease-in-out duration-500 relative',
    enterToClass: 'opacity-100',
    leaveFromClass: 'h-full max-h-fit',
    leaveToClass: 'h-0',
    leaveActiveClass: 'transition-all ease-in-out duration-500 overflow-hidden',
  };
});
const el = ref<
  InstanceType<typeof TransitionGroup> & { $el: HTMLOListElement }
>();

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
const topIndex = useTransform(
  ref(0),
  (v) => v,
  (v) => clamp(v, 0, totalCount.value - 1)
);
const hasPrevious = computed(() => {
  return topIndex.value > 0;
});
const hasNext = computed(() => {
  return topIndex.value < totalCount.value - props.size;
});

const itemByIndex = (index: number) => {
  return scrollContainer.value?.querySelector<HTMLLIElement>(
    `li[data-index="${index}"]`
  );
};

const scrollViewport = (offset: number) => {
  if (offset === 0) {
    return;
  }
  const topIndexBefore = topIndex.value;
  topIndex.value += offset;
  const topIndexAfter = topIndex.value;
  const actualOffset = topIndexAfter - topIndexBefore;
  if (actualOffset < 0) {
    nextTick(() => {
      const itemBefore = itemByIndex(topIndexBefore);
      const itemAfter = itemByIndex(topIndexAfter);
      const el = scrollContainer.value;

      if (itemAfter && itemBefore && el) {
        el.scrollTop -= itemAfter.offsetTop - itemBefore.offsetTop;
      }
    });
  }
};

const onScrollToTop = throttle(() => {
  if (!hasPrevious.value) {
    return;
  }
  scrollViewport(-Math.round(props.size / 2));
}, 100);
const onScrollToBottom = throttle(() => {
  if (!hasNext.value) {
    return;
  }
  scrollViewport(Math.round(props.size / 2));
}, 100);

useInfiniteScroll(scrollContainer, {
  onScrollToTop,
  onScrollToBottom,
  margin: (el) => Math.min(200, el.offsetHeight * 0.3),
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

    nextTick(() => {
      el.scroll({
        top: el.scrollHeight,
        behavior: 'smooth',
      });
    });
  },
  { deep: true }
);
</script>
