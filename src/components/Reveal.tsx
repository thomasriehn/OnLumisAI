"use client";
import { useEffect, useRef } from "react";
export function Reveal({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const node = ref.current;
    if (!node || window.matchMedia("(prefers-reduced-motion: reduce)").matches)
      return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          node.classList.add("is-visible");
          observer.disconnect();
        }
      },
      { threshold: 0.08 },
    );
    node.classList.add("reveal-ready");
    observer.observe(node);
    return () => observer.disconnect();
  }, []);
  return (
    <div ref={ref} className="reveal">
      {children}
    </div>
  );
}
