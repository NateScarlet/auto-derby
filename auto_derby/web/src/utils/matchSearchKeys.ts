export default function matchSearchKeys(
  query: string,
  searchKeys: string[]
): boolean {
  return query
    .toLowerCase()
    .split(' ')
    .every((keyword) =>
      searchKeys.some((key) => key.toLowerCase().includes(keyword))
    );
}
