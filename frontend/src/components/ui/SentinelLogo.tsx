import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
  glow?: boolean;
}

export const SentinelLogo: React.FC<LogoProps> = ({ className = '', size = 32, glow = true }) => {
  return (
    <div
      className={`relative inline-flex items-center justify-center flex-shrink-0 ${className}`}
      style={{ width: size, height: size }}
    >
      {/* Dynamic Cyber Ambient Glow */}
      {glow && (
        <div
          className="absolute inset-0 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-fuchsia-500 opacity-60 blur-md animate-pulse pointer-events-none"
          style={{ width: size, height: size }}
        />
      )}

      {/* Futuristic Cyber Aegis Shield SVG */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="relative z-10 drop-shadow-[0_2px_10px_rgba(6,182,212,0.4)]"
      >
        <defs>
          <linearGradient id="shieldBorderGrad" x1="4" y1="4" x2="44" y2="44" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#22D3EE" />
            <stop offset="50%" stopColor="#6366F1" />
            <stop offset="100%" stopColor="#A855F7" />
          </linearGradient>

          <linearGradient id="shieldFillGrad" x1="24" y1="4" x2="24" y2="44" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0B132B" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#020617" stopOpacity="0.98" />
          </linearGradient>

          <linearGradient id="coreEnergyGrad" x1="16" y1="14" x2="32" y2="34" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="50%" stopColor="#818CF8" />
            <stop offset="100%" stopColor="#C084FC" />
          </linearGradient>

          <radialGradient id="cyberCoreGlow" cx="24" cy="24" r="10" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#38BDF8" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Outer Shield Hull with Cyber Angled Edge */}
        <path
          d="M24 3L40 9V21C40 31.8 33.2 41.5 24 45C14.8 41.5 8 31.8 8 21V9L24 3Z"
          fill="url(#shieldFillGrad)"
          stroke="url(#shieldBorderGrad)"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* Inner Tactical Border */}
        <path
          d="M24 7L36 11.5V20.5C36 28.8 30.8 36.3 24 39.5C17.2 36.3 12 28.8 12 20.5V11.5L24 7Z"
          stroke="#1E293B"
          strokeWidth="1.2"
          strokeDasharray="2 2"
        />

        {/* Radiant Core Glow */}
        <circle cx="24" cy="24" r="8" fill="url(#cyberCoreGlow)" />

        {/* Central Sentinel Forge Core (The Cyber Anvil / Aegis Emblem) */}
        <path
          d="M24 13L30 19L27 25H21L18 19L24 13Z"
          fill="url(#coreEnergyGrad)"
        />
        <path
          d="M24 25V33M20 33H28"
          stroke="#38BDF8"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* Security Spark Points */}
        <circle cx="24" cy="19" r="1.5" fill="#FFFFFF" />
        <circle cx="15" cy="15" r="1" fill="#22D3EE" opacity="0.8" />
        <circle cx="33" cy="15" r="1" fill="#A855F7" opacity="0.8" />
      </svg>
    </div>
  );
};

export default SentinelLogo;
