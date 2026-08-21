export default function AboutPage() {
  return (
    <div className="py-20 px-6 sm:px-12 lg:px-20 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8 text-emerald-400">About NeuroScan AI</h1>
      <div className="prose prose-invert prose-emerald max-w-none">
        <p className="text-xl text-slate-300 leading-relaxed mb-8">
          Our mission is to democratize access to advanced medical imaging analysis. By leveraging state-of-the-art Convolutional Neural Networks (CNNs), we provide instant, highly accurate preliminary analysis of brain MRI scans.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-12">
          <div className="bg-slate-900/50 p-8 rounded-xl border border-white/5">
            <h3 className="text-2xl font-semibold text-white mb-4">Our Technology</h3>
            <p className="text-slate-400">We utilize a custom-trained deep learning architecture that has been validated against thousands of clinical MRI scans, achieving high sensitivity and specificity in tumor detection.</p>
          </div>
          <div className="bg-slate-900/50 p-8 rounded-xl border border-white/5">
            <h3 className="text-2xl font-semibold text-white mb-4">Our Vision</h3>
            <p className="text-slate-400">To empower healthcare professionals globally with AI tools that reduce diagnostic time and improve patient outcomes through early detection.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
