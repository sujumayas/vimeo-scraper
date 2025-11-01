import React from 'react';
import { cx, useDark, paletteFor } from '../theme';

export const Badge: React.FC<{ tone?: string; children: React.ReactNode }>=({ tone = 'neutral', children })=>{
  const dark = useDark();
  const t = paletteFor(tone, dark);
  return <span className={cx('text-xs px-2 py-[2px] border rounded-[3px]', t.border, t.bg, t.text)}>{children}</span>;
};

export const Status: React.FC<{ value: string; tone?: string }> = ({ value, tone = 'neutral' }) => <Badge tone={tone}>{value}</Badge>;
