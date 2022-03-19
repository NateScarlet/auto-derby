import { isDevelopmentMode } from '@/settings';

export default function assertNever(...args: never[]): void {
  if (isDevelopmentMode) {
    // eslint-disable-next-line no-console
    console.warn('assertNever', ...args);
  }
}
