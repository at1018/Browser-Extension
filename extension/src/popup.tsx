import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import { analyzeScreenshot } from './lib/api';
import './index.css';

const sendBackgroundCommand = <T,>(type: string): Promise<T> => {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type }, (response) => {
      if (!response || response.success !== true) {
        reject(response?.error ?? 'Background command failed');
        return;
      }

      resolve(response.payload as T);
    });
  });
};

const PopupApp = () => {
  const [personas] = useState(['developer', 'qa', 'student', 'designer', 'shopper', 'analyst']);
  const [persona, setPersona] = useState('developer');
  const [status, setStatus] = useState('Ready to capture.');
  const [analysis, setAnalysis] = useState<any>(null);
  const [isWorking, setIsWorking] = useState(false);

  const handleCapture = async () => {
    try {
      setIsWorking(true);
      setStatus('Capturing screenshot...');
      const payload = await sendBackgroundCommand<{ imageData: string }>('CAPTURE_SCREENSHOT');
      setStatus('Uploading screenshot for analysis...');
      const result = await analyzeScreenshot(payload.imageData, persona);
      setAnalysis(result);
      setStatus('Analysis complete.');
    } catch (error) {
      setStatus(`Error: ${String(error)}`);
    } finally {
      setIsWorking(false);
    }
  };

  const handleClipboard = async () => {
    try {
      setIsWorking(true);
      setStatus('Reading clipboard image...');
      const payload = await sendBackgroundCommand<{ imageData: string }>('READ_CLIPBOARD');
      setStatus('Uploading clipboard screenshot for analysis...');
      const result = await analyzeScreenshot(payload.imageData, persona);
      setAnalysis(result);
      setStatus('Analysis complete.');
    } catch (error) {
      setStatus(`Error: ${String(error)}`);
    } finally {
      setIsWorking(false);
    }
  };

  return (
    <div className="min-w-[340px] max-w-[420px] p-4 bg-slate-950 text-white">
      <h1 className="text-xl font-semibold">AI Visual Copilot</h1>
      <p className="mt-2 text-sm text-slate-300">
        Capture screenshots, detect text, and route analysis to persona workflows.
      </p>
      <div className="mt-4 space-y-3">
        <label className="block text-xs uppercase tracking-[0.2em] text-slate-500">Persona</label>
        <select
          value={persona}
          onChange={(event) => setPersona(event.target.value)}
          className="w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-cyan-500"
        >
          {personas.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        <button
          onClick={handleCapture}
          disabled={isWorking}
          className="w-full rounded-xl bg-cyan-500 px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Capture Screenshot
        </button>
        <button
          onClick={handleClipboard}
          disabled={isWorking}
          className="w-full rounded-xl border border-slate-700 px-4 py-3 text-sm text-white hover:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-60"
        >
          Read Clipboard
        </button>
      </div>

      <div className="mt-4 rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
        <p className="font-semibold text-slate-200">Status</p>
        <p className="mt-2 whitespace-pre-wrap">{status}</p>
      </div>

      {analysis && (
        <div className="mt-4 rounded-3xl border border-slate-800 bg-slate-900 p-4 text-sm text-slate-300">
          <p className="font-semibold text-slate-200">Latest analysis</p>
          <pre className="mt-2 max-h-48 overflow-auto text-xs text-slate-100">
            {JSON.stringify(analysis, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

const root = createRoot(document.getElementById('root')!);
root.render(<PopupApp />);
