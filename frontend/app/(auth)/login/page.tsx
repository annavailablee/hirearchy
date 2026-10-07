"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { useAuth } from "@/lib/auth";
import { ApiError } from "@/lib/api";

type Mode = "login" | "register";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, password, fullName);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(
          typeof err.detail === "string"
            ? err.detail
            : "Something went wrong. Check your details."
        );
      } else {
        setError("Network error. Is the backend running?");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="mb-8">
        <h1 className="font-display text-4xl leading-tight tracking-tight text-ink">
          {mode === "login" ? "Welcome back." : "Create your account."}
        </h1>
        <p className="mt-2 text-sm text-mauve">
          {mode === "login"
            ? "Sign in to continue your search."
            : "Set up your Hirearchy workspace in seconds."}
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        {mode === "register" && (
          <Field
            label="Full name"
            value={fullName}
            onChange={setFullName}
            type="text"
            placeholder="Your name"
            autoComplete="name"
          />
        )}
        <Field
          label="Email"
          value={email}
          onChange={setEmail}
          type="email"
          placeholder="you@example.com"
          autoComplete="email"
          required
        />
        <Field
          label="Password"
          value={password}
          onChange={setPassword}
          type="password"
          placeholder={mode === "register" ? "At least 8 characters" : "••••••••"}
          autoComplete={mode === "register" ? "new-password" : "current-password"}
          required
          minLength={mode === "register" ? 8 : undefined}
        />

        {error && (
          <div className="text-[15px] text-danger bg-danger/10 border border-danger/20 rounded-md px-3 py-2">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-plum text-blush-50 py-2.5 text-sm font-medium transition-all hover:bg-ink disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting
            ? "Working…"
            : mode === "login"
              ? "Sign in"
              : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-sm text-mauve text-center">
        {mode === "login" ? "New to Hirearchy?" : "Already have an account?"}{" "}
        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
          className="text-plum font-medium underline-offset-4 hover:underline"
        >
          {mode === "login" ? "Create an account" : "Sign in"}
        </button>
      </p>
    </motion.div>
  );
}

function Field({
  label,
  value,
  onChange,
  type,
  placeholder,
  autoComplete,
  required,
  minLength,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type: string;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
  minLength?: number;
}) {
  return (
    <label className="block">
      <span className="block text-[14px] uppercase tracking-[0.14em] text-mauve mb-1.5 font-medium">
        {label}
      </span>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoComplete={autoComplete}
        required={required}
        minLength={minLength}
        className="w-full rounded-lg bg-white border border-border px-3.5 py-2.5 text-sm text-ink placeholder:text-mauve/50 outline-none transition-colors focus:border-plum focus:ring-2 focus:ring-plum/10"
      />
    </label>
  );
}