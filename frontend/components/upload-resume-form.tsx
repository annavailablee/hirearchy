"use client";

import { useRef, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Upload, X, FileText } from "lucide-react";
import { apiUpload, ApiError } from "@/lib/api";
import type { ResumeDetail } from "@/lib/resumes-types";

export function UploadResumeForm({
  onUploaded,
}: {
  onUploaded: (resume: ResumeDetail) => void;
}) {
  const [open, setOpen] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!file || !name) return;
    setSubmitting(true);
    setError(null);

    const fd = new FormData();
    fd.append("file", file);
    fd.append("name", name);

    try {
      const resume = await apiUpload<ResumeDetail>("/resumes", fd);
      onUploaded(resume);
      setFile(null);
      setName("");
      setOpen(false);
      if (inputRef.current) inputRef.current.value = "";
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          typeof err.detail === "string"
            ? err.detail
            : "Upload failed. Check the file type and size."
        );
      } else {
        setError("Network error. Is the backend running?");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen((o) => !o)}
        className="inline-flex items-center gap-2 rounded-lg bg-plum text-blush-50 px-4 py-2 text-sm font-medium hover:bg-ink transition-colors"
      >
        <Upload size={15} strokeWidth={2.2} />
        Upload resume
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <form
              onSubmit={submit}
              className="mt-5 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-display text-xl text-ink">
                  Upload a resume
                </h3>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-md p-1 text-mauve hover:text-plum hover:bg-blush-100 transition-colors"
                  aria-label="Close"
                >
                  <X size={14} strokeWidth={2} />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="block md:col-span-2">
                  <span className="block text-[11px] uppercase tracking-[0.14em] text-mauve mb-1.5 font-medium">
                    Resume name
                  </span>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    maxLength={120}
                    placeholder="e.g. General SWE, Backend, AI/ML"
                    className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink placeholder:text-mauve/50 outline-none focus:border-plum focus:ring-2 focus:ring-plum/10"
                  />
                </label>

                <label className="block md:col-span-2">
                  <span className="block text-[11px] uppercase tracking-[0.14em] text-mauve mb-1.5 font-medium">
                    PDF file (max 5 MB)
                  </span>
                  <div
                    onClick={() => inputRef.current?.click()}
                    className="cursor-pointer rounded-lg border border-dashed border-border bg-blush-50/50 hover:bg-blush-50 px-4 py-6 text-center transition-colors"
                  >
                    {file ? (
                      <div className="flex items-center justify-center gap-2 text-ink">
                        <FileText size={15} strokeWidth={1.9} />
                        <span className="text-sm font-medium">{file.name}</span>
                        <span className="text-[11px] text-mauve">
                          ({(file.size / 1024).toFixed(0)} KB)
                        </span>
                      </div>
                    ) : (
                      <p className="text-sm text-mauve">
                        Click to choose a PDF file
                      </p>
                    )}
                  </div>
                  <input
                    ref={inputRef}
                    type="file"
                    accept="application/pdf"
                    onChange={(e) => {
                      const f = e.target.files?.[0] ?? null;
                      setFile(f);
                    }}
                    className="hidden"
                  />
                </label>
              </div>

              {error && (
                <div className="mt-4 text-[13px] text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
                  {error}
                </div>
              )}

              <div className="mt-5 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-mauve hover:text-plum transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !file || !name}
                  className="rounded-lg bg-plum text-blush-50 px-4 py-2 text-sm font-medium hover:bg-ink disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {submitting ? "Uploading…" : "Upload"}
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}