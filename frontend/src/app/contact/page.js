export default function ContactPage() {
  return (
    <div className="py-20 px-6 sm:px-12 lg:px-20 max-w-3xl mx-auto">
      <h1 className="text-4xl font-bold mb-4 text-emerald-400 text-center">Contact Us</h1>
      <p className="text-slate-400 text-center mb-12 text-lg">Have questions about our API or enterprise solutions? Reach out to our team.</p>
      
      <div className="bg-slate-900/50 p-8 rounded-2xl border border-white/5 shadow-xl">
        <form className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">First Name</label>
              <input type="text" className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all" placeholder="John" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Last Name</label>
              <input type="text" className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all" placeholder="Doe" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
            <input type="email" className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all" placeholder="john@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">Message</label>
            <textarea rows={4} className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all" placeholder="How can we help you?"></textarea>
          </div>
          <button type="button" className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-8 py-4 rounded-lg transition-all shadow-lg hover:shadow-emerald-500/25">
            Send Message
          </button>
        </form>
      </div>
    </div>
  );
}
