<template>
  <div ref="el">
    <figure class="flex items-start bg-checkerboard p-px">
      <img ref="img" :src="value.url" />
      <template v-if="layersExpanded">
        <template v-for="({ name, url }, index) in layers" :key="index">
          <figure>
            <img :src="url" />
            <figcaption>{{ name }}</figcaption>
          </figure>
        </template>
      </template>
      <template v-else>
        <template v-if="selectedLayer">
          <figure>
            <img :src="selectedLayer.url" />
            <figcaption>{{ selectedLayer.name }}</figcaption>
          </figure>
        </template>
        <template
          v-for="{ label, inputAttrs, key } in selectedLayerInputData"
          :key="key"
        >
          <label>
            <input v-bind="inputAttrs" />
            <span>{{ label }}</span>
          </label>
        </template>
      </template>
    </figure>
    <figcaption>{{ value.caption }}</figcaption>
  </div>
</template>

<script setup lang="ts">
import type { ImageRecord } from '@/log-record';
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
const selectedLayer = computed(() => {
  const index = selectedLayerIndex.value;
  const v = layers.value;
  if (index in v) {
    return v[index];
  }
});
const selectedLayerInputData = computed(() =>
  layers.value.map(({ name }, index) => ({
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
const layersExpanded = computed(
  () => width.value * (layers.value.length + 1) < elWidth.value - 2
);
</script>
