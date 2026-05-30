import { captureVisibleTab, readClipboardImage } from './lib/screenshot';

chrome.runtime.onInstalled.addListener(() => {
  console.log('AI Visual Copilot background worker installed');
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'CAPTURE_SCREENSHOT') {
    captureVisibleTab()
      .then((payload) => sendResponse({ success: true, payload }))
      .catch((error) => sendResponse({ success: false, error: String(error) }));
    return true;
  }

  if (message?.type === 'READ_CLIPBOARD') {
    readClipboardImage()
      .then((payload) => sendResponse({ success: true, payload }))
      .catch((error) => sendResponse({ success: false, error: String(error) }));
    return true;
  }
});
