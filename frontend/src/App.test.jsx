import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App.jsx";

describe("App", () => {
  beforeEach(() => {
    // fetches on mount; keep it offline for this smoke test
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new Error("offline"))));
  });

  it("renders the dashboard header", () => {
    render(<App />);
    expect(
      screen.getByRole("heading", { name: /facility-security-risk-analytics/i }),
    ).toBeInTheDocument();
  });

  it("shows an error state when the backend is unreachable", async () => {
    render(<App />);
    expect(await screen.findByText(/could not load facilities/i)).toBeInTheDocument();
  });

  it("shows the archetypes tab", () => {
    render(<App />);
    expect(screen.getByRole("button", { name: /archetypes/i })).toBeInTheDocument();
  });
});
