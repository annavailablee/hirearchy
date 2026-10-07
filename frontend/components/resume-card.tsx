"use client";

import { motion } from "motion/react";
import { FileText, Star, Trash2, AlertCircle, CheckCircle2 } from "lucide-react";
import type { Resume } from "@/lib/resumes-types";

export function ResumeCard({
  resume,
  onSetPrimary,
  onDelete,
  onClick,
  active,
  index,
}: {
  resume: Resume;
  onSetPrimary: (id: string) => void;
  onDelete: (id: string) => void;
  onClick: () => void;
  active: boolean;
  index: number;
}) {
  const sizeKB = Math.round(resume.file_size / 1024);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.3,
        delay: index * 0.04,
        ease: [0.22, 1, 0.36, 1],
      }}
      onClick={onClick}
      className={`group cursor-pointer rounded-2xl bg-white ring-1 p-5 transition-all ${
        active
          ? "ring-plum ring-2 shadow-lift"
          : "ring-border/40 shadow-soft hover:ring-border/70 hover:shadow-lift"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="rounded-lg bg-blush-100 p-2 text-plum shrink-0">
            <FileText size={16} strokeWidth={1.9} />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <h3 className="font-display text-xl text-ink leading-tight truncate">
                {resume.name}
              </h3>
              {resume.is_primary && (
                <Star
                  size={12}
                  strokeWidth={2.2}
                  className="text-accent fill-accent shrink-0"
                  aria-label="Primary"
                />
              )}
            </div>
            <p className="text-[14px] text-mauve truncate mt-0.5">
              {resume.original_filename}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {!resume.is_primary && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSetPrimary(resume.id);
              }}
              className="rounded-md p-1.5 text-mauve/60 hover:text-accent hover:bg-blush-100 transition-colors opacity-0 group-hover:opacity-100"
              title="Set as primary"
              aria-label="Set as primary"
            >
              <Star size={13} strokeWidth={2} />
            </button>
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(resume.id);
            }}
            className="rounded-md p-1.5 text-mauve/60 hover:text-danger hover:bg-danger/5 transition-colors opacity-0 group-hover:opacity-100"
            title="Delete"
            aria-label="Delete"
          >
            <Trash2 size={13} strokeWidth={2} />
          </button>
        </div>
      </div>

      <div className="flex items-center justify-between text-[14px] mt-4 pt-3 border-t border-border/40">
        <span className="inline-flex items-center gap-1.5">
          {resume.extraction_status === "success" ? (
            <>
              <CheckCircle2 size={11} strokeWidth={2.2} className="text-accent" />
              <span className="text-mauve">Parsed</span>
            </>
          ) : resume.extraction_status === "failed" ? (
            <>
              <AlertCircle size={11} strokeWidth={2.2} className="text-danger" />
              <span className="text-danger">Extraction failed</span>
            </>
          ) : (
            <>
              <span className="h-2 w-2 rounded-full bg-mauve/40" />
              <span className="text-mauve">Pending</span>
            </>
          )}
        </span>
        <span className="text-mauve/70 tabular-nums">{sizeKB} KB</span>
      </div>
    </motion.div>
  );
}