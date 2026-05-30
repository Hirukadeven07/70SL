export default function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden animate-pulse">
      <div className="aspect-[16/9] bg-slate-200" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-slate-200 rounded w-3/4" />
        <div className="h-4 bg-slate-200 rounded w-1/2" />
        <div className="h-6 bg-slate-200 rounded w-1/3" />
        <div className="flex gap-2">
          <div className="h-5 bg-slate-200 rounded w-16" />
          <div className="h-5 bg-slate-200 rounded w-20" />
          <div className="h-5 bg-slate-200 rounded w-14" />
        </div>
      </div>
    </div>
  )
}
