"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { BarChart3, TrendingUp, Target } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import type {
  ApplicationInsights,
  SkillInsights,
} from "@/lib/insights-types";
import { AnimatedNumber } from "@/components/count-up";

export default function InsightsPage() {
  const [skills, setSkills] = useState<SkillInsights | null>(null);
  const [apps, setApps] = useState<ApplicationInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [s, a] = await Promise.all([
          apiFetch<SkillInsights>("/insights/skills"),
          apiFetch<ApplicationInsights>("/insights/applications"),
        ]);
        if (!cancelled) {
          setSkills(s);
          setApps(a);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Could not load insights (${err.status})`
              : "Could not reach the backend."
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-5xl mx-auto">
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="mb-10"
        >
          <div className="flex items-center gap-2 mb-2 text-mauve text-[13px]">
            <BarChart3 size={14} strokeWidth={1.8} />
            Insights
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            Your patterns
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed">
            What your saved jobs and applications say about your search.
          </p>
        </motion.header>

        {loading && (
          <div className="flex items-center gap-3 text-mauve text-sm py-8">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
            Analyzing…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
            {error}
          </div>
        )}

        {!loading && !error && skills && apps && (
          <motion.div
            initial="hidden"
            animate="show"
            variants={{
              hidden: {},
              show: { transition: { staggerChildren: 0.08 } },
            }}
            className="space-y-8"
          >
            {/* Application funnel */}
            <motion.section
              variants={{
                hidden: { opacity: 0, y: 8 },
                show: { opacity: 1, y: 0 },
              }}
              className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8"
            >
              <div className="flex items-center gap-2 mb-6">
                <Target size={16} className="text-plum" strokeWidth={1.9} />
                <h2 className="font-display text-2xl text-ink">
                  Application funnel
                </h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <FunnelMetric label="Tracked" value={apps.total} />
                <FunnelMetric
                  label="Response rate"
                  value={apps.response_rate_pct}
                  suffix="%"
                  decimals={1}
                />
                <FunnelMetric
                  label="Interview rate"
                  value={apps.interview_rate_pct}
                  suffix="%"
                  decimals={1}
                />
                <FunnelMetric
                  label="Offers"
                  value={apps.by_status.OFFER ?? 0}
                  accent
                />
              </div>
              {apps.total > 0 && (
                <div className="mt-6 pt-6 border-t border-border/40">
                  <p className="text-[11px] uppercase tracking-[0.14em] text-mauve mb-3 font-medium">
                    By status
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(apps.by_status).map(([status, count]) => (
                      <span
                        key={status}
                        className="inline-flex items-baseline gap-1.5 rounded-full bg-blush-50 ring-1 ring-border/60 px-3 py-1 text-[11px]"
                      >
                        <span className="text-mauve uppercase tracking-[0.1em]">
                          {status}
                        </span>
                        <span className="text-ink font-medium tabular-nums">
                          {count}
                        </span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.section>

            {/* Skill analysis */}
            <motion.section
              variants={{
                hidden: { opacity: 0, y: 8 },
                show: { opacity: 1, y: 0 },
              }}
              className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8"
            >
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp size={16} className="text-plum" strokeWidth={1.9} />
                <h2 className="font-display text-2xl text-ink">
                  Skill analysis
                </h2>
              </div>
              <p className="text-[13px] text-mauve mb-6">
                Across your {skills.jobs_analyzed} analyzed job
                {skills.jobs_analyzed === 1 ? "" : "s"}
                {skills.resume_analyzed && (
                  <>
                    {" "}
                    · compared to{" "}
                    <span className="font-medium text-ink">
                      {skills.resume_analyzed.name}
                    </span>
                  </>
                )}
              </p>

              {skills.skills.length > 0 && (
                <div className="flex items-center gap-5 mb-5 text-[11px]">
                  <span className="inline-flex items-center gap-1.5 text-mauve">
                    <span className="h-2 w-2 rounded-full bg-plum" />
                    You have it
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-mauve">
                    <span className="h-2 w-2 rounded-full bg-blush" />
                    Skill gap
                  </span>
                </div>
              )}

              {skills.jobs_analyzed < 3 && skills.skills.length > 0 && (
                <p className="text-[12px] text-mauve/70 italic mb-5">
                  Save a few more jobs to see meaningful frequency patterns —
                  with only {skills.jobs_analyzed} job
                  {skills.jobs_analyzed === 1 ? "" : "s"}, every skill appears in
                  100% of them.
                </p>
              )}

              {skills.skills.length === 0 ? (
                <p className="text-[13px] text-mauve">
                  Save jobs to build a picture of what skills matter for your
                  search.
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
                  {skills.skills.slice(0, 16).map((s, i) => (
                    <motion.div
                      key={s.canonical}
                      initial={{ opacity: 0, x: -6 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: i * 0.03 }}
                      className="flex items-center gap-3"
                    >
                      <span className="w-28 text-[13px] text-ink font-medium truncate">
                        {s.canonical}
                      </span>
                      <div className="flex-1 h-1.5 rounded-full bg-blush-100/70 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${s.frequency_pct}%` }}
                          transition={{
                            duration: 0.6,
                            delay: 0.2 + i * 0.03,
                            ease: [0.22, 1, 0.36, 1],
                          }}
                          className={`h-full rounded-full ${
                            s.user_has ? "bg-plum" : "bg-blush"
                          }`}
                        />
                      </div>
                      <span className="w-12 text-right text-[11px] text-mauve tabular-nums shrink-0">
                        {s.frequency_pct.toFixed(0)}%
                      </span>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.section>
          </motion.div>
        )}
      </div>
    </div>
  );
}

function FunnelMetric({
  label,
  value,
  suffix,
  decimals = 0,
  accent = false,
}: {
  label: string;
  value: number;
  suffix?: string;
  decimals?: number;
  accent?: boolean;
}) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-[0.16em] text-mauve mb-2 font-medium">
        {label}
      </p>
      <p
        className={`font-display text-3xl leading-none tabular-nums ${
          accent && value > 0 ? "text-accent" : "text-ink"
        }`}
      >
        <AnimatedNumber value={value} suffix={suffix} decimals={decimals} />
      </p>
    </div>
  );
}