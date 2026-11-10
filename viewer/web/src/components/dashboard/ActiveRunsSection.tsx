// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

import type { RunSummary } from "@/lib/types";
import { isRunActive, truncateRunId, formatRelativeTime } from "@/lib/dashboard-stats";
import { navigateTo } from "@/lib/router";
import { useViewerDispatch } from "@/lib/viewer-context";
import { Badge } from "@/components/ui/badge";
import { RunProgressBar } from "@/components/dashboard/RunProgressBar";

type ActiveRunsSectionProps = {
  runs: RunSummary[];
};

export function ActiveRunsSection({ runs }: ActiveRunsSectionProps): JSX.Element | null {
  const dispatch = useViewerDispatch();
  const activeRuns = runs.filter(isRunActive);

  if (activeRuns.length === 0) return null;

  const handleRunClick = (runId: string) => {
    dispatch({ type: "SET_RUN_FILTER", payload: runId });
    navigateTo({ page: "viewer" });
  };

  return (
    <section>
      <h2 className="mb-2 text-[10px] font-medium uppercase tracking-[0.06em] text-[var(--text-tertiary)]">
        Active Runs
      </h2>
      <div className="flex flex-col gap-2">
        {activeRuns.map((run) => (
          <button
            key={run.run_id}
            type="button"
            onClick={() => handleRunClick(run.run_id)}
            className="w-full cursor-pointer rounded-md border border-[var(--border-default)] border-l-[var(--accent)] border-l-[3px] bg-[var(--surface-0)] px-4 py-3 text-left transition-colors hover:bg-[var(--surface-1)]"
          >
            <div className="flex items-center gap-2">
              <span className="relative flex size-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--accent)] opacity-60" />
                <span className="relative inline-flex size-2 rounded-full bg-[var(--accent)]" />
              </span>
              <span className="font-mono text-[11px] text-[var(--text-primary)]">
                {truncateRunId(run.run_id)}
              </span>
              <Badge variant="default">running</Badge>
              <span className="text-[11px] text-[var(--text-tertiary)]">
                {run.result_count}/{run.prompt_count ?? "?"} prompts
              </span>
              {run.model_id ? (
                <span className="text-[11px] text-[var(--text-quaternary)]">{run.model_id}</span>
              ) : null}
              <span className="ml-auto text-[11px] text-[var(--text-quaternary)]">
                {formatRelativeTime(run.updated_at ?? run.created_at)}
              </span>
            </div>
            <div className="mt-2">
              <RunProgressBar
                successCount={run.success_count}
                failedCount={run.failed_count}
                totalCount={run.prompt_count ?? run.result_count}
              />
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
