export function isPosterValid(poster_path: string | null | undefined): boolean {
  return Boolean(poster_path && poster_path.startsWith("http"));
}

export function getPosterUrl(poster_path: string | null | undefined): string {
  return isPosterValid(poster_path) ? (poster_path as string) : "";
}
