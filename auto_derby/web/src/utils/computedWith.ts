import type { Ref, UnwrapRef } from 'vue';
import { ref, watch } from 'vue';

export default function computedWith<
  T extends Parameters<typeof watch>[0],
  TResult
>(
  source: T,
  cb: (v: T) => TResult,
  { deep }: { deep?: boolean } = {}
): Ref<UnwrapRef<TResult>> {
  const ret = ref(cb(source));
  watch(
    source,
    (v) => {
      ret.value = ref(cb(v)).value;
    },
    { deep }
  );
  return ret;
}
