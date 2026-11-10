// SPDX-License-Identifier: Apache-2.0

import { type JSX } from "react";

import { useViewer, useViewerDispatch } from "@/lib/viewer-context";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function RunSelector(): JSX.Element {
  const { bootstrap, selectedRunId } = useViewer();
  const dispatch = useViewerDispatch();

  const runs = bootstrap?.runs ?? [];

  if (runs.length === 0) {
    return (
      <p className="text-[11px] text-[#bbb]">No runs available</p>
    );
  }

  return (
    <Select
      value={selectedRunId ?? "all"}
      onValueChange={(value) =>
        dispatch({
          type: "SET_RUN_FILTER",
          payload: value === "all" ? null : value,
        })
      }
    >
      <SelectTrigger size="sm" className="h-7 w-full text-[11px]">
        <SelectValue placeholder="All runs" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">All runs</SelectItem>
        {runs.map((run) => (
          <SelectItem key={run.run_id} value={run.run_id}>
            <span className="truncate font-mono text-[11px]">{run.run_id}</span>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
