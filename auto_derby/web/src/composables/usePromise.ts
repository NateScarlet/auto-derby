import type { Ref, UnwrapRef } from 'vue';
import { ref, watch } from 'vue';

interface UsePromiseOption {
  keepLatest?: boolean;
}

function usePromise<T>(
  v: Ref<Promise<T>>,
  d: Ref<T>,
  o?: UsePromiseOption
): Ref<UnwrapRef<T>>;
function usePromise<T>(
  v: Ref<Promise<T>>,
  d?: undefined,
  o?: UsePromiseOption
): Ref<UnwrapRef<T> | undefined>;
function usePromise<T>(
  v: Ref<Promise<T>>,
  d: Ref<T> | undefined = undefined,
  { keepLatest = false }: UsePromiseOption = {}
): Ref<UnwrapRef<T> | undefined> {
  const ret = ref<T | undefined>(d?.value);

  watch(
    v,
    (n) => {
      if (!keepLatest) {
        ret.value = ref(d?.value).value;
      }
      n.then((value) => {
        if (v.value !== n) {
          // outdated
          return;
        }
        ret.value = ref(value).value;
      });
    },
    {
      immediate: true,
    }
  );

  return ret;
}

export default usePromise;
