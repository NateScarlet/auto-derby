export default function limitTextLength(s: string, maxLength: number): string {
  if (s.length <= maxLength) {
    return s;
  }

  const extraLength = s.length - maxLength;
  const extraLengthText = `(${extraLength} more)`;
  const extraLength2 = extraLength + extraLengthText.length;
  const extraLengthText2 = `(${extraLength2} more)`;
  return s.slice(0, maxLength - extraLengthText.length) + extraLengthText2;
}
