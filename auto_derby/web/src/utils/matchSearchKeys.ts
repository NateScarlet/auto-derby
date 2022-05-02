export default function matchSearchKeys(
  query: string,
  searchKeys: string[]
): boolean {
  return query
    .split(' ')
    .every((keyword) => searchKeys.some((key) => key.includes(keyword)));
}
