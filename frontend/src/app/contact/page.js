"use client";

export default function ContactPage() {
  return (
    <div className="py-20 px-6 sm:px-12 lg:px-20 max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold mb-4 font-mono text-center glitch-text" data-text="CONTACT US" style={{color: '#ff006e', textShadow: '0 0 20px #ff006e'}}>CONTACT US</h1>
      <p className="font-mono text-center mb-12 text-lg" style={{color: '#00f0ff', textShadow: '0 0 8px #00f0ff'}}>▌ Have questions? Reach out to our team. We'll respond ASAP. ▌</p>
      
      <div className="p-8 border-2" style={{borderColor: '#c700ff', background: '#000000', boxShadow: '0 0 30px #c700ff/30'}}>
        <form className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-bold font-mono mb-2" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>FIRST NAME</label>
              <input type="text" className="w-full px-4 py-3 font-mono focus:outline-none" placeholder="John" style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}} onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'} onBlur={(e) => e.target.style.boxShadow = 'none'} />
            </div>
            <div>
              <label className="block text-sm font-bold font-mono mb-2" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>LAST NAME</label>
              <input type="text" className="w-full px-4 py-3 font-mono focus:outline-none" placeholder="Doe" style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}} onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'} onBlur={(e) => e.target.style.boxShadow = 'none'} />
            </div>
          </div>
          <div>
            <label className="block text-sm font-bold font-mono mb-2" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>EMAIL</label>
            <input type="email" className="w-full px-4 py-3 font-mono focus:outline-none" placeholder="you@example.com" style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}} onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'} onBlur={(e) => e.target.style.boxShadow = 'none'} />
          </div>
          <div>
            <label className="block text-sm font-bold font-mono mb-2" style={{color: '#00ff41', textShadow: '0 0 8px #00ff41'}}>MESSAGE</label>
            <textarea rows={4} className="w-full px-4 py-3 font-mono focus:outline-none" placeholder="What's on your mind?" style={{background: '#000000', border: '2px solid #ff006e', color: '#00ff41', textShadow: '0 0 5px #00ff41'}} onFocus={(e) => e.target.style.boxShadow = '0 0 15px #ff006e'} onBlur={(e) => e.target.style.boxShadow = 'none'}></textarea>
          </div>
          <button type="button" className="w-full font-bold px-8 py-4 font-mono text-lg transition-all border-2" style={{color: '#000000', backgroundColor: '#00ff41', borderColor: '#00ff41', textShadow: '0 0 5px #00ff41', boxShadow: '0 0 15px #00ff41'}}>
            SEND MESSAGE 
          </button>
        </form>
      </div>
    </div>
  );
}
