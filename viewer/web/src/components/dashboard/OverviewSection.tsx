// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

import type { DashboardOverview } from "@/lib/types";
import { formatBytes, formatCost } from "@/lib/dashboard-stats";
import { StatBox } from "@/components/dashboard/StatBox";

type OverviewSectionProps = {
  stats: DashboardOverview;
};

export function OverviewSection({ stats }: OverviewSectionProps): JSX.Element {
  return (
    <section>
      <h2 className="mb-2 text-[10px] font-medium uppercase tracking-[0.06em] text-[var(--text-tertiary)]">
        Overview
      </h2>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        <StatBox
          label="Records"
          value={String(stats.total_records)}
          detail={`${stats.category_count} categor${stats.category_count !== 1 ? "ies" : "y"}${stats.is_filtered ? " in current view" : ""}`}
        />
        <StatBox
          label="Runs"
          value={String(stats.total_runs)}
          detail={`${stats.model_count} model${stats.model_count !== 1 ? "s" : ""}, ${stats.sdk_count} SDK${stats.sdk_count !== 1 ? "s" : ""}`}
        />
        <StatBox
          label="Total Cost"
          value={formatCost(stats.total_cost_usd)}
          detail={
            stats.average_cost_usd != null
              ? `${formatCost(stats.average_cost_usd)} avg/record`
              : undefined
          }
        />
        <StatBox
          label="Data Size"
          value={stats.data_size_bytes != null ? formatBytes(stats.data_size_bytes) : "—"}
          detail={stats.data_size_bytes != null ? "excl. gitignored" : undefined}
        />
      </div>
    </section>
  );
}
