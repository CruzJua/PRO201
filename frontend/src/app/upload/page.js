"use client";

import { useEffect, useRef, useState } from "react";

const displayLabels = { glioma: "Glioma", meningioma: "Meningioma", notumor: "No tumor", pituitary: "Pituitary" };

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  const selectFile = (selectedFile) => {
    if (!selectedFile?.type.startsWith("image/")) {
      setError("Please choose a valid JPG or PNG image.");
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError(null);
  };

  const handleDrop = (event) => { event.preventDefault(); selectFile(event.dataTransfer.files[0]); };

  const clearFile = () => {
    setPreview(null);
    setFile(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/predict", { method: "POST", body: formData });
      if (!response.ok) {
        let message = `Analysis failed with status ${response.status}`;
        try {
          const data = await response.json();
          if (data?.detail) message = data.detail;
        } catch {
          // Keep the status-based fallback when the response is not JSON.
        }
        throw new Error(message);
      }
      setResult(await response.json());
    } catch (uploadError) {
      setError(uploadError.message || "The scan could not be analyzed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <section className="analyzer-header shell">
        <div>
          <p className="eyebrow">Analyzer / working surface</p>
          <h1 className="display page-hero__title">Upload.<br /><em>Inspect the signal.</em></h1>
        </div>
        <div className="analyzer-header__note">
          <p>Use a clear, cropped brain MRI image. The current model accepts common image formats.</p>
          <p className="mono-note">JPG / PNG · MAX 50 MB · 4-CLASS OUTPUT</p>
        </div>
      </section>

      <section className="analyzer shell">
        <div className={`drop-zone${preview ? " drop-zone--selected" : ""}`} onDragOver={(event) => event.preventDefault()} onDrop={handleDrop}>
          {!preview ? (
            <div className="drop-zone__empty">
              <span className="drop-zone__index">01 / INPUT</span>
              <div className="upload-mark" aria-hidden="true">+</div>
              <h2>Select an MRI image</h2>
              <p>Drop an image onto this field or choose one from your device.</p>
              <button type="button" onClick={() => fileInputRef.current?.click()} className="button button--primary">Choose file <span aria-hidden="true">↗</span></button>
            </div>
          ) : (
            <div className="scan-preview">
              <span className="drop-zone__index">01 / INPUT READY</span>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={preview} alt="Preview of the selected MRI scan" />
              <div className="scan-preview__meta">
                <div><span>Selected image</span><p>{file?.name}</p></div>
                <div className="scan-preview__actions">
                  <button type="button" onClick={clearFile} className="button button--quiet" disabled={loading}>Remove</button>
                  <button type="button" onClick={handleUpload} className="button button--primary" disabled={loading}>{loading ? "Analyzing…" : "Run analysis"} <span aria-hidden="true">↗</span></button>
                </div>
              </div>
            </div>
          )}
          <input type="file" ref={fileInputRef} onChange={(event) => selectFile(event.target.files[0])} accept="image/jpeg,image/png,image/webp" className="visually-hidden" />
        </div>

        <aside className="analyzer-aside">
          <p className="eyebrow">Before you begin</p>
          <ol>
            <li><span>01</span>Remove any identifying patient information.</li>
            <li><span>02</span>Use one axial brain MRI image at a time.</li>
            <li><span>03</span>Treat the result as a research signal only.</li>
          </ol>
          <p className="research-warning">Not for clinical decision-making or emergency use.</p>
        </aside>
      </section>

      {error && (
        <section className="result-panel result-panel--error shell" role="alert">
          <p className="result-panel__label">Analysis interrupted</p><h2>{error}</h2><p>Check that the local model service is running, then try again.</p>
        </section>
      )}

      {result && (
        <section className="result-panel shell" aria-live="polite">
          <div className="result-summary">
            <p className="result-panel__label">02 / Model output</p><h2>{result.predicted_label}</h2>
            <p className="confidence-value">{(result.confidence * 100).toFixed(1)}%</p><span>Model confidence</span>
          </div>
          {result.probabilities && (
            <div className="probability-list">
              <p className="eyebrow">Full probability distribution</p>
              {Object.entries(result.probabilities).map(([key, value]) => (
                <div className="probability-row" key={key}>
                  <div><span>{displayLabels[key] || key}</span><span>{(value * 100).toFixed(1)}%</span></div>
                  <div className="probability-track" aria-hidden="true"><span style={{ width: `${value * 100}%` }} /></div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      <section className="analyzer-disclaimer shell"><span>03 / CONTEXT</span><p>This output describes a model prediction, not a medical finding.</p></section>
    </>
  );
}
