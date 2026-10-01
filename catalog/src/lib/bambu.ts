/**
 * Bambu Studio on macOS registers bambustudioopen://, the link MakerWorld
 * uses. Bambu Studio downloads the URL itself, so it only works where the
 * file is reachable without a login.
 */
export function bambuStudioLink(fileUrl: string): string {
  return `bambustudioopen://${encodeURIComponent(fileUrl)}`;
}
