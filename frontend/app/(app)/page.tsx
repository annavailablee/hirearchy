"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { ArrowUpRight, AlertTriangle, Sparkles } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { apiFetch, ApiError } from "@/lib/api";
import type { DashboardResponse } from "@/lib/dashboard-types";
import { AnimatedNumber } from "@/components/count-up";
import { AttentionCard } from "@/components/attention-card";
import { UpcomingRow } from "@/components/upcoming-item";
import { TopSkillBar } from "@/components/top-skill-bar";

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const res = await apiFetch<DashboardResponse>("/dashboard");
        if (!cancelled) setData(res);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Could not load dashboard (${err.status})`
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

  const firstName = user?.full_name?.split(" ")[0] ?? "there";

  return (
    <div className="p-8 md:p-12 max-w-[1100px] mx-auto">
      {/* ---- Hero ---- */}
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="mb-10"
      >
        <p className="text-[13px] text-mauve mb-2 tracking-wide">
          {greeting()},
        </p>
        <h1 className="font-display text-5xl leading-none tracking-tight text-ink">
          {firstName}.
        </h1>
        {data && (
          <p className="mt-4 text-mauve max-w-xl leading-relaxed">
            {data.applications.total > 0
              ? `You have ${data.applications.total} application${data.applications.total === 1 ? "" : "s"} tracked and ${data.upcoming.length} upcoming deadline${data.upcoming.length === 1 ? "" : "s"}.`
              : "Start by discovering roles and saving the ones worth your time."}
          </p>
        )}
      </motion.header>

      {/* ---- Loading ---- */}
      {loading && (
        <div className="flex items-center gap-3 text-mauve text-sm">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
          Loading your dashboard…
        </div>
      )}

      {/* ---- Error ---- */}
      {error && (
        <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {/* ---- Content ---- */}
      {data && (
        <motion.div
          initial="hidden"
          animate="show"
          variants={{
            hidden: {},
            show: { transition: { staggerChildren: 0.06 } },
          }}
          className="space-y-8"
        >
          {/* Metrics row */}
          <motion.section
            variants={{
              hidden: { opacity: 0, y: 8 },
              show: { opacity: 1, y: 0 },
            }}
          >
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                label="Tracked"
                value={data.applications.total}
              />
              <MetricCard
                label="Response rate"
                value={data.applications.response_rate_pct}
                suffix="%"
                decimals={1}
              />
              <MetricCard
                label="Interviews"
                value={
                  (data.applications.by_status.INTERVIEW ?? 0) +
                  (data.applications.by_status.OFFER ?? 0)
                }
              />
              <MetricCard
                label="Offers"
                value={data.applications.by_status.OFFER ?? 0}
                accent
              />
            </div>
          </motion.section>

          {/* Two-column: Attention | Skills */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Attention Required */}
            <motion.section
              variants={{
                hidden: { opacity: 0, y: 8 },
                show: { opacity: 1, y: 0 },
              }}
              className="lg:col-span-3 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6"
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <AlertTriangle size={15} className="text-plum" strokeWidth={1.9} />
                  <h2 className="font-display text-xl text-ink">
                    Attention required
                  </h2>
                </div>
                {data.attention.overdue_count > 0 && (
                  <span className="text-[11px] uppercase tracking-[0.12em] text-danger font-medium">
                    {data.attention.overdue_count} overdue
                  </span>
                )}
              </div>
              {data.attention.top_items.length === 0 ? (
                <EmptyNote>
                  Nothing overdue or urgent. Nice.
                </EmptyNote>
              ) : (
                <div>
                  {data.attention.top_items.map((item) => (
                    <AttentionCard key={item.id} item={item} />
                  ))}
                </div>
              )}
            </motion.section>

            {/* Top Skills */}
            <motion.section
              variants={{
                hidden: { opacity: 0, y: 8 },
                show: { opacity: 1, y: 0 },
              }}
              className="lg:col-span-2 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6"
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={15} className="text-plum" strokeWidth={1.9} />
                <h2 className="font-display text-xl text-ink">
                  Top requested skills
                </h2>
              </div>
              {data.top_skills.length === 0 ? (
                <EmptyNote>
                  Save jobs to see which skills dominate your target set.
                </EmptyNote>
              ) : (
                <div>
                  {data.top_skills.map((s, i) => (
                    <TopSkillBar key={s.canonical} skill={s} index={i} />
                  ))}
                </div>
              )}
            </motion.section>
          </div>

          {/* Two-column: Upcoming | Gaps */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
            {/* Upcoming */}
            <motion.section
              variants={{
                hidden: { opacity: 0, y: 8 },
                show: { opacity: 1, y: 0 },
              }}
              className="lg:col-span-3 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6"
            >
              <h2 className="font-display text-xl text-ink mb-3">
                Upcoming
              </h2>
              {data.upcoming.length === 0 ? (
                <EmptyNote>No deadlines in the near future.</EmptyNote>
              ) : (
                <div>
                  {data.upcoming.map((item) => (
                    <UpcomingRow key={item.deadline_id} item={item} />
                  ))}
                </div>
              )}
            </motion.section>

            {/* Gaps */}
            <motion.section
              variants={{
                hidden: { opacity: 0, y: 8 },
                show: { opacity: 1, y: 0 },
              }}
              className="lg:col-span-2 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6"
            >
              <h2 className="font-display text-xl text-ink mb-3">
                Skill gaps
              </h2>
              {data.gaps.length === 0 ? (
                <EmptyNote>
                  No significant gaps in your current target set.
                </EmptyNote>
              ) : (
                <>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {data.gaps.slice(0, 10).map((g) => (
                      <span
                        key={g}
                        className="inline-flex items-center rounded-full bg-blush-100 text-plum px-3 py-1 text-[12px] font-medium ring-1 ring-border"
                      >
                        {g}
                      </span>
                    ))}
                  </div>
                  <a
                    href="/skill-gaps"
                    className="inline-flex items-center gap-1 text-[12px] font-medium text-plum hover:text-ink transition-colors"
                  >
                    View full analysis
                    <ArrowUpRight size={12} strokeWidth={2.2} />
                  </a>
                </>
              )}
            </motion.section>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function MetricCard({
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
    <div className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft px-5 py-4">
      <p className="text-[10px] uppercase tracking-[0.16em] text-mauve mb-2.5 font-medium">
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

function EmptyNote({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-[13px] text-mauve/80 py-3 leading-relaxed">
      {children}
    </p>
  );
}