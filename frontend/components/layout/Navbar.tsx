import Link from "next/link";

import Logo from "@/components/common/Logo";
import Container from "./Container";
import ThemeToggle from "../common/ThemeToggle";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur">
      <Container>
        <div className="flex h-16 items-center justify-between">
          <Logo />

          <nav className="hidden gap-8 md:flex">
            <Link href="/">Home</Link>
            <Link href="/features">Features</Link>
            <Link href="/architecture">Architecture</Link>
            <Link href="/github">GitHub</Link>
          </nav>

          <div className="flex items-center gap-4">
            <ThemeToggle />

            <button className="rounded-lg bg-cyan-500 px-5 py-2 font-medium text-black transition hover:bg-cyan-400">
              Login
            </button>
          </div>
        </div>
      </Container>
    </header>
  );
}
