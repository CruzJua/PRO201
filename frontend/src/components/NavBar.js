"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/components/AuthProvider";

export default function NavBar() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-md border-b-2 border-[#ff006e]" style={{background: '#000000', boxShadow: '0 0 20px #ff006e/30'}}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold tracking-tighter font-mono" style={{color: '#00ff41', textShadow: '0 0 15px #00ff41'}}>
          ◆ NEUROSCAN ◆
        </Link>
        <nav className="flex items-center gap-6">
          <Link href="/" className="text-sm font-bold font-mono transition-all hover:drop-shadow-lg" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>HOME</Link>
          <Link href="/about" className="text-sm font-bold font-mono transition-all hover:drop-shadow-lg" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>ABOUT</Link>
          <Link href="/upload" className="text-sm font-bold font-mono transition-all hover:drop-shadow-lg" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>ANALYZE</Link>
          <Link href="/contact" className="text-sm font-bold font-mono transition-all hover:drop-shadow-lg" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>CONTACT</Link>
          {user ? (
            <div className="flex items-center gap-4 ml-4 pl-4 border-l-2 border-[#c700ff]">
              <span className="text-sm font-mono hidden sm:block" style={{color: '#ffff00', textShadow: '0 0 8px #ffff00'}}>{user.email}</span>
              <button
                onClick={handleSignOut}
                className="text-sm font-bold font-mono px-3 py-1.5 transition-all border border-[#ff006e]"
                style={{color: '#ff006e', textShadow: '0 0 8px #ff006e', boxShadow: '0 0 10px #ff006e/30'}}
              >
                LOGOUT
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3 ml-4 pl-4 border-l-2 border-[#c700ff]">
              <Link
                href="/login"
                className="text-sm font-bold font-mono transition-all"
                style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}
              >
                LOGIN
              </Link>
              <Link
                href="/signup"
                className="text-sm font-bold font-mono px-3 py-1.5 border border-[#00ff41]"
                style={{color: '#000000', backgroundColor: '#00ff41', textShadow: '0 0 5px #00ff41', boxShadow: '0 0 15px #00ff41'}}
              >
                SIGNUP
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
