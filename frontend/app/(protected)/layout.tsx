import {
  cookies,
} from "next/headers";

import {
  redirect,
} from "next/navigation";

import AppNavigation from "@/components/layout/AppNavigation";

import {
  SESSION_COOKIE_NAME,
  verifySessionToken,
} from "@/lib/auth";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const cookieStore =
    await cookies();

  const token =
    cookieStore.get(
      SESSION_COOKIE_NAME,
    )?.value;

  if (
    !verifySessionToken(token)
  ) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-background">
      <AppNavigation />

      <main>
        {children}
      </main>
    </div>
  );
}
