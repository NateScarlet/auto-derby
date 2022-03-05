<template>
  <div class="max-w-lg m-auto space-y-2">
    <div class="text-center bg-white sticky top-0">
      <p>select matching item for this image:</p>
      <img :src="pageData.imageURL" class="sticky m-auto" />
      <form
        :action="pageData.submitURL"
        method="POST"
        class="flex items-center justify-center gap-2 mx-2"
      >
        <label>
          <span class="bg-gray-200 mx-2 rounded-full px-4">id</span>
          <input
            v-model.number="formData.id"
            type="number"
            name="id"
            class="spin-button-none w-16 text-center"
          />
        </label>
        <SingleModeItem
          :value="currentOption"
          class="inline-block border border-gray-200 flex-auto rounded px-2"
        ></SingleModeItem>
        <button
          type="submit"
          class="bg-theme-green text-white rounded p-2 font-bold"
        >
          確認
        </button>
      </form>
    </div>
    <ul class="space-y-2">
      <li
        v-for="i in pageData.options"
        :key="i.id"
        class="bg-white rounded border border-gray-200 p-2"
        @click="formData.id = i.id"
      >
        <SingleModeItem :value="i"></SingleModeItem>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed, reactive } from 'vue';
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
const formData = reactive({
  id: pageData.defaultValue,
});

const currentOption = computed(
  () =>
    pageData.options.find((i) => i.id === formData.id) ?? {
      id: formData.id,
      name: 'unknown',
      description: 'unknown',
    }
);
</script>
