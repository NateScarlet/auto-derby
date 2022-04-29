import VueMessageService from '@/infrastructure/vue-message-service';
import type MessageService from '@/services/message';

export { MessageService };
export interface Application {
  message: MessageService;
}
export function defineApplication(v: Application): Application {
  return v;
}

const app = defineApplication({
  message: new VueMessageService(),
});
export default app;
