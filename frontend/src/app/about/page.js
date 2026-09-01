export default function AboutPage() {
  return (
    <div className="py-20 px-6 sm:px-12 lg:px-20 max-w-4xl mx-auto">
      <h1 className="text-5xl font-bold mb-8 font-mono glitch-text" data-text="ABOUT NEUROSCAN" style={{color: '#00ff41', textShadow: '0 0 20px #00ff41'}}>ABOUT NEUROSCAN</h1>
      <div className="space-y-8">
        <p className="text-lg font-mono leading-relaxed" style={{color: '#00f0ff', textShadow: '0 0 10px #00f0ff'}}>
          ▌ MISSION: Democratize access to advanced AI-powered medical imaging analysis using cutting-edge neural networks for instant, highly accurate brain MRI scan analysis. Built for the private MRI scanner enjoyer.▌
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="p-8 border-2" style={{borderColor: '#ff006e', background: '#000000', boxShadow: '0 0 20px #ff006e/30'}}>
            <h3 className="text-2xl font-bold font-mono mb-4" style={{color: '#ff006e', textShadow: '0 0 10px #ff006e'}}>⚡ OUR TECHNOLOGY</h3>
            <p className="font-mono text-sm" style={{color: '#ffff00', textShadow: '0 0 8px #ffff00'}}>Custom CNN trained on 10k+ clinical scans | High sensitivity & specificity | Real-time processing | Secure architecture</p>
          </div>
          <div className="p-8 border-2" style={{borderColor: '#00f0ff', background: '#000000', boxShadow: '0 0 20px #00f0ff/30'}}>
            <h3 className="text-2xl font-bold font-mono mb-4" style={{color: '#00f0ff', textShadow: '0 0 10px #00f0ff'}}>⚡ OUR VISION</h3>
            <p className="font-mono text-sm" style={{color: '#ffff00', textShadow: '0 0 8px #ffff00'}}>Empower healthcare professionals globally | Reduce diagnostic time | Improve patient outcomes | Enable early detection</p>
          </div>
        </div>
      </div>
    </div>
  );
}
