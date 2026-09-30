type IconProps = {
  className?: string;
};

const base = "h-6 w-6";

export function IconShield({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M12 3l7 3v5.5c0 4.5-3 7.7-7 9.5-4-1.8-7-5-7-9.5V6l7-3z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M9 12l2 2 4-4"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconServer({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <rect
        x="3.5"
        y="4"
        width="17"
        height="6"
        rx="1.4"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <rect
        x="3.5"
        y="14"
        width="17"
        height="6"
        rx="1.4"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <circle cx="7" cy="7" r="0.9" fill="currentColor" />
      <circle cx="7" cy="17" r="0.9" fill="currentColor" />
    </svg>
  );
}

export function IconDatabase({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <ellipse
        cx="12"
        cy="5.5"
        rx="7.5"
        ry="2.5"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M4.5 5.5v13c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5v-13"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M4.5 12c0 1.4 3.4 2.5 7.5 2.5s7.5-1.1 7.5-2.5"
        stroke="currentColor"
        strokeWidth="1.6"
      />
    </svg>
  );
}

export function IconLock({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <rect
        x="5"
        y="11"
        width="14"
        height="9"
        rx="1.8"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M8 11V7.5a4 4 0 018 0V11"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconCpu({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <rect
        x="7"
        y="7"
        width="10"
        height="10"
        rx="1.4"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <rect
        x="10"
        y="10"
        width="4"
        height="4"
        rx="0.8"
        stroke="currentColor"
        strokeWidth="1.4"
      />
      <path
        d="M9 3v2.2M15 3v2.2M9 18.8V21M15 18.8V21M3 9h2.2M3 15h2.2M18.8 9H21M18.8 15H21"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconEuro({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M17 6.5A6.7 6.7 0 0012 4.3c-3.6 0-6.5 3-6.5 7.7s2.9 7.7 6.5 7.7A6.7 6.7 0 0017 17.5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <path
        d="M3.8 10.2h8M3.8 13.8h8"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconUsers({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <circle cx="9" cy="8" r="3" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M3.5 20c0-3.3 2.5-6 5.5-6s5.5 2.7 5.5 6"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <circle cx="17" cy="9" r="2.4" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M15.5 20c.2-2.6 1.6-4.7 3.6-5.6"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconCheckCircle({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M8.5 12.3l2.3 2.3 4.7-5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconArrowRight({ className = "h-4 w-4" }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M4 12h16M14 6l6 6-6 6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconBuilding({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <rect
        x="4"
        y="3.5"
        width="11"
        height="17"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <rect
        x="15"
        y="9"
        width="5"
        height="11.5"
        rx="1"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M7 7h1.4M11 7h1.4M7 11h1.4M11 11h1.4M7 15h1.4M11 15h1.4"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconPlug({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M9 3v5M15 3v5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
      <path
        d="M6.5 8h11v3.5c0 3-2.4 5.5-5.5 5.5s-5.5-2.5-5.5-5.5V8z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M12 17v4"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconSearch({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <circle
        cx="10.5"
        cy="10.5"
        r="6"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M15 15l5 5"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconChat({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M4 5.5h16v10.5H9.5L5.5 19v-3H4z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M7.5 9.5h9M7.5 12.5h6"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
      />
    </svg>
  );
}

export function IconLayers({ className = base }: IconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M12 3.5l8 4.2-8 4.2-8-4.2 8-4.2z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M4 12l8 4.2 8-4.2"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="M4 15.8l8 4.2 8-4.2"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}
