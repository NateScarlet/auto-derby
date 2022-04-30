import type { Ref } from 'vue';
import useEventListener from '@/composables/useEventListener';

export default function useInfiniteScroll<T extends HTMLElement>(
  container: Ref<T | undefined>,
  {
    onScrollToBottom,
    onScrollToTop,
  }: {
    onScrollToTop?: (el: T) => void;
    onScrollToBottom?: (el: T) => void;
  }
): void {
  useEventListener(container, 'scroll', (e) => {
    const el = e.target as T;
    if (el.scrollTop + el.clientHeight === el.scrollHeight) {
      onScrollToBottom?.(el);
    } else if (el.scrollTop === 0) {
      onScrollToTop?.(el);
    }
  });
}
