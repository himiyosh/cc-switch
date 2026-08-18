import { getVersion } from "@tauri-apps/api/app";

// Fork: updates are taken by merging upstream and rebuilding, never over the
// wire. Upstream's signed releases would verify against the bundled pubkey and
// replace this build, silently dropping the local Codex fixes, so the updater
// endpoints are gone from tauri.conf.json and every check short-circuits to
// "up to date" before touching the plugin.
const OTA_UPDATES_DISABLED = true;

export type UpdateChannel = "stable" | "beta";

export interface UpdateInfo {
  currentVersion: string;
  availableVersion: string;
  notes?: string;
  pubDate?: string;
}

export interface CheckOptions {
  timeout?: number;
  channel?: UpdateChannel;
}

export async function getCurrentVersion(): Promise<string> {
  try {
    return await getVersion();
  } catch {
    return "";
  }
}

export async function checkForUpdate(
  opts: CheckOptions = {},
): Promise<
  { status: "up-to-date" } | { status: "available"; info: UpdateInfo }
> {
  if (OTA_UPDATES_DISABLED) {
    return { status: "up-to-date" };
  }

  // 动态引入，避免在未安装插件时导致打包期问题
  const { check } = await import("@tauri-apps/plugin-updater");

  const currentVersion = await getCurrentVersion();
  const update = await check({ timeout: opts.timeout ?? 30000 } as any);

  if (!update) {
    return { status: "up-to-date" };
  }

  const info: UpdateInfo = {
    currentVersion,
    availableVersion: (update as any).version ?? "",
    notes: (update as any).notes,
    pubDate: (update as any).date,
  };

  return { status: "available", info };
}
