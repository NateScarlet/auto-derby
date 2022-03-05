<template>
  <div class="max-w-lg m-auto">
    <form :action="pageData.submitURL" method="POST">
      <button type="submit">submit</button>
    </form>
    <ul class="space-y-2">
      <li
        v-for="i in pageData.options"
        :key="i.id"
        class="bg-white rounded border border-gray-200 p-2"
      >
        <SingleModeItem :value="i"></SingleModeItem>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import type { PageDataSingleModeItemSelect } from '@/page-data';
import pageData from '@/page-data';
import SingleModeItem from '@/components/SingleModeItem.vue';
const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataSingleModeItemSelect>,
    required: true,
  },
});
const _ = props;
</script>
