"use client";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

export default function UploadPage() {
  const { user, session, loading } = useAuth();
  const router = useRouter();

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleDragOver = (e) => e.preventDefault();

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith("image/")) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
      setResult(null);
      setError(null);
    } else {
      setError("Please drop a valid image file.");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = `Upload failed with status ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData?.detail) errorMsg = errorData.detail;
        } catch (_) {
          // ignore parse error
        }
        throw new Error(errorMsg);
      }

      setResult(await response.json());
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message || "An error occurred during upload.");
    } finally {
      setUploading(false);
    }
  };

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <svg
          className="animate-spin h-8 w-8 text-emerald-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      </div>
    );
  }

  return (
    <div className="py-20 px-6 sm:px-12 lg:px-20 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 text-emerald-400 text-center">Upload MRI Scan</h1>

      <div
        className="border-2 border-dashed border-emerald-600/40 rounded-xl p-8 sm:p-16 text-center bg-slate-900/50 backdrop-blur-sm transition-all hover:border-emerald-500/60"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {!preview ? (
          <>
            <svg className="w-20 h-20 mx-auto text-emerald-500 mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <h2 className="text-2xl font-semibold mb-4 text-white">Select a file or drag and drop here</h2>
            <p className="text-slate-400 mb-8">JPG, PNG file size no more than 50MB</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-8 py-3 rounded-lg transition-all shadow-lg hover:shadow-emerald-500/25"
            >
              Select File
            </button>
          </>
        ) : (
          <div className="flex flex-col items-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={preview} alt="MRI Preview" className="max-h-64 rounded-lg shadow-xl mb-6 border border-slate-700" />
            <div className="flex gap-4">
              <button
                onClick={() => { setPreview(null); setFile(null); setResult(null); setError(null); }}
                disabled={uploading}
                className="bg-slate-700 hover:bg-slate-600 text-white font-semibold px-6 py-2 rounded-lg transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-8 py-2 rounded-lg transition-all shadow-lg hover:shadow-emerald-500/25 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[140px]"
              >
                {uploading ? (
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                ) : (
                  "Analyze Image"
                )}
              </button>
            </div>
          </div>
        )}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          className="hidden"
        />
      </div>

      {error && (
        <div className="mt-8 p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-200 text-center">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-8 p-6 bg-slate-900/80 border border-emerald-500/30 rounded-xl shadow-xl">
          <h3 className="text-2xl font-bold text-white mb-6 text-center">Analysis Results</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-950 p-4 rounded-lg border border-white/5">
              <p className="text-sm text-slate-400 mb-1">Diagnosis</p>
              <p className="text-xl font-semibold text-emerald-400">{result.predicted_label}</p>
            </div>
            <div className="bg-slate-950 p-4 rounded-lg border border-white/5">
              <p className="text-sm text-slate-400 mb-1">Confidence Score</p>
              <p className="text-xl font-semibold text-white">{(result.confidence * 100).toFixed(2)}%</p>
            </div>
          </div>
          {result.probabilities && (
            <div className="mt-6 bg-slate-950 p-4 rounded-lg border border-white/5">
              <p className="text-sm text-slate-400 mb-3">Class Probabilities</p>
              <div className="space-y-3">
                {Object.entries(result.probabilities).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-300">{key}</span>
                      <span className="text-slate-300">{(value * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5">
                      <div
                        className="bg-emerald-500 h-1.5 rounded-full"
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
