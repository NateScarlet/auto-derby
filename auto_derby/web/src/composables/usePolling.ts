import useCleanup from '@/composables/useCleanup';

export default function usePolling(
  cb: () => Promise<void> | void,
  scheduleNext: (next: () => void) => void = requestAnimationFrame
) {
  const { addCleanup } = useCleanup();
  let isStopped = false;

  const stop = () => {
    isStopped = true;
  };
  addCleanup(stop);

  const run = async () => {
    if (isStopped) {
      return;
    }
    await cb();
    scheduleNext(run);
  };
  run();

  return { stop };
}
