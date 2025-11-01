import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type ThemeValue = {
  dark: boolean;
  setDark: React.Dispatch<React.SetStateAction<boolean>>;
};

const ThemeCtx = createContext<ThemeValue | null>(null);
export const useTheme = () => {
  const ctx = useContext(ThemeCtx);
  if (!ctx) throw new Error('useTheme must be used within <ThemeProvider>');
  return ctx;
};
export const useDark = () => useTheme().dark;
export const cx = (...arr: Array<string | false | null | undefined>) => arr.filter(Boolean).join(' ');

export const ThemeProvider: React.FC<{ children: React.ReactNode }>
  = ({ children }) => {
  const [dark, setDark] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    const stored = localStorage.getItem('theme');
    if (stored === 'dark') return true;
    if (stored === 'light') return false;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  useEffect(() => {
    if (typeof window !== 'undefined') localStorage.setItem('theme', dark ? 'dark' : 'light');
  }, [dark]);
  const value = useMemo(() => ({ dark, setDark }), [dark]);
  return <ThemeCtx.Provider value={value}>{children}</ThemeCtx.Provider>;
};

// Palettes (light/dark)
export const PALETTE_LIGHT = {
  neutral: { bg: 'bg-neutral-50', border: 'border-neutral-300', text: 'text-neutral-700' },
  info:    { bg: 'bg-sky-50',     border: 'border-sky-300',     text: 'text-sky-800' },
  success: { bg: 'bg-emerald-50', border: 'border-emerald-300', text: 'text-emerald-800' },
  warning: { bg: 'bg-amber-50',   border: 'border-amber-300',   text: 'text-amber-800' },
  danger:  { bg: 'bg-rose-50',    border: 'border-rose-300',    text: 'text-rose-800' },
  note:    { bg: 'bg-stone-50',   border: 'border-stone-300',   text: 'text-stone-700' },
} as const;
export const PALETTE_DARK = {
  neutral: { bg: 'bg-neutral-900', border: 'border-neutral-700', text: 'text-neutral-200' },
  info:    { bg: 'bg-sky-900/30',     border: 'border-sky-700',     text: 'text-sky-200' },
  success: { bg: 'bg-emerald-900/30', border: 'border-emerald-700', text: 'text-emerald-200' },
  warning: { bg: 'bg-amber-900/30',   border: 'border-amber-700',   text: 'text-amber-200' },
  danger:  { bg: 'bg-rose-900/30',    border: 'border-rose-700',    text: 'text-rose-200' },
  note:    { bg: 'bg-stone-900/30',   border: 'border-stone-700',   text: 'text-stone-200' },
} as const;
export const paletteFor = (tone: keyof typeof PALETTE_LIGHT | string, dark: boolean) => (dark ? (PALETTE_DARK as any) : (PALETTE_LIGHT as any))[tone] || (dark ? PALETTE_DARK.neutral : PALETTE_LIGHT.neutral);
