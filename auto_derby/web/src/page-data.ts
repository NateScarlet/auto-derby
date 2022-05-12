import rawItemData from 'auto-derby/data/single_mode_items.jsonl?raw';
import assertNever from '@/utils/assertNever';
import pluginSelectPageData from '@/samples/plugin_select.json';
import { isDevelopmentMode } from './settings';

export enum PageType {
  SINGLE_MODE_ITEM_SELECT = 'SINGLE_MODE_ITEM_SELECT',
  LOG = 'LOG',
  PLUGIN_SELECT = 'PLUGIN_SELECT',
}

export interface SingleModeItem {
  id: number;
  name: string;
  description: string;
}

export interface PageDataSingleModeItemSelect {
  type: PageType.SINGLE_MODE_ITEM_SELECT;
  imageURL: string;
  options: SingleModeItem[];
  submitURL?: string;
  defaultValue?: number;
}

export interface PageDataLog {
  type: PageType.LOG;
  streamURL: string;
}

export interface Plugin {
  name: string;
  doc: string;
}

export interface PageDataPluginSelect {
  type: PageType.PLUGIN_SELECT;
  plugins: Plugin[];
  submitURL?: string;
  defaultValue?: string[];
}

export type PageData =
  | PageDataSingleModeItemSelect
  | PageDataLog
  | PageDataPluginSelect;

function getPageData(): PageData {
  const el = document.getElementById('data');
  if (!el) {
    throw new Error("'#data' element not found");
  }
  if (isDevelopmentMode) {
    const u = new URL(window.location.href);
    const tp = u.searchParams.get('type') as PageType;
    switch (tp) {
      case PageType.SINGLE_MODE_ITEM_SELECT:
        return {
          type: PageType.SINGLE_MODE_ITEM_SELECT,
          imageURL: 'https://httpbin.org/image/png',
          submitURL: 'https://httpbin.org/anything',
          defaultValue: 0,
          options: rawItemData
            .split('\n')
            .filter((i) => i)
            .map((i) => JSON.parse(i)),
        };
      case PageType.LOG:
        return {
          type: PageType.LOG,
          streamURL: '/log',
        };
      case PageType.PLUGIN_SELECT:
        return {
          ...pluginSelectPageData,
          submitURL: 'https://httpbin.org/status/200',
        } as PageDataPluginSelect;
      default:
        assertNever(tp);
        window.location.href = `/?type=${PageType.SINGLE_MODE_ITEM_SELECT}`;
    }
  }
  return JSON.parse(el.innerHTML);
}

const pageData = getPageData();
export default pageData;
