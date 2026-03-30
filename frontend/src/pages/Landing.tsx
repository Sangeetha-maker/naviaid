import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useUserStore } from '../stores/userStore'

const FEATURES = [
  { icon: '🏛️', title: 'Government Schemes', desc: '100+ Tamil Nadu state & central government schemes' },
  { icon: '💼', title: 'Jobs & Skill Training', desc: 'PMKVY, apprenticeships, and job fairs near you' },
  { icon: '🩺', title: 'Health Services', desc: 'Ayushman Bharat, CM Health Insurance, free clinics' },
  { icon: '🎓', title: 'Scholarships', desc: 'Post-matric, merit, minority scholarships' },
  { icon: '🎤', title: 'Voice First', desc: 'Search in Tamil or English using your voice' },
  { icon: '📱', title: 'Works Offline', desc: 'PWA – install on your phone, works without internet' },
]

export default function Landing() {
  const { t } = useTranslation()
  const { user } = useUserStore()

  return (
    <div className="min-h-screen overflow-x-hidden">
      {/* Hero */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-4 text-center overflow-hidden">
        {/* Background blobs */}
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
        {/* Grid overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wMiI+PHBhdGggZD0iTTAgMGg0MHY0MEgweiIvPjwvZz48L2c+PHBhdGggZD0iTTAgMGg0MHY0MEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik00MCAwSDBNMCA0MEg0MCIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMC4wMyIgc3Ryb2tlLXdpZHRoPSIwLjUiLz48L3N2Zz4=')] opacity-40 pointer-events-none" />

        <div className="relative z-10 max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-300 text-sm font-medium mb-8 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
            Free · Tamil Nadu · AI-Powered
          </div>

          {/* Logo + brand */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl shadow-blue-500/40">
              <span className="text-white font-bold text-2xl">N</span>
            </div>
            <span className="text-4xl md:text-5xl font-bold text-white tracking-tight">NaviAid</span>
          </div>

          <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white leading-tight mb-6">
            Find Government Schemes<br />
            <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
              Built for Tamil Nadu
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-8 leading-relaxed">
            AI-powered, voice-first platform to discover scholarships, jobs, health services and
            government schemes tailored to <strong className="text-slate-300">your profile</strong>.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {user ? (
              <Link to="/dashboard"
                className="btn-primary text-base px-8 py-4 shadow-xl shadow-blue-500/30 hover:scale-105 transition-transform">
                Go to Dashboard →
              </Link>
            ) : (
              <>
                <Link to="/login"
                  className="btn-primary text-base px-8 py-4 shadow-xl shadow-blue-500/30 hover:scale-105 transition-transform">
                  {t('get_started')} — It's Free
                </Link>
                <Link to="/search"
                  className="btn btn-ghost text-base px-8 border border-slate-600 hover:border-slate-400 hover:scale-105 transition-transform">
                  Browse Schemes
                </Link>
              </>
            )}
          </div>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 mt-16 pt-8 border-t border-slate-800">
            {[
              ['100+', 'Schemes & Jobs'],
              ['35', 'TN Districts'],
              ['Free', 'Always'],
            ].map(([val, label]) => (
              <div key={label} className="text-center">
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">{val}</div>
                <div className="text-xs text-slate-500 mt-1">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-4">Everything you need</h2>
          <p className="text-slate-400 text-center max-w-xl mx-auto mb-12">
            Designed for underprivileged communities across Tamil Nadu — accessible, voice-first, free.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map(({ icon, title, desc }) => (
              <div key={title}
                className="card hover:scale-[1.02] transition-transform cursor-default">
                <div className="text-3xl mb-3">{icon}</div>
                <h3 className="font-semibold text-white mb-1">{title}</h3>
                <p className="text-slate-400 text-sm">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to find your benefits?
          </h2>
          <p className="text-slate-400 mb-8">
            Join thousands of Tamil Nadu residents discovering schemes they didn't know they qualified for.
          </p>
          <Link to="/login"
            className="btn-primary text-base px-10 py-4 shadow-xl shadow-blue-500/30 hover:scale-105 transition-transform inline-flex">
            Start for Free →
          </Link>
        </div>
      </section>
    </div>
  )
}
