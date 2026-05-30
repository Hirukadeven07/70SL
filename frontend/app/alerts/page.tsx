import AlertForm from '@/components/AlertForm'

export const metadata = {
  title: 'Alerts | 70SL Sri Lanka 4x4 Listings',
  description: 'Create email alerts for new 4x4 and double-cab listings in Sri Lanka.',
}

export default function AlertsPage() {
  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-brand-primary to-slate-800 py-14 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="font-display font-bold text-3xl sm:text-5xl text-white tracking-widest uppercase mb-2">
            Alerts
          </h1>
          <p className="text-slate-300 text-sm sm:text-base max-w-xl">
            Set up an email alert and we&apos;ll notify you the moment a new listing matches your
            criteria — no more checking manually.
          </p>
        </div>
      </section>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* How it works */}
          <div>
            <h2 className="text-lg font-bold text-brand-text mb-6 uppercase tracking-wide">
              How it works
            </h2>
            <ol className="space-y-6">
              {[
                {
                  step: '01',
                  title: 'Set your criteria',
                  body: 'Choose body type, price range, district, fuel type, and more.',
                },
                {
                  step: '02',
                  title: 'Enter your email',
                  body: 'We store only your email and filter preferences — nothing else.',
                },
                {
                  step: '03',
                  title: 'Get notified',
                  body: 'Receive an email whenever a matching listing is scraped from Ikman, Riyasewana, or Sarathi Ads.',
                },
              ].map(({ step, title, body }) => (
                <li key={step} className="flex gap-5">
                  <span className="font-display font-bold text-3xl text-brand-cta leading-none shrink-0">
                    {step}
                  </span>
                  <div>
                    <h3 className="font-semibold text-brand-text mb-1">{title}</h3>
                    <p className="text-sm text-brand-muted leading-relaxed">{body}</p>
                  </div>
                </li>
              ))}
            </ol>

            {/* Sources */}
            <div className="mt-10 p-5 bg-white border border-slate-200 rounded-xl">
              <p className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-4">
                Listings scraped from
              </p>
              <div className="flex flex-wrap gap-3">
                {[
                  { label: 'Ikman.lk',       classes: 'bg-blue-50 text-blue-700 border-blue-200' },
                  { label: 'Riyasewana.com',  classes: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
                  { label: 'Sarathiads.lk',  classes: 'bg-amber-50 text-amber-700 border-amber-200' },
                ].map(({ label, classes }) => (
                  <span key={label} className={`px-3 py-1 text-xs font-semibold border rounded-full ${classes}`}>
                    {label}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Alert form */}
          <div>
            <AlertForm />
          </div>
        </div>
      </div>
    </>
  )
}
