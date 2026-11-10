// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

type RunProgressBarProps = {
  successCount: number;
  failedCount: number;
  totalCount: number;
};

export function RunProgressBar({ successCount, failedCount, totalCount }: RunProgressBarProps): JSX.Element {
  if (totalCount === 0) {
    return <div className="h-[3px] w-full rounded-full bg-[var(--surface-3)]" />;
  }

  const successPct = (successCount / totalCount) * 100;
  const failedPct = (failedCount / totalCount) * 100;
  const remainingPct = 100 - successPct - failedPct;

  return (
    <div className="flex h-[3px] w-full overflow-hidden rounded-full bg-[var(--surface-3)]">
      {successPct > 0 ? (
        <div
          className="h-full bg-[var(--success)]"
          style={{ width: `${successPct}%` }}
        />
      ) : null}
      {failedPct > 0 ? (
        <div
          className="h-full bg-[var(--destructive)]"
          style={{ width: `${failedPct}%` }}
        />
      ) : null}
      {remainingPct > 0 ? (
        <div
          className="h-full bg-[var(--surface-3)]"
          style={{ width: `${remainingPct}%` }}
        />
      ) : null}
    </div>
  );
}
