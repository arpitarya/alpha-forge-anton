/** Image-attachment helpers for vision input — clipboard paste + file pick. */

export const MAX_IMAGES = 4;
const MAX_BYTES = 4_500_000; // mirrors backend MAX_IMAGE_CHARS budget

/** Read a File into a data URL, rejecting non-images and oversized blobs. */
export function fileToDataUrl(file: File): Promise<string | null> {
  return new Promise((resolve) => {
    if (!file.type.startsWith("image/") || file.size > MAX_BYTES) {
      resolve(null);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => resolve(typeof reader.result === "string" ? reader.result : null);
    reader.onerror = () => resolve(null);
    reader.readAsDataURL(file);
  });
}

/** Extract image data URLs from a clipboard paste, capped at MAX_IMAGES. */
export async function imagesFromClipboard(items: DataTransferItemList): Promise<string[]> {
  const files: File[] = [];
  for (const it of Array.from(items)) {
    if (it.kind === "file" && it.type.startsWith("image/")) {
      const f = it.getAsFile();
      if (f) files.push(f);
    }
  }
  const urls = await Promise.all(files.slice(0, MAX_IMAGES).map(fileToDataUrl));
  return urls.filter((u): u is string => u !== null);
}
