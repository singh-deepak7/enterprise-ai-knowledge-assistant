import AppNavigation from "@/components/layout/AppNavigation";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <AppNavigation />

      <main>
        {children}
      </main>
    </div>
  );
}