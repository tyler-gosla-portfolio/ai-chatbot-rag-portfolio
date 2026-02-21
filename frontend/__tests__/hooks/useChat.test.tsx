import { describe, expect, it } from "vitest";
import { renderHook } from "@testing-library/react";
import { useStreaming } from "../../hooks/useStreaming";

describe("useStreaming", () => {
  it("returns initial state", () => {
    const { result } = renderHook(() => useStreaming("chat-1"));
    expect(result.current.streamText).toBe("");
    expect(result.current.isStreaming).toBe(false);
  });
});
