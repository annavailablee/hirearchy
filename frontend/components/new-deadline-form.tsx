"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Plus, X } from "lucide-react";
import { KIND_OPTIONS } from "@/lib/deadlines-types";

export function NewDeadlineForm({
  onCreate,
}: {
  onCreate: (payload: {
    title: string;
    kind: string;
    due_at: string;
    notes: string | null;
  }) => Promise<void>;
}) {
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [kind, setKind] = useState<string>("custom");
  const [dueAt, setDueAt] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!title || !dueAt) return;
    setSubmitting(true);
    try {
      // datetime-local gives "YYYY-MM-DDTHH:mm" — treat as local time → ISO UTC
      const iso = new Date(dueAt).toISOString();
      await onCreate({
        title,
        kind,
        due_at: iso,
        notes: notes || null,
      });
      setTitle("");
      setKind("custom");
      setDueAt("");
      setNotes("");
      setOpen(false);
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
        <Plus size={15} strokeWidth={2.2} />
        New deadline
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
              className="mt-5 rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-6 grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <div className="md:col-span-2 flex items-center justify-between mb-1">
                <h3 className="font-display text-xl text-ink">New deadline</h3>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-md p-1 text-mauve hover:text-plum hover:bg-blush-100 transition-colors"
                  aria-label="Close"
                >
                  <X size={14} strokeWidth={2} />
                </button>
              </div>

              <Field label="Title" className="md:col-span-2">
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  maxLength={255}
                  placeholder="e.g. Google OA"
                  className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink placeholder:text-mauve/50 outline-none focus:border-plum focus:ring-2 focus:ring-plum/10"
                />
              </Field>

              <Field label="Type">
                <select
                  value={kind}
                  onChange={(e) => setKind(e.target.value)}
                  className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink outline-none focus:border-plum focus:ring-2 focus:ring-plum/10"
                >
                  {KIND_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="Due">
                <input
                  type="datetime-local"
                  value={dueAt}
                  onChange={(e) => setDueAt(e.target.value)}
                  required
                  className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink outline-none focus:border-plum focus:ring-2 focus:ring-plum/10"
                />
              </Field>

              <Field label="Notes (optional)" className="md:col-span-2">
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                  placeholder="Any context you want to remember"
                  className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink placeholder:text-mauve/50 outline-none focus:border-plum focus:ring-2 focus:ring-plum/10 resize-none"
                />
              </Field>

              <div className="md:col-span-2 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-mauve hover:text-plum transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || !title || !dueAt}
                  className="rounded-lg bg-plum text-blush-50 px-4 py-2 text-sm font-medium hover:bg-ink disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {submitting ? "Creating…" : "Create deadline"}
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function Field({
  label,
  children,
  className,
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <label className={`block ${className ?? ""}`}>
      <span className="block text-[11px] uppercase tracking-[0.14em] text-mauve mb-1.5 font-medium">
        {label}
      </span>
      {children}
    </label>
  );
}