<template>
  <div class="max-w-lg m-auto flex flex-col overflow-hidden h-screen">
    <PluginList
      v-model="formData.value"
      :items="pageData.plugins"
      class="flex-auto overflow-auto"
    ></PluginList>
    <form class="flex-none" action="javascript:void(0)" @submit="submit()">
      <button
        type="submit"
        class="bg-theme-green text-white rounded p-2 font-bold w-full"
      >
        確認
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { PageDataPluginSelect } from '@/page-data';
import type { PropType } from 'vue';
import { reactive } from 'vue';
import PluginList from '@/components/PluginList.vue';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataPluginSelect>,
    required: true,
  },
});

const formData = reactive({
  value: props.pageData.defaultValue ?? [],
});

const submit = () => {
  // TODO
};
</script>
