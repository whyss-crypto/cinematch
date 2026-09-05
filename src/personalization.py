"""Session-level user profile and feedback state.

A thin, serializable wrapper over four lists. Designed so a real database
or auth layer can later replace persistence without touching the
recommendation logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserProfile:
    """Per-session preference state (no auth needed for the MVP)."""

    liked: List[str] = field(default_factory=list)
    disliked: List[str] = field(default_factory=list)
    recently_viewed: List[str] = field(default_factory=list)

    # ----- likes
    def like(self, title: str) -> None:
        self.remove_dislike(title)
        if title not in self.liked:
            self.liked.append(title)

    def unlike(self, title: str) -> None:
        if title in self.liked:
            self.liked.remove(title)

    # ----- dislikes
    def dislike(self, title: str) -> None:
        self.unlike(title)
        if title not in self.disliked:
            self.disliked.append(title)

    def remove_dislike(self, title: str) -> None:
        if title in self.disliked:
            self.disliked.remove(title)

    # ----- history
    def view(self, title: str, history_limit: int = 12) -> None:
        if title in self.recently_viewed:
            self.recently_viewed.remove(title)
        self.recently_viewed.insert(0, title)
        del self.recently_viewed[history_limit:]

    # ----- derived
    def preferred_genres(self, movie_genres: Optional[dict] = None) -> List[str]:
        """Genres of liked movies ordered by frequency.

        ``movie_genres`` maps title -> genre list (from the catalog); used
        by the UI to render the preference summary.
        """
        if not movie_genres:
            return []
        counts: dict = {}
        for title in self.liked:
            for genre in movie_genres.get(title, []):
                counts[genre] = counts.get(genre, 0) + 1
        return [g for g, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]

    @property
    def is_new_user(self) -> bool:
        return len(self.liked) == 0

    def to_dict(self) -> dict:
        return {
            "liked": list(self.liked),
            "disliked": list(self.disliked),
            "recently_viewed": list(self.recently_viewed),
        }

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "UserProfile":
        data = data or {}
        return cls(
            liked=list(data.get("liked") or []),
            disliked=list(data.get("disliked") or []),
            recently_viewed=list(data.get("recently_viewed") or []),
        )
