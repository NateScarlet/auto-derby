// spell-checker: words ponyfill
import { ResizeObserver as ResizeObserverPonyfill } from '@juggle/resize-observer';

function getResizeObserver() {
  if (typeof ResizeObserver === 'undefined') {
    return ResizeObserverPonyfill;
  }
  return ResizeObserver;
}

export default function addResizeListener(
  el: Element,
  fn: (entry: ResizeObserverEntry) => void
): () => void {
  const Observer = getResizeObserver();
  const ob = new Observer((entries): void => {
    entries.forEach((i) => {
      fn(i);
    });
  });
  ob.observe(el);
  return (): void => ob.disconnect();
}
