"use client";

import { useState } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";

export default function SignUpPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    setError(null);
    const { error: authError } = await supabase.auth.signUp({ email, password });
    if (authError) {
      setError(authError.message);
      setLoading(false);
    } else {
      setSuccess(true);
    }
  };

  if (success) {
    return (
      <section className="auth-success shell">
        <p className="eyebrow">Account created / one step remains</p>
        <p className="auth-success__mark" aria-hidden="true">✓</p>
        <h1 className="display display-medium">Check your<br /><em>inbox.</em></h1>
        <p>We sent a confirmation link to <strong>{email}</strong>. Activate the account, then return to sign in.</p>
        <Link href="/login" className="button button--outline">Go to login <span aria-hidden="true">→</span></Link>
      </section>
    );
  }

  return (
    <section className="auth-page shell">
      <div className="auth-intro">
        <p className="eyebrow">Secure access / new user</p>
        <h1 className="display">Create your<br /><em>research access.</em></h1>
        <p>An account keeps the analyzer gated and lets the backend verify each image request.</p>
      </div>
      <form onSubmit={handleSubmit} className="auth-form">
        <p className="auth-form__index">01 / NEW ACCOUNT</p>
        <label><span>Email address</span><input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label>
        <label><span>Password</span><input type="password" required minLength={6} autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Six characters minimum" /></label>
        <label><span>Confirm password</span><input type="password" required minLength={6} autoComplete="new-password" value={confirm} onChange={(event) => setConfirm(event.target.value)} placeholder="Repeat your password" /></label>
        {error && <p className="auth-message auth-message--error" role="alert">{error}</p>}
        <button type="submit" disabled={loading} className="button button--primary auth-submit">{loading ? "Creating account…" : "Create account"} <span aria-hidden="true">↗</span></button>
        <p className="auth-switch">Already registered? <Link href="/login">Log in →</Link></p>
      </form>
    </section>
  );
}
