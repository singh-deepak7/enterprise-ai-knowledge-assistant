import Link from "next/link";

import Logo from "@/components/common/Logo";
import ThemeToggle from "@/components/common/ThemeToggle";
import LogoutButton from "@/components/auth/LogoutButton";

import Container from "./Container";
import MobileMenu from "./MobileMenu";
import NavLink from "./NavLink";

interface NavbarProps {
  isAuthenticated?: boolean;
}

export default function Navbar({
  isAuthenticated = false,
}: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 border-b bg-background/80 backdrop-blur">
      <Container>
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Logo />

          {/* Desktop Navigation */}
          <nav className="hidden items-center gap-8 md:flex">
            <NavLink href="/">
              Home
            </NavLink>

            <NavLink href="/#features">
              Features
            </NavLink>

            <NavLink href="/#architecture">
              Architecture
            </NavLink>

            <a
              href="https://github.com/singh-deepak7/enterprise-ai-knowledge-assistant"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground transition hover:text-foreground"
            >
              GitHub
            </a>
          </nav>

          {/* Desktop Actions */}
          <div className="hidden items-center gap-4 md:flex">
            <ThemeToggle />

            {isAuthenticated ? (
              <LogoutButton />
            ) : (
              <Link
                href="/login"
                className="rounded-lg bg-cyan-500 px-5 py-2 font-medium text-black transition hover:bg-cyan-400"
              >
                Login
              </Link>
            )}
          </div>

          {/* Mobile Menu */}
          <MobileMenu />
        </div>
      </Container>
    </header>
  );
}