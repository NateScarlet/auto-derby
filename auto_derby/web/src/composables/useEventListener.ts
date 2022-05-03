import type { Ref } from 'vue';
import { watch } from 'vue';
import useCleanup from '@/composables/useCleanup';

export interface EventTarget<Args extends unknown[]> {
  addEventListener(...args: Args): void;
  removeEventListener(...args: Args): void;
}

function useEventListener<K extends keyof WindowEventMap>(
  target: Ref<Window | undefined>,
  type: K,
  listener: (this: Window, ev: WindowEventMap[K]) => unknown,
  options?: boolean | EventListenerOptions
): void;
function useEventListener<K extends keyof DocumentEventMap>(
  target: Ref<Document | undefined>,
  type: K,
  listener: (this: Document, ev: DocumentEventMap[K]) => unknown,
  options?: boolean | EventListenerOptions
): void;
function useEventListener<K extends keyof HTMLElementEventMap>(
  target: Ref<HTMLElement | undefined>,
  type: K,
  listener: (this: Document, ev: HTMLElementEventMap[K]) => unknown,
  options?: boolean | EventListenerOptions
): void;
function useEventListener<Args extends unknown[]>(
  target: Ref<EventTarget<Args> | undefined>,
  ...args: Args
): void;
function useEventListener<Args extends unknown[]>(
  target: Ref<EventTarget<Args> | undefined>,
  ...args: Args
): void {
  const { addCleanup, cleanup } = useCleanup();

  watch(
    target,
    (v) => {
      cleanup();
      if (!v) {
        return;
      }
      v.addEventListener(...args);
      addCleanup(() => {
        v.removeEventListener(...args);
      });
    },
    { immediate: true }
  );
}

export default useEventListener;
