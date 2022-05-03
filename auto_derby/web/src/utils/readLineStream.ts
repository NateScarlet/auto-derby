export default async function readLineStream({
  stream,
  encoding = 'utf-8',
  onLine,
}: {
  stream: ReadableStream<Uint8Array>;
  encoding?: string;
  onLine: (line: string) => Promise<void> | void;
}): Promise<void> {
  const reader = stream.getReader();
  let b = '';
  const decoder = new TextDecoder(encoding);
  async function read() {
    const { value, done } = await reader.read();
    if (done) {
      if (b) {
        await onLine(b);
      }
      return;
    }
    const text = decoder.decode(value);

    let p = 0;
    for (let i = 0; i < text.length; i += 1) {
      const c = text[i];
      if (c === '\n') {
        // eslint-disable-next-line no-await-in-loop
        await onLine(b + text.slice(p, i));
        p = i + 1;
        b = '';
      }
    }
    b += text.slice(p);
    await read();
  }
  await read();
}
