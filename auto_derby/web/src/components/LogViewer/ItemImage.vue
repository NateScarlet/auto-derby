<template>
  <div ref="el">
    <figure
      class="flex flex-wrap items-start bg-checkerboard p-px relative gap-2"
    >
      <img ref="img" :src="selectedLayer.url" />
      <template v-if="expandLayers">
        <template v-for="({ name, url }, index) in layers" :key="index">
          <figure>
            <img :src="url" />
            <figcaption class="text-white bg-black bg-opacity-50 px-1">
              {{ name }}
            </figcaption>
          </figure>
        </template>
      </template>
    </figure>
    <template v-if="!expandLayers">
      <div v-if="selectedLayerInputData.length > 1" class="space-x-1">
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
    </template>
    <figcaption>{{ value.caption }}</figcaption>
  </div>
</template>

<script setup lang="ts">
import type { ImageLayer, ImageRecord } from '@/log-record';
import type { PropType } from 'vue';
import { computed, ref } from 'vue';
import useElementSize from '@/composables/useElementSize';

const props = defineProps({
  value: {
    type: Object as PropType<ImageRecord>,
    required: true,
  },
});
const layers = computed(() => props.value.layers ?? []);

const img = ref<HTMLImageElement>();
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
const { width } = useElementSize(img);
const { width: elWidth } = useElementSize(el);
const expandLayers = computed(() => width.value * 3 < elWidth.value - 20);
</script>
