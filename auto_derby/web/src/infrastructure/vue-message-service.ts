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
        class:
          'fixed top-2 w-screen flex flex-col items-center pointer-events-none',
        appear: true,
        tag: 'ol',
        enterActiveClass: 'transition-all ease-in-out duration-300 absolute',
        enterFromClass: 'transform -translate-y-full -mt-4',
        leaveActiveClass: 'transition-all ease-int-out duration-300 absolute',
        leaveToClass: 'transform -translate-y-full -mt-4',
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
const pendingMessages = [] as {
  render: () => VNode;
  onAppear: (close: () => void) => void;
}[];

let isProcessing = false;
const processMessages = async () => {
  if (isProcessing) {
    return;
  }
  isProcessing = true;
  try {
    while (pendingMessages.length > 0) {
      const [{ render, onAppear }] = pendingMessages.splice(0, 1);
      const key = nextKey;
      nextKey += 1;
      listData.messages.push({ key, render });
      // eslint-disable-next-line no-await-in-loop
      await new Promise<void>((resolve) => {
        const close = () => {
          setTimeout(resolve, 500);
          const index = listData.messages.findIndex((i) => i.key === key);
          if (index < 0) {
            return;
          }
          listData.messages.splice(index, 1);
        };
        onAppear(close);
      });
    }
  } finally {
    isProcessing = false;
  }
};

function message(render: () => VNode): Promise<() => void> {
  return new Promise((resolve) => {
    pendingMessages.push({
      render,
      onAppear: (close) => {
        resolve(close);
      },
    });
    processMessages();
  });
}

export default class VueMessageService implements MessageService {
  async info(
    text: string,
    duration = Math.min(10e3, 1000 + text.length * 200)
  ): Promise<void> {
    const close = await message(() =>
      h(
        'li',
        {
          class: [
            'p-2 rounded max-w-md w-full shadow min-h-16 pointer-events-auto',
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

  async error(
    text: string,
    duration = Math.min(10e3, 1000 + text.length * 200)
  ): Promise<void> {
    const close = await message(() =>
      h(
        'li',
        {
          class: [
            'p-2 rounded max-w-md w-full shadow min-h-16 pointer-events-auto',
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
  s.info('test info2');
  setTimeout(() => {
    s.error('test error');
  }, 1e3);
}
