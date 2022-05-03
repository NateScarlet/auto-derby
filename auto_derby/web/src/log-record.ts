import assertNever from '@/utils/assertNever';

export enum RecordType {
  TEXT = 'TEXT',
  IMAGE = 'IMAGE',
}

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}
export interface AbstractRecord {
  /** iso8601 timestamp */
  ts: string;
  lv: LogLevel;
  t: RecordType;
  source?: string;
}

export interface TextRecord extends AbstractRecord {
  t: RecordType.TEXT;
  msg: string;
}

export interface ImageLayer {
  name: string;
  url: string;
}

export interface ImageRecord extends AbstractRecord {
  t: RecordType.IMAGE;
  url: string;
  caption: string;
  layers?: ImageLayer[];
}

export type LogRecord = Readonly<TextRecord | ImageRecord>;

export function searchKeys(v: LogRecord): string[] {
  const { t, source } = v;
  const ret: string[] = [];
  if (source) {
    ret.push(source);
  }
  switch (t) {
    case RecordType.TEXT:
      ret.push(v.msg);
      break;
    case RecordType.IMAGE:
      ret.push(v.caption, ...(v.layers?.map((i) => i.name) ?? []));
      break;
    default:
      assertNever(t);
  }
  return ret;
}
