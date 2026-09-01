"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/components/AuthProvider";

const navItems = [["Home", "/"], ["Method", "/about"], ["Analyze", "/upload"], ["Contact", "/contact"]];

export default function NavBar() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link href="/" className="wordmark" aria-label="NeuroScan home"><span>Neuro</span><span>/ Scan</span></Link>
        <span className="header-note">Medical imaging research prototype</span>
        <nav className="site-nav" aria-label="Primary navigation">
          {navItems.map(([label, href], index) => (
            <Link href={href} key={href}><span>{String(index + 1).padStart(2, "0")}</span>{label}</Link>
          ))}
          {!loading && (user ? (
            <>
              <span className="auth-identity" title={user.email}>{user.email}</span>
              <button type="button" onClick={handleSignOut}><span>05</span>Sign out</button>
            </>
          ) : (
            <>
              <Link href="/login"><span>05</span>Log in</Link>
              <Link href="/signup" className="site-nav__accent"><span>06</span>Sign up</Link>
            </>
          ))}
        </nav>
      </div>
    </header>
  );
}
