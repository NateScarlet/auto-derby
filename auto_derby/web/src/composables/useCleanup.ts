import { getCurrentInstance, onUnmounted } from 'vue';

export default function useCleanup(): {
  addCleanup: (cb: () => void) => void;
  cleanup: () => void;
} {
  const callbacks: (() => void)[] = [];
  const addCleanup = (cb: () => void) => {
    callbacks.push(cb);
  };
  const cleanup = () => {
    while (callbacks.length > 0) {
      callbacks.pop()?.();
    }
  };

  if (getCurrentInstance()) {
    onUnmounted(cleanup);
  }

  return {
    addCleanup,
    cleanup,
  };
}
