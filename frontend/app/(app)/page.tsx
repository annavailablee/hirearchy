export default function DashboardPage() {
  return (
    <div className="p-10 max-w-6xl">
      <header className="mb-12">
        <p className="text-[13px] text-mauve mb-2 tracking-wide">Good morning</p>
        <h1 className="font-display text-5xl leading-tight tracking-tight text-ink">
          Welcome to Hirearchy
        </h1>
        <p className="mt-3 text-mauve max-w-xl">
          Your career intelligence hub. Session 3 will fill this with real data
          from your backend.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <MetricCard label="Applications" value="—" />
        <MetricCard label="Interviews" value="—" />
        <MetricCard label="Skill gaps" value="—" />
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-soft ring-1 ring-border/40">
      <p className="text-[10px] uppercase tracking-[0.16em] text-mauve mb-3">
        {label}
      </p>
      <p className="font-display text-4xl text-ink leading-none">{value}</p>
    </div>
  );
}