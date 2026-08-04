import Container from "@/components/layout/Container";
import StatCard from "@/components/common/StatCard";

const stats = [
  {
    value: "500+",
    label: "Documents",
  },
  {
    value: "100K+",
    label: "Embeddings",
  },
  {
    value: "4",
    label: "AI Agents",
  },
  {
    value: "<2 sec",
    label: "Average Response",
  },
];

export default function Stats() {
  return (
    <section className="pb-24">
      <Container>
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {stats.map((item) => (
            <StatCard
              key={item.label}
              value={item.value}
              label={item.label}
            />
          ))}
        </div>
      </Container>
    </section>
  );
}