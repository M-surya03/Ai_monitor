// components/animations/index.jsx
// Replaces FadeAnimation.jsx and SlideAnimation.jsx
// CSS-based — no framer-motion dependency needed

import { useRef, useEffect, useState } from "react";

export function FadeIn({ children, delay = 0, duration = 0.3, style = {}, ...props }) {
  return (
    <div
      style={{
        animation: `fade-in ${duration}s ease both`,
        animationDelay: `${delay}s`,
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}

export function FadeUp({ children, delay = 0, duration = 0.35, style = {}, ...props }) {
  return (
    <div
      style={{
        animation: `fade-up ${duration}s cubic-bezier(.22,.68,0,1.2) both`,
        animationDelay: `${delay}s`,
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}

export function SlideInRight({ children, delay = 0, duration = 0.3, style = {}, ...props }) {
  return (
    <div
      style={{
        animation: `slide-in-r ${duration}s cubic-bezier(.22,.68,0,1.1) both`,
        animationDelay: `${delay}s`,
        ...style,
      }}
      {...props}
    >
      {children}
    </div>
  );
}

// Stagger children with sequential fade-up
export function StaggerList({ children, stagger = 0.06, baseDelay = 0 }) {
  return (
    <>
      {Array.isArray(children)
        ? children.map((child, i) => (
            <FadeUp key={i} delay={baseDelay + i * stagger}>
              {child}
            </FadeUp>
          ))
        : <FadeUp delay={baseDelay}>{children}</FadeUp>}
    </>
  );
}