"use client";

import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { User, Save, Check, Plus, X } from "lucide-react";
import { apiFetch, ApiError } from "@/lib/api";
import {
  EMPLOYMENT_TYPE_OPTIONS,
  EXPERIENCE_LEVEL_OPTIONS,
  REMOTE_PREF_OPTIONS,
  type Profile,
} from "@/lib/profile-types";
import { Sparkles } from "lucide-react";
import type { ProfileSuggestion } from "@/lib/profile-types";

type Draft = {
  education: string;
  degree: string;
  graduation_year: string;
  current_location: string;
  preferred_locations: string[];
  remote_preference: string;
  preferred_employment_types: string[];
  target_roles: string[];
  experience_level: string;
  salary_min: string;
  salary_currency: string;
  work_authorization: string;
};

function profileToDraft(p: Profile): Draft {
  return {
    education: p.education ?? "",
    degree: p.degree ?? "",
    graduation_year: p.graduation_year?.toString() ?? "",
    current_location: p.current_location ?? "",
    preferred_locations: p.preferred_locations ?? [],
    remote_preference: p.remote_preference ?? "",
    preferred_employment_types: p.preferred_employment_types ?? [],
    target_roles: p.target_roles ?? [],
    experience_level: p.experience_level ?? "",
    salary_min: p.salary_min?.toString() ?? "",
    salary_currency: p.salary_currency ?? "",
    work_authorization: p.work_authorization ?? "",
  };
}

function draftToPayload(d: Draft) {
  // Only send fields the user has filled; "" means "clear".
  return {
    education: d.education || null,
    degree: d.degree || null,
    graduation_year: d.graduation_year ? Number(d.graduation_year) : null,
    current_location: d.current_location || null,
    preferred_locations: d.preferred_locations,
    remote_preference: d.remote_preference || null,
    preferred_employment_types: d.preferred_employment_types,
    target_roles: d.target_roles,
    experience_level: d.experience_level || null,
    salary_min: d.salary_min ? Number(d.salary_min) : null,
    salary_currency: d.salary_currency || null,
    work_authorization: d.work_authorization || null,
  };
}

export default function ProfilePage() {
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [prefilling, setPrefilling] = useState(false);
  const [prefillNotes, setPrefillNotes] = useState<string[] | null>(null);
  useEffect(() => {
    let cancelled = false;
    apiFetch<Profile>("/profile")
      .then((p) => {
        if (!cancelled) setDraft(profileToDraft(p));
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof ApiError
              ? `Could not load profile (${err.status})`
              : "Could not reach the backend."
          );
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function save() {
    if (!draft) return;
    setSaving(true);
    setError(null);
    try {
      await apiFetch<Profile>("/profile", {
        method: "PUT",
        body: JSON.stringify(draftToPayload(draft)),
      });
      setSavedAt(Date.now());
      setTimeout(() => setSavedAt(null), 2500);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? `Could not save (${err.status})`
          : "Could not reach the backend."
      );
    } finally {
      setSaving(false);
    }
  }

  async function prefillFromResume() {
    if (!draft) return;
    setPrefilling(true);
    setPrefillNotes(null);
    setError(null);
    try {
      const s = await apiFetch<ProfileSuggestion>("/profile/suggestions");
      // Merge only the fields that came back non-null. Never overwrite
      // values the user already filled in.
      setDraft({
        ...draft,
        degree: draft.degree || s.degree || "",
        education: draft.education || s.education || "",
        graduation_year:
          draft.graduation_year ||
          (s.graduation_year ? String(s.graduation_year) : ""),
      });
      setPrefillNotes(s.notes);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          err.status === 400
            ? "Upload a resume first — no primary resume found."
            : err.status === 404
              ? "Resume not found."
              : err.status === 422
                ? "We couldn't read text from your resume (it might be a scanned image)."
                : `Could not prefill (${err.status})`
        );
      } else {
        setError("Network error.");
      }
    } finally {
      setPrefilling(false);
    }
  }


  if (loading || !draft) {
    return (
      <div className="p-12 max-w-3xl mx-auto">
        <div className="flex items-center gap-3 text-mauve text-sm">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-mauve/30 border-t-plum" />
          Loading profile…
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 md:p-10 lg:p-12">
      <div className="max-w-3xl mx-auto">
        <motion.header
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
          className="mb-10"
        >
          <div className="flex items-center gap-2 mb-2 text-mauve text-[15px]">
            <User size={14} strokeWidth={1.8} />
            Profile
          </div>
          <h1 className="font-display text-5xl leading-none tracking-tight text-ink mb-4">
            About you
          </h1>
          <p className="text-mauve max-w-xl leading-relaxed">
            This powers your job matching. The more you fill in, the more
            accurate your scores.
          </p>
        </motion.header>

        {error && (
          <div className="mb-6 rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
            {error}
          </div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="space-y-6"
        >
          <Section title="Education">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Institution">
                <TextInput
                  value={draft.education}
                  onChange={(v) => setDraft({ ...draft, education: v })}
                  placeholder="e.g. Sahrdaya College of Engineering"
                />
              </Field>
              <Field label="Degree">
                <TextInput
                  value={draft.degree}
                  onChange={(v) => setDraft({ ...draft, degree: v })}
                  placeholder="e.g. B.Tech in Computer Science"
                />
              </Field>
              <Field label="Graduation year">
                <TextInput
                  value={draft.graduation_year}
                  onChange={(v) => setDraft({ ...draft, graduation_year: v })}
                  type="number"
                  placeholder="2027"
                />
              </Field>
            </div>
          </Section>

          <Section title="Location">
            <div className="grid grid-cols-1 gap-4">
              <Field label="Current location">
                <TextInput
                  value={draft.current_location}
                  onChange={(v) => setDraft({ ...draft, current_location: v })}
                  placeholder="e.g. Bangalore, India"
                />
              </Field>
              <Field label="Preferred locations">
                <ChipInput
                  values={draft.preferred_locations}
                  onChange={(v) =>
                    setDraft({ ...draft, preferred_locations: v })
                  }
                  placeholder="Add a location and press Enter"
                />
              </Field>
              <Field label="Remote preference">
                <SelectInput
                  value={draft.remote_preference}
                  onChange={(v) =>
                    setDraft({ ...draft, remote_preference: v })
                  }
                  options={[...REMOTE_PREF_OPTIONS]}
                  placeholder="Not set"
                />
              </Field>
            </div>
          </Section>

          <Section title="Job preferences">
            <div className="grid grid-cols-1 gap-4">
              <Field label="Target roles">
                <ChipInput
                  values={draft.target_roles}
                  onChange={(v) => setDraft({ ...draft, target_roles: v })}
                  placeholder="e.g. Backend Engineer, AI Engineer"
                />
              </Field>
              <Field label="Employment types">
                <MultiChipSelect
                  values={draft.preferred_employment_types}
                  onChange={(v) =>
                    setDraft({ ...draft, preferred_employment_types: v })
                  }
                  options={[...EMPLOYMENT_TYPE_OPTIONS]}
                />
              </Field>
              <Field label="Experience level">
                <SelectInput
                  value={draft.experience_level}
                  onChange={(v) =>
                    setDraft({ ...draft, experience_level: v })
                  }
                  options={[...EXPERIENCE_LEVEL_OPTIONS]}
                  placeholder="Not set"
                />
              </Field>
            </div>
          </Section>

          <Section title="Compensation & authorization">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field label="Minimum salary">
                <TextInput
                  value={draft.salary_min}
                  onChange={(v) => setDraft({ ...draft, salary_min: v })}
                  type="number"
                  placeholder="e.g. 600000"
                />
              </Field>
              <Field label="Currency">
                <TextInput
                  value={draft.salary_currency}
                  onChange={(v) => setDraft({ ...draft, salary_currency: v })}
                  placeholder="e.g. INR, USD"
                />
              </Field>
              <Field label="Work authorization" className="md:col-span-2">
                <TextInput
                  value={draft.work_authorization}
                  onChange={(v) =>
                    setDraft({ ...draft, work_authorization: v })
                  }
                  placeholder="e.g. Indian citizen, no sponsorship needed"
                />
              </Field>
            </div>
          </Section>
          {/* Save bar */}
          <div className="sticky bottom-6 flex items-center justify-end gap-3">
            <button
              onClick={prefillFromResume}
              disabled={prefilling}
              className="inline-flex items-center gap-2 rounded-lg bg-white ring-1 ring-border text-plum px-4 py-2.5 text-sm font-medium hover:bg-blush-50 disabled:opacity-50 transition-colors shadow-soft"
            >
              <Sparkles size={14} strokeWidth={2} />
              {prefilling ? "Reading resume…" : "Prefill from resume"}
            </button>
            {savedAt && (
              <motion.span
                initial={{ opacity: 0, x: 4 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="inline-flex items-center gap-1.5 text-[14px] text-accent"
              >
                <Check size={13} strokeWidth={2.4} />
                Saved
              </motion.span>
            )}
            <button
              onClick={save}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg bg-plum text-blush-50 px-5 py-2.5 text-sm font-medium hover:bg-ink disabled:opacity-50 transition-colors shadow-lift"
            >
              <Save size={14} strokeWidth={2.2} />
              {saving ? "Saving…" : "Save profile"}
            </button>
          </div>
          {prefillNotes && prefillNotes.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl bg-blush-50 ring-1 ring-border/40 px-5 py-4"
            >
              <p className="text-[14px] uppercase tracking-[0.14em] text-mauve mb-2 font-medium">
                Resume analysis
              </p>
              <ul className="space-y-1">
                {prefillNotes.map((n, i) => (
                  <li key={i} className="text-[14px] text-mauve leading-relaxed">
                    · {n}
                  </li>
                ))}
              </ul>
              <p className="text-[14px] text-mauve/70 mt-3">
                Review the filled fields before saving. Nothing is saved until
                you press <span className="font-medium">Save profile</span>.
              </p>
            </motion.div>
          )}

          {/* Save bar */}
          <div className="sticky bottom-6 flex items-center justify-end gap-3">
            {savedAt && (
              <motion.span
                initial={{ opacity: 0, x: 4 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="inline-flex items-center gap-1.5 text-[14px] text-accent"
              >
                <Check size={13} strokeWidth={2.4} />
                Saved
              </motion.span>
            )}
            <button
              onClick={save}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-lg bg-plum text-blush-50 px-5 py-2.5 text-sm font-medium hover:bg-ink disabled:opacity-50 transition-colors shadow-lift"
            >
              <Save size={14} strokeWidth={2.2} />
              {saving ? "Saving…" : "Save profile"}
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl bg-white ring-1 ring-border/40 shadow-soft p-8">
      <h2 className="font-display text-xl text-ink mb-6">{title}</h2>
      {children}
    </div>
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
      <span className="block text-[14px] uppercase tracking-[0.14em] text-mauve mb-1.5 font-medium">
        {label}
      </span>
      {children}
    </label>
  );
}

function TextInput({
  value,
  onChange,
  type = "text",
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <input
      type={type}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink placeholder:text-mauve/50 outline-none focus:border-plum focus:ring-2 focus:ring-plum/10"
    />
  );
}

function SelectInput({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  placeholder?: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-lg bg-blush-50 border border-border px-3 py-2 text-sm text-ink outline-none focus:border-plum focus:ring-2 focus:ring-plum/10"
    >
      <option value="">{placeholder ?? "Select…"}</option>
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

function ChipInput({
  values,
  onChange,
  placeholder,
}: {
  values: string[];
  onChange: (v: string[]) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState("");

  function add() {
    const v = input.trim();
    if (v && !values.includes(v)) onChange([...values, v]);
    setInput("");
  }

  return (
    <div className="rounded-lg bg-blush-50 border border-border px-3 py-2 focus-within:border-plum focus-within:ring-2 focus-within:ring-plum/10 transition-all">
      {values.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {values.map((v) => (
            <span
              key={v}
              className="inline-flex items-center gap-1 rounded-full bg-white ring-1 ring-border/60 px-2.5 py-0.5 text-[14px] text-ink"
            >
              {v}
              <button
                type="button"
                onClick={() => onChange(values.filter((x) => x !== v))}
                className="text-mauve/60 hover:text-danger transition-colors"
                aria-label={`Remove ${v}`}
              >
                <X size={10} strokeWidth={2.4} />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="flex items-center gap-1.5">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-sm text-ink placeholder:text-mauve/50 outline-none"
        />
        {input.trim() && (
          <button
            type="button"
            onClick={add}
            className="rounded p-0.5 text-mauve hover:text-plum transition-colors"
            aria-label="Add"
          >
            <Plus size={13} strokeWidth={2.4} />
          </button>
        )}
      </div>
    </div>
  );
}

function MultiChipSelect({
  values,
  onChange,
  options,
}: {
  values: string[];
  onChange: (v: string[]) => void;
  options: { value: string; label: string }[];
}) {
  function toggle(v: string) {
    if (values.includes(v)) onChange(values.filter((x) => x !== v));
    else onChange([...values, v]);
  }
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => {
        const active = values.includes(o.value);
        return (
          <button
            key={o.value}
            type="button"
            onClick={() => toggle(o.value)}
            className={`rounded-full px-3.5 py-1.5 text-[14px] font-medium ring-1 transition-all ${
              active
                ? "bg-plum text-blush-50 ring-plum"
                : "bg-white text-mauve ring-border/60 hover:text-plum hover:ring-border"
            }`}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}