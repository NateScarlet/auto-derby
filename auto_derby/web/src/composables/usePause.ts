import type { Ref, UnwrapRef } from 'vue';
import { watch, ref } from 'vue';

export default function usePause<T>(
  value: Ref<T>,
  paused: Ref<boolean>
): Ref<UnwrapRef<T>> {
  const ret = ref(value.value);
  watch([value, paused], ([v, paused]) => {
    if (paused) {
      return;
    }
    ret.value = ref(v).value;
  });
  return ret;
}
