export interface CropRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export async function cropDataUrl(dataUrl: string, rect: CropRect): Promise<string> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      try {
        const ratio = window.devicePixelRatio || 1;
        const canvas = document.createElement('canvas');
        canvas.width = Math.round(rect.width * ratio);
        canvas.height = Math.round(rect.height * ratio);
        const context = canvas.getContext('2d');

        if (!context) {
          throw new Error('Unable to get canvas context');
        }

        context.drawImage(
          image,
          Math.round(rect.x * ratio),
          Math.round(rect.y * ratio),
          Math.round(rect.width * ratio),
          Math.round(rect.height * ratio),
          0,
          0,
          Math.round(rect.width * ratio),
          Math.round(rect.height * ratio)
        );

        resolve(canvas.toDataURL('image/png'));
      } catch (err) {
        reject(err);
      }
    };
    image.onerror = (event) => {
      reject(new Error('Failed to load screenshot image')); 
    };
    image.src = dataUrl;
  });
}
