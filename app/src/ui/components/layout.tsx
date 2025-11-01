import React from 'react';
import { cx, useDark } from '../theme';

export const Page: React.FC<{ children: React.ReactNode }>=({ children })=>{
  const dark = useDark();
  return (
    <div className={cx('min-h-screen font-mono p-8', dark ? 'bg-neutral-950 text-neutral-100' : 'bg-neutral-50 text-neutral-800')}>{children}</div>
  );
};

export const PageHeader: React.FC<{ title: React.ReactNode; subtitle?: React.ReactNode; right?: React.ReactNode }>=({ title, subtitle, right })=>{
  const dark = useDark();
  return (
    <header className="mb-8">
      <div className="flex items-end justify-between gap-4">
        <h1 className={cx('text-3xl pb-2 border-b', dark ? 'border-neutral-700' : 'border-neutral-400')}>{title}</h1>
        {right}
      </div>
      {subtitle ? (<p className={cx('mt-2 text-sm', dark ? 'text-neutral-400' : 'text-neutral-600')}>{subtitle}</p>) : null}
    </header>
  );
};

export const Section: React.FC<{ title: React.ReactNode; children: React.ReactNode }>=({ title, children })=>{
  const dark = useDark();
  return (
    <section className={cx('mb-10 p-4 rounded-[3px] border', dark ? 'bg-neutral-900 border-neutral-700' : 'bg-white border-neutral-200')}>
      <h2 className={cx('text-xl mb-2 pb-1 border-b', dark ? 'border-neutral-700' : 'border-neutral-300')}>{title}</h2>
      {children}
    </section>
  );
};

export const Divider: React.FC = () => {
  const dark = useDark();
  return <hr className={cx('my-4', dark ? 'border-neutral-700' : 'border-neutral-200')} />;
};
