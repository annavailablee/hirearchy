"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { MoreHorizontal, Briefcase, ArrowRight, Trash2 } from "lucide-react";
import { NEXT_STATUSES } from "@/lib/applications-types";

type CardApp = {
  id: string;
  job_id: string;
  current_status: string;
  created_at: string;
  updated_at: string;
  job_title: string;
  company: string;
};

export function ApplicationCard({
  app,
  onTransition,
  onDelete,
  index,
}: {
  app: CardApp;
  onTransition: (id: string, toStatus: string) => void;
  onDelete: (id: string) => void;
  index: number;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const nexts = NEXT_STATUSES[app.current_status] ?? [];

  const days = Math.floor(
    (Date.now() - new Date(app.updated_at).getTime()) / 86400000
  );

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{
        duration: 0.3,
        delay: index * 0.03,
        ease: [0.22, 1, 0.36, 1],
      }}
      className="relative rounded-xl bg-white ring-1 ring-border/40 shadow-soft p-4 hover:ring-border/70 transition-colors"
    >
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="min-w-0">
          <p className="text-[13px] font-medium text-ink truncate leading-tight">
            {app.job_title}
          </p>
          <p className="text-[11px] text-mauve truncate mt-0.5">
            {app.company}
          </p>
        </div>
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="rounded-md p-1 -mr-1 text-mauve hover:bg-blush-100 hover:text-plum transition-colors shrink-0"
          aria-label="Actions"
        >
          <MoreHorizontal size={14} strokeWidth={1.9} />
        </button>
      </div>

      <div className="flex items-center gap-1.5 text-[10px] text-mauve/70 tabular-nums">
        <Briefcase size={10} strokeWidth={2} />
        {days === 0 ? "Today" : `${days}d in stage`}
      </div>

      <AnimatePresence>
        {menuOpen && (
          <>
            {/* click-away backdrop */}
            <button
              className="fixed inset-0 z-10 cursor-default"
              onClick={() => setMenuOpen(false)}
              aria-hidden
            />
            <motion.div
              initial={{ opacity: 0, y: -4, scale: 0.96 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -4, scale: 0.96 }}
              transition={{ duration: 0.15 }}
              className="absolute right-2 top-10 z-20 w-40 rounded-lg bg-white ring-1 ring-border shadow-lift overflow-hidden"
            >
              {nexts.length === 0 && (
                <p className="px-3 py-2.5 text-[11px] text-mauve">
                  Terminal state
                </p>
              )}
              {nexts.map((s) => (
                <button
                  key={s}
                  onClick={() => {
                    onTransition(app.id, s);
                    setMenuOpen(false);
                  }}
                  className="flex w-full items-center gap-2 px-3 py-2 text-[12px] text-ink hover:bg-blush-50 transition-colors"
                >
                  <ArrowRight size={11} strokeWidth={2.2} className="text-mauve" />
                  Move to {s.toLowerCase()}
                </button>
              ))}
              <button
                onClick={() => {
                  onDelete(app.id);
                  setMenuOpen(false);
                }}
                className="flex w-full items-center gap-2 px-3 py-2 text-[12px] text-danger hover:bg-danger/5 transition-colors border-t border-border/40"
              >
                <Trash2 size={11} strokeWidth={2.2} />
                Delete
              </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </motion.div>
  );
}