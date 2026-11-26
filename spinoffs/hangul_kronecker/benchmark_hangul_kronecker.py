#!/usr/bin/env python3
"""
Elysia Spin-off #3: Hangul Jamo Kronecker Phase Wavevector Tokenizer & Robustness Benchmark.
Maps each Korean syllable -> (초성 19, 중성 21, 종성 28) -> SO(2) ⊗ SO(2) ⊗ SO(2) = 8x8 (64-D).
Zero external dependencies (stdlib math), exact Eikonal norm conservation ||v||_2 = sqrt(8).
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple


class PureHangulKroneckerTokenizer:
    """Zero-dependency 64-D Hangul Jamo Kronecker phase wavevector encoder."""

    def __init__(self) -> None:
        self.cho_angles = [2.0 * math.pi * i / 19.0 for i in range(19)]
        self.jung_angles = [2.0 * math.pi * i / 21.0 for i in range(21)]
        self.jong_angles = [2.0 * math.pi * i / 28.0 for i in range(28)]

    @staticmethod
    def decompose(char: str) -> Optional[Tuple[int, int, int]]:
        code = ord(char) - 0xAC00
        if code < 0 or code > 11171:
            return None
        cho = code // 588
        jung = (code % 588) // 28
        jong = code % 28
        return cho, jung, jong

    @staticmethod
    def _rot2(theta: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        c, s = math.cos(theta), math.sin(theta)
        return ((c, -s), (s, c))

    @staticmethod
    def _kron(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        out: List[List[float]] = []
        for row_a in A:
            for row_b in B:
                out.append([a * b for a in row_a for b in row_b])
        return out

    def encode_char(self, char: str) -> List[float]:
        jamo = self.decompose(char)
        if jamo is None:
            return [0.0] * 64
        cho, jung, jong = jamo
        m_cho = [list(r) for r in self._rot2(self.cho_angles[cho])]
        m_jung = [list(r) for r in self._rot2(self.jung_angles[jung])]
        m_jong = [list(r) for r in self._rot2(self.jong_angles[jong])]
        m8 = self._kron(self._kron(m_cho, m_jung), m_jong)
        return [val for row in m8 for val in row]

    def encode_word_mean(self, word: str) -> List[float]:
        vecs = [self.encode_char(c) for c in word if self.decompose(c) is not None]
        if not vecs:
            return [0.0] * 64
        n = float(len(vecs))
        return [sum(v[i] for v in vecs) / n for i in range(64)]


def cosine_sim(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb + 1e-12)


def main() -> int:
    tok = PureHangulKroneckerTokenizer()
    print("=================================================================")
    print("  Elysia Spin-off #3 Benchmark: Hangul Jamo Kronecker Tokenizer")
    print("=================================================================")

    # 1. Exhaustive Eikonal norm check across ALL 11,172 Hangul syllables!
    target_norm = math.sqrt(8.0)
    max_norm_err = 0.0
    for code in range(0xAC00, 0xD7A4):
        vec = tok.encode_char(chr(code))
        err = abs(math.sqrt(sum(x * x for x in vec)) - target_norm)
        if err > max_norm_err:
            max_norm_err = err
    assert max_norm_err < 1e-12
    print(f"[Eikonal Norm  ] All 11,172 Hangul syllables verified | max_err={max_norm_err:.2e} (target=sqrt(8))")

    # 2. Phonological / 1-Jamo Typo Robustness vs Unrelated Pairs
    typo_pairs = [
        ("사랑", "사량"),
        ("엘리시아", "엘리시야"),
        ("인공지능", "인공지늫"),
        ("우주공간", "우주공감"),
        ("인과법칙", "인과법칫"),
    ]
    unrelated_pairs = [
        ("사랑", "컴퓨터"),
        ("엘리시아", "벽돌집"),
        ("인공지능", "바나나"),
        ("우주공간", "젓가락"),
        ("인과법칙", "소나무"),
    ]

    typo_sims = [cosine_sim(tok.encode_word_mean(a), tok.encode_word_mean(b)) for a, b in typo_pairs]
    unrel_sims = [cosine_sim(tok.encode_word_mean(a), tok.encode_word_mean(b)) for a, b in unrelated_pairs]

    mean_typo = sum(typo_sims) / len(typo_sims)
    mean_unrel = sum(unrel_sims) / len(unrel_sims)
    margin = mean_typo - mean_unrel
    assert margin > 0.35, f"Expected strong separation margin, got {margin}"

    print(f"[Typo Robust   ] 1-Jamo Typo Mean Cosine Sim   : {mean_typo:+.4f}")
    print(f"[Unrelated Base] Unrelated Pair Mean Cosine Sim: {mean_unrel:+.4f}")
    print(f"[Separation Gap] Margin (Typo - Unrelated)     : {margin:+.4f} (Zero-Training / Zero-Vocab)")
    print("ALL Spin-off #3 CHECKS PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
