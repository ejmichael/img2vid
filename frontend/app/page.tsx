"use client";

import { useState, useRef, useCallback } from "react";

type AppState = "idle" | "processing" | "complete" | "error";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [prompt, setPrompt] = useState("");
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) return;
    setImage(file);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target?.result as string);
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const startPolling = useCallback((jobId: string) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${jobId}`);
        if (!res.ok) return;
        const data = (await res.json()) as {
          status: string;
          result?: string;
          error?: string;
        };

        if (data.status === "complete" && data.result) {
          stopPolling();
          setVideoUrl(data.result);
          setAppState("complete");
        } else if (data.status === "error") {
          stopPolling();
          setErrorMsg(data.error ?? "Generation failed");
          setAppState("error");
        }
      } catch {
        // Keep polling on transient errors
      }
    }, 3000);
  }, []);

  const handleSubmit = async () => {
    if (!image || !prompt.trim()) return;

    setAppState("processing");
    setErrorMsg(null);
    setVideoUrl(null);

    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("prompt", prompt);

      const res = await fetch("/api/generate", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = (await res.json()) as { error?: string };
        throw new Error(err.error ?? "Failed to submit");
      }

      const { jobId } = (await res.json()) as { jobId: string };
      startPolling(jobId);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to generate");
      setAppState("error");
    }
  };

  const reset = () => {
    stopPolling();
    setAppState("idle");
    setImage(null);
    setImagePreview(null);
    setPrompt("");
    setVideoUrl(null);
    setErrorMsg(null);
  };

  const canSubmit = !!image && prompt.trim().length > 0;

  return (
    <main className="min-h-screen flex flex-col items-center py-16 px-4">
      <div className="w-full max-w-2xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">Image → Video</h1>
          <p className="text-zinc-500 text-sm">Powered by LTX-Video</p>
        </div>

        {/* Idle / Error states */}
        {(appState === "idle" || appState === "error") && (
          <div className="space-y-5">
            {/* Drop zone */}
            <div
              role="button"
              tabIndex={0}
              onClick={() => fileInputRef.current?.click()}
              onKeyDown={(e) =>
                e.key === "Enter" && fileInputRef.current?.click()
              }
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              className={`border-2 border-dashed rounded-2xl cursor-pointer transition-colors select-none ${
                dragOver
                  ? "border-indigo-400 bg-indigo-950/30"
                  : "border-zinc-700 hover:border-zinc-500"
              } ${imagePreview ? "p-2" : "p-14 text-center"}`}
            >
              {imagePreview ? (
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full max-h-80 object-contain rounded-xl"
                />
              ) : (
                <div className="space-y-3">
                  <div className="text-5xl">🖼️</div>
                  <p className="text-zinc-300 font-medium">
                    Click or drag an image here
                  </p>
                  <p className="text-zinc-600 text-sm">
                    PNG, JPG, WEBP supported
                  </p>
                </div>
              )}
            </div>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleFile(f);
              }}
            />

            {/* Prompt */}
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the motion… e.g. 'The camera slowly zooms in, flowers gently sway in the breeze'"
              rows={3}
              className="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3 text-sm placeholder:text-zinc-600 focus:outline-none focus:border-indigo-500 resize-none"
            />

            {errorMsg && (
              <p className="text-red-400 text-sm text-center">{errorMsg}</p>
            )}

            <button
              onClick={handleSubmit}
              disabled={!canSubmit}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 disabled:text-zinc-600 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors"
            >
              Generate Video
            </button>
          </div>
        )}

        {/* Processing state */}
        {appState === "processing" && (
          <div className="flex flex-col items-center gap-6 py-20">
            <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            <div className="text-center space-y-1">
              <p className="text-zinc-200 font-medium">Generating your video…</p>
              <p className="text-zinc-500 text-sm">This usually takes 1–5 minutes</p>
            </div>
          </div>
        )}

        {/* Complete state */}
        {appState === "complete" && videoUrl && (
          <div className="space-y-4">
            <video
              src={videoUrl}
              controls
              autoPlay
              loop
              playsInline
              className="w-full rounded-2xl border border-zinc-800"
            />
            <div className="flex gap-3">
              <a
                href={videoUrl}
                target="_blank"
                rel="noopener noreferrer"
                download="generated.mp4"
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition-colors text-center text-sm"
              >
                Download Video
              </a>
              <button
                onClick={reset}
                className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white font-semibold py-3 rounded-xl transition-colors text-sm"
              >
                Generate Another
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
