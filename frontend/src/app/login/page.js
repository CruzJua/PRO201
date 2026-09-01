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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const { error } = await supabase.auth.signInWithPassword({ email, password });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      router.push("/upload");
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <h1 className="text-4xl font-bold text-center mb-8 font-mono glitch-text" data-text="[LOG IN]" style={{color: '#ff006e', textShadow: '0 0 20px #ff006e'}}>[LOG IN]</h1>
        <form
          onSubmit={handleSubmit}
          className="border-2 p-8 space-y-5"
          style={{borderColor: '#00f0ff', background: '#000000', boxShadow: '0 0 30px #00f0ff/30'}}
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
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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
            style={{color: '#000000', backgroundColor: '#00ff41', borderColor: '#00ff41', textShadow: '0 0 5px #00ff41', boxShadow: '0 0 15px #00ff41'}}
          >
            {loading ? ">>> AUTHENTICATING <<<" : ">>> LOGIN <<<"}
          </button>
          <p className="text-center text-sm font-mono" style={{color: '#00f0ff'}}>
            NO ACCOUNT?{" "}
            <Link href="/signup" className="font-bold" style={{color: '#ffff00', textShadow: '0 0 8px #ffff00'}}>
              CREATE ONE
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
