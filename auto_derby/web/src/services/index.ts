import VueMessageService from '@/infrastructure/vue-message-service';
import type MessageService from '@/services/message';

export { MessageService };
export interface Services {
  message: MessageService;
}

function defineServices(v: Services): Services {
  return v;
}

export default defineServices({
  message: new VueMessageService(),
});
