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
    <template v-for="(i, index) in records" :key="index">
      <ListItem
        class="bg-white rounded"
        :value="i"
        :lineno="index + 1"
      ></ListItem>
    </template>
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
import { ref, toRef, watch } from 'vue';
import ListItem from '@/components/LogViewer/ListItem.vue';

const props = defineProps({
  records: {
    type: Array as PropType<LogRecord[]>,
    required: true,
  },
});
const records = toRef(props, 'records');
const el = ref<
  InstanceType<typeof TransitionGroup> & { $el: HTMLOListElement }
>();

watch(
  [el, records],
  ([el]) => {
    if (!el) {
      return;
    }

    setTimeout(() => {
      el.$el.scroll({
        top: el.$el.scrollHeight,
        behavior: 'smooth',
      });
    }, 500);
  },
  { deep: true }
);
</script>
