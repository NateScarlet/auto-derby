import { mdiLoading } from '@mdi/js';
// https://vitejs.dev/guide/assets.html#importing-asset-as-string
import browserCheckFailHTML from '@/assets/browser-check-fail.html?raw';
import initialLoadingHTML from '@/assets/initial-loading.html?raw';

export default function browserCheck(fn?: () => void): void {
  try {
    if (Object.entries === undefined) {
      throw new Error('Object.entries is not supported');
    }
    if (Array.prototype.flatMap === undefined) {
      throw new Error('Array.prototype.flatMap is not supported');
    }
    if (typeof CSS === 'undefined' || CSS.supports === undefined) {
      throw new Error('CSS.supports is not supported');
    }
    if (!CSS.supports('display', 'grid')) {
      throw new Error('grid layout is not supported');
    }
    fn?.();
  } catch (err) {
    const el = document.getElementById('app');
    if (!el) {
      throw new Error('missing app element');
    }
    el.id = 'browser-check-message'; // prevent load app
    el.innerHTML = browserCheckFailHTML;

    const pre = document.getElementById('error');
    if (pre) {
      pre.innerText = String(err);
    }
    const errText =
      err instanceof Error ? err.stack ?? err.message : String(err);

    // https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-an-issue#creating-an-issue-from-a-url-query
    const newIssueURL = `https://github.com/NateScarlet/auto-derby/issues/new?title=${encodeURIComponent(
      `[web] ${err instanceof Error ? err.message : String(err).slice(0, 80)}`
    )}&body=${encodeURIComponent(`\
## Version

${__VERSION__}

## URL

${document.location.href}

## User Agent

${navigator.userAgent}

## Error

\`\`\`
${errText}
\`\`\`
`)}&labels=bug`;

    const anchors =
      document.querySelectorAll<HTMLAnchorElement>('a.new-issue-link');
    for (let i = 0; i < anchors.length; i += 1) {
      const a = anchors.item(i);
      a.href = newIssueURL;
    }

    throw err;
  }
}

function createLoading() {
  const el = document.createElement('div');
  document.getElementById('app')?.append(el);
  el.innerHTML = initialLoadingHTML;
  const path = document.getElementById('loading-icon-svg-path');
  if (path) {
    path.setAttribute('d', mdiLoading);
  }
}

(() => {
  browserCheck(() => {
    createLoading();
  });
})();
