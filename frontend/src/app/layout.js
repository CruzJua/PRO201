import Link from "next/link";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import NavBar from "@/components/NavBar";

export const metadata = {
  title: { default: "NeuroScan — MRI Classification Research", template: "%s — NeuroScan" },
  description: "A research prototype for rapid, AI-assisted brain MRI image classification.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <NavBar />
          <main>{children}</main>
          <footer className="site-footer">
            <div className="site-footer__top">
              <p className="display-small">A clearer first look at complex scans.</p>
              <Link href="/upload" className="text-link text-link--light">Open analyzer <span aria-hidden="true">↗</span></Link>
            </div>
            <div className="site-footer__bottom">
              <p>NEUROSCAN / RESEARCH BUILD</p>
              <p>For educational use — not a medical diagnosis</p>
              <p>© 2026</p>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
