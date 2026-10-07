"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import {
  LayoutDashboard,
  Compass,
  Briefcase,
  CalendarClock,
  FileText,
  TrendingUp,
  BarChart3,
  User,
  Settings,
  type LucideIcon,
} from "lucide-react";

type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
};

type NavGroup = {
  label: string;
  items: NavItem[];
};

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Main",
    items: [
      { href: "/", label: "Dashboard", icon: LayoutDashboard },
      { href: "/discover", label: "Discover", icon: Compass },
      { href: "/applications", label: "Applications", icon: Briefcase },
      { href: "/deadlines", label: "Deadlines", icon: CalendarClock },
    ],
  },
  {
    label: "Career",
    items: [
      { href: "/resumes", label: "Resumes", icon: FileText },
      { href: "/skill-gaps", label: "Skill Gaps", icon: TrendingUp },
      { href: "/insights", label: "Insights", icon: BarChart3 },
    ],
  },
  {
    label: "Account",
    items: [
      { href: "/profile", label: "Profile", icon: User },
      { href: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sticky top-0 h-screen w-[240px] shrink-0 bg-plum text-blush-50 flex flex-col py-7">
      {/* Brand */}
      <div className="px-6 mb-10">
        <h1 className="font-display text-2xl leading-none tracking-tight">
          Hirearchy
        </h1>
        <p className="mt-1.5 text-[10px] uppercase tracking-[0.18em] text-blush-100/50">
          Find · Match · Apply
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-7 overflow-y-auto">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            <p className="px-3 mb-2 text-[10px] uppercase tracking-[0.16em] text-blush-100/45 font-medium">
              {group.label}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={`relative flex items-center gap-3 px-3 py-2 rounded-lg text-[15px] transition-colors ${
                        isActive
                          ? "text-blush-50"
                          : "text-blush-100/70 hover:text-blush-50 hover:bg-white/5"
                      }`}
                    >
                      {isActive && (
                        <motion.div
                          layoutId="sidebar-active"
                          className="absolute inset-0 rounded-lg bg-white/10 ring-1 ring-white/10"
                          transition={{
                            type: "spring",
                            stiffness: 400,
                            damping: 32,
                          }}
                        />
                      )}
                      <Icon size={16} strokeWidth={1.75} className="relative shrink-0" />
                      <span className="relative font-medium">{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer slot — will hold user chip once auth is wired */}
      <div className="px-6 pt-6 mt-4 text-[10px] uppercase tracking-[0.18em] text-blush-100/40">
        v0.1
      </div>
    </aside>
  );
}