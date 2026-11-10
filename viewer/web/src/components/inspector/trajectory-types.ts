// SPDX-License-Identifier: Apache-2.0

// Enriched trajectory types and parser — preserves fields that the inspector
// needs from both message rows and runtime trace events.

export type TraceUsage = {
  prompt_tokens?: number;
  candidates_tokens?: number;
  total_tokens?: number;
  cached_tokens?: number;
};

export type EnrichedToolCall = {
  id?: string;
  type?: string;
  function?: { name?: string; arguments?: string };
  custom?: { name?: string; input?: string };
};

export type EnrichedTraceMessage = {
  kind: "message";
  eventType: "message";
  role: string;
  content?: unknown;
  thought_summary?: string;
  tool_calls?: EnrichedToolCall[];
  usage?: TraceUsage;
  name?: string;
  tool_call_id?: string;
  tool_type?: string;
  timestamp?: number;
};

export type EnrichedCompactionEvent = {
  kind: "compaction";
  eventType: string;
  trigger?: string;
  modelId?: string;
  usage?: TraceUsage;
  beforeNextInputTokens?: number | null;
  afterNextInputTokens?: number | null;
  estimatedSavedNextInputTokens?: number | null;
  beforeItemCount?: number | null;
  afterItemCount?: number | null;
  previousResponseIdCleared?: boolean;
  estimateError?: string;
  billedCostUsd?: number | null;
  timestamp?: number;
  raw: Record<string, unknown>;
};

export type EnrichedGenericTraceEvent = {
  kind: "event";
  eventType: string;
  title: string;
  usage?: TraceUsage;
  timestamp?: number;
  raw: Record<string, unknown>;
};

export type EnrichedTraceEvent =
  | EnrichedTraceMessage
  | EnrichedCompactionEvent
  | EnrichedGenericTraceEvent;

export type EnrichedTraceTurn = {
  index: number;
  cost: Record<string, unknown> | null;
  events: EnrichedTraceEvent[];
  timestamp: number | null;
};

// ---------------------------------------------------------------------------
// Shared utilities
// ---------------------------------------------------------------------------

export function asRecord(value: unknown): Record<string, unknown> | null {
  return typeof value === "object" && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

export function asNumber(value: unknown): number | null {
  return typeof value === "number" ? value : null;
}

export function asString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

export function formatUsd(value: unknown): string {
  const number = asNumber(value);
  return number == null ? "--" : `$${number.toFixed(4)}`;
}

export function formatCount(value: unknown): string {
  const number = asNumber(value);
  return number == null ? "--" : number.toLocaleString();
}

export function excerpt(text: string, max = 220): string {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (normalized.length <= max) return normalized;
  return `${normalized.slice(0, max - 1)}...`;
}

export function messageText(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (typeof item === "string") return item;
        const record = asRecord(item);
        if (!record) return "";
        if (typeof record.text === "string") return record.text;
        return "";
      })
      .filter(Boolean)
      .join("\n");
  }
  if (content == null) return "";
  try {
    return JSON.stringify(content);
  } catch {
    return String(content);
  }
}

export function fullMessageText(content: unknown): string {
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    const parts = content
      .map((item) => {
        if (typeof item === "string") return item;
        const record = asRecord(item);
        if (!record) return null;
        if (typeof record.text === "string") return record.text;
        try {
          return JSON.stringify(record, null, 2);
        } catch {
          return String(record);
        }
      })
      .filter((value): value is string => Boolean(value));
    return parts.join("\n\n");
  }
  if (content == null) return "";
  if (typeof content === "object") {
    try {
      return JSON.stringify(content, null, 2);
    } catch {
      return String(content);
    }
  }
  return String(content);
}

export function overallTraceTotals(cost: Record<string, unknown> | null): Record<string, unknown> | null {
  return asRecord(cost?.all_in_total) ?? asRecord(cost?.total);
}

function asUsage(value: unknown): TraceUsage | undefined {
  const record = asRecord(value);
  if (!record) return undefined;
  return {
    prompt_tokens: asNumber(record.prompt_tokens) ?? undefined,
    candidates_tokens: asNumber(record.candidates_tokens) ?? undefined,
    total_tokens: asNumber(record.total_tokens) ?? undefined,
    cached_tokens: asNumber(record.cached_tokens) ?? undefined,
  };
}

function titleCaseEventType(eventType: string): string {
  return eventType
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function turnHasAssistant(turn: EnrichedTraceTurn): boolean {
  return turn.events.some((event) => event.kind === "message" && event.role === "assistant");
}

function ensurePendingTurn(
  turns: EnrichedTraceTurn[],
  costTurns: unknown[],
): EnrichedTraceTurn {
  const lastTurn = turns[turns.length - 1];
  if (lastTurn && !turnHasAssistant(lastTurn)) {
    return lastTurn;
  }
  const nextTurn: EnrichedTraceTurn = {
    index: turns.length + 1,
    cost: asRecord(costTurns[turns.length]),
    events: [],
    timestamp: null,
  };
  turns.push(nextTurn);
  return nextTurn;
}

function compactionMaintenanceEvents(cost: Record<string, unknown> | null): Record<string, unknown>[] {
  if (!Array.isArray(cost?.maintenance_events)) return [];
  return cost.maintenance_events
    .map((event) => asRecord(event))
    .filter((event): event is Record<string, unknown> => event !== null)
    .filter((event) => {
      const kind = asString(event.kind) ?? asString(event.type);
      return kind === "compaction";
    });
}

function isMatchingCompactionEvent(
  traceEntry: Record<string, unknown>,
  maintenanceEvent: Record<string, unknown>,
): boolean {
  const traceTurn = asNumber(traceEntry.turn_before_request);
  const maintenanceTurn = asNumber(maintenanceEvent.turn_before_request);
  if (traceTurn != null && maintenanceTurn != null && traceTurn !== maintenanceTurn) {
    return false;
  }

  const traceTrigger = asString(traceEntry.trigger);
  const maintenanceTrigger = asString(maintenanceEvent.trigger);
  if (traceTrigger && maintenanceTrigger && traceTrigger !== maintenanceTrigger) {
    return false;
  }

  return true;
}

function takeCompactionMaintenanceEvent(
  traceEntry: Record<string, unknown>,
  maintenanceEvents: Record<string, unknown>[],
  startIndex: number,
): { event: Record<string, unknown> | null; nextIndex: number } {
  for (let index = startIndex; index < maintenanceEvents.length; index += 1) {
    const candidate = maintenanceEvents[index];
    if (isMatchingCompactionEvent(traceEntry, candidate)) {
      return { event: candidate, nextIndex: index + 1 };
    }
  }
  if (startIndex < maintenanceEvents.length) {
    return { event: maintenanceEvents[startIndex], nextIndex: startIndex + 1 };
  }
  return { event: null, nextIndex: startIndex };
}

function parseNonMessageEvent(
  entry: Record<string, unknown>,
  maintenanceEvent: Record<string, unknown> | null,
  timestamp: number | null,
): EnrichedTraceEvent {
  const eventType = asString(entry.type) ?? "event";
  const usage = asUsage(entry.usage) ?? asUsage(maintenanceEvent?.tokens);

  if (eventType === "compaction") {
    const billedCosts = asRecord(maintenanceEvent?.costs_usd);
    return {
      kind: "compaction",
      eventType,
      trigger: asString(entry.trigger) ?? undefined,
      modelId: asString(entry.model_id) ?? undefined,
      usage,
      beforeNextInputTokens: asNumber(entry.before_next_input_tokens),
      afterNextInputTokens: asNumber(entry.after_next_input_tokens),
      estimatedSavedNextInputTokens: asNumber(entry.estimated_saved_next_input_tokens),
      beforeItemCount: asNumber(entry.before_item_count),
      afterItemCount: asNumber(entry.after_item_count),
      previousResponseIdCleared:
        typeof entry.previous_response_id_cleared === "boolean"
          ? entry.previous_response_id_cleared
          : undefined,
      estimateError: asString(entry.estimate_error) ?? undefined,
      billedCostUsd: asNumber(billedCosts?.total),
      timestamp: timestamp ?? undefined,
      raw: entry,
    };
  }

  return {
    kind: "event",
    eventType,
    title: titleCaseEventType(eventType),
    usage,
    timestamp: timestamp ?? undefined,
    raw: entry,
  };
}

// ---------------------------------------------------------------------------
// Enriched parser
// ---------------------------------------------------------------------------

export function parseEnrichedTurns(
  traceText: string | null,
  cost: Record<string, unknown> | null,
): EnrichedTraceTurn[] {
  const costTurns = Array.isArray(cost?.turns) ? cost.turns : [];

  if (!traceText) {
    return costTurns.map((turn, index) => ({
      index: index + 1,
      cost: asRecord(turn),
      events: [],
      timestamp: null,
    }));
  }

  const entries = traceText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line) as Record<string, unknown>;
      } catch {
        return null;
      }
    })
    .filter((entry): entry is Record<string, unknown> => entry !== null);

  const turns: EnrichedTraceTurn[] = [];
  const maintenanceEvents = compactionMaintenanceEvents(cost);
  let compactionMaintenanceIndex = 0;

  for (const entry of entries) {
    const timestamp = asNumber(entry.ts);
    const message = asRecord(entry.message);
    const role = asString(message?.role);

    if (message && role) {
      const traceMessage: EnrichedTraceMessage = {
        kind: "message",
        eventType: "message",
        role,
        content: message.content,
        thought_summary: asString(message.thought_summary) ?? undefined,
        tool_calls: Array.isArray(message.tool_calls)
          ? (message.tool_calls as EnrichedToolCall[])
          : undefined,
        usage: asUsage(message.usage),
        name: asString(message.name) ?? undefined,
        tool_call_id: asString(message.tool_call_id) ?? undefined,
        tool_type: asString(message.tool_type) ?? undefined,
        timestamp: timestamp ?? undefined,
      };

      if (role === "assistant") {
        const pendingTurn = turns[turns.length - 1];
        if (pendingTurn && !turnHasAssistant(pendingTurn)) {
          pendingTurn.events.push(traceMessage);
          if (pendingTurn.timestamp == null) {
            pendingTurn.timestamp = timestamp;
          }
          continue;
        }

        turns.push({
          index: turns.length + 1,
          cost: asRecord(costTurns[turns.length]),
          events: [traceMessage],
          timestamp,
        });
        continue;
      }

      if (turns.length === 0) continue;
      turns[turns.length - 1].events.push(traceMessage);
      continue;
    }

    const eventType = asString(entry.type);
    if (!eventType || eventType === "message") {
      continue;
    }

    let maintenanceEvent: Record<string, unknown> | null = null;
    if (eventType === "compaction") {
      const match = takeCompactionMaintenanceEvent(
        entry,
        maintenanceEvents,
        compactionMaintenanceIndex,
      );
      maintenanceEvent = match.event;
      compactionMaintenanceIndex = match.nextIndex;
    }

    const turn = ensurePendingTurn(turns, costTurns);
    turn.events.push(parseNonMessageEvent(entry, maintenanceEvent, timestamp));
    if (turn.timestamp == null) {
      turn.timestamp = timestamp;
    }
  }

  if (turns.length === 0) {
    return costTurns.map((turn, index) => ({
      index: index + 1,
      cost: asRecord(turn),
      events: [],
      timestamp: null,
    }));
  }

  return turns;
}
