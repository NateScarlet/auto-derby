export default async function loadImage(
  url: string
): Promise<HTMLImageElement> {
  const img = new Image();
  img.src = url;
  img.alt = url;
  await img.decode();
  return img;
}
