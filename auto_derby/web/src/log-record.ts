export enum RecordType {
  TEXT = 'TEXT',
  IMAGE = 'IMAGE',
}

export interface AbstractRecord {
  t: RecordType;
  /** iso8601 timestamp */
  ts: string;
}

export interface TextRecord extends AbstractRecord {
  t: RecordType.TEXT;
  msg: String;
}

export interface ImageRecord extends AbstractRecord {
  t: RecordType.IMAGE;
  url: string;
  caption: string;
}

export type LogRecord = Readonly<TextRecord | ImageRecord>;
