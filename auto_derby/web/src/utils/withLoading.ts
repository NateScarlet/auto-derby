import type { Ref } from 'vue';

export default function withLoading<TArgs extends unknown[], TReturn>(
  loadingCount: Ref<number>,
  fn: (...args: TArgs) => TReturn
): (...args: TArgs) => TReturn {
  return (...args) => {
    loadingCount.value += 1;
    let isAsync = false;
    try {
      const ret = fn(...args);
      if (ret instanceof Promise) {
        isAsync = true;
        ret.finally(() => {
          loadingCount.value -= 1;
        });
      }
      return ret;
    } finally {
      if (!isAsync) {
        loadingCount.value -= 1;
      }
    }
  };
}
