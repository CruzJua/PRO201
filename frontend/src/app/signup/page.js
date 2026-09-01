"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function SignUpPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    setError(null);

    const { error } = await supabase.auth.signUp({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      setSuccess(true);
    }
  };

  if (success) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6">
        <div className="text-center max-w-md">
          <div className="w-16 h-16 flex items-center justify-center mx-auto mb-6" style={{border: '2px solid #00ff41', boxShadow: '0 0 20px #00ff41'}}>
            <svg
              className="w-8 h-8"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              style={{color: '#00ff41', filter: 'drop-shadow(0 0 10px #00ff41)'}}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold font-mono mb-3" style={{color: '#ffff00', textShadow: '0 0 15px #ffff00'}}>EMAIL CONFIRMED</h2>
          <p className="font-mono mb-6" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>
            ▌Verification link sent to {' '}<br/>
            <strong style={{color: '#00ff41'}}>{email}</strong> ▌
          </p>
          <Link href="/login" className="font-bold font-mono text-sm px-4 py-2 border-2" style={{color: '#000000', backgroundColor: '#00f0ff', borderColor: '#00f0ff', boxShadow: '0 0 15px #00f0ff'}}>
            GO TO LOGIN
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <h1 className="text-4xl font-bold text-center mb-8 font-mono" style={{color: '#ff006e', textShadow: '0 0 20px #ff006e'}}>
          CREATE ACCOUNT
        </h1>
        <form
          onSubmit={handleSubmit}
          className="p-8 space-y-5 border-2"
          style={{borderColor: '#c700ff', background: '#000000', boxShadow: '0 0 30px #c700ff/30'}}
        >
          <div>
            <label className="block text-sm font-bold font-mono mb-1.5" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>
              EMAIL ADDRESS
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2.5 font-mono focus:outline-none"
              placeholder="you@example.com"
              style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}}
              onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'}
              onBlur={(e) => e.target.style.boxShadow = 'none'}
            />
          </div>
          <div>
            <label className="block text-sm font-bold font-mono mb-1.5" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>
              PASSWORD
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2.5 font-mono focus:outline-none"
              placeholder="••••••••"
              style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}}
              onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'}
              onBlur={(e) => e.target.style.boxShadow = 'none'}
            />
          </div>
          <div>
            <label className="block text-sm font-bold font-mono mb-1.5" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>
              CONFIRM PASSWORD
            </label>
            <input
              type="password"
              required
              minLength={6}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              className="w-full px-4 py-2.5 font-mono focus:outline-none"
              placeholder="••••••••"
              style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}}
              onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'}
              onBlur={(e) => e.target.style.boxShadow = 'none'}
            />
          </div>
          {error && (
            <p className="text-sm font-mono px-4 py-2.5 border-2" style={{color: '#ffff00', borderColor: '#ff006e', background: '#000000', textShadow: '0 0 10px #ffff00'}}>
              ERROR: {error}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full font-bold py-2.5 font-mono text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed border-2"
            style={{color: '#000000', backgroundColor: '#c700ff', borderColor: '#c700ff', textShadow: '0 0 5px #c700ff', boxShadow: '0 0 15px #c700ff'}}
          >
            {loading ? ">>> CREATING ACCOUNT <<<" : ">>> CREATE ACCOUNT <<<"}
          </button>
          <p className="text-center text-sm font-mono" style={{color: '#00f0ff'}}>
            ALREADY HAVE AN ACCOUNT?{" "}
            <Link href="/login" className="font-bold" style={{color: '#ffff00', textShadow: '0 0 8px #ffff00'}}>
              LOG IN
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
