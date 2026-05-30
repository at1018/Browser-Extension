# Extension Architecture

## Phase 2: Chrome Extension Scaffold

The extension is designed as a Manifest V3 React application with the following responsibilities:

- Screenshot capture using `chrome.tabs.captureVisibleTab`
- Clipboard image detection for pasted screenshots
- Background service worker for message routing
- Popup UI for workflow entry and quick actions
- Overlay UI injected into web pages for future annotation and selection

## Folder Structure

- `extension/package.json` — build scripts and dependencies
- `extension/vite.config.ts` — Vite configuration for popup and overlay bundling
- `extension/public/manifest.json` — Chrome Extension manifest V3
- `extension/public/popup.html` — popup entry page
- `extension/public/overlay.html` — overlay entry page
- `extension/src/background.ts` — service worker and Chrome message handling
- `extension/src/contentScript.ts` — injects the overlay container into pages
- `extension/src/popup.tsx` — React popup UI
- `extension/src/overlay.tsx` — React overlay UI
- `extension/src/lib/screenshot.ts` — screenshot and clipboard helpers
- `extension/src/index.css` — Tailwind styling

## How It Works

- The extension popup provides buttons for capture and clipboard actions.
- The background worker listens for commands and performs screenshot acquisition.
- The content script injects a React overlay into each page for region selection and insight capture.
- The overlay UI supports page region selection, annotation notes, and analysis submission to the backend.

## Next Steps

1. Hook popup buttons to background messages.
2. Wire screenshot payloads to the backend analysis API.
3. Expand overlay UI with screenshot annotation and persona selection.
4. Add Chrome extension packaging and CI build support.
