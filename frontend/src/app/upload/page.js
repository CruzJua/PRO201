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
        <div className="flex flex-col items-center gap-4">
          <div className="text-3xl font-bold font-mono" style={{color: '#ff006e', textShadow: '0 0 20px #ff006e', animation: 'pulse 1s infinite'}}>
            LOADING 
          </div>
          <svg
            className="h-8 w-8"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            style={{color: '#00ff41', filter: 'drop-shadow(0 0 10px #00ff41)', animation: 'spin 1s linear infinite'}}
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
      </div>
    );
  }

  return (
    <div className="py-20 px-6 sm:px-12 lg:px-20 max-w-4xl mx-auto">
      <h1 className="text-5xl font-bold mb-8 font-mono text-center glitch-text" data-text="UPLOAD MRI SCAN" style={{color: '#00ff41', textShadow: '0 0 20px #00ff41'}}>UPLOAD MRI SCAN</h1>

      <div
        className="border-2 border-dashed p-8 sm:p-16 text-center transition-all"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        style={{borderColor: '#ff006e', background: '#000000', boxShadow: '0 0 25px #ff006e/20'}}
      >
        {!preview ? (
          <>
            <svg className="w-20 h-20 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{color: '#00f0ff', filter: 'drop-shadow(0 0 10px #00f0ff)'}}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <h2 className="text-2xl font-bold mb-4 font-mono" style={{color: '#ffff00', textShadow: '0 0 15px #ffff00'}}>▌SELECT FILE OR DRAG & DROP▌</h2>
            <p className="mb-8 font-mono" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>JPG or PNG | Max 50MB</p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="font-bold px-8 py-3 font-mono text-lg border-2 transition-all"
              style={{color: '#000000', backgroundColor: '#ff006e', borderColor: '#ff006e', boxShadow: '0 0 15px #ff006e', textShadow: '0 0 5px #ff006e'}}
            >
              SELECT FILE
            </button>
          </>
        ) : (
          <div className="flex flex-col items-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={preview} alt="MRI Preview" className="max-h-64 mb-6 border-2" style={{borderColor: '#00ff41', boxShadow: '0 0 20px #00ff41/30'}} />
            <div className="flex gap-4">
              <button
                onClick={() => { setPreview(null); setFile(null); setResult(null); setError(null); }}
                disabled={uploading}
                className="font-bold px-6 py-2 font-mono text-lg border-2 transition-all disabled:opacity-50"
                style={{color: '#000000', backgroundColor: '#c700ff', borderColor: '#c700ff', boxShadow: '0 0 15px #c700ff'}}
              >
                CANCEL
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading}
                className="font-bold px-8 py-2 font-mono text-lg border-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[180px]"
                style={{color: '#000000', backgroundColor: '#00ff41', borderColor: '#00ff41', boxShadow: '0 0 15px #00ff41'}}
              >
                {uploading ? (
                  <div className="flex items-center gap-2">
                    <svg className="h-5 w-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    ANALYZING
                  </div>
                ) : (
                  ">>> ANALYZE <<<"
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
        <div className="mt-8 p-4 font-mono text-center border-2" style={{color: '#ffff00', borderColor: '#ff006e', background: '#000000', textShadow: '0 0 10px #ffff00', boxShadow: '0 0 15px #ff006e/30'}}>
          ERROR: {error}
        </div>
      )}

      {result && (
        <div className="mt-8 p-6 border-2" style={{borderColor: '#00f0ff', background: '#000000', boxShadow: '0 0 30px #00f0ff/30'}}>
          <h3 className="text-3xl font-bold mb-6 text-center font-mono" style={{color: '#00ff41', textShadow: '0 0 15px #00ff41'}}> ANALYSIS RESULTS </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 border-2" style={{borderColor: '#ff006e', background: '#000000', boxShadow: '0 0 15px #ff006e/20'}}>
              <p className="text-sm font-mono mb-1" style={{color: '#00f0ff', textShadow: '0 0 5px #00f0ff'}}>DIAGNOSIS</p>
              <p className="text-xl font-bold font-mono" style={{color: '#ffff00', textShadow: '0 0 10px #ffff00'}}>{result.predicted_label}</p>
            </div>
            <div className="p-4 border-2" style={{borderColor: '#c700ff', background: '#000000', boxShadow: '0 0 15px #c700ff/20'}}>
              <p className="text-sm font-mono mb-1" style={{color: '#00f0ff', textShadow: '0 0 5px #00f0ff'}}>CONFIDENCE SCORE</p>
              <p className="text-xl font-bold font-mono" style={{color: '#00ff41', textShadow: '0 0 10px #00ff41'}}>{(result.confidence * 100).toFixed(2)}%</p>
            </div>
          </div>
          {result.probabilities && (
            <div className="mt-6 p-4 border-2" style={{borderColor: '#00ff41', background: '#000000', boxShadow: '0 0 15px #00ff41/20'}}>
              <p className="text-sm font-bold font-mono mb-3" style={{color: '#ffff00', textShadow: '0 0 8px #ffff00'}}>CLASS PROBABILITIES</p>
              <div className="space-y-3">
                {Object.entries(result.probabilities).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex justify-between text-xs mb-1 font-mono">
                      <span style={{color: '#00f0ff', textShadow: '0 0 5px #00f0ff'}}>{key}</span>
                      <span style={{color: '#00f0ff', textShadow: '0 0 5px #00f0ff'}}>{(value * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-2" style={{background: '#1a1a1a', border: '1px solid #ff006e'}}>
                      <div
                        className="h-2 transition-all"
                        style={{ width: `${value * 100}%`, background: 'linear-gradient(90deg, #ff006e, #00f0ff)', boxShadow: '0 0 10px #ff006e' }}
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
