import { debounce } from 'lodash-es';
import type { Ref } from 'vue';
import { computed, ref, watch } from 'vue';

export default function useStabled<T>(
  value: Ref<T>,
  minChangeInterval: number
): Ref<T> {
  const buffer = ref(value.value) as Ref<T>;
  const setValue = debounce(
    (v: T) => {
      buffer.value = v;
    },
    minChangeInterval,
    { trailing: true }
  );
  watch(value, (v) => {
    setValue(v);
  });
  return computed({
    get() {
      return buffer.value;
    },
    set(newValue: T) {
      value.value = newValue;
    },
  });
}
