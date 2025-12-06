"""Problem generation service for review feature."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ProblemType(str, Enum):
    """Type of review problem."""

    SPEAKING = "speaking"
    LISTENING = "listening"
    PHRASE = "phrase"  # Traditional phrase review


@dataclass
class SpeakingProblem:
    """Speaking problem for review."""

    sentence: str
    phrase_highlight: tuple[int, int]  # start, end position of the target phrase


@dataclass
class ListeningProblem:
    """Listening problem for review."""

    sentence: str
    word_options: List[str]
    distractors: List[str]


# Template sentences for generating problems
# {phrase} is replaced with the review phrase
SPEAKING_TEMPLATES = [
    "I think {phrase} is important.",
    "Could you tell me about {phrase}?",
    "I'd like to practice {phrase}.",
    "Let me explain {phrase}.",
    "Have you ever tried {phrase}?",
    "I'm interested in {phrase}.",
    "What do you think about {phrase}?",
    "I need to work on {phrase}.",
    "Can you help me with {phrase}?",
    "I want to improve my {phrase}.",
]

# Common distractor words for listening problems
DISTRACTOR_WORDS = [
    "always", "never", "sometimes", "often",
    "really", "actually", "probably", "maybe",
    "good", "bad", "nice", "great",
    "should", "could", "would", "might",
    "very", "quite", "rather", "somewhat",
    "here", "there", "where", "when",
    "this", "that", "these", "those",
]


class ProblemGenerator:
    """Service for generating Speaking/Listening problems from review phrases."""

    @staticmethod
    def generate_speaking_problem(phrase: str) -> SpeakingProblem:
        """Generate a Speaking problem containing the target phrase.

        Args:
            phrase: The review phrase to include in the problem

        Returns:
            SpeakingProblem with sentence and phrase highlight position
        """
        template = random.choice(SPEAKING_TEMPLATES)
        sentence = template.format(phrase=phrase)

        # Find the position of the phrase in the sentence
        start = sentence.find(phrase)
        end = start + len(phrase) if start >= 0 else 0

        return SpeakingProblem(
            sentence=sentence,
            phrase_highlight=(start, end),
        )

    @staticmethod
    def generate_listening_problem(phrase: str) -> ListeningProblem:
        """Generate a Listening problem containing the target phrase.

        Args:
            phrase: The review phrase to include in the problem

        Returns:
            ListeningProblem with sentence, word options, and distractors
        """
        template = random.choice(SPEAKING_TEMPLATES)
        sentence = template.format(phrase=phrase)

        # Tokenize the sentence into words
        words = sentence.split()

        # Select random distractor words (2-4 words)
        num_distractors = min(random.randint(2, 4), len(DISTRACTOR_WORDS))
        distractors = random.sample(DISTRACTOR_WORDS, num_distractors)

        return ListeningProblem(
            sentence=sentence,
            word_options=words,
            distractors=distractors,
        )

    @staticmethod
    def select_problem_type() -> ProblemType:
        """Randomly select a problem type with weighted distribution.

        Distribution:
        - Speaking: 40%
        - Listening: 40%
        - Phrase (traditional): 20%
        """
        rand = random.random()
        if rand < 0.4:
            return ProblemType.SPEAKING
        elif rand < 0.8:
            return ProblemType.LISTENING
        else:
            return ProblemType.PHRASE
