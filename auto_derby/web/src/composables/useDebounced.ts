import type { Ref } from 'vue';
import { computed } from 'vue';
import type { DebounceSettings } from 'lodash-es';
import { debounce } from 'lodash-es';

export default function useDebounced<T>(
  value: Ref<T>,
  wait?: number,
  options?: DebounceSettings
): Ref<T> {
  return computed({
    get() {
      return value.value;
    },
    set: debounce(
      (v: T) => {
        value.value = v;
      },
      wait,
      options
    ),
  });
}
