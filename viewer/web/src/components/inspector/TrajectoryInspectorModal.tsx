// SPDX-License-Identifier: Apache-2.0

import { useMemo, type JSX } from "react";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { TrajectoryTurnCard } from "./TrajectoryTurnCard";
import {
  parseEnrichedTurns,
  asRecord,
  formatUsd,
  formatCount,
  overallTraceTotals,
} from "./trajectory-types";

type TrajectoryInspectorModalProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  cost: Record<string, unknown> | null;
  traceText: string | null;
};

export function TrajectoryInspectorModal({
  open,
  onOpenChange,
  cost,
  traceText,
}: TrajectoryInspectorModalProps): JSX.Element {
  const turns = useMemo(
    () => (open ? parseEnrichedTurns(traceText, cost) : []),
    [open, traceText, cost],
  );

  const total = overallTraceTotals(cost);
  const totalTokens = asRecord(total?.tokens);
  const totalCosts = asRecord(total?.costs_usd);
  const modelId = typeof cost?.model_id === "string" ? cost.model_id : null;
  const baseTimestamp = turns.find((turn) => turn.timestamp != null)?.timestamp ?? null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[85vh] w-[95vw] max-w-4xl flex-col gap-0 overflow-hidden p-0">
        {/* Header */}
        <div className="flex shrink-0 items-center justify-between border-b border-[var(--border-default)] px-5 py-3">
          <DialogHeader className="min-w-0 gap-2">
            <DialogTitle className="text-sm">Trajectory Inspector</DialogTitle>
            <DialogDescription className="sr-only">
              Full agent trajectory with thought summaries, tool calls, runtime events, and results.
            </DialogDescription>
            <div className="flex flex-wrap items-center gap-2">
              {modelId ? (
                <Badge variant="default">
                  <span className="font-mono text-[10px]">{modelId}</span>
                </Badge>
              ) : null}
              <Badge variant="success">{formatUsd(totalCosts?.total)}</Badge>
              <Badge variant="secondary">
                {formatCount(totalTokens?.total_tokens)} tok
              </Badge>
              <Badge variant="secondary">{turns.length} turns</Badge>
            </div>
          </DialogHeader>
          <DialogClose className="shrink-0" />
        </div>

        {/* Scrollable body */}
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="divide-y divide-[var(--border-subtle)] px-5">
            {turns.length > 0 ? (
              turns.map((turn) => (
                <div key={turn.index} className="min-w-0 py-4 first:pt-4 last:pb-5">
                  <TrajectoryTurnCard
                    turn={turn}
                    baseTimestamp={baseTimestamp}
                  />
                </div>
              ))
            ) : (
              <p className="py-8 text-center text-xs text-[var(--text-quaternary)]">
                No trajectory data available.
              </p>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
