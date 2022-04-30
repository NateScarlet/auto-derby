export default function clamp(v: number, min: number, max: number): number {
  if (max <= min) {
    return min;
  }
  return Math.min(Math.max(v, min), max);
}
