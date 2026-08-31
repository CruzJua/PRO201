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
    <header className="sticky top-0 z-50 w-full backdrop-blur-md border-b border-white/10 bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold tracking-tighter text-emerald-400">
          NeuroScan AI
        </Link>
        <nav className="flex items-center gap-6">
          <Link href="/" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Home</Link>
          <Link href="/about" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">About</Link>
          <Link href="/upload" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Upload MRI</Link>
          <Link href="/contact" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Contact</Link>
          {user ? (
            <div className="flex items-center gap-4">
              <span className="text-sm text-slate-400 hidden sm:block">{user.email}</span>
              <button
                onClick={handleSignOut}
                className="text-sm font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-md transition-colors"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors"
              >
                Log In
              </Link>
              <Link
                href="/signup"
                className="text-sm font-medium bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-md transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
