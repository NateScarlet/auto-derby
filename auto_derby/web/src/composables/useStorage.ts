import type { Ref, UnwrapRef } from 'vue';
import { ref, watch } from 'vue';
import useCleanup from '@/composables/useCleanup';

export type StorageLike = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

function useStorage<T>(
  storage: StorageLike,
  key: string,
  default_: T
): Ref<UnwrapRef<T>>;
function useStorage<T>(
  storage: StorageLike,
  key: string,
  default_?: T
): Ref<UnwrapRef<T> | undefined> {
  const { addCleanup } = useCleanup();
  const ret = ref<T | undefined>(default_);
  const load = () => {
    const value = storage.getItem(key);
    if (value != null) {
      ret.value = JSON.parse(value);
    }
  };
  load();
  const onStorage = (e: StorageEvent) => {
    if (e.storageArea !== storage || e.key !== key) {
      return;
    }
    load();
  };
  window.addEventListener('storage', onStorage);
  addCleanup(() => window.removeEventListener('storage', onStorage));
  watch(
    ret,
    (v) => {
      if (v == null) {
        storage.removeItem(key);
      } else {
        storage.setItem(key, JSON.stringify(v));
      }
    },
    { deep: true }
  );

  return ret;
}

export default useStorage;
