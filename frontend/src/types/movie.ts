export interface Movie {
  movie_id: number;
  title: string;
  release_year: number | null;
  genres: string[];
  keywords: string[];
  cast: string[];
  director: string[];
  overview: string;
  runtime: number | null;
  rating: number | null;
  vote_count: number;
  poster_path: string;
  backdrop_path: string;
}

export interface MovieWithScore extends Movie {
  rank_score?: number;
  content_similarity?: number;
  genre_match?: number;
  explanation?: string | null;
}

export interface ExplainResult {
  source: string;
  recommended: string;
  explanation: string;
  shared_genres: string[];
  shared_director: boolean;
  shared_cast: string[];
  shared_keywords: string[];
}
