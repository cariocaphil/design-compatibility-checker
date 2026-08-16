/**
 * Centralized environment configuration for the frontend.
 *
 * `INTERNAL_API_URL` is used for server-side requests (e.g. Server Components,
 * Route Handlers) and, inside Compose, resolves to the backend's service name
 * (see PROJECT_SPEC.md section 7). `NEXT_PUBLIC_API_URL` is used for
 * browser-side requests and resolves to a host-exposed localhost port.
 *
 * Sensible localhost defaults are provided so `pnpm dev` works without Compose.
 */

export function getInternalApiUrl(): string {
  return process.env.INTERNAL_API_URL ?? "http://localhost:8000";
}

export function getPublicApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}
