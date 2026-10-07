"use client";

import { motion } from "motion/react";
import { Check, X, Minus } from "lucide-react";

type Variant = "matched" | "missing" | "preferred-missing" | "preferred-matched";

const CONFIG: Record<
  Variant,
  { bg: string; text: string; ring: string; icon: typeof Check }
> = {
  matched: {
    bg: "bg-accent/15",
    text: "text-plum",
    ring: "ring-accent/30",
    icon: Check,
  },
  missing: {
    bg: "bg-danger/10",
    text: "text-danger",
    ring: "ring-danger/20",
    icon: X,
  },
  "preferred-missing": {
    bg: "bg-blush-100/70",
    text: "text-mauve",
    ring: "ring-border",
    icon: Minus,
  },
  "preferred-matched": {
    bg: "bg-accent/10",
    text: "text-plum",
    ring: "ring-accent/20",
    icon: Check,
  },
};

export function SkillChip({
  name,
  variant,
  index = 0,
  title,
}: {
  name: string;
  variant: Variant;
  index?: number;
  title?: string;
}) {
  const cfg = CONFIG[variant];
  const Icon = cfg.icon;
  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        duration: 0.25,
        delay: index * 0.03,
        ease: [0.22, 1, 0.36, 1],
      }}
      title={title}
      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[14px] font-medium ring-1 ${cfg.bg} ${cfg.text} ${cfg.ring}`}
    >
      <Icon size={11} strokeWidth={2.4} />
      {name}
    </motion.span>
  );
}