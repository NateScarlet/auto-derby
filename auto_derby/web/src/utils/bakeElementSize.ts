export default function bakeElementSiz(el: Element) {
  if (!(el instanceof HTMLElement)) {
    return;
  }
  const style = window.getComputedStyle(el);
  el.style.width = style.width;
  el.style.height = style.height;
}
