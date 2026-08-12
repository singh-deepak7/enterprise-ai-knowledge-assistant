interface StatCardProps {
  value: string;
  label: string;
}

export default function StatCard({
  value,
  label,
}: StatCardProps) {
  return (
    <div className="rounded-2xl border bg-card/70 p-6 backdrop-blur">
      <h3 className="text-3xl font-bold text-cyan-400">
        {value}
      </h3>

      <p className="mt-2 text-sm text-muted-foreground">
        {label}
      </p>
    </div>
  );
}