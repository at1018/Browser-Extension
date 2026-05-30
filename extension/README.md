# AI Visual Copilot Chrome Extension

This folder contains the Chrome Extension scaffold for AI Visual Copilot.

## Features

- Chrome Manifest V3 extension shell
- React + TypeScript + Tailwind UI
- Background service worker
- Popup and overlay UI
- Screenshot capture helper stubs

## Development

Install dependencies:

```bash
cd extension
npm install
```

Run development server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

## Environment

Create a local `.env` file to configure the backend API URL. The scaffold includes a default developer file:

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Backend Integration

This extension currently communicates with the backend at `/api/screenshots/analyze`.
Run the backend locally from `backend/` before testing the extension UI.

## Notes

The current scaffold provides the structure and UI entry points for Phase 2 along with screenshot capture, clipboard support, and a page region selection overlay.
