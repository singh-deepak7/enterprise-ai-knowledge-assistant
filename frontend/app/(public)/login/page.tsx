"use client";

import {
  FormEvent,
  useState,
} from "react";

import Link from "next/link";
import {
  useRouter,
} from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (
      !username.trim() ||
      !password
    ) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response =
        await fetch(
          "/api/auth/login",
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              username:
                username.trim(),
              password,
            }),
          },
        );

      if (!response.ok) {
        let message =
          "Login failed.";

        try {
          const result =
            (await response.json()) as {
              message?: string;
            };

          message =
            result.message ??
            message;
        } catch {
          // Keep default message.
        }

        throw new Error(
          message,
        );
      }

      router.push("/chat");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md space-y-6 rounded-xl border p-8">
        <div>
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            ← Back to home
          </Link>

          <h1 className="mt-6 text-2xl font-semibold">
            Sign in
          </h1>

          <p className="mt-2 text-sm text-muted-foreground">
            Access the Enterprise AI
            Knowledge Assistant.
          </p>
        </div>

        <form
          className="space-y-4"
          onSubmit={handleSubmit}
        >
          <div className="space-y-2">
            <label
              htmlFor="username"
              className="text-sm font-medium"
            >
              Username
            </label>

            <input
              id="username"
              type="text"
              autoComplete="username"
              value={username}
              disabled={loading}
              onChange={(event) =>
                setUsername(
                  event.target.value,
                )
              }
              className="w-full rounded-md border bg-background px-3 py-2"
            />
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="text-sm font-medium"
            >
              Password
            </label>

            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              disabled={loading}
              onChange={(event) =>
                setPassword(
                  event.target.value,
                )
              }
              className="w-full rounded-md border bg-background px-3 py-2"
            />
          </div>

          {error && (
            <div className="rounded-md border border-destructive p-3 text-sm text-destructive">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={
              loading ||
              !username.trim() ||
              !password
            }
            className="w-full rounded-md bg-primary px-4 py-2 font-medium text-primary-foreground disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>
        </form>
      </div>
    </main>
  );
}