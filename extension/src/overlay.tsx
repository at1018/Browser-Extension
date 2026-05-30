import React, { useMemo, useState } from 'react';
import { analyzeScreenshot } from './lib/api';
import { cropDataUrl, CropRect } from './lib/image';
import './index.css';

function sendBackgroundCommand<T>(type: string): Promise<T> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type }, (response) => {
      if (!response || response.success !== true) {
        reject(response?.error ?? 'Background command failed');
        return;
      }
      resolve(response.payload as T);
    });
  });
}

const SelectionOverlay: React.FC<{
  active: boolean;
  selection: CropRect | null;
  onCancel: () => void;
  onSelected: (rect: CropRect) => void;
}> = ({ active, selection, onCancel, onSelected }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [start, setStart] = useState<{ x: number; y: number } | null>(null);

  const getRelativeRect = (x: number, y: number, startX: number, startY: number) => {
    const left = Math.min(startX, x);
    const top = Math.min(startY, y);
    return {
      x: left,
      y: top,
      width: Math.abs(x - startX),
      height: Math.abs(y - startY),
    };
  };

  return (
    <div className="fixed inset-0 z-[999999] pointer-events-none">
      <div className="pointer-events-auto absolute inset-0 bg-slate-950/10 backdrop-blur-sm" />
      <div
        className="pointer-events-auto absolute inset-0"
        onPointerDown={(event) => {
          if (!active) {
            return;
          }
          event.preventDefault();
          setStart({ x: event.clientX, y: event.clientY });
          setIsDragging(true);
        }}
        onPointerMove={(event) => {
          if (!active || !isDragging || !start) {
            return;
          }
          const rect = getRelativeRect(event.clientX, event.clientY, start.x, start.y);
          onSelected(rect);
        }}
        onPointerUp={(event) => {
          if (!active || !start) {
            return;
          }
          setIsDragging(false);
          const rect = getRelativeRect(event.clientX, event.clientY, start.x, start.y);
          if (rect.width > 10 && rect.height > 10) {
            onSelected(rect);
          } else {
            onCancel();
          }
        }}
      />

      {selection && (
        <div
          className="absolute border-2 border-cyan-400 bg-cyan-400/10"
          style={{ left: selection.x, top: selection.y, width: selection.width, height: selection.height }}
        />
      )}
    </div>
  );
};

const OverlayApp = () => {
  const [selection, setSelection] = useState<CropRect | null>(null);
  const [stage, setStage] = useState<'idle' | 'selecting' | 'ready' | 'processing'>('idle');
  const [annotation, setAnnotation] = useState('');
  const [status, setStatus] = useState('Tap "Select Region" to begin.');
  const [analysis, setAnalysis] = useState<any>(null);
  const [persona, setPersona] = useState('developer');

  const selectionSummary = useMemo(() => {
    if (!selection) {
      return 'No selection yet.';
    }
    return `Selected region: ${selection.width.toFixed(0)}×${selection.height.toFixed(0)} at (${selection.x.toFixed(0)}, ${selection.y.toFixed(0)})`;
  }, [selection]);

  const handleStartSelection = () => {
    setStage('selecting');
    setSelection(null);
    setStatus('Drag to select an area on the page. Release to confirm.');
  };

  const handleSelectionComplete = (rect: CropRect) => {
    setSelection(rect);
    setStage('ready');
    setStatus('Selection ready. Capture or restart when ready.');
  };

  const handleCancelSelection = () => {
    setSelection(null);
    setStage('idle');
    setStatus('Selection canceled. Tap "Select Region" to begin again.');
  };

  const handleCaptureRegion = async () => {
    if (!selection) {
      setStatus('Please select a region first.');
      return;
    }

    try {
      setStage('processing');
      setStatus('Capturing screenshot from the current tab...');
      const payload = await sendBackgroundCommand<{ imageData: string }>('CAPTURE_SCREENSHOT');
      setStatus('Cropping selected region...');
      const croppedDataUrl = await cropDataUrl(payload.imageData, selection);
      setStatus('Sending selected region for analysis...');
      const result = await analyzeScreenshot(croppedDataUrl, persona, {
        annotation,
        selection,
      });
      setAnalysis(result);
      setStatus('Analysis complete.');
    } catch (error) {
      setStatus(`Error: ${String(error)}`);
    } finally {
      setStage('idle');
    }
  };

  return (
    <>
      {stage === 'selecting' && (
        <SelectionOverlay
          active={stage === 'selecting'}
          selection={selection}
          onCancel={handleCancelSelection}
          onSelected={handleSelectionComplete}
        />
      )}

      <div className="fixed bottom-4 right-4 z-[999998] w-[340px] rounded-3xl border border-slate-700 bg-slate-950/95 p-4 text-slate-100 shadow-2xl backdrop-blur-xl">
        <div className="flex items-center justify-between gap-2">
          <div>
            <h2 className="text-lg font-semibold">AI Visual Copilot</h2>
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Overlay selection</p>
          </div>
          <button
            onClick={() => setSelection(null)}
            className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-slate-700"
          >
            Reset
          </button>
        </div>

        <div className="mt-4 space-y-3">
          <label className="block text-xs uppercase tracking-[0.2em] text-slate-500">Persona</label>
          <select
            value={persona}
            onChange={(event) => setPersona(event.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-cyan-500"
          >
            <option value="developer">developer</option>
            <option value="qa">qa</option>
            <option value="student">student</option>
            <option value="designer">designer</option>
            <option value="shopper">shopper</option>
            <option value="analyst">analyst</option>
          </select>

          <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
            <button
              onClick={handleStartSelection}
              disabled={stage === 'selecting' || stage === 'processing'}
              className="rounded-2xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Select Region
            </button>
            <button
              onClick={handleCaptureRegion}
              disabled={!selection || stage === 'processing'}
              className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-100 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Capture Region
            </button>
          </div>

          <label className="block text-xs uppercase tracking-[0.2em] text-slate-500">Annotation</label>
          <textarea
            value={annotation}
            onChange={(event) => setAnnotation(event.target.value)}
            rows={3}
            placeholder="Add a note or task for this selection"
            className="w-full rounded-2xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-cyan-500"
          />

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-3 text-sm text-slate-300">
            <p className="font-semibold text-slate-100">Status</p>
            <p className="mt-1">{status}</p>
            <p className="mt-2 text-xs text-slate-500">{selectionSummary}</p>
          </div>
        </div>

        {analysis && (
          <div className="mt-4 rounded-3xl border border-slate-800 bg-slate-900 p-3 text-xs text-slate-200">
            <p className="font-semibold text-slate-100">Last analysis</p>
            <pre className="mt-2 max-h-40 overflow-auto text-[11px] text-slate-300">{JSON.stringify(analysis, null, 2)}</pre>
          </div>
        )}
      </div>
    </>
  );
};

export default OverlayApp;
