"use client";

import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { CalendarClock } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import type { Deadline } from "@/lib/deadlines-types";
import { DeadlineRow } from "@/components/deadline-row";
import { NewDeadlineForm } from "@/components/new-deadline-form";

type Sections = {
  attention: Deadline[];
  thisWeek: Deadline[];
  later: Deadline[];
};

export default function DeadlinesPage() {
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const res = await apiFetch<Deadline[]>("/deadlines");
      setDeadlines(res);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `Could not load deadlines (${err.status})`
          : "Could not reach the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const sections = useMemo<Sections>(() => {
    const now = Date.now();
    const weekFromNow = now + 7 * 86400000;
    const attention: Deadline[] = [];
    const thisWeek: Deadline[] = [];
    const later: Deadline[] = [];

    for (const d of deadlines) {
      if (d.completed_at) continue;
      const due = new Date(d.due_at).getTime();
      if (d.priority === "OVERDUE" || d.priority === "URGENT") {
        attention.push(d);
      } else if (due <= weekFromNow) {
        thisWeek.push(d);
      } else {
        later.push(d);
      }
    }

    // Sort each by due_at ascending
    const byDue = (a: Deadline, b: Deadline) =>
      new Date(a.due_at).getTime() - new Date(b.due_at).getTime();
    attention.sort(byDue);
    thisWeek.sort(byDue);
    later.sort(byDue);

    return { attention, thisWeek, later };
  }, [deadlines]);

  async function handleComplete(id: string) {
    const prev = deadlines;
    setDeadlines((cur) => cur.filter((d) => d.id !== id));
    try {
      await apiFetch(`/deadlines/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ completed: true }),
      });
    } catch {
      setDeadlines(prev);
    }
  }

  async function handleCreate(payload: {
    title: string;
    kind: string;
    due_at: string;
    notes: string | null;
  }) {
    const created = await apiFetch<Deadline>("/deadlines", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setDeadlines((cur) => [...cur, created]);
  }

  const totalActive =
    sections.attention.length + sections.thisWeek.length + sections.later.length;

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-4xl mx-auto">
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="mb-8"
        >
          <div className="flex items-center gap-2 mb-2 text-mauve text-[13px]">
            <CalendarClock size={14} strokeWidth={1.8} />
            Deadlines
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            What&apos;s next
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed mb-6">
            {totalActive === 0
              ? "Nothing on the calendar. Add a deadline below to keep track."
              : `${totalActive} active deadline${totalActive === 1 ? "" : "s"}. Overdue and urgent items sort to the top.`}
          </p>
          <NewDeadlineForm onCreate={handleCreate} />
        </motion.header>

        {loading && (
          <div className="flex items-center gap-3 text-mauve text-sm py-8">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
            Loading deadlines…
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
            {error}
          </div>
        )}

        {!loading && !error && totalActive === 0 && (
          <div className="rounded-2xl border border-dashed border-border py-16 text-center">
            <p className="font-display text-2xl text-ink mb-2">
              All clear.
            </p>
            <p className="text-sm text-mauve max-w-md mx-auto">
              No active deadlines. New ones you add will show up here, sorted by
              urgency.
            </p>
          </div>
        )}

        <AnimatePresence>
          {sections.attention.length > 0 && (
            <Section
              key="attention"
              label="Attention required"
              tone="danger"
              count={sections.attention.length}
            >
              {sections.attention.map((d, i) => (
                <DeadlineRow
                  key={d.id}
                  deadline={d}
                  onComplete={handleComplete}
                  index={i}
                />
              ))}
            </Section>
          )}

          {sections.thisWeek.length > 0 && (
            <Section
              key="this-week"
              label="This week"
              count={sections.thisWeek.length}
            >
              {sections.thisWeek.map((d, i) => (
                <DeadlineRow
                  key={d.id}
                  deadline={d}
                  onComplete={handleComplete}
                  index={i}
                />
              ))}
            </Section>
          )}

          {sections.later.length > 0 && (
            <Section key="later" label="Later" count={sections.later.length}>
              {sections.later.map((d, i) => (
                <DeadlineRow
                  key={d.id}
                  deadline={d}
                  onComplete={handleComplete}
                  index={i}
                />
              ))}
            </Section>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function Section({
  label,
  count,
  tone,
  children,
}: {
  label: string;
  count: number;
  tone?: "danger";
  children: React.ReactNode;
}) {
  return (
    <motion.section
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className="mb-10 last:mb-0"
    >
      <div className="flex items-baseline gap-2.5 mb-3 pb-2 border-b border-border/50">
        <h2
          className={`font-display text-2xl ${
            tone === "danger" ? "text-danger" : "text-ink"
          }`}
        >
          {label}
        </h2>
        <span className="text-[12px] text-mauve/70 tabular-nums">{count}</span>
      </div>
      <div>{children}</div>
    </motion.section>
  );
}