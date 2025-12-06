"""Word matching service for Speaking evaluation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class WordMatch:
    """Result of word matching for a single word."""

    word: str
    matched: bool
    position: int


@dataclass
class SpeakingEvaluationResult:
    """Result of Speaking evaluation with partial matching."""

    word_matches: List[WordMatch]
    score: float  # 0.0 - 100.0
    matched_count: int
    total_count: int


def normalize_word(word: str) -> str:
    """Normalize a word for comparison.

    - Remove punctuation
    - Convert to lowercase
    - Strip whitespace
    """
    # Remove punctuation except apostrophes within words
    cleaned = re.sub(r"[^\w\s']", "", word)
    # Remove leading/trailing apostrophes
    cleaned = cleaned.strip("'")
    return cleaned.lower().strip()


def tokenize_text(text: str) -> List[str]:
    """Tokenize text into words, preserving original form."""
    # Split by whitespace
    words = text.split()
    # Filter empty strings
    return [w for w in words if w.strip()]


class WordMatcher:
    """Service for matching words between expected text and user transcript."""

    @staticmethod
    def evaluate_speaking(
        expected_text: str,
        user_transcript: str,
    ) -> SpeakingEvaluationResult:
        """Evaluate speaking by comparing expected text with user transcript.

        Uses partial matching to compare words at each position.

        Args:
            expected_text: The expected/correct text
            user_transcript: The user's spoken text (from STT)

        Returns:
            SpeakingEvaluationResult with word-level matching info and score
        """
        expected_words = tokenize_text(expected_text)
        user_words = tokenize_text(user_transcript)

        if not expected_words:
            return SpeakingEvaluationResult(
                word_matches=[],
                score=0.0,
                matched_count=0,
                total_count=0,
            )

        # Normalize words for comparison
        normalized_expected = [normalize_word(w) for w in expected_words]
        normalized_user = [normalize_word(w) for w in user_words]

        # Create a set of user words for lookup
        user_word_set = set(normalized_user)

        # Match each expected word
        word_matches: List[WordMatch] = []
        matched_count = 0

        for i, (orig_word, norm_word) in enumerate(
            zip(expected_words, normalized_expected)
        ):
            # Check if the normalized word exists in user's words
            matched = norm_word in user_word_set and norm_word != ""
            if matched:
                matched_count += 1

            word_matches.append(
                WordMatch(
                    word=orig_word,
                    matched=matched,
                    position=i,
                )
            )

        # Calculate score
        total_count = len(expected_words)
        score = (matched_count / total_count * 100) if total_count > 0 else 0.0

        return SpeakingEvaluationResult(
            word_matches=word_matches,
            score=round(score, 1),
            matched_count=matched_count,
            total_count=total_count,
        )

    @staticmethod
    def evaluate_listening(
        expected_text: str,
        user_answer: str,
    ) -> tuple[bool, str]:
        """Evaluate listening by comparing expected text with user's answer.

        Uses exact matching (normalized).

        Args:
            expected_text: The expected/correct text
            user_answer: The user's constructed answer

        Returns:
            Tuple of (is_correct, expected_text)
        """
        # Normalize both for comparison
        expected_normalized = " ".join(
            normalize_word(w) for w in tokenize_text(expected_text)
        )
        user_normalized = " ".join(
            normalize_word(w) for w in tokenize_text(user_answer)
        )

        is_correct = expected_normalized == user_normalized
        return is_correct, expected_text
