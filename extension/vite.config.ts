import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        popup: 'public/popup.html',
        overlay: 'public/overlay.html',
        background: 'src/background.ts',
        contentScript: 'src/contentScript.ts',
      },
    },
  },
});
