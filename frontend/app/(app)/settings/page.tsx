"use client";

import { motion } from "motion/react";
import { Settings as SettingsIcon, Mail, User as UserIcon, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-3xl mx-auto">
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="mb-10"
        >
          <div className="flex items-center gap-2 mb-2 text-mauve text-[13px]">
            <SettingsIcon size={14} strokeWidth={1.8} />
            Settings
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            Account
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed">
            Manage your Hirearchy account.
          </p>
        </motion.header>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="space-y-6"
        >
          <div className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8">
            <h2 className="font-display text-xl text-ink mb-6">Profile</h2>
            <div className="space-y-4">
              <Row icon={<UserIcon size={14} strokeWidth={1.9} />} label="Name">
                <span className="text-[14px] text-ink">
                  {user?.full_name ?? "—"}
                </span>
              </Row>
              <Row icon={<Mail size={14} strokeWidth={1.9} />} label="Email">
                <span className="text-[14px] text-ink">{user?.email}</span>
              </Row>
            </div>
            <p className="text-[12px] text-mauve/70 mt-6 leading-relaxed">
              Need to change your email or password? Contact support — self-service
              account editing is coming soon.
            </p>
          </div>

          <div className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8">
            <h2 className="font-display text-xl text-ink mb-2">Session</h2>
            <p className="text-[13px] text-mauve mb-5 leading-relaxed">
              Sign out of your Hirearchy account on this device.
            </p>
            <button
              onClick={logout}
              className="inline-flex items-center gap-2 rounded-lg border border-danger/30 text-danger px-4 py-2 text-sm font-medium hover:bg-danger/5 transition-colors"
            >
              <LogOut size={14} strokeWidth={2} />
              Sign out
            </button>
          </div>

          <div className="rounded-2xl border border-dashed border-border p-8 text-center">
            <p className="text-[13px] text-mauve leading-relaxed">
              Notification preferences, appearance, and privacy settings are
              coming in a future release.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function Row({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-border/40 last:border-0">
      <div className="rounded-md bg-blush-100 p-1.5 text-plum shrink-0">
        {icon}
      </div>
      <span className="text-[11px] uppercase tracking-[0.14em] text-mauve font-medium w-20 shrink-0">
        {label}
      </span>
      {children}
    </div>
  );
}