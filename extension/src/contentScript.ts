import React from 'react';
import { createRoot } from 'react-dom/client';
import OverlayApp from './overlay';
import './index.css';

const mountOverlay = () => {
  if (document.getElementById('ai-visual-copilot-overlay-root')) {
    return;
  }

  const container = document.createElement('div');
  container.id = 'ai-visual-copilot-overlay-root';
  document.body.appendChild(container);

  const root = createRoot(container);
  root.render(<OverlayApp />);
};

mountOverlay();
