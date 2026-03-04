import { create } from "zustand";
import { apiFetch } from "@/lib/api";

export type AuthUser = {
  id: string;
  email: string;
  is_verified: boolean;
  role: string;
};

type AuthState = {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
  init: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  loading: false,
  error: null,
  initialized: false,

  init: async () => {
    const { initialized } = get();
    if (initialized) return;
    set({ loading: true, error: null });
    try {
      const me = await apiFetch<AuthUser>("/api/auth/me");
      set({ user: me });
    } catch (err: any) {
      if (err?.message === "UNAUTHENTICATED") {
        set({ user: null });
      } else {
        set({ user: null, error: "Failed to load user." });
      }
    } finally {
      set({ loading: false, initialized: true });
    }
  },

  login: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      await apiFetch("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      const me = await apiFetch<AuthUser>("/api/auth/me");
      set({ user: me });
    } catch (err: any) {
      set({
        error:
          err?.message === "UNAUTHENTICATED"
            ? "Invalid email or password."
            : "Login failed.",
      });
      throw err;
    } finally {
      set({ loading: false });
    }
  },

  register: async (email: string, password: string) => {
    set({ loading: true, error: null });
    try {
      await apiFetch("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      const me = await apiFetch<AuthUser>("/api/auth/me");
      set({ user: me });
    } catch (err: any) {
      set({
        error:
          err?.message && typeof err.message === "string"
            ? err.message
            : "Registration failed.",
      });
      throw err;
    } finally {
      set({ loading: false });
    }
  },

  logout: async () => {
    try {
      await apiFetch("/api/auth/logout", {
        method: "POST",
        body: JSON.stringify({}),
        skipAuthRefresh: true,
      });
    } catch {
      // ignore
    } finally {
      set({ user: null });
    }
  },
}));

