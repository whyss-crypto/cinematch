import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type TasteState = {
  liked: string[];
  disliked: string[];
  viewed: string[];
  like: (title: string) => void;
  unlike: (title: string) => void;
  dislike: (title: string) => void;
  undislike: (title: string) => void;
  view: (title: string) => void;
  clear: () => void;
};

const TasteCtx = createContext<TasteState | null>(null);

const KEY = "cinematch:taste:v2";

function load(): Pick<TasteState, "liked" | "disliked" | "viewed"> {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { liked: [], disliked: [], viewed: [] };
}

export function TasteProvider({ children }: { children: ReactNode }) {
  const [liked, setLiked] = useState<string[]>(() => load().liked);
  const [disliked, setDisliked] = useState<string[]>(() => load().disliked);
  const [viewed, setViewed] = useState<string[]>(() => load().viewed);

  useEffect(() => {
    localStorage.setItem(KEY, JSON.stringify({ liked, disliked, viewed }));
  }, [liked, disliked, viewed]);

  const like = (t: string) => {
    setDisliked((d) => d.filter((x) => x !== t));
    setLiked((l) => (l.includes(t) ? l : [...l, t]));
  };
  const unlike = (t: string) => setLiked((l) => l.filter((x) => x !== t));
  const dislike = (t: string) => {
    setLiked((l) => l.filter((x) => x !== t));
    setDisliked((d) => (d.includes(t) ? d : [...d, t]));
  };
  const undislike = (t: string) => setDisliked((d) => d.filter((x) => x !== t));
  const view = (t: string) =>
    setViewed((v) => [t, ...v.filter((x) => x !== t)].slice(0, 12));
  const clear = () => {
    setLiked([]);
    setDisliked([]);
    setViewed([]);
  };

  return (
    <TasteCtx.Provider value={{ liked, disliked, viewed, like, unlike, dislike, undislike, view, clear }}>
      {children}
    </TasteCtx.Provider>
  );
}

export function useTaste() {
  const ctx = useContext(TasteCtx);
  if (!ctx) throw new Error("useTaste outside provider");
  return ctx;
}
