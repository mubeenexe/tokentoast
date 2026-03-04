const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

type ApiOptions = RequestInit & { skipAuthRefresh?: boolean };

export async function apiFetch<T>(
  path: string,
  options: ApiOptions = {},
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const { skipAuthRefresh, ...fetchOptions } = options;

  const res = await fetch(url, {
    ...fetchOptions,
    credentials: "include", // send cookies
    headers: {
      "Content-Type": "application/json",
      ...(fetchOptions.headers || {}),
    },
  });

  if (res.status === 401 && !skipAuthRefresh) {
    // Try silent refresh, then retry once.
    const refreshed = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });

    if (refreshed.ok) {
      const retry = await fetch(url, {
        ...fetchOptions,
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          ...(fetchOptions.headers || {}),
        },
      });

      if (!retry.ok) {
        throw new Error(`API error after refresh: ${retry.status}`);
      }

      return retry.json() as Promise<T>;
    }

    // Refresh failed → treat as unauthenticated.
    throw new Error("UNAUTHENTICATED");
  }

  if (!res.ok) {
    let message = `API error: ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail && typeof body.detail === "string") {
        message = body.detail;
      }
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}
