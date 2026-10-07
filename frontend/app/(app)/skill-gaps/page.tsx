"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { TrendingUp, Check, X } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import type { SkillInsights } from "@/lib/insights-types";

export default function SkillGapsPage() {
  const [data, setData] = useState<SkillInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    apiFetch<SkillInsights>("/insights/skills")
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Could not load skill gaps (${err.status})`
              : "Could not reach the backend."
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const strengths = data?.skills.filter((s) => s.user_has) ?? [];
  const gaps = data?.skills.filter((s) => !s.user_has && s.frequency_pct >= 20) ?? [];

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
            <TrendingUp size={14} strokeWidth={1.8} />
            Skill Gaps
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            What to learn next
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed">
            Skills that appear in your target jobs but aren&apos;t on your
            resume yet.
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

        {!loading && !error && data && data.jobs_analyzed === 0 && (
          <div className="rounded-2xl border border-dashed border-border py-16 text-center">
            <p className="font-display text-2xl text-ink mb-2">
              Not enough data yet.
            </p>
            <p className="text-sm text-mauve max-w-md mx-auto">
              Save at least a few jobs from Discover and Hirearchy will
              identify the gaps.
            </p>
          </div>
        )}

        {!loading && !error && data && data.jobs_analyzed > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gaps */}
            <motion.section
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8"
            >
              <div className="flex items-baseline gap-2 mb-6">
                <h2 className="font-display text-2xl text-ink">Gaps</h2>
                <span className="text-[12px] text-mauve/70 tabular-nums">
                  {gaps.length}
                </span>
              </div>
              {gaps.length === 0 ? (
                <p className="text-[13px] text-mauve leading-relaxed">
                  No significant gaps. Your resume covers the recurring
                  requirements in your target set.
                </p>
              ) : (
                <div className="space-y-3">
                  {gaps.map((s, i) => (
                    <motion.div
                      key={s.canonical}
                      initial={{ opacity: 0, x: -6 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: i * 0.05 }}
                      className="flex items-center justify-between gap-4 py-2 border-b border-border/40 last:border-0"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="rounded-md bg-danger/10 p-1 text-danger shrink-0">
                          <X size={12} strokeWidth={2.4} />
                        </div>
                        <div className="min-w-0">
                          <p className="text-[14px] font-medium text-ink truncate">
                            {s.canonical}
                          </p>
                          <p className="text-[11px] text-mauve/70 capitalize">
                            {s.category}
                          </p>
                        </div>
                      </div>
                      <span className="text-[12px] text-mauve tabular-nums shrink-0">
                        {s.frequency_pct.toFixed(0)}%
                      </span>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.section>

            {/* Strengths */}
            <motion.section
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.4,
                delay: 0.1,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8"
            >
              <div className="flex items-baseline gap-2 mb-6">
                <h2 className="font-display text-2xl text-ink">Strengths</h2>
                <span className="text-[12px] text-mauve/70 tabular-nums">
                  {strengths.length}
                </span>
              </div>
              {strengths.length === 0 ? (
                <p className="text-[13px] text-mauve leading-relaxed">
                  Upload a resume so we can identify your strengths.
                </p>
              ) : (
                <div className="space-y-3">
                  {strengths.map((s, i) => (
                    <motion.div
                      key={s.canonical}
                      initial={{ opacity: 0, x: -6 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: i * 0.05 }}
                      className="flex items-center justify-between gap-4 py-2 border-b border-border/40 last:border-0"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <div className="rounded-md bg-accent/15 p-1 text-plum shrink-0">
                          <Check size={12} strokeWidth={2.4} />
                        </div>
                        <div className="min-w-0">
                          <p className="text-[14px] font-medium text-ink truncate">
                            {s.canonical}
                          </p>
                          <p className="text-[11px] text-mauve/70 capitalize">
                            {s.category}
                          </p>
                        </div>
                      </div>
                      <span className="text-[12px] text-mauve tabular-nums shrink-0">
                        {s.frequency_pct.toFixed(0)}%
                      </span>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.section>
          </div>
        )}
      </div>
    </div>
  );
}