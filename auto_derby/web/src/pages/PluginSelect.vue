<template>
  <div class="max-w-lg m-auto flex flex-col overflow-hidden h-screen">
    <template v-if="isSubmitted">
      <div class="absolute inset-0 flex flex-center bg-white">
        <div>
          <h1 class="text-lg font-bold">Done</h1>
          <p>this page can be closed.</p>
        </div>
      </div>
    </template>
    <div class="flex-auto overflow-auto">
      <template v-if="tab === Tab.PICK">
        <PluginList
          v-model="formData.value"
          :items="pageData.plugins"
          class="h-full"
        ></PluginList>
      </template>
      <template v-else-if="tab === Tab.SORT">
        <PluginSort v-model="formData.value" class="h-full" />
      </template>
      <template v-else> missing tab: {{ tab }} </template>
    </div>
    <form
      class="flex-none flex gap-2 m-1"
      action="javascript:void(0)"
      @submit="submit()"
    >
      <button
        type="button"
        class="rounded p-2 w-1/4"
        v-bind="tabButtonAttrs(Tab.PICK)"
      >
        Pick
      </button>
      <button
        type="button"
        class="rounded p-2 w-1/4"
        v-bind="tabButtonAttrs(Tab.SORT)"
      >
        Sort
      </button>
      <button
        type="submit"
        class="bg-theme-green text-white rounded p-2 font-bold w-1/2"
        :disabled="loadingCount > 0"
      >
        確認
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { PageDataPluginSelect } from '@/page-data';
import type { PropType } from 'vue';
import { ref, reactive } from 'vue';
import PluginList from '@/components/PluginList.vue';
import PluginSort from '@/components/PluginSort.vue';
import withLoading from '@/utils/withLoading';
import pageData from '@/page-data';
import services from '@/services';

const props = defineProps({
  pageData: {
    type: Object as PropType<PageDataPluginSelect>,
    required: true,
  },
});

const formData = reactive({
  value: props.pageData.defaultValue ?? [],
});

enum Tab {
  PICK,
  SORT,
}

const tab = ref(Tab.PICK);

const tabButtonAttrs = (v: Tab) => {
  const isCurrent = v === tab.value;
  return {
    type: 'button' as const,
    class: [isCurrent ? 'border-theme-green bg-white' : ''],
    onClick: () => {
      tab.value = v;
    },
  };
};

const loadingCount = ref(0);
const isSubmitted = ref(false);
const submit = withLoading(loadingCount, async () => {
  const { submitURL = window.location.href } = props.pageData;
  const { value } = formData;
  const resp = await fetch(submitURL, {
    method: 'POST',
    body: JSON.stringify({ value }),
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!(resp.status >= 200 && resp.status < 300)) {
    services.message.error(`submit failed: ${resp.status} ${resp.statusText}`);
    return;
  }
  services.message.info('submitted');
  isSubmitted.value = true;
});
</script>
