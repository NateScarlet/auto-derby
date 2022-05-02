<template>
  <ol ref="el" class="max-h-screen overflow-y-auto overflow-x-hidden space-y-1">
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
  </ol>
</template>

<script setup lang="ts">
import type { LogRecord } from '@/log-record';
import type { PropType } from 'vue';
import { nextTick, watch, watchEffect, computed, ref, toRef } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';
import computedWith from '@/utils/computedWith';
import useInfiniteScroll from '@/composables/useInfiniteScroll';
import usePause from '@/composables/usePause';
import useTransform from '@/composables/useTransform';
import clamp from '@/utils/clamp';
import { throttle } from 'lodash-es';
import useDebounced from '@/composables/useDebounced';
import useEventListener from '@/composables/useEventListener';
import usePropVModel from '@/composables/usePropVModel';

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
  filter: {
    type: Function as PropType<(v: LogRecord, index: number) => boolean>,
    default: () => true,
  },
});
const emit = defineEmits<{
  (e: 'update:paused', v: boolean): void;
}>();
const paused = usePropVModel({ emit }, props, 'paused');
const records = toRef(props, 'records');

const el = ref<HTMLOListElement>();

const scrollContainer = el;
const totalCountRaw = useDebounced(ref(props.records.length), 100, {
  leading: true,
});
watch(
  () => props.records.length,
  (v) => {
    totalCountRaw.value = v;
  },
  { deep: true }
);
const totalCount = usePause(totalCountRaw, paused);
const topIndex = useTransform(
  ref(0),
  (v) => v,
  (v) => clamp(v, 0, totalCount.value - 1)
);

const itemByIndex = (index: number) => {
  return scrollContainer.value?.querySelector<HTMLLIElement>(
    `li[data-index="${index}"]`
  );
};

const onScrollBackward = () => {
  paused.value = true;
};

useEventListener(scrollContainer, 'wheel', (e) => {
  if (e.deltaY < 0) {
    onScrollBackward();
  }
});

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

const visibleRecords = computedWith(
  [totalCount, topIndex, () => props.filter],
  () => {
    const { records, size, filter } = props;
    const ret: {
      value: LogRecord;
      key: number;
      index: number;
    }[] = [];

    for (let index = topIndex.value; index < records.length; index += 1) {
      if (ret.length === size) {
        break;
      }
      const i = records[index];
      if (!filter(i, index)) {
        continue;
      }
      ret.push({
        value: i,
        key: index,
        index,
      });
    }
    return ret;
  }
);
watchEffect(() => {
  if (!props.paused) {
    topIndex.value = Math.max(0, totalCountRaw.value - props.size);
  }
});

const hasPrevious = computed(() => {
  if (topIndex.value === 0) {
    return false;
  }
  for (let index = 0; index < records.value.length; index += 1) {
    if (index >= topIndex.value) {
      return false;
    }
    const i = records.value[index];
    if (props.filter(i, index)) {
      return true;
    }
  }
  return false;
});
watchEffect(() => {
  if (visibleRecords.value.length < props.size && hasPrevious.value) {
    topIndex.value -= 1;
  }
});
const hasNext = computed(() => {
  if (visibleRecords.value.length === 0) {
    return false;
  }
  const endRecord = visibleRecords.value[visibleRecords.value.length - 1];

  for (
    let index = endRecord.index + 1;
    index < records.value.length;
    index += 1
  ) {
    const i = records.value[index];
    if (props.filter(i, index)) {
      return true;
    }
  }
  return false;
});

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

watch(
  [() => props.paused, scrollContainer, totalCount],
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
