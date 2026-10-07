"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "motion/react";
import { Briefcase } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import {
  STATUS_COLUMNS,
  type Application,
  type StatusKey,
} from "@/lib/applications-types";
import type { Job } from "@/lib/jobs-types";
import { ApplicationCard } from "@/components/application-card";

const TERMINAL_STATUSES = ["REJECTED", "WITHDRAWN", "EXPIRED"] as const;
type AppWithJob = Application & { job_title: string; company: string };

export default function ApplicationsPage() {
  const [apps, setApps] = useState<AppWithJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [applications, jobs] = await Promise.all([
          apiFetch<Application[]>("/applications?limit=200"),
          apiFetch<Job[]>("/jobs?limit=100"),
        ]);
        const jobMap = new Map(jobs.map((j) => [j.id, j]));
        const enriched: AppWithJob[] = applications.map((a) => {
          const job = jobMap.get(a.job_id);
          return {
            ...a,
            job_title: job?.title ?? "Unknown role",
            company: job?.company ?? "Unknown company",
          };
        });
        if (!cancelled) setApps(enriched);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Could not load applications (${err.status})`
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

const grouped = useMemo(() => {
  const map: Record<string, AppWithJob[]> = {};
  for (const col of STATUS_COLUMNS) map[col.key] = [];
  for (const app of apps) {
    if (map[app.current_status]) map[app.current_status].push(app);
  }
  return map;
}, [apps]);

const closedApps = useMemo(
  () => apps.filter((a) => (TERMINAL_STATUSES as readonly string[]).includes(a.current_status)),
  [apps]
);

const activeCount = useMemo(
  () => apps.filter((a) => !(TERMINAL_STATUSES as readonly string[]).includes(a.current_status)).length,
  [apps]
);

  async function handleTransition(id: string, toStatus: string) {
    // Optimistic update
    const prev = apps;
    setApps((cur) =>
      cur.map((a) => (a.id === id ? { ...a, current_status: toStatus } : a))
    );
    try {
      await apiFetch(`/applications/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ to_status: toStatus }),
      });
    } catch {
      // Revert on failure
      setApps(prev);
    }
  }

  async function handleDelete(id: string) {
    const prev = apps;
    setApps((cur) => cur.filter((a) => a.id !== id));
    try {
      await apiFetch(`/applications/${id}`, { method: "DELETE" });
    } catch {
      setApps(prev);
    }
  }

  const total = apps.length;

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-[1400px] mx-auto">
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 mb-2 text-mauve text-[15px]">
            <Briefcase size={14} strokeWidth={1.8} />
            Applications
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            Your pipeline
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed">
            {total === 0
              ? "Save jobs from Discover to start tracking them here."
              : `${activeCount} active · ${closedApps.length} closed`}
          </p>
        </motion.header>

        {loading && (
          <div className="flex items-center gap-3 text-mauve text-sm py-8">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
            Loading applications…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
            {error}
          </div>
        )}

        {!loading && !error && total === 0 && (
          <div className="rounded-2xl border border-dashed border-border py-16 text-center">
            <p className="font-display text-2xl text-ink mb-2">
              No applications yet.
            </p>
            <p className="text-sm text-mauve max-w-md mx-auto">
              Save a job from the Discover page to add it here.
            </p>
          </div>
        )}

        {!loading && !error && total > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {STATUS_COLUMNS.map((col) => (
              <motion.div
                key={col.key}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                className="flex flex-col"
              >
                <div className="flex items-baseline justify-between mb-3 px-1">
                  <h2 className="text-[14px] uppercase tracking-[0.14em] text-mauve font-medium">
                    {col.label}
                  </h2>
                  <span className="text-[14px] text-mauve/60 tabular-nums">
                    {grouped[col.key].length}
                  </span>
                </div>
                <div className="flex flex-col gap-2.5 min-h-[120px]">
                  {grouped[col.key].map((app, i) => (
                    <ApplicationCard
                      key={app.id}
                      app={app}
                      onTransition={handleTransition}
                      onDelete={handleDelete}
                      index={i}
                    />
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        )}
        {/* ---- Closed section ---- */}
        {!loading && !error && closedApps.length > 0 && (
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="mt-10 pt-8 border-t border-border/50"
          >
            <details className="group">
              <summary className="cursor-pointer list-none flex items-center gap-2 select-none">
                <span className="text-[14px] uppercase tracking-[0.14em] text-mauve font-medium">
                  Closed
                </span>
                <span className="text-[14px] text-mauve/60 tabular-nums">
                  {closedApps.length}
                </span>
                <span className="text-[14px] text-mauve/50 ml-1 group-open:hidden">
                  (click to expand)
                </span>
              </summary>
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
                {closedApps.map((app, i) => (
                  <ApplicationCard
                    key={app.id}
                    app={app}
                    onTransition={handleTransition}
                    onDelete={handleDelete}
                    index={i}
                  />
                ))}
              </div>
            </details>
          </motion.section>
        )}
      </div>
    </div>
  );
}
