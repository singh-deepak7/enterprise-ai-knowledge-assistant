import Hero from "@/components/landing/Hero";
import Stats from "@/components/landing/Stats";
import Features from "@/components/landing/Features";
import TechStack from "@/components/landing/TechStack";
import Architecture from "@/components/landing/Architecture";
import CTA from "@/components/landing/CTA";

import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

import FadeIn from "@/components/common/FadeIn";

export default function HomePage() {
  return (
   <>
  <Navbar />
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