"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Building2, MapPin, Clock, ArrowUpRight } from "lucide-react";
import type { Job } from "@/lib/jobs-types";

const REMOTE_LABEL: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  onsite: "On-site",
  any: "Flexible",
};

const EMPLOYMENT_LABEL: Record<string, string> = {
  internship: "Internship",
  "full-time": "Full-time",
  "part-time": "Part-time",
  contract: "Contract",
};

export function JobCard({ job, index = 0 }: { job: Job; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.35,
        delay: index * 0.04,
        ease: [0.22, 1, 0.36, 1],
      }}
      whileHover={{ y: -2 }}
    >
      <Link
        href={`/discover/${job.id}`}
        className="group block h-full rounded-2xl bg-white ring-1 ring-border/40 shadow-soft hover:shadow-lift hover:ring-border/70 transition-all p-6"
      >
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0">
            <h3 className="font-display text-xl text-ink leading-tight truncate">
              {job.title}
            </h3>
            <div className="flex items-center gap-1.5 mt-1 text-[15px] text-mauve">
              <Building2 size={12} strokeWidth={1.8} />
              <span className="truncate">{job.company}</span>
            </div>
          </div>
          <ArrowUpRight
            size={16}
            strokeWidth={2}
            className="text-mauve/50 group-hover:text-plum transition-colors shrink-0 mt-1"
          />
        </div>

        <div className="flex flex-wrap gap-1.5 mb-4">
          {job.location && (
            <Pill icon={<MapPin size={10} strokeWidth={2} />}>
              {job.location}
            </Pill>
          )}
          {job.remote_type && (
            <Pill accent>
              {REMOTE_LABEL[job.remote_type] ?? job.remote_type}
            </Pill>
          )}
          {job.employment_type && (
            <Pill>
              {EMPLOYMENT_LABEL[job.employment_type] ?? job.employment_type}
            </Pill>
          )}
        </div>

        <div className="flex items-center gap-1.5 text-[14px] text-mauve/70 pt-3 border-t border-border/40">
          <Clock size={11} strokeWidth={1.8} />
          <span>
            Added{" "}
            {new Date(job.created_at).toLocaleDateString(undefined, {
              month: "short",
              day: "numeric",
            })}
          </span>
        </div>
      </Link>
    </motion.div>
  );
}

function Pill({
  children,
  accent,
  icon,
}: {
  children: React.ReactNode;
  accent?: boolean;
  icon?: React.ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[14px] font-medium ring-1 ${
        accent
          ? "bg-blush-100 text-plum ring-border"
          : "bg-blush-50 text-mauve ring-border/50"
      }`}
    >
      {icon}
      {children}
    </span>
  );
}