import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative py-20 px-6 sm:px-12 lg:px-20">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl font-bold mb-6 leading-tight">
            <span className="text-emerald-400">Brain Tumor</span>
            {' '}Detection
          </h1>
          <p className="text-xl text-slate-300 mb-8 leading-relaxed">
            Instant AI-powered analysis of MRI scans to detect potential brain tumors with high accuracy.
          </p>
        </div>
      </section>

      {/* Upload Section */}
      <section className="py-16 px-6 sm:px-12 lg:px-20 bg-slate-900/50">
        <div className="max-w-2xl mx-auto">
          <Link href="/upload" className="block border-2 border-dashed border-emerald-600/40 rounded-lg p-12 text-center hover:border-emerald-500/60 transition-colors hover:bg-emerald-500/5 cursor-pointer">
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold mb-2">Upload MRI Image</h2>
            <p className="text-slate-400">Click here to go to the upload page</p>
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 px-6 sm:px-12 lg:px-20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center mb-4 text-emerald-400 font-bold text-lg">
                1
              </div>
              <h3 className="font-semibold text-lg mb-2">Upload</h3>
              <p className="text-slate-400">Submit your MRI scan image for analysis</p>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center mb-4 text-emerald-400 font-bold text-lg">
                2
              </div>
              <h3 className="font-semibold text-lg mb-2">Analyze</h3>
              <p className="text-slate-400">Our CNN processes the image in seconds</p>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col items-center text-center">
              <div className="w-12 h-12 rounded-full bg-emerald-600/20 border border-emerald-500/50 flex items-center justify-center mb-4 text-emerald-400 font-bold text-lg">
                3
              </div>
              <h3 className="font-semibold text-lg mb-2">Results</h3>
              <p className="text-slate-400">Receive detailed analysis and confidence score</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6 sm:px-12 lg:px-20 bg-slate-900/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Why Choose Us</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="border border-emerald-600/20 rounded-lg p-6 hover:border-emerald-500/40 transition-colors">
              <h3 className="text-emerald-400 font-semibold mb-2">High Accuracy</h3>
              <p className="text-slate-400">Advanced deep learning model trained on thousands of MRI scans</p>
            </div>
            <div className="border border-emerald-600/20 rounded-lg p-6 hover:border-emerald-500/40 transition-colors">
              <h3 className="text-emerald-400 font-semibold mb-2">Fast Results</h3>
              <p className="text-slate-400">Get analysis results in seconds, not minutes</p>
            </div>
            <div className="border border-emerald-600/20 rounded-lg p-6 hover:border-emerald-500/40 transition-colors">
              <h3 className="text-emerald-400 font-semibold mb-2">Easy to Use</h3>
              <p className="text-slate-400">Simple upload interface requires no medical expertise</p>
            </div>
            <div className="border border-emerald-600/20 rounded-lg p-6 hover:border-emerald-500/40 transition-colors">
              <h3 className="text-emerald-400 font-semibold mb-2">Secure</h3>
              <p className="text-slate-400">Your MRI scans are processed securely and never stored</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-6 sm:px-12 lg:px-20 text-center">
        <h2 className="text-3xl font-bold mb-6">Ready to get started?</h2>
        <Link href="/upload" className="inline-block bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-8 py-3 rounded-lg transition-colors">
          Upload Your MRI
        </Link>
      </section>
    </div>
  );
}
