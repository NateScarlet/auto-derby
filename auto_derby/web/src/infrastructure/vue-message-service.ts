import type { MessageService } from '@/services';
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
        class: 'fixed bottom-0 right-0 flex flex-col-reverse items-end',
        appear: true,
        tag: 'ol',
        moveClass: 'transition ease-in-out duration-200',
        enterActiveClass: 'transition ease-in-out duration-300',
        enterFromClass: 'opacity-0 transform translate-x-full',
        leaveActiveClass: 'transition ease-in-out duration-1000',
        leaveToClass: 'opacity-0',
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
  info(text: string, duration = 3000 + 200 * text.length): void {
    const close = message(() =>
      h(
        'li',
        {
          class:
            'p-3 rounded-sm w-64 mx-2 my-1 bg-gray-900 text-white break-all',
        },
        text
      )
    );
    setTimeout(close, duration);
  }

  error(text: string, duration = 3000 + 200 * text.length): void {
    const close = message(() =>
      h(
        'li',
        {
          class:
            'p-3 rounded-sm w-64 mx-2 my-1 bg-red-700 text-white break-all',
        },
        text
      )
    );
    setTimeout(close, duration);
  }
}
