import { cookies } from "next/headers";

import Hero from "@/components/landing/Hero";
import Stats from "@/components/landing/Stats";
import Features from "@/components/landing/Features";
import TechStack from "@/components/landing/TechStack";
import Architecture from "@/components/landing/Architecture";
import CTA from "@/components/landing/CTA";

import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

import {
  SESSION_COOKIE_NAME,
  verifySessionToken,
} from "@/lib/auth";

export default async function HomePage() {
  const cookieStore = await cookies();

  const token = cookieStore.get(
    SESSION_COOKIE_NAME,
  )?.value;

  const isAuthenticated =
    verifySessionToken(token);

  return (
    <>
      <Navbar
        isAuthenticated={isAuthenticated}
      />

      <Hero />
      <Stats />
      <Features />
      <TechStack />
      <Architecture />
      <CTA />
      <Footer />
    </>
  );
}