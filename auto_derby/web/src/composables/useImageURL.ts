import usePromise from '@/composables/usePromise';
import loadImage from '@/utils/loadImage';
import { computed } from 'vue';

export default function useImageURL(url: () => string) {
  const image = usePromise(computed(() => loadImage(url())));
  return {
    image,
    height: () => computed(() => image.value?.naturalHeight ?? 0),
    width: () => computed(() => image.value?.naturalWidth ?? 0),
  };
}
