import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import Home from "@/app/page";

describe("Home", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows a connected status when the backend health check succeeds", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );

    const ui = await Home();
    render(ui);

    expect(screen.getByText("Connected")).toBeInTheDocument();
  });

  it("shows an unavailable status and error detail when the backend is unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("fetch failed")));

    const ui = await Home();
    render(ui);

    expect(screen.getByText("Unavailable")).toBeInTheDocument();
    expect(screen.getByText("fetch failed")).toBeInTheDocument();
  });

  it("shows an unavailable status when the backend responds with a non-ok status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({}),
      }),
    );

    const ui = await Home();
    render(ui);

    expect(screen.getByText("Unavailable")).toBeInTheDocument();
    expect(screen.getByText(/status 503/i)).toBeInTheDocument();
  });
});
