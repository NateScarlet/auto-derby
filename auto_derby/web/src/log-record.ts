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
  msg: String;
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
