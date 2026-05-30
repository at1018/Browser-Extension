const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface AnalyzeScreenshotRequest {
  image_base64: string;
  source: string;
  persona?: string;
  meta?: Record<string, unknown>;
}

export interface AnalyzeScreenshotResponse {
  analysis_id: string;
  intent: string;
  persona: string;
  results: Record<string, unknown>;
}

export async function analyzeScreenshot(
  imageBase64: string,
  persona: string = 'developer',
  meta: Record<string, unknown> = {}
): Promise<AnalyzeScreenshotResponse> {
  const response = await fetch(`${API_BASE_URL}/api/screenshots/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_base64: imageBase64,
      source: 'chrome-extension',
      persona,
      meta,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed: ${response.status} ${errorText}`);
  }

  return response.json();
}
