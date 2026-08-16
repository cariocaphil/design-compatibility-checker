import styles from "./page.module.css";
import { getInternalApiUrl } from "@/lib/env";

// The backend health check must run on every request rather than being
// baked into the build output, since backend availability can change
// independently of the frontend build/deploy.
export const dynamic = "force-dynamic";

type BackendHealth = { state: "ok" } | { state: "error"; message: string };

async function checkBackendHealth(): Promise<BackendHealth> {
  try {
    const response = await fetch(`${getInternalApiUrl()}/health`, { cache: "no-store" });

    if (!response.ok) {
      return {
        state: "error",
        message: `Backend responded with status ${response.status}.`,
      };
    }

    const data: unknown = await response.json();
    const status = (data as { status?: unknown } | null)?.status;

    if (status === "ok") {
      return { state: "ok" };
    }

    return { state: "error", message: "Backend responded with an unexpected payload." };
  } catch (error) {
    const message = error instanceof Error ? error.message : "Backend is not reachable.";
    return { state: "error", message };
  }
}

export default async function Home() {
  const backendHealth = await checkBackendHealth();
  const isHealthy = backendHealth.state === "ok";

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <p className={styles.eyebrow}>Design Compatibility Checker</p>
        <h1 className={styles.title}>Phase 1 project foundation</h1>
        <p className={styles.subtitle}>
          The screenshot and Figma analysis pipeline is not implemented yet. This page confirms that
          the frontend and backend services are wired together.
        </p>

        <div className={`${styles.statusCard} ${isHealthy ? styles.statusOk : styles.statusError}`}>
          <span className={styles.statusDot} aria-hidden="true" />
          <div>
            <p className={styles.statusLabel}>Backend status</p>
            <p className={styles.statusValue}>{isHealthy ? "Connected" : "Unavailable"}</p>
            {!isHealthy && <p className={styles.statusDetail}>{backendHealth.message}</p>}
          </div>
        </div>
      </main>
    </div>
  );
}
