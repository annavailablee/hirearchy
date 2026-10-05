export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-blush-50">
      {/* Left: brand panel */}
      <div className="hidden lg:flex flex-col justify-between bg-plum text-blush-50 p-12">
        <div>
          <h1 className="font-display text-4xl leading-none tracking-tight">
            Hirearchy
          </h1>
          <p className="mt-3 text-sm text-blush-100/60 uppercase tracking-[0.18em]">
            Find · Match · Apply · Track
          </p>
        </div>
        <div className="max-w-md">
          <p className="font-display text-3xl leading-snug">
            Your job search,{" "}
            <span className="text-blush">organized.</span>
          </p>
          <p className="mt-4 text-sm text-blush-100/70 leading-relaxed">
            Upload your resume, discover roles matched to your skills, track
            applications through every stage, and see exactly which skills to
            build next.
          </p>
        </div>
        <p className="text-[10px] text-blush-100/40 uppercase tracking-[0.18em]">
          A career intelligence platform
        </p>
      </div>

      {/* Right: form panel */}
      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}