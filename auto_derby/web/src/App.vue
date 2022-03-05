<template>
  <div class="bg-gray-200 text-theme-text min-h-screen">
    <component :is="page.component" :page-data="pageData"></component>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';
import pageData, { PageType } from '@/page-data';
import DefaultPageVue from '@/pages/DefaultPage.vue';
import SingleModeItemSelectVue from '@/pages/SingleModeItemSelect.vue';

interface Page {
  component: Component;
}

const pages = new Map<PageType, Page>([
  [PageType.SINGLE_MODE_ITEM_SELECT, { component: SingleModeItemSelectVue }],
]);

const page: Page = pages.get(pageData.type) ?? {
  component: DefaultPageVue,
};
</script>
