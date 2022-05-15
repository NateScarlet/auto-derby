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
import { watch, nextTick, computed, ref, toRef } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';
import computedWith from '@/utils/computedWith';
import useInfiniteScroll from '@/composables/useInfiniteScroll';
import { throttle } from 'lodash-es';
import usePropVModel from '@/composables/usePropVModel';
import usePolling from '@/composables/usePolling';
import useStabled from '@/composables/useStabled';

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
  endIndex: {
    type: Number,
    default: 0,
  },
});
const emit = defineEmits<{
  (e: 'update:endIndex', v: number): void;
}>();
const loadingCount = ref(0);
const paused = toRef(props, 'paused');
const records = toRef(props, 'records');
const recordByIndex = (index: number): LogRecord | undefined => {
  return records.value[index];
};
const endIndex = useStabled(usePropVModel({ emit }, props, 'endIndex'), 10);
const el = ref<HTMLOListElement>();

const scrollContainer = el;
const totalCount = ref(props.records.length);
usePolling(() => {
  totalCount.value = props.records.length;
});

const itemElement = (index: number) => {
  return (
    scrollContainer.value?.querySelector<HTMLLIElement>(
      `li[data-index="${index}"]`
    ) ?? undefined
  );
};

const visibleRecords = computedWith(
  [totalCount, endIndex, () => props.filter],
  () => {
    const { size, filter } = props;
    const ret: {
      value: LogRecord;
      key: number;
      index: number;
    }[] = [];

    for (let index = endIndex.value; index >= 0; index -= 1) {
      if (ret.length === size) {
        break;
      }
      const i = recordByIndex(index);
      if (i && filter(i, index)) {
        ret.splice(0, 0, {
          value: i,
          key: index,
          index,
        });
      }
    }
    return ret;
  }
);

const offsetEndIndex = (offset: number): void => {
  if (offset === 0) {
    return;
  }
  let newEndIndex = endIndex.value;
  const maxMatchCount = Math.abs(offset);
  let matchCount = 0;
  const direction = offset > 0 ? 1 : -1;
  const { filter } = props;
  for (
    let index = endIndex.value + direction;
    index < totalCount.value && index >= 0;
    index += direction
  ) {
    if (matchCount === maxMatchCount) {
      break;
    }
    const i = recordByIndex(index);
    if (!i) {
      continue;
    }
    if (filter(i, index)) {
      matchCount += 1;
      newEndIndex = index;
    }
  }
  endIndex.value = newEndIndex;
};

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
  offsetEndIndex(offset);

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

const hasPrevious = computed(() => {
  if (endIndex.value === 0) {
    return false;
  }
  const topIndex = visibleRecords.value[0]?.index ?? endIndex.value;
  for (let index = 0; index < topIndex; index += 1) {
    const i = recordByIndex(index);
    if (!i) {
      continue;
    }
    if (props.filter(i, index)) {
      return true;
    }
  }
  return false;
});
const hasNext = computed(() => {
  if (!paused.value) {
    return false;
  }
  if (visibleRecords.value.length === 0) {
    return false;
  }
  for (let index = endIndex.value + 1; index < totalCount.value; index += 1) {
    const i = recordByIndex(index);
    if (!i) {
      continue;
    }
    if (props.filter(i, index)) {
      return true;
    }
  }
  return false;
});

// infinite scroll
watch(endIndex, () => {
  // prevent infinite loop (endIndex -> scroll -> endIndex)
  loadingCount.value += 1;
  setTimeout(() => {
    loadingCount.value -= 1;
  }, 100);
});
const onScrollToTop = () => {
  if (loadingCount.value > 0) {
    return;
  }
  if (!hasPrevious.value) {
    return;
  }
  scrollViewport(-Math.round(props.size / 2));
};
const onScrollToBottom = () => {
  if (loadingCount.value > 0) {
    return;
  }
  if (!hasNext.value) {
    return;
  }
  scrollViewport(Math.round(props.size / 2));
};
useInfiniteScroll(scrollContainer, {
  onScrollToTop,
  onScrollToBottom,
  margin: (el) => Math.min(el.clientHeight * 0.5, el.scrollHeight * 0.2),
});

// auto scroll to end
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
