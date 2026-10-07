"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { FileText, Sparkles } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import type { Resume, ResumeDetail, ResumeSkill } from "@/lib/resumes-types";
import { ResumeCard } from "@/components/resume-card";
import { UploadResumeForm } from "@/components/upload-resume-form";
import { SkillChip } from "@/components/skill-chip";

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [activeResumeId, setActiveResumeId] = useState<string | null>(null);
  const [activeSkills, setActiveSkills] = useState<ResumeSkill[]>([]);
  const [skillsLoading, setSkillsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const res = await apiFetch<Resume[]>("/resumes");
        if (!cancelled) {
          setResumes(res);
          // Auto-select the primary resume, or the first one.
          const initial = res.find((r) => r.is_primary) ?? res[0];
          if (initial) setActiveResumeId(initial.id);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Could not load resumes (${err.status})`
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

  // Load skills whenever the active resume changes.
  useEffect(() => {
    if (!activeResumeId) {
      setActiveSkills([]);
      return;
    }
    let cancelled = false;
    setSkillsLoading(true);
    apiFetch<ResumeSkill[]>(`/resumes/${activeResumeId}/skills`)
      .then((res) => {
        if (!cancelled) setActiveSkills(res);
      })
      .catch(() => {
        if (!cancelled) setActiveSkills([]);
      })
      .finally(() => {
        if (!cancelled) setSkillsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [activeResumeId]);

  function handleUploaded(resume: ResumeDetail) {
    setResumes((cur) => [resume, ...cur]);
    setActiveResumeId(resume.id);
  }

  async function handleSetPrimary(id: string) {
    const prev = resumes;
    setResumes((cur) =>
      cur.map((r) => ({ ...r, is_primary: r.id === id }))
    );
    try {
      await apiFetch(`/resumes/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_primary: true }),
      });
    } catch {
      setResumes(prev);
    }
  }

  async function handleDelete(id: string) {
    const prev = resumes;
    setResumes((cur) => cur.filter((r) => r.id !== id));
    if (activeResumeId === id) setActiveResumeId(null);
    try {
      await apiFetch(`/resumes/${id}`, { method: "DELETE" });
    } catch {
      setResumes(prev);
    }
  }

  const activeResume = resumes.find((r) => r.id === activeResumeId) ?? null;

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-6xl mx-auto">
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 mb-2 text-mauve text-[13px]">
            <FileText size={14} strokeWidth={1.8} />
            Resumes
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            Your documents
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed mb-6">
            Keep multiple versions of your resume. Set a primary, and Hirearchy
            uses it to score job matches.
          </p>
          <UploadResumeForm onUploaded={handleUploaded} />
        </motion.header>

        {loading && (
          <div className="flex items-center gap-3 text-mauve text-sm py-8">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
            Loading resumes…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
            {error}
          </div>
        )}

        {!loading && !error && resumes.length === 0 && (
          <div className="rounded-2xl border border-dashed border-border py-16 text-center">
            <p className="font-display text-2xl text-ink mb-2">
              No resumes yet.
            </p>
            <p className="text-sm text-mauve max-w-md mx-auto">
              Upload a PDF resume above. The first one becomes your primary
              automatically.
            </p>
          </div>
        )}

        {!loading && !error && resumes.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-8 items-start">
            {/* Resume list */}
            <div className="space-y-3">
              <AnimatePresence>
                {resumes.map((r, i) => (
                  <ResumeCard
                    key={r.id}
                    resume={r}
                    index={i}
                    active={r.id === activeResumeId}
                    onSetPrimary={handleSetPrimary}
                    onDelete={handleDelete}
                    onClick={() => setActiveResumeId(r.id)}
                  />
                ))}
              </AnimatePresence>
            </div>

            {/* Skills panel */}
            <motion.aside
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
              className="sticky top-8 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6"
            >
              <div className="flex items-center gap-2 mb-4">
                <Sparkles size={15} className="text-plum" strokeWidth={1.9} />
                <h2 className="font-display text-xl text-ink">
                  Detected skills
                </h2>
              </div>

              {!activeResume ? (
                <p className="text-[13px] text-mauve leading-relaxed">
                  Select a resume to see the skills Hirearchy extracted from it.
                </p>
              ) : activeResume.extraction_status !== "success" ? (
                <p className="text-[13px] text-danger leading-relaxed">
                  We couldn&apos;t extract text from this resume. Try a different
                  PDF — scanned images don&apos;t work.
                </p>
              ) : skillsLoading ? (
                <div className="flex items-center gap-2 text-mauve text-[12px]">
                  <div className="h-3 w-3 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
                  Extracting…
                </div>
              ) : activeSkills.length === 0 ? (
                <p className="text-[13px] text-mauve leading-relaxed">
                  No skills detected. This usually means the resume text
                  doesn&apos;t contain standard tech keywords.
                </p>
              ) : (
                <>
                  <p className="text-[11px] text-mauve/70 mb-3">
                    {activeSkills.length} skill
                    {activeSkills.length === 1 ? "" : "s"} found in{" "}
                    <span className="font-medium text-mauve">
                      {activeResume.name}
                    </span>
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {activeSkills.map((s, i) => (
                      <SkillChip
                        key={s.canonical}
                        name={s.canonical}
                        variant="matched"
                        index={i}
                        title={s.context ?? undefined}
                      />
                    ))}
                  </div>
                </>
              )}
            </motion.aside>
          </div>
        )}
      </div>
    </div>
  );
}