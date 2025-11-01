import React from 'react';
import { cx, useDark } from '../theme';

export const Button: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'ghost' | 'solid' }>
= ({ children, variant = 'ghost', className = '', ...props }) => {
  const dark = useDark();
  const base = cx('inline-block px-3 py-1 text-sm border select-none rounded-[3px]', dark ? 'border-neutral-700 hover:bg-neutral-800 active:bg-neutral-700' : 'border-neutral-300 hover:bg-neutral-100 active:bg-neutral-200');
  const ghost = 'bg-transparent';
  const solid = dark ? 'bg-neutral-800 hover:bg-neutral-700' : 'bg-neutral-100 hover:bg-neutral-200';
  const styles = variant === 'solid' ? cx(base, solid) : cx(base, ghost);
  return <button className={cx(styles, className)} {...props}>{children}</button>;
};

export const Input: React.FC<React.InputHTMLAttributes<HTMLInputElement>> = ({ className = '', ...props }) => {
  const dark = useDark();
  return <input {...props} className={cx('px-2 py-1 text-sm focus:outline-none focus:ring-0', dark ? 'border border-neutral-700 bg-neutral-900 text-neutral-100 focus:border-neutral-500' : 'border border-neutral-300 bg-white text-neutral-800 focus:border-neutral-500', className)} />;
};

export const Select: React.FC<React.SelectHTMLAttributes<HTMLSelectElement> & { options?: Array<string | {label: string; value: string}> }>
= ({ className = '', options = [], ...props }) => {
  const dark = useDark();
  return (
    <select {...props} className={cx('px-2 py-1 text-sm focus:outline-none focus:ring-0', dark ? 'border border-neutral-700 bg-neutral-900 text-neutral-100 focus:border-neutral-500' : 'border border-neutral-300 bg-white text-neutral-800 focus:border-neutral-500', className)}>
      {options.map((o) => <option key={(o as any).value ?? o as string} value={(o as any).value ?? o as string}>{(o as any).label ?? o as string}</option>)}
    </select>
  );
};

export const Checkbox: React.FC<React.InputHTMLAttributes<HTMLInputElement> & { label?: React.ReactNode }>
= ({ label, ...props }) => {
  const dark = useDark();
  return (
    <label className="inline-flex items-center gap-2 text-sm">
      <input type="checkbox" className={cx('border', dark ? 'border-neutral-700 bg-neutral-900' : 'border-neutral-300 bg-white')} {...props} />
      {label ? <span>{label}</span> : null}
    </label>
  );
};

export const Toolbar: React.FC<{ children: React.ReactNode }>=({ children })=>{
  const dark = useDark();
  return <div className={cx('flex flex-wrap items-center gap-2 p-2 border rounded-[3px]', dark ? 'border-neutral-700 bg-neutral-900' : 'border-neutral-300 bg-white')}>{children}</div>;
};
