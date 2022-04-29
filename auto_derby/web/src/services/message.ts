export default interface MessageService {
  info(msg: string): void;
  error(msg: string): void;
}
