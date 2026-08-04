import { BrainCircuit } from "lucide-react";
import Link from "next/link";

export default function Logo() {
  return (
    <Link href="/" className="flex items-center gap-3">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500 text-black">
        <BrainCircuit className="h-6 w-6" />
      </div>

      <div>
        <h1 className="text-lg font-bold tracking-tight">
          Enterprise AI
        </h1>

        <p className="text-xs text-muted-foreground">
          Knowledge Assistant
        </p>
      </div>
    </Link>
  );
}