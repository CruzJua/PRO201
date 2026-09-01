import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="relative py-20 px-6 sm:px-12 lg:px-20 border-b-2 border-[#ff006e]/50">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl font-bold mb-6 leading-tight glitch-text" data-text="BRAIN TUMOR DETECTION">
            <span style={{color: '#00ff41', textShadow: '0 0 20px #00ff41'}}>BRAIN TUMOR</span>
            {' '}
            <span style={{color: '#00f0ff', textShadow: '0 0 20px #00f0ff'}}>DETECTION</span>
          </h1>
          <p className="text-lg mb-8 leading-relaxed font-mono" style={{color: '#ffff00', textShadow: '0 0 10px #ffff00'}}>
            ▌INSTANT AI-POWERED MRI ANALYSIS▌ | HIGH ACCURACY DETECTION
          </p>
        </div>
      </section>

      {/* Upload Section */}
      <section className="py-16 px-6 sm:px-12 lg:px-20 border-b-2 border-[#c700ff]/50">
        <div className="max-w-2xl mx-auto">
          <Link href="/upload" className="block border-2 border-[#ff006e] p-12 text-center hover:border-[#00f0ff] transition-all hover:shadow-lg cursor-pointer hover:bg-black/30" style={{boxShadow: '0 0 20px #ff006e/30'}}>
            <div className="mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{color: '#00ff41', filter: 'drop-shadow(0 0 10px #00ff41)'}}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-2 font-mono" style={{color: '#ff006e', textShadow: '0 0 10px #ff006e'}}>▌UPLOAD MRI IMAGE▌</h2>
            <p className="font-mono" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}> CLICK TO ANALYZE </p>
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 px-6 sm:px-12 lg:px-20 border-b-2 border-[#00f0ff]/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center font-mono" style={{color: '#00ff41', textShadow: '0 0 15px #00ff41'}}> HOW IT WORKS </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <div className="flex flex-col items-center text-center border border-[#ff006e] p-6" style={{boxShadow: '0 0 15px #ff006e/30'}}>
              <div className="w-12 h-12 flex items-center justify-center mb-4 text-2xl font-bold font-mono mb-4" style={{color: '#ffff00', border: '2px solid #ffff00', textShadow: '0 0 10px #ffff00'}}>
                1
              </div>
              <h3 className="font-bold text-lg mb-2 font-mono" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>UPLOAD</h3>
              <p className="font-mono text-sm" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>Submit your MRI scan for analysis</p>
            </div>

            {/* Step 2 */}
            <div className="flex flex-col items-center text-center border border-[#00f0ff] p-6" style={{boxShadow: '0 0 15px #00f0ff/30'}}>
              <div className="w-12 h-12 flex items-center justify-center mb-4 text-2xl font-bold font-mono mb-4" style={{color: '#ffff00', border: '2px solid #ffff00', textShadow: '0 0 10px #ffff00'}}>
                2
              </div>
              <h3 className="font-bold text-lg mb-2 font-mono" style={{color: '#ff006e', textShadow: '0 0 8px #ff006e'}}>ANALYZE</h3>
              <p className="font-mono text-sm" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>AI model processes image instantly</p>
            </div>

            {/* Step 3 */}
            <div className="flex flex-col items-center text-center border border-[#c700ff] p-6" style={{boxShadow: '0 0 15px #c700ff/30'}}>
              <div className="w-12 h-12 flex items-center justify-center mb-4 text-2xl font-bold font-mono mb-4" style={{color: '#ffff00', border: '2px solid #ffff00', textShadow: '0 0 10px #ffff00'}}>
                3
              </div>
              <h3 className="font-bold text-lg mb-2 font-mono" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>RESULTS</h3>
              <p className="font-mono text-sm" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>Get detailed analysis & confidence score</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6 sm:px-12 lg:px-20 border-b-2 border-[#ff006e]/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center font-mono" style={{color: '#c700ff', textShadow: '0 0 15px #c700ff'}}>WHY CHOOSE US</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="border-2 border-[#00ff41] p-6 hover:border-[#ffff00] transition-all" style={{boxShadow: '0 0 15px #00ff41/20'}}>
              <h3 className="font-bold mb-2 font-mono text-lg" style={{color: '#00ff41', textShadow: '0 0 10px #00ff41'}}>⚡ HIGH ACCURACY</h3>
              <p className="font-mono text-sm" style={{color: '#00f0ff'}}>Advanced neural networks trained on 10k+ MRI scans</p>
            </div>
            <div className="border-2 border-[#ff006e] p-6 hover:border-[#ffff00] transition-all" style={{boxShadow: '0 0 15px #ff006e/20'}}>
              <h3 className="font-bold mb-2 font-mono text-lg" style={{color: '#ff006e', textShadow: '0 0 10px #ff006e'}}>⚡ LIGHTNING FAST</h3>
              <p className="font-mono text-sm" style={{color: '#00f0ff'}}>Get results in milliseconds, not minutes</p>
            </div>
            <div className="border-2 border-[#00f0ff] p-6 hover:border-[#ffff00] transition-all" style={{boxShadow: '0 0 15px #00f0ff/20'}}>
              <h3 className="font-bold mb-2 font-mono text-lg" style={{color: '#00f0ff', textShadow: '0 0 10px #00f0ff'}}>⚡ EASY TO USE</h3>
              <p className="font-mono text-sm" style={{color: '#00ff41'}}>Simple interface - no medical expertise needed</p>
            </div>
            <div className="border-2 border-[#c700ff] p-6 hover:border-[#ffff00] transition-all" style={{boxShadow: '0 0 15px #c700ff/20'}}>
              <h3 className="font-bold mb-2 font-mono text-lg" style={{color: '#c700ff', textShadow: '0 0 10px #c700ff'}}>⚡ SECURE</h3>
              <p className="font-mono text-sm" style={{color: '#00f0ff'}}>Encrypted processing, zero data retention</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 sm:px-12 lg:px-20 text-center border-t-2 border-b-2 border-[#00f0ff]/50">
        <h2 className="text-4xl font-bold mb-6 font-mono glitch-text" data-text="READY TO ANALYZE?" style={{color: '#ff006e', textShadow: '0 0 20px #ff006e'}}>READY TO ANALYZE?</h2>
        <Link href="/upload" className="inline-block font-bold px-8 py-4 rounded-none transition-all font-mono text-lg" style={{color: '#000000', backgroundColor: '#ffff00', border: '2px solid #ffff00', boxShadow: '0 0 20px #ffff00', textShadow: '0 0 5px #ffff00'}}>
          ▌ UPLOAD YOUR MRI NOW ▌
        </Link>
      </section>
    </div>
  );
}
