"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "motion/react";
import { Search, Compass } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import type { Job } from "@/lib/jobs-types";
import { JobCard } from "@/components/job-card";
import { div } from "motion/react-m";

const REMOTE_FILTERS = [
  { value: "", label: "All" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
];

const EMPLOYMENT_FILTERS = [
  { value: "", label: "Any" },
  { value: "internship", label: "Internship" },
  { value: "full-time", label: "Full-time" },
];

export default function DiscoverPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [remote, setRemote] = useState("");
  const [employment, setEmployment] = useState("");

  // Debounced fetch whenever filters change.
  useEffect(() => {
    const ctrl = new AbortController();
    const handle = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (search) params.set("q", search);
        if (remote) params.set("remote_type", remote);
        if (employment) params.set("employment_type", employment);
        params.set("limit", "50");

        const res = await apiFetch<Job[]>(`/jobs?${params.toString()}`);
        setJobs(res);
      } catch (err) {
        if (err instanceof ApiError) setError(`Could not load jobs (${err.status})`);
        else setError("Could not reach the backend.");
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => {
      clearTimeout(handle);
      ctrl.abort();
    };
  }, [search, remote, employment]);

  const resultCount = useMemo(() => jobs.length, [jobs]);

  return (
    <div className="p-8 md:p-10 lg:p-12">
    <div className="max-w-6xl mx-auto"></div>
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="mb-8"
      >
        <div className="flex items-center gap-2 mb-2 text-mauve text-[13px]">
          <Compass size={14} strokeWidth={1.8} />
          Discover
        </div>
        <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
          Opportunities
        </h1>
        <p className="text-mauve max-w-xl leading-relaxed">
          Everything in your pipeline. Filter by what matters, then dive in.
        </p>
      </motion.header>

      {/* Search + filters */}
      <div className="mb-8 space-y-3">
        <div className="relative">
          <Search
            size={16}
            strokeWidth={1.9}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-mauve/60"
          />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or company…"
            className="w-full rounded-xl bg-white border border-border px-11 py-3 text-sm text-ink placeholder:text-mauve/50 outline-none transition-colors focus:border-plum focus:ring-2 focus:ring-plum/10"
          />
        </div>

        <div className="flex flex-wrap gap-x-6 gap-y-3">
          <FilterRow
            label="Location"
            options={REMOTE_FILTERS}
            value={remote}
            onChange={setRemote}
          />
          <FilterRow
            label="Type"
            options={EMPLOYMENT_FILTERS}
            value={employment}
            onChange={setEmployment}
          />
        </div>
      </div>

      {/* Result count */}
      {!loading && !error && (
        <p className="text-[12px] text-mauve/80 mb-4">
          {resultCount} {resultCount === 1 ? "opportunity" : "opportunities"}
        </p>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 text-mauve text-sm py-8">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
          Loading jobs…
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      )}

      {/* Empty */}
      {!loading && !error && jobs.length === 0 && (
        <div className="rounded-2xl border border-dashed border-border py-16 text-center">
          <p className="font-display text-2xl text-ink mb-2">
            No opportunities yet.
          </p>
          <p className="text-sm text-mauve max-w-md mx-auto">
            {search || remote || employment
              ? "Try removing a filter or searching for something else."
              : "Add a job via the API to get started."}
          </p>
        </div>
      )}

      {/* Grid */}
      {!loading && !error && jobs.length > 0 && (
            <div className="grid gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">          {jobs.map((job, i) => (
            <JobCard key={job.id} job={job} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}


function FilterRow({
  label,
  options,
  value,
  onChange,
}: {
  label: string;
  options: { value: string; label: string }[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] uppercase tracking-[0.16em] text-mauve/70 font-medium">
        {label}
      </span>
      <div className="flex gap-1">
        {options.map((opt) => {
          const active = value === opt.value;
          return (
            <button
              key={opt.value}
              onClick={() => onChange(opt.value)}
              className={`rounded-full px-3 py-1 text-[11px] font-medium transition-all ring-1 ${
                active
                  ? "bg-plum text-blush-50 ring-plum"
                  : "bg-white text-mauve ring-border/60 hover:text-plum hover:ring-border"
              }`}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}