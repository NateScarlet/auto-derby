import type { Ref } from 'vue';
import { computed } from 'vue';
import equalArray from '@/utils/equalArray';

export interface Encoding<T> {
  decode: (s: string) => T;
  encode: (v: T) => string;
}

export default function useStringArray(array: Ref<string[]>) {
  const toggle = (
    item: string,
    force?: boolean,
    { prepend = false }: { prepend?: boolean } = {}
  ) => {
    const current = array.value.includes(item);
    const wanted = force ?? !current;
    if (current === wanted) {
      return;
    }
    if (wanted) {
      array.value = prepend ? [item, ...array.value] : [...array.value, item];
    } else {
      array.value = array.value.filter((i) => i !== item);
    }
  };

  const toSingle = (defaultValue: string = '') =>
    computed({
      get() {
        return array.value[0] ?? defaultValue;
      },
      set(v: string) {
        array.value = v ? [v] : [];
      },
    });

  const to2DArray = (unitSeparator: string = '\x1f') =>
    computed({
      get() {
        return array.value.map((i) => i.split(unitSeparator));
      },
      set(v: string[][]) {
        const n = v.map((i) => i.join(unitSeparator));
        if (equalArray(array.value, n)) {
          return;
        }
        array.value = n;
      },
    });

  const toBoolean = ({
    trueValue = '1',
    isTrue = (v) => v !== '0',
  }: {
    trueValue?: string;
    isTrue?: (v: string) => boolean;
  } = {}) =>
    computed({
      get() {
        return array.value.some((i) => isTrue(i));
      },
      set(v: boolean) {
        array.value = v ? [trueValue] : [];
      },
    });

  const toEnum = <T extends string>(validValues: T[]) =>
    computed({
      get(): T {
        return (
          validValues.find((i) => array.value.includes(i)) ?? validValues[0]
        );
      },
      set(v: T) {
        array.value = [v];
      },
    });
  const toFlags = <T extends string>(validValues: T[]) =>
    computed({
      get(): T[] {
        return validValues.filter((i) => array.value.includes(i));
      },
      set(v: T[]) {
        array.value = v;
      },
    });

  const toDecoded = <T>(encoding: Encoding<T>) =>
    computed({
      get(): T[] {
        return array.value.map((i) => encoding.decode(i));
      },
      set(v: T[]) {
        const n = v.map((i) => encoding.encode(i));
        if (equalArray(array.value, n)) {
          return;
        }
        array.value = n;
      },
    });

  return {
    toggle,
    toSingle,
    to2DArray,
    toDecoded,
    toBoolean,
    toEnum,
    toFlags,
  };
}
