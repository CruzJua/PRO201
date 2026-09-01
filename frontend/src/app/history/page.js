"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HistoryPage() {
  const { user, session, loading: authLoading } = useAuth();
  const router = useRouter();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [authLoading, user, router]);

  const accessToken = session?.access_token;

  useEffect(() => {
    if (!accessToken) return;
    // `loading` already starts true, so it is never set synchronously here —
    // a token refresh refetches in the background against the current list.
    let active = true;
    fetch(`${API_URL}/predictions`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Server error ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (!active) return;
        setPredictions(data.predictions ?? []);
        setError(null);
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [accessToken]);

  if (authLoading || !user) {
    return (
      <section className="auth-loading shell" aria-live="polite">
        <p className="eyebrow">History</p>
        <p className="display display-medium">Checking access…</p>
      </section>
    );
  }

  return (
    <>
      <section className="analyzer-header shell">
        <div>
          <p className="eyebrow">Account / scan history</p>
          <h1 className="display page-hero__title">
            Your scans.<br /><em>All in one place.</em>
          </h1>
        </div>
        <div className="analyzer-header__note">
          <p>Every MRI you have analyzed while signed in is listed here.</p>
          <p className="mono-note">AUTHENTICATED · {user.email}</p>
        </div>
      </section>

      <section className="analyzer shell">
        {loading && (
          <p className="eyebrow" aria-live="polite">Loading history…</p>
        )}
        {error && (
          <div className="result-panel result-panel--error" role="alert">
            <p className="result-panel__label">Could not load history</p>
            <h2>{error}</h2>
          </div>
        )}
        {!loading && !error && predictions.length === 0 && (
          <div className="drop-zone">
            <div className="drop-zone__empty">
              <span className="drop-zone__index">NO RECORDS</span>
              <h2>No predictions yet</h2>
              <p>Run your first analysis to see results here.</p>
              <Link href="/upload" className="button button--primary">Go to Analyzer <span aria-hidden="true">↗</span></Link>
            </div>
          </div>
        )}
        {!loading && predictions.length > 0 && (
          <div className="probability-list">
            <p className="eyebrow">
              {predictions.length} scan{predictions.length !== 1 ? "s" : ""} on record
            </p>
            {predictions.map((pred) => (
              <div className="probability-row" key={pred.pred_id} style={{ alignItems: "flex-start", gap: "1.5rem", flexWrap: "wrap" }}>
                {pred.image_url && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={pred.image_url}
                    alt={`MRI scan — ${pred.label}`}
                    style={{ width: "80px", height: "80px", objectFit: "cover", borderRadius: "4px", flexShrink: 0 }}
                  />
                )}
                <div>
                  <span style={{ fontWeight: 600 }}>{pred.label}</span>
                  <p className="mono-note" style={{ marginTop: "0.25rem" }}>ID {pred.pred_id}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="analyzer-disclaimer shell">
        <span>CONTEXT</span>
        <p>These are model predictions, not medical findings.</p>
      </section>
    </>
  );
}
