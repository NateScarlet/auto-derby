import Sortable from 'sortablejs';
import type { Ref } from 'vue';
import { ref, watch } from 'vue';
import useCleanup from '@/composables/useCleanup';

export type UseSortableOptions = Omit<Sortable.Options, 'store'>;

export default function useSortable(
  el: Ref<HTMLElement | undefined>,
  options: Ref<UseSortableOptions | undefined> = ref()
): {
  sortable: Ref<Sortable | undefined>;
  order: Ref<string[]>;
  sort: <T>(array: T[], id: (v: T, index: number) => string) => void;
  sortRef: <T>(
    array: Ref<readonly T[]>,
    id: (v: T, index: number) => string
  ) => void;
} {
  const { addCleanup, cleanup } = useCleanup();

  const sortable = ref<Sortable>();
  const order = ref<string[]>([]);
  watch([el, options], ([elValue, o]) => {
    cleanup();
    if (!elValue) {
      sortable.value = undefined;
      return;
    }
    const s = new Sortable(elValue, {
      ...o,
      store: {
        get() {
          return order.value;
        },
        set(v) {
          order.value = v.toArray();
        },
      },
    });
    addCleanup(() => s.destroy());
    sortable.value = s;
  });

  const sort = <T>(array: T[], id: (v: T, index: number) => string): void => {
    const currentOrder = array.map(id);
    const orig = array.slice();
    order.value.forEach((i, newIndex) => {
      const oldIndex = currentOrder.indexOf(i);
      if (oldIndex < 0) {
        return;
      }
      array[newIndex] = orig[oldIndex];
    });
  };

  const sortRef = <T>(
    array: Ref<readonly T[]>,
    id: (v: T, index: number) => string
  ): void => {
    const arr = array.value.slice();
    sort(arr, id);
    array.value = arr;
  };

  return {
    sortable,
    order,
    sort,
    sortRef,
  };
}
