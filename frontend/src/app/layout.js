import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Brain Tumor Detection",
  description: "AI-powered analysis of MRI scans",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-950 text-white">
        <header className="sticky top-0 z-50 w-full backdrop-blur-md border-b border-white/10 bg-slate-950/80">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <Link href="/" className="text-xl font-bold tracking-tighter text-emerald-400">
              NeuroScan AI
            </Link>
            <nav className="flex gap-6">
              <Link href="/" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Home</Link>
              <Link href="/about" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">About</Link>
              <Link href="/upload" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Upload MRI</Link>
              <Link href="/contact" className="text-sm font-medium text-slate-300 hover:text-emerald-400 transition-colors">Contact</Link>
            </nav>
          </div>
        </header>
        <main className="flex-1">
          {children}
        </main>
      </body>
    </html>
  );
}
