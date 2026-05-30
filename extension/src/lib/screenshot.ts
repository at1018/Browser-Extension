export const captureVisibleTab = async (): Promise<{ imageData: string }> => {
  return new Promise((resolve, reject) => {
    try {
      chrome.tabs.captureVisibleTab({ format: 'png' }, (dataUrl) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError.message);
          return;
        }
        resolve({ imageData: dataUrl });
      });
    } catch (error) {
      reject(error);
    }
  });
};

export const readClipboardImage = async (): Promise<{ imageData: string }> => {
  if (!navigator.clipboard || !navigator.clipboard.read) {
    throw new Error('Clipboard API not supported in this context');
  }

  const clipboardItems = await navigator.clipboard.read();
  for (const item of clipboardItems) {
    if (item.types.includes('image/png')) {
      const blob = await item.getType('image/png');
      const reader = new FileReader();

      return new Promise((resolve, reject) => {
        reader.onloadend = () => {
          resolve({ imageData: reader.result as string });
        };
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(blob);
      });
    }
  }

  throw new Error('No image found in clipboard');
};
