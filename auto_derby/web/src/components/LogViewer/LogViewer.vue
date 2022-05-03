<template>
  <ol
    ref="el"
    class="max-h-screen overflow-x-hidden space-y-1"
    :class="[paused ? 'overflow-y-auto' : 'overflow-y-hidden']"
  >
    <template v-if="hasPrevious">
      <button
        type="button"
        class="w-full text-blue-500 underline"
        @click="onScrollToTop()"
      >
        load more records
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
        load more records
      </button>
    </span>
    <div v-if="visibleRecords.length === 0" class="flex flex-center h-full">
      <div class="text-center">
        <h1 class="text-2xl">Log Viewer</h1>
        <p v-if="!paused">waiting for record</p>
        <p v-else>no matched record</p>
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
import { throttle } from 'lodash-es';
import usePropVModel from '@/composables/usePropVModel';
import usePolling from '@/composables/usePolling';
import useDebounced from '@/composables/useDebounced';

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
// avoid update too fast when reading from buffer.
const totalCountRaw = useDebounced(ref(props.records.length), 50);
watch(
  () => props.records.length,
  (v) => {
    totalCountRaw.value = v;
  },
  { deep: true }
);
const totalCount = usePause(totalCountRaw, paused);
const topIndex = ref(0);
const itemElement = (index: number) => {
  return scrollContainer.value?.querySelector<HTMLLIElement>(
    `li[data-index="${index}"]`
  );
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

const scrollAnchorElement = () => {
  let ret: HTMLElement | undefined;
  const container = scrollContainer.value;
  if (!container) {
    return ret;
  }
  visibleRecords.value.some((i) => {
    const el = itemElement(i.index);
    if (!el) {
      return false;
    }
    if (container.scrollTop <= el.offsetTop) {
      ret = el;
      return true;
    }
    return false;
  });
  return ret;
};
const scrollViewport = throttle((offset: number) => {
  if (offset === 0) {
    return;
  }
  topIndex.value += offset;

  // recover scroll position
  const el = scrollContainer.value;
  if (!el) {
    return;
  }
  const anchorEl = scrollAnchorElement();
  if (!anchorEl) {
    return;
  }
  // scroll top relative to anchor
  const anchorTop = el.scrollTop - anchorEl.offsetTop;
  nextTick(() => {
    el.scrollTop = anchorEl.offsetTop + anchorTop;
  });
}, 100);

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
  if (!paused.value) {
    return false;
  }
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

const onScrollToTop = () => {
  if (!hasPrevious.value) {
    return;
  }
  scrollViewport(-Math.round(props.size / 2));
};
const onScrollToBottom = () => {
  if (!hasNext.value) {
    return;
  }
  scrollViewport(Math.round(props.size / 2));
};

useInfiniteScroll(scrollContainer, {
  onScrollToTop,
  onScrollToBottom,
  margin: (el) => Math.min(el.clientHeight * 3, el.scrollHeight * 0.2),
});

usePolling(() => {
  if (paused.value) {
    return;
  }
  const el = scrollContainer.value;
  if (!el) {
    return;
  }

  // manual smooth scroll, browsers has different behavior
  el.scrollTop = el.scrollTop * 0.6 + (el.scrollHeight - el.offsetHeight) * 0.4;
});
</script>
