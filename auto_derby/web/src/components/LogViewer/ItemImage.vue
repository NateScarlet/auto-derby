<template>
  <div ref="el">
    <div class="flex flex-wrap items-start bg-checkerboard p-px relative gap-2">
      <template v-if="expandLayers">
        <img :src="mainLayer.url" />
        <template v-for="({ name, url }, index) in layers" :key="index">
          <figure>
            <img :src="url" />
            <figcaption class="text-white bg-black bg-opacity-50 px-1">
              {{ name }}
            </figcaption>
          </figure>
        </template>
      </template>
      <template v-else>
        <img :src="selectedLayer.url" class="bg-checkerboard p-px" />
      </template>
    </div>
    <div
      v-if="!expandLayers && selectedLayerInputData.length > 1"
      class="space-x-1"
    >
      <template
        v-for="{ label, inputAttrs, key } in selectedLayerInputData"
        :key="key"
      >
        <label>
          <input v-bind="inputAttrs" />
          <span>{{ label }}</span>
        </label>
      </template>
    </div>
    <div>{{ value.caption }}</div>
  </div>
</template>

<script setup lang="ts">
import type { ImageLayer, ImageRecord } from '@/log-record';
import type { PropType } from 'vue';
import { computed, ref } from 'vue';
import useElementSize from '@/composables/useElementSize';
import useImageURL from '@/composables/useImageURL';

const props = defineProps({
  value: {
    type: Object as PropType<ImageRecord>,
    required: true,
  },
});
const layers = computed(() => props.value.layers ?? []);

const el = ref<HTMLElement>();
const selectedLayerIndex = ref(0);
const mainLayer = computed<ImageLayer>(() => ({
  name: 'main',
  url: props.value.url,
}));
const selectedLayer = computed(() => {
  const index = selectedLayerIndex.value - 1;
  const v = layers.value;
  if (index in v) {
    return v[index];
  }
  return mainLayer.value;
});
const selectedLayerInputData = computed(() =>
  [mainLayer.value, ...layers.value].map(({ name }, index) => ({
    key: index,
    label: name,
    inputAttrs: {
      type: 'radio' as const,
      checked: selectedLayerIndex.value === index,
      onChange: (e: Event) => {
        const el = e.target as HTMLInputElement;
        if (el.checked) {
          selectedLayerIndex.value = index;
        }
      },
    },
  }))
);
const width = useImageURL(() => mainLayer.value.url).width();
const { width: elWidth } = useElementSize(el);
const expandLayers = computed(() => width.value * 3 < elWidth.value - 20);
</script>
