// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

type StatBoxProps = {
  label: string;
  value: string;
  detail?: string;
};

export function StatBox({ label, value, detail }: StatBoxProps): JSX.Element {
  return (
    <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-0)] px-4 py-3">
      <p className="text-[10px] font-medium uppercase tracking-[0.06em] text-[var(--text-tertiary)]">
        {label}
      </p>
      <p className="mt-1 font-mono text-[18px] font-medium leading-tight text-[var(--text-primary)]">
        {value}
      </p>
      {detail ? (
        <p className="mt-1 text-[11px] text-[var(--text-quaternary)]">{detail}</p>
      ) : null}
    </div>
  );
}
