import type { Ref } from 'vue';
import { computed } from 'vue';

export default function useTransform<TIn, TOut>(
  value: Ref<TIn>,
  transformGet: (v: TIn) => TOut,
  transformSet: (v: TOut) => TIn = (v) => v as unknown as TIn
) {
  return computed({
    get() {
      return transformGet(value.value);
    },
    set(v: TOut) {
      value.value = transformSet(v);
    },
  });
}
