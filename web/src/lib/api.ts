import { handleDemo } from "./demo";

const BFF = "/api/backend";

function demoFallback<T>(path: string, method: string, rawBody?: string): T | null {
  const joined = path.replace(/^\//, "");
  let body: Record<string, unknown> = {};
  if (rawBody) {
    try {
      body = JSON.parse(rawBody) as Record<string, unknown>;
    } catch {
      body = {};
    }
  }
  return handleDemo(joined, method, body) as T | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const rawBody = typeof init?.body === "string" ? init.body : undefined;

  try {
    const res = await fetch(`${BFF}${path}`, {
      ...init,
      headers: {
        "content-type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });
    if (res.ok) {
      return (await res.json()) as T;
    }
    const text = await res.text();
    const fallback = demoFallback<T>(path, method, rawBody);
    if (fallback !== null) return fallback;
    throw new Error(text || `Request failed: ${res.status}`);
  } catch (err) {
    const fallback = demoFallback<T>(path, method, rawBody);
    if (fallback !== null) return fallback;
    throw err instanceof Error ? err : new Error("Request failed");
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
};
