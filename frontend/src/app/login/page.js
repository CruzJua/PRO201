"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    const { error: authError } = await supabase.auth.signInWithPassword({ email, password });
    if (authError) {
      setError(authError.message);
      setLoading(false);
    } else {
      router.push("/upload");
    }
  };

  return (
    <section className="auth-page shell">
      <div className="auth-intro">
        <p className="eyebrow">Secure access / returning user</p>
        <h1 className="display">Enter the<br /><em>research space.</em></h1>
        <p>Sign in to access the authenticated MRI analyzer and submit an image to the model.</p>
      </div>
      <form onSubmit={handleSubmit} className="auth-form">
        <p className="auth-form__index">01 / CREDENTIALS</p>
        <label><span>Email address</span><input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
        <label><span>Password</span><input type="password" required autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="••••••••" /></label>
        {error && <p className="auth-message auth-message--error" role="alert">{error}</p>}
        <button type="submit" disabled={loading} className="button button--primary auth-submit">{loading ? "Signing in…" : "Sign in"} <span aria-hidden="true">↗</span></button>
        <p className="auth-switch">New to NeuroScan? <Link href="/signup">Create an account →</Link></p>
      </form>
    </section>
  );
}
