"use client";

import { motion } from "framer-motion";

interface Props {
  children: React.ReactNode;
}

export default function FadeIn({
  children,
}: Props) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 150,
      }}
      whileInView={{
        opacity: 1,
        y: 0,
      }}
      viewport={{
        once: true,
      }}
      transition={{
        duration: 2,
      }}
    >
      {children}
    </motion.div>
  );
}