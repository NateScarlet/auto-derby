import type { MessageService } from '@/services';
import { isDevelopmentMode } from '@/settings';
import type { VNode } from 'vue';
import { TransitionGroup, defineComponent, h, reactive } from 'vue';

const listData = reactive({
  messages: [] as {
    key: number;
    render: () => VNode;
  }[],
});

export const MessageList = defineComponent<
  Record<string, unknown>,
  typeof listData
>({
  name: 'MessageList',
  data() {
    return listData;
  },
  render() {
    return h(
      TransitionGroup,
      {
        class: 'fixed top-0 w-screen flex flex-col items-center',
        appear: true,
        tag: 'ol',
        moveClass: 'transition ease-in-out duration-200',
        enterActiveClass: 'transition ease-in-out duration-300',
        enterFromClass: 'opacity-0 transform -translate-y-full',
        leaveActiveClass: 'transition ease-in-out duration-1000 absolute',
        leaveToClass: 'transform -translate-y-full',
      },
      () =>
        this.messages.map((i) => {
          const ret = i.render();
          ret.key = i.key;
          return ret;
        })
    );
  },
});

let nextKey = 0;

/**
 * add a message to list using render function.
 * @param render message render function
 * @returns message close function.
 */
export function message(render: () => VNode): () => void {
  const key = nextKey;
  nextKey += 1;

  listData.messages.splice(0, 0, { key, render });
  return () => {
    const index = listData.messages.findIndex((i) => i.key === key);
    if (index < 0) {
      return;
    }
    listData.messages.splice(index, 1);
  };
}

export default class VueMessageService implements MessageService {
  info(text: string, duration = Math.min(3000, text.length * 200)): void {
    const close = message(() =>
      h(
        'li',
        {
          class: [
            'p-2 rounded max-w-md w-full shadow min-h-12 mt-2',
            'border-2 border-theme-toast',
            'flex flex-center',
            'bg-gray-50 text-theme-text break-all font-bold',
          ],
        },
        text
      )
    );
    setTimeout(close, duration);
  }

  error(text: string, duration = Math.min(3000, text.length * 200)): void {
    const close = message(() =>
      h(
        'li',
        {
          class: [
            'p-2 rounded max-w-md w-full shadow min-h-12 mt-2',
            'border-2 border-red-400',
            'flex flex-center',
            'bg-red-50 text-theme-text break-all font-bold',
          ],
        },
        text
      )
    );
    setTimeout(close, duration);
  }
}

if (isDevelopmentMode) {
  const s = new VueMessageService();
  s.info('test info');
  setTimeout(() => {
    s.error('test error');
  }, 1e3);
}
