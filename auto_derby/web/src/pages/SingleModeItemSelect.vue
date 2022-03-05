<template>
  <div class="max-w-lg m-auto space-y-2">
    <div class="bg-gray-200 sticky top-0 space-y-2">
      <div class="text-center bg-white p-1 rounded">
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
              v-model.number="inputData.id"
              type="number"
              name="id"
              class="spin-button-none w-16 text-center"
            />
          </label>
          <SingleModeItemVue
            :value="currentOption"
            class="inline-block border border-gray-200 flex-auto rounded px-2"
            id-hidden
          ></SingleModeItemVue>
          <button
            type="submit"
            class="bg-theme-green text-white rounded p-2 font-bold"
          >
            確認
          </button>
        </form>
      </div>
      <label class="w-full flex items-center">
        <svg class="inline align-top fill-current h-8" viewBox="0 0 24 24">
          <path :d="mdiMagnify"></path>
        </svg>
        <input
          v-model="inputData.q"
          class="flex-auto"
          type="search"
          placeholder="search"
        />
      </label>
    </div>
    <ul class="space-y-2">
      <li
        v-for="{ key, attrs, value } in listData"
        :key="key"
        class="bg-white rounded p-2"
        v-bind="attrs"
      >
        <SingleModeItemVue :value="value"></SingleModeItemVue>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';
import { computed, reactive } from 'vue';
import type { PageDataSingleModeItemSelect, SingleModeItem } from '@/page-data';
import pageData from '@/page-data';
import SingleModeItemVue from '@/components/SingleModeItem.vue';

import { mdiMagnify } from '@mdi/js';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataSingleModeItemSelect>,
    required: true,
  },
});
const _ = props;
const inputData = reactive({
  id: pageData.defaultValue,
  q: '',
});

function itemSearchKeys(i: SingleModeItem): string[] {
  return [i.name, i.description];
}

const listData = computed(() =>
  pageData.options
    .filter((i) => itemSearchKeys(i).some((j) => j.includes(inputData.q)))
    .map((i) => {
      const isSelected = i.id === inputData.id;
      return {
        key: i.id,
        value: i,
        attrs: {
          class: [
            'border border-2 cursor-pointer',
            isSelected ? 'border-theme-green' : 'border-gray-200',
          ],
          onClick: () => {
            inputData.id = i.id;
          },
        },
      };
    })
);

const currentOption = computed(
  () =>
    pageData.options.find((i) => i.id === inputData.id) ?? {
      id: inputData.id,
      name: 'unknown',
      description: 'unknown',
    }
);
</script>
