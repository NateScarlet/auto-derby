<template>
  <form action="javascript:void(0)" @submit="submit()">
    <PluginList v-model="formData.value" :items="pageData.plugins"></PluginList>
    <button
      type="submit"
      class="bg-theme-green text-white rounded p-2 font-bold"
    >
      確認
    </button>
  </form>
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
