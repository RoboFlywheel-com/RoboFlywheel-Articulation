// SPDX-License-Identifier: Apache-2.0

import type { JSX } from "react";

import type { RunSummary } from "@/lib/types";
import { truncateRunId, formatRelativeTime, isRunActive } from "@/lib/dashboard-stats";
import { navigateTo } from "@/lib/router";
import { useViewerDispatch } from "@/lib/viewer-context";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type RecentRunsSectionProps = {
  runs: RunSummary[];
};

const HEAD_CLASSES = "h-8 px-3 text-[10px] font-medium uppercase tracking-[0.06em] text-[var(--text-quaternary)]";

function runStatusBadge(run: RunSummary): JSX.Element {
  if (isRunActive(run)) {
    return <Badge variant="default">running</Badge>;
  }
  if (run.failed_count > 0 && run.success_count === 0) {
    return <Badge variant="destructive">failed</Badge>;
  }
  if (run.failed_count > 0) {
    return <Badge variant="warning">partial</Badge>;
  }
  if (run.result_count > 0) {
    return <Badge variant="success">done</Badge>;
  }
  return <Badge variant="secondary">{run.status ?? "—"}</Badge>;
}

export function RecentRunsSection({ runs }: RecentRunsSectionProps): JSX.Element | null {
  const dispatch = useViewerDispatch();

  if (runs.length === 0) return null;

  const handleRunClick = (runId: string) => {
    dispatch({ type: "SET_RUN_FILTER", payload: runId });
    navigateTo({ page: "viewer" });
  };

  return (
    <section>
      <h2 className="mb-2 text-[10px] font-medium uppercase tracking-[0.06em] text-[var(--text-tertiary)]">
        Recent Runs
      </h2>
      <div className="rounded-md border border-[var(--border-default)] bg-[var(--surface-0)]">
        <Table className="text-[11px]">
          <TableHeader>
            <TableRow className="border-b border-[var(--border-default)] hover:bg-transparent">
              <TableHead className={HEAD_CLASSES}>Run</TableHead>
              <TableHead className={HEAD_CLASSES}>Status</TableHead>
              <TableHead className={`${HEAD_CLASSES} w-full`}>Collection</TableHead>
              <TableHead className={HEAD_CLASSES}>Model</TableHead>
              <TableHead className={HEAD_CLASSES}>Results</TableHead>
              <TableHead className={HEAD_CLASSES}>Created</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {runs.map((run) => {
              const collection = run.collection ?? "—";
              const truncatedId = truncateRunId(run.run_id);
              const needsIdTooltip = truncatedId !== run.run_id;

              return (
                <TableRow
                  key={run.run_id}
                  className="cursor-pointer border-b border-[var(--border-subtle)] hover:bg-[var(--surface-1)]"
                  onClick={() => handleRunClick(run.run_id)}
                >
                  <TableCell className="whitespace-nowrap px-3 py-2 font-mono text-[var(--text-primary)]">
                    {needsIdTooltip ? (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span>{truncatedId}</span>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-[360px] font-mono text-[10px]">
                          {run.run_id}
                        </TooltipContent>
                      </Tooltip>
                    ) : (
                      truncatedId
                    )}
                  </TableCell>
                  <TableCell className="px-3 py-2">{runStatusBadge(run)}</TableCell>
                  <TableCell className="max-w-[200px] truncate px-3 py-2 text-[var(--text-secondary)]">
                    {collection.length > 24 ? (
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="truncate">{collection}</span>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="max-w-[400px] text-[11px]">
                          {collection}
                        </TooltipContent>
                      </Tooltip>
                    ) : (
                      collection
                    )}
                  </TableCell>
                  <TableCell className="whitespace-nowrap px-3 py-2 text-[var(--text-secondary)]">
                    {run.model_id ?? "—"}
                  </TableCell>
                  <TableCell className="whitespace-nowrap px-3 py-2 font-mono text-[var(--text-secondary)]">
                    {run.success_count}/{run.prompt_count ?? run.result_count}
                  </TableCell>
                  <TableCell className="whitespace-nowrap px-3 py-2 text-[var(--text-quaternary)]">
                    {formatRelativeTime(run.created_at)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </section>
  );
}
