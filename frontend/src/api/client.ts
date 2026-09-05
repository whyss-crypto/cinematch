import type { Movie, MovieWithScore, ExplainResult } from "../types/movie";

const BASE = "";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const api = {
  health: () => get<{ status: string; movies: number; genres: number }>("/api/health"),
  genres: () => get<string[]>("/api/genres"),
  movies: (params: { limit?: number; offset?: number; sort?: string } = {}) => {
    const qs = new URLSearchParams();
    if (params.limit) qs.set("limit", String(params.limit));
    if (params.offset) qs.set("offset", String(params.offset));
    if (params.sort) qs.set("sort", params.sort);
    return get<Movie[]>(`/api/movies?${qs}`);
  },
  popular: (n = 12) => get<Movie[]>(`/api/movies?limit=${n}&sort=popular`),
  trending: (n = 12) => get<Movie[]>(`/api/movies?limit=${n}&sort=trending`),
  byId: (id: number) => get<Movie>(`/api/movies/by-id/${id}`),
  byTitle: (title: string) => get<Movie>(`/api/movies/by-title/${encodeURIComponent(title)}`),
  search: (q: string, n = 18) =>
    get<{ query: string; count: number; results: Movie[] }>(
      `/api/movies/search?q=${encodeURIComponent(q)}&n=${n}`
    ),
  suggest: (q: string, n = 8) =>
    get<string[]>(`/api/movies/suggest?q=${encodeURIComponent(q)}&n=${n}`),

  similar: (payload: { movie_title?: string; movie_id?: number; n?: number }) =>
    post<{ count: number; results: MovieWithScore[] }>("/api/recommend/similar", payload),

  byGenre: (genres: string[], n = 12) =>
    post<{ count: number; results: MovieWithScore[] }>("/api/recommend/by-genre", { genres, n }),

  forUser: (liked: string[], disliked: string[] = [], n = 12) =>
    post<{ count: number; results: MovieWithScore[] }>("/api/recommend/for-user", {
      liked_movies: liked,
      disliked_movies: disliked,
      n,
    }),

  explain: (source: string, recommended: string) =>
    post<ExplainResult>("/api/explain", {
      source_movie: source,
      recommended_movie: recommended,
    }),

  stats: () =>
    get<{ movies: number; genres: string[]; year_range: [number, number] }>("/api/stats"),
};
