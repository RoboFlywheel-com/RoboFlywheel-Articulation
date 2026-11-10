// SPDX-License-Identifier: Apache-2.0

import { type JSX } from "react";

import type { StagingEntry, ViewerSelection } from "@/lib/types";
import { useViewer, useViewerDispatch } from "@/lib/viewer-context";
import { Badge } from "@/components/ui/badge";

function formatTimeAgo(dateString: string | null): string | null {
  if (!dateString) return null;
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return null;

  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function isRunningEntry(entry: StagingEntry): boolean {
  const status = (entry.status ?? "").toLowerCase();
  return status !== "failed" && status !== "success";
}

function statusDotClass(): string {
  return "bg-[#d97706] staging-pulse";
}

function isStagingSelected(selection: ViewerSelection | null, entry: StagingEntry): boolean {
  return (
    selection?.kind === "staging" &&
    selection.runId === entry.run_id &&
    selection.recordId === entry.record_id
  );
}

interface StagingItemProps {
  entry: StagingEntry;
  isSelected: boolean;
  onSelect: () => void;
}

function StagingItem({ entry, isSelected, onSelect }: StagingItemProps): JSX.Element {
  const summaryText = entry.prompt_preview || entry.title || "Untitled";
  const metadata = [
    entry.status,
    entry.model_id,
    entry.turn_count !== null ? `turn ${entry.turn_count}` : null,
    formatTimeAgo(entry.updated_at),
  ].filter((item): item is string => Boolean(item));

  return (
    <div className="px-1.5">
      <div
        className={`group flex items-start gap-2 rounded-lg border-l-2 border-[#d97706] px-2.5 py-2 transition-colors duration-100 ${
          isSelected ? "bg-[rgba(217,119,6,0.08)]" : "hover:bg-[var(--surface-1)]"
        }`}
      >
        <button
          type="button"
          onClick={onSelect}
          className="min-w-0 flex-1 rounded-sm py-0 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgba(217,119,6,0.2)]"
          title={summaryText}
        >
          <div className="flex items-start gap-1.5">
            <span className={`mt-[5px] size-[6px] shrink-0 rounded-full ${statusDotClass()}`} />
            <p
              className={`break-words text-[11px] leading-[1.45] ${
                isSelected ? "font-medium text-[var(--text-primary)]" : "text-[var(--text-secondary)]"
              }`}
            >
              {summaryText}
            </p>
          </div>

          <div className="mt-1 ml-[14px] flex flex-wrap items-center gap-x-1 gap-y-0.5 text-[9.5px] text-[var(--text-tertiary)]">
            {metadata.map((item, index) => (
              <span key={`${entry.run_id}-${item}`} className="flex items-center gap-x-1">
                {index > 0 ? <span className="text-[var(--border-strong)]">&middot;</span> : null}
                <span>{item}</span>
              </span>
            ))}
          </div>

          {!entry.has_checkpoint_urdf ? (
            <p className="mt-1 ml-[14px] text-[9.5px] text-[var(--text-quaternary)]">
              Awaiting first compile
            </p>
          ) : null}
        </button>
      </div>
    </div>
  );
}

export function StagingSection(): JSX.Element | null {
  const { bootstrap, selection } = useViewer();
  const dispatch = useViewerDispatch();

  const allEntries = bootstrap?.staging_entries ?? [];
  const entries = allEntries.filter(isRunningEntry);
  if (entries.length === 0) return null;

  return (
    <div className="border-b border-[var(--border-default)]">
      {/* Section header */}
      <div className="flex items-center justify-between bg-[rgba(217,119,6,0.04)] px-4 py-2">
        <Badge variant="warning">STAGING</Badge>
        <span className="text-[10px] tabular-nums text-[var(--text-quaternary)]">{entries.length}</span>
      </div>

      {/* Staging items */}
      <div className="space-y-0 py-0.5">
        {entries.map((entry) => (
          <StagingItem
            key={`${entry.run_id}:${entry.record_id}`}
            entry={entry}
            isSelected={isStagingSelected(selection, entry)}
            onSelect={() =>
              dispatch({
                type: "SELECT_ITEM",
                payload: { kind: "staging", runId: entry.run_id, recordId: entry.record_id },
              })
            }
          />
        ))}
      </div>
    </div>
  );
}
