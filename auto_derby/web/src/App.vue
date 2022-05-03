<template>
  <div class="bg-gray-200 text-theme-text min-h-screen">
    <div class="absolute top-0 right-0 text-gray-400 hidden lg:block">
      {{ version }}
    </div>
    <component :is="page.component" :page-data="pageData"></component>
    <MessageList class="messages z-20"></MessageList>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';
import pageData, { PageType } from '@/page-data';
import DefaultPageVue from '@/pages/DefaultPage.vue';
import SingleModeItemSelectVue from '@/pages/SingleModeItemSelect.vue';
import LogPageVue from '@/pages/LogPage.vue';
import { MessageList } from '@/infrastructure/vue-message-service';

const version = __VERSION__;
interface Page {
  component: Component;
}

const pages = new Map<PageType, Page>([
  [PageType.SINGLE_MODE_ITEM_SELECT, { component: SingleModeItemSelectVue }],
  [PageType.LOG, { component: LogPageVue }],
]);

const page: Page = pages.get(pageData.type) ?? {
  component: DefaultPageVue,
};
</script>
