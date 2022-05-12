<template>
  <li>
    <div>{{ value.name }}</div>
    <div class="whitespace-pre">{{ value.doc }}</div>
    <div>
      <input v-model="localSelected" type="checkbox" />
    </div>
  </li>
</template>

<script setup lang="ts">
import usePropVModel from '@/composables/usePropVModel';
import type { Plugin } from '@/page-data';
import type { PropType } from 'vue';

const props = defineProps({
  value: {
    type: Object as PropType<Plugin>,
    required: true,
  },
  selected: {
    type: Boolean,
  },
});
const emit = defineEmits<{
  (e: 'update:selected', v: boolean): void;
}>();
const localSelected = usePropVModel({ emit }, props, 'selected');
</script>
