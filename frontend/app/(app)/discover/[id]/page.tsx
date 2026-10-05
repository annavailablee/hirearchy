"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "motion/react";
import {
  ArrowLeft,
  Building2,
  MapPin,
  ExternalLink,
  Briefcase,
  Bookmark,
  BookmarkCheck,
} from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import type { JobDetail } from "@/lib/jobs-types";
import type { MatchResult, BestResumeResult } from "@/lib/match-types";
import { MatchScoreRing } from "@/components/match-score-ring";
import { BreakdownBar } from "@/components/breakdown-bar";
import { SkillChip } from "@/components/skill-chip";

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [job, setJob] = useState<JobDetail | null>(null);
  const [match, setMatch] = useState<MatchResult | null>(null);
  const [bestResume, setBestResume] = useState<BestResumeResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const id = params.id;
    if (!id) return;
    let cancelled = false;

    async function load() {
      try {
        const job = await apiFetch<JobDetail>(`/jobs/${id}`);
        if (cancelled) return;
        setJob(job);

        // Match and best-resume are best-effort: they 400 if no resume exists.
        const [m, b] = await Promise.all([
          apiFetch<MatchResult>(`/jobs/${id}/match`, { method: "POST" }).catch(
            () => null
          ),
          apiFetch<BestResumeResult>(`/jobs/${id}/best-resume`).catch(() => null),
        ]);
        if (cancelled) return;
        setMatch(m);
        setBestResume(b);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? err.status === 404
                ? "This job doesn't exist."
                : `Could not load job (${err.status})`
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
  }, [params.id]);

  async function handleSave() {
    if (!job || saved || saving) return;
    setSaving(true);
    try {
      await apiFetch(`/jobs/${job.id}/save`, { method: "POST" });
      setSaved(true);
    } catch {
      // Idempotent endpoint — a 409 here means already saved.
      setSaved(true);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="p-12 max-w-5xl mx-auto">
        <div className="flex items-center gap-3 text-mauve text-sm">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
          Loading job…
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="p-12 max-w-5xl mx-auto">
        <Link
          href="/discover"
          className="inline-flex items-center gap-1.5 text-sm text-mauve hover:text-plum mb-6"
        >
          <ArrowLeft size={14} /> Back to Discover
        </Link>
        <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
          {error ?? "Job not found."}
        </div>
      </div>
    );
  }

  const recommendedResume = bestResume?.resumes.find((r) => r.is_recommended);

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-5xl mx-auto">
        <Link
          href="/discover"
          className="inline-flex items-center gap-1.5 text-[13px] text-mauve hover:text-plum transition-colors mb-8"
        >
          <ArrowLeft size={14} strokeWidth={1.9} /> Back to Discover
        </Link>

        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
          className="mb-8"
        >
          <h1 className="font-display text-5xl leading-tight tracking-tight text-ink mb-3">
            {job.title}
          </h1>
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2 text-[13px] text-mauve">
            <span className="inline-flex items-center gap-1.5">
              <Building2 size={14} strokeWidth={1.8} />
              {job.company}
            </span>
            {job.location && (
              <span className="inline-flex items-center gap-1.5">
                <MapPin size={14} strokeWidth={1.8} />
                {job.location}
              </span>
            )}
            {job.employment_type && (
              <span className="inline-flex items-center gap-1.5">
                <Briefcase size={14} strokeWidth={1.8} />
                {job.employment_type}
              </span>
            )}
            {job.source_url && (
              <a
                href={job.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 hover:text-plum transition-colors"
              >
                <ExternalLink size={13} strokeWidth={1.8} />
                Original posting
              </a>
            )}
          </div>
        </motion.header>

        {/* Actions */}
        <div className="flex flex-wrap gap-3 mb-10">
          <button
            onClick={handleSave}
            disabled={saved || saving}
            className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              saved
                ? "bg-accent/15 text-plum ring-1 ring-accent/30"
                : "bg-plum text-blush-50 hover:bg-ink"
            } disabled:cursor-default`}
          >
            {saved ? (
              <BookmarkCheck size={15} strokeWidth={1.9} />
            ) : (
              <Bookmark size={15} strokeWidth={1.9} />
            )}
            {saved ? "Saved" : saving ? "Saving…" : "Save job"}
          </button>
        </div>

        {/* Match + breakdown + resume recommendation */}
        {match ? (
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="grid grid-cols-1 lg:grid-cols-[auto_1fr] gap-8 items-center rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8 mb-8"
          >
            <div className="flex justify-center">
              <MatchScoreRing score={match.score} />
            </div>
            <div className="space-y-4">
              <p className="font-display text-2xl text-ink leading-snug">
                {scoreLabel(match.score)}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                {match.breakdown.map((item, i) => (
                  <BreakdownBar key={item.name} item={item} index={i} />
                ))}
              </div>
            </div>
          </motion.section>
        ) : (
          <div className="rounded-xl border border-dashed border-border px-5 py-6 text-[13px] text-mauve mb-8">
            Upload a resume to see your compatibility score for this job.
          </div>
        )}

        {/* Recommended resume */}
        {recommendedResume && (
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-2xl bg-blush-50 ring-1 ring-border/40 px-6 py-5 mb-8"
          >
            <p className="text-[11px] uppercase tracking-[0.14em] text-mauve mb-1.5 font-medium">
              Recommended resume
            </p>
            <div className="flex flex-wrap items-baseline gap-3">
              <p className="font-display text-xl text-ink">
                {recommendedResume.name}
              </p>
              <span className="text-[12px] text-plum font-medium tabular-nums">
                {recommendedResume.score}% match
              </span>
            </div>
            {recommendedResume.matched_skills.length > 0 && (
              <p className="text-[12px] text-mauve mt-2">
                Matches on {recommendedResume.matched_skills.slice(0, 6).join(", ")}
                {recommendedResume.matched_skills.length > 6 && "…"}
              </p>
            )}
          </motion.section>
        )}

        {/* Skills */}
        {match && (
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8 mb-8"
          >
            <h2 className="font-display text-2xl text-ink mb-6">
              Why this matches you
            </h2>

            {match.matched_required_skills.length > 0 && (
              <SkillGroup
                label="Matched required"
                skills={match.matched_required_skills.map((s) => ({
                  name: s.canonical,
                  variant: "matched" as const,
                  title: s.context ?? undefined,
                }))}
              />
            )}

            {match.matched_preferred_skills.length > 0 && (
              <SkillGroup
                label="Matched preferred"
                skills={match.matched_preferred_skills.map((s) => ({
                  name: s.canonical,
                  variant: "preferred-matched" as const,
                  title: s.context ?? undefined,
                }))}
              />
            )}

            {match.missing_required_skills.length > 0 && (
              <SkillGroup
                label="Missing required"
                skills={match.missing_required_skills.map((name) => ({
                  name,
                  variant: "missing" as const,
                }))}
              />
            )}

            {match.missing_preferred_skills.length > 0 && (
              <SkillGroup
                label="Missing preferred"
                skills={match.missing_preferred_skills.map((name) => ({
                  name,
                  variant: "preferred-missing" as const,
                }))}
              />
            )}
          </motion.section>
        )}

        {/* Description */}
        {job.description && (
          <motion.section
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8"
          >
            <h2 className="font-display text-2xl text-ink mb-4">
              About the role
            </h2>
            <p className="text-[14px] text-ink/85 leading-relaxed whitespace-pre-wrap">
              {job.description}
            </p>
          </motion.section>
        )}
      </div>
    </div>
  );
}

function scoreLabel(score: number) {
  if (score >= 85) return "Excellent fit.";
  if (score >= 70) return "Strong match.";
  if (score >= 55) return "Worth considering.";
  if (score >= 40) return "Partial fit.";
  return "Low compatibility.";
}

function SkillGroup({
  label,
  skills,
}: {
  label: string;
  skills: { name: string; variant: "matched" | "missing" | "preferred-missing" | "preferred-matched"; title?: string }[];
}) {
  return (
    <div className="mb-6 last:mb-0">
      <p className="text-[11px] uppercase tracking-[0.14em] text-mauve mb-2.5 font-medium">
        {label} · {skills.length}
      </p>
      <div className="flex flex-wrap gap-2">
        {skills.map((s, i) => (
          <SkillChip
            key={s.name}
            name={s.name}
            variant={s.variant}
            index={i}
            title={s.title}
          />
        ))}
      </div>
    </div>
  );
}