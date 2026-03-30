import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useUserStore } from '../stores/userStore'
import { updateProfile } from '../lib/api'
import clsx from 'clsx'

const TN_DISTRICTS = [
  'Chennai','Coimbatore','Madurai','Tiruchirappalli','Salem',
  'Tirunelveli','Tiruppur','Vellore','Erode','Thoothukkudi',
  'Dindigul','Thanjavur','Ranipet','Sivaganga','Virudhunagar',
  'Kancheepuram','Nagercoil','Karur','Namakkal','Cuddalore',
  'Krishnagiri','Dharmapuri','Villupuram','Ariyalur','Perambalur',
  'Nagapattinam','Mayiladuthurai','Tiruvarur','Pudukkottai','Ramanathapuram',
  'Tenkasi','Chengalpattu','Tirupattur','Kallakurichi','The Nilgiris',
]

const CATEGORIES = ['scholarship','job','health','loan','housing','agriculture','skill_training']
const EDUCATIONS = ['Below 5th','5th-10th','10th Pass','12th Pass','ITI/Diploma','UG Degree','PG/PhD']
const OCCUPATIONS = ['Unemployed','Student','Farmer','Daily Wage','Self Employed','Private Job','Government Job']
const CASTES = ['General','OBC','MBC','SC','ST']
const GENDERS = ['Male','Female','Transgender','Prefer not to say']

type FormData = {
  name: string; age: string; gender: string; district: string;
  caste: string; annual_income: string; education: string;
  occupation: string; interested_categories: string[]
}

const STEPS = [
  { title: 'Personal Info', fields: ['name','age','gender'] },
  { title: 'Location & Background', fields: ['district','caste','annual_income'] },
  { title: 'Education & Work', fields: ['education','occupation'] },
  { title: 'Interests', fields: ['interested_categories'] },
  { title: 'All Set!', fields: [] },
]

export default function Onboard() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setUser } = useUserStore()
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState<FormData>({
    name: '', age: '', gender: '', district: '', caste: '',
    annual_income: '', education: '', occupation: '', interested_categories: [],
  })

  const set = (key: keyof FormData, value: string | string[]) =>
    setForm((f) => ({ ...f, [key]: value }))

  const toggleCat = (cat: string) => {
    const arr = form.interested_categories
    set('interested_categories', arr.includes(cat) ? arr.filter((c) => c !== cat) : [...arr, cat])
  }

  const handleFinish = async () => {
    setLoading(true)
    try {
      const updated = await updateProfile({
        ...form,
        age: form.age ? parseInt(form.age) : undefined,
        annual_income: form.annual_income ? parseInt(form.annual_income) : undefined,
        is_onboarded: true,
      })
      setUser({ ...updated, is_onboarded: true })
      navigate('/dashboard')
    } catch {
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  const progress = ((step + 1) / STEPS.length) * 100

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
      <div className="w-full max-w-lg">
        {/* Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-slate-400 mb-2">
            <span>{t('step')} {step + 1} {t('of')} {STEPS.length}</span>
            <span>{STEPS[step].title}</span>
          </div>
          <div className="h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="bg-slate-800/70 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 shadow-2xl">
          {/* Step 0 – Personal */}
          {step === 0 && (
            <div className="flex flex-col gap-4">
              <h2 className="text-xl font-bold text-white mb-2">Personal Information</h2>
              <div>
                <label className="label" htmlFor="ob-name">{t('name')}</label>
                <input id="ob-name" className="input" value={form.name}
                  onChange={(e) => set('name', e.target.value)} placeholder="Your full name" />
              </div>
              <div>
                <label className="label" htmlFor="ob-age">{t('age')}</label>
                <input id="ob-age" className="input" type="number" min={5} max={120}
                  value={form.age} onChange={(e) => set('age', e.target.value)} placeholder="e.g. 24" />
              </div>
              <div>
                <label className="label">{t('gender')}</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {GENDERS.map((g) => (
                    <button key={g} type="button"
                      className={clsx('px-3 py-1.5 rounded-xl text-sm border transition-colors',
                        form.gender === g
                          ? 'bg-blue-600 border-blue-500 text-white'
                          : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-blue-500')}
                      onClick={() => set('gender', g)}>{g}</button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 1 – Location */}
          {step === 1 && (
            <div className="flex flex-col gap-4">
              <h2 className="text-xl font-bold text-white mb-2">Location & Background</h2>
              <div>
                <label className="label" htmlFor="ob-district">{t('district')}</label>
                <select id="ob-district" className="input" value={form.district}
                  onChange={(e) => set('district', e.target.value)}>
                  <option value="">Select district</option>
                  {TN_DISTRICTS.map((d) => <option key={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label className="label">{t('caste')}</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {CASTES.map((c) => (
                    <button key={c} type="button"
                      className={clsx('px-3 py-1.5 rounded-xl text-sm border transition-colors',
                        form.caste === c
                          ? 'bg-blue-600 border-blue-500 text-white'
                          : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-blue-500')}
                      onClick={() => set('caste', c)}>{c}</button>
                  ))}
                </div>
              </div>
              <div>
                <label className="label" htmlFor="ob-income">{t('annual_income')}</label>
                <input id="ob-income" className="input" type="number" min={0}
                  value={form.annual_income} onChange={(e) => set('annual_income', e.target.value)}
                  placeholder="e.g. 150000" />
              </div>
            </div>
          )}

          {/* Step 2 – Education */}
          {step === 2 && (
            <div className="flex flex-col gap-4">
              <h2 className="text-xl font-bold text-white mb-2">Education & Work</h2>
              <div>
                <label className="label">{t('education')}</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {EDUCATIONS.map((e) => (
                    <button key={e} type="button"
                      className={clsx('px-3 py-1.5 rounded-xl text-sm border transition-colors',
                        form.education === e
                          ? 'bg-indigo-600 border-indigo-500 text-white'
                          : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-indigo-500')}
                      onClick={() => set('education', e)}>{e}</button>
                  ))}
                </div>
              </div>
              <div>
                <label className="label">{t('occupation')}</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {OCCUPATIONS.map((o) => (
                    <button key={o} type="button"
                      className={clsx('px-3 py-1.5 rounded-xl text-sm border transition-colors',
                        form.occupation === o
                          ? 'bg-indigo-600 border-indigo-500 text-white'
                          : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-indigo-500')}
                      onClick={() => set('occupation', o)}>{o}</button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 3 – Interests */}
          {step === 3 && (
            <div className="flex flex-col gap-4">
              <h2 className="text-xl font-bold text-white mb-2">What are you looking for?</h2>
              <div className="flex flex-wrap gap-2">
                {CATEGORIES.map((cat) => (
                  <button key={cat} type="button"
                    onClick={() => toggleCat(cat)}
                    className={clsx('px-4 py-2 rounded-xl text-sm border font-medium transition-all',
                      form.interested_categories.includes(cat)
                        ? 'bg-blue-600 border-blue-500 text-white scale-[1.03]'
                        : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-blue-500')}
                  >
                    {t(cat)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 4 – Done */}
          {step === 4 && (
            <div className="flex flex-col items-center text-center gap-4 py-4">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-xl shadow-green-500/30">
                <span className="text-4xl">🎉</span>
              </div>
              <h2 className="text-2xl font-bold text-white">You're all set!</h2>
              <p className="text-slate-400 text-sm max-w-xs">
                NaviAid will now show you personalised government schemes, jobs and scholarships.
              </p>
            </div>
          )}

          {/* Nav buttons */}
          <div className="flex justify-between mt-8">
            <button
              onClick={() => setStep((s) => Math.max(0, s - 1))}
              disabled={step === 0}
              className="btn btn-ghost"
            >
              {t('back')}
            </button>
            {step < STEPS.length - 1 ? (
              <button onClick={() => setStep((s) => s + 1)} className="btn-primary">
                {t('next')}
              </button>
            ) : (
              <button onClick={handleFinish} disabled={loading} className="btn-primary">
                {loading
                  ? <span className="inline-block w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  : t('finish')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
