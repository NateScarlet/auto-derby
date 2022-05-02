export default function equalArray<T extends unknown[]>(a: T, b: T): boolean {
  if (a.length !== b.length) {
    return false;
  }

  return a.every((v, index) => b[index] === v);
}
