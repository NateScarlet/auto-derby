export default function compare<T>(a: T, b: T): -1 | 0 | 1 {
  if (a > b) {
    return 1;
  }
  if (a < b) {
    return -1;
  }
  return 0;
}
