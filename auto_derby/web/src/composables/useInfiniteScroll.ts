import type { Ref } from 'vue';
import useEventListener from '@/composables/useEventListener';

export default function useInfiniteScroll<T extends HTMLElement>(
  container: Ref<T | undefined>,
  {
    onScrollToBottom,
    onScrollToTop,
    margin = () => 0,
    marginBottom = margin,
    marginTop = margin,
  }: {
    onScrollToTop?: (el: T) => void;
    onScrollToBottom?: (el: T) => void;
    margin?: (el: T) => number;
    marginTop?: (el: T) => number;
    marginBottom?: (el: T) => number;
  }
): void {
  useEventListener(container, 'scroll', (e) => {
    const el = e.target as T;
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - marginBottom(el)) {
      onScrollToBottom?.(el);
    } else if (el.scrollTop < marginTop(el)) {
      onScrollToTop?.(el);
    }
  });
}
