from __future__ import annotations
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

Grid = List[List[int]]  # 9x9, 0 = empty

# ---------------------------
# 基本ユーティリティ
# ---------------------------
def deep_copy(g: Grid) -> Grid:
    return [row[:] for row in g]

def box_index(r: int, c: int) -> int:
    return (r // 3) * 3 + (c // 3)

def candidates(g: Grid, r: int, c: int) -> List[int]:
    if g[r][c] != 0:
        return []
    used = set(g[r])  # row
    used |= {g[i][c] for i in range(9)}  # col
    br, bc = (r // 3) * 3, (c // 3) * 3
    used |= {g[i][j] for i in range(br, br + 3) for j in range(bc, bc + 3)}  # box
    return [v for v in range(1, 10) if v not in used]

def find_mrv_cell(g: Grid) -> Optional[Tuple[int, int, List[int]]]:
    """MRV (minimum remaining values): 候補が最少のマスを選ぶ"""
    best = None
    best_cands = None
    for r in range(9):
        for c in range(9):
            if g[r][c] == 0:
                cs = candidates(g, r, c)
                if not cs:
                    return (r, c, [])  # dead end
                if best is None or len(cs) < len(best_cands):
                    best = (r, c)
                    best_cands = cs
                    if len(best_cands) == 1:
                        return (r, c, best_cands)
    if best is None:
        return None
    return (best[0], best[1], best_cands)


# ---------------------------
# 解く（1解 / 一意性 / 難易度指標）
# ---------------------------
@dataclass
class SolveStats:
    nodes: int = 0          # 探索ノード数（難易度指標）
    backtracks: int = 0     # バックトラック回数

def solve_one(g: Grid, rng: random.Random, stats: Optional[SolveStats] = None) -> Optional[Grid]:
    """ランダム順で1解を探す。見つかれば解を返す。"""
    cell = find_mrv_cell(g)
    if cell is None:
        return deep_copy(g)  # solved
    r, c, cs = cell
    if not cs:
        return None
    if stats:
        stats.nodes += 1
    rng.shuffle(cs)
    for v in cs:
        g[r][c] = v
        sol = solve_one(g, rng, stats)
        if sol is not None:
            g[r][c] = 0
            return sol
        if stats:
            stats.backtracks += 1
        g[r][c] = 0
    return None

def count_solutions(g: Grid, limit: int = 2) -> int:
    """解の個数を数える（limit で打ち切り）。一意性チェック用。"""
    cnt = 0

    def dfs() -> None:
        nonlocal cnt
        if cnt >= limit:
            return
        cell = find_mrv_cell(g)
        if cell is None:
            cnt += 1
            return
        r, c, cs = cell
        if not cs:
            return
        # 候補は固定順でも良い（ここは一意性確認なのでランダム不要）
        for v in cs:
            g[r][c] = v
            dfs()
            g[r][c] = 0
            if cnt >= limit:
                return

    dfs()
    return cnt

def difficulty_score(g: Grid, seed: int = 0, trials: int = 1) -> int:
    """
    難易度の簡易スコア：ソルバの探索ノード数（小さいほど易しい）。
    trials > 1 でランダム順のブレを平均化。
    """
    total = 0
    for t in range(trials):
        rng = random.Random(seed + t)
        gg = deep_copy(g)
        st = SolveStats()
        sol = solve_one(gg, rng, st)
        if sol is None:
            # 解けない（矛盾）なら極大
            return 10**9
        total += st.nodes
    return total // trials


# ---------------------------
# 完成盤（解）生成
# ---------------------------
def generate_full_solution(seed: int = 0) -> Grid:
    rng = random.Random(seed)
    g = [[0]*9 for _ in range(9)]
    sol = solve_one(g, rng)
    if sol is None:
        raise RuntimeError("Failed to generate a full solution.")
    return sol


# ---------------------------
# 問題生成（削る・一意性維持・難易度調整）
# ---------------------------
@dataclass
class DifficultyPreset:
    # 探索ノード数の目標帯（目安）。環境・乱数でぶれます。
    min_nodes: int
    max_nodes: int
    # 最小ヒント数の下限（作りすぎてスカスカになりすぎるのを防止）
    min_clues: int = 24
    # 削りの試行回数（大きいほど狙った難易度に寄せやすいが生成が重い）
    removal_attempts: int = 2000
    # 対称性（Trueなら中心対称に削る）
    symmetry: bool = True

TUTORIAL = "tutorial"
EASY = "easy"
MEDIUM = "medium"
HARD = "hard"
EXPERT = "expert"

PRESETS: Dict[str, DifficultyPreset] = {
    TUTORIAL: DifficultyPreset(min_nodes=0,  max_nodes=20,   min_clues=45, removal_attempts=200,  symmetry=True),
    EASY:   DifficultyPreset(min_nodes=0,    max_nodes=200,  min_clues=34, removal_attempts=1200, symmetry=True),
    MEDIUM: DifficultyPreset(min_nodes=200,  max_nodes=800,  min_clues=30, removal_attempts=1800, symmetry=True),
    HARD:   DifficultyPreset(min_nodes=800,  max_nodes=3000, min_clues=26, removal_attempts=2600, symmetry=True),
    EXPERT: DifficultyPreset(min_nodes=3000, max_nodes=12000,min_clues=24, removal_attempts=4000, symmetry=False),
}

def generate_puzzle(
    seed: int = 0,
    difficulty: str = MEDIUM,
    *,
    target_nodes: Optional[Tuple[int, int]] = None,
    min_clues: Optional[int] = None,
    symmetry: Optional[bool] = None,
    removal_attempts: Optional[int] = None,
    score_trials: int = 1,
) -> Tuple[Grid, Grid, int]:
    """
    returns: (puzzle, solution, score_nodes)
    - difficulty: easy/medium/hard/expert
    - target_nodes: (min,max) を直接指定したい場合
    - score_trials: 難易度評価のブレ低減（1で高速、3以上で安定）
    """
    if difficulty not in PRESETS and target_nodes is None:
        raise ValueError(f"Unknown difficulty '{difficulty}'. Choose from {list(PRESETS)} or pass target_nodes.")
    preset = PRESETS.get(difficulty, DifficultyPreset(0, 10**9))

    if target_nodes is None:
        target_nodes = (preset.min_nodes, preset.max_nodes)
    if min_clues is None:
        min_clues = preset.min_clues
    if symmetry is None:
        symmetry = preset.symmetry
    if removal_attempts is None:
        removal_attempts = preset.removal_attempts

    rng = random.Random(seed)

    # 1) 完成盤
    solution = generate_full_solution(seed=seed)

    # 2) 削って問題化（ベストを保持）
    puzzle = deep_copy(solution)
    positions = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(positions)

    best_puzzle = deep_copy(puzzle)
    best_score = difficulty_score(best_puzzle, seed=seed+999, trials=score_trials)

    def clue_count(g: Grid) -> int:
        return sum(1 for r in range(9) for c in range(9) if g[r][c] != 0)

    # removal loop
    attempts = 0
    while attempts < removal_attempts:
        attempts += 1
        # ランダムに1マス選ぶ
        r, c = rng.choice(positions)
        if puzzle[r][c] == 0:
            continue

        # 対称削りの場合、ペアも対象
        r2, c2 = (8 - r, 8 - c) if symmetry else (r, c)
        backup1, backup2 = puzzle[r][c], puzzle[r2][c2]
        puzzle[r][c] = 0
        puzzle[r2][c2] = 0

        # ヒント数下限
        if clue_count(puzzle) < min_clues:
            puzzle[r][c], puzzle[r2][c2] = backup1, backup2
            continue

        # 一意性チェック
        tmp = deep_copy(puzzle)
        if count_solutions(tmp, limit=2) != 1:
            puzzle[r][c], puzzle[r2][c2] = backup1, backup2
            continue

        # 難易度評価
        sc = difficulty_score(puzzle, seed=seed+1234, trials=score_trials)
        lo, hi = target_nodes

        # 目標帯に入っていれば、さらに削り続けつつベスト更新
        # 目標帯外でも、目標に近いならベストとして保持する
        def dist_to_band(x: int) -> int:
            if x < lo:
                return lo - x
            if x > hi:
                return x - hi
            return 0

        if dist_to_band(sc) <= dist_to_band(best_score):
            best_puzzle = deep_copy(puzzle)
            best_score = sc

        # 既に帯の中で、なおかつヒントを減らせているなら継続
        # 帯を大きく外れた（難しすぎ/易しすぎ）なら「戻す」こともあり得るが、
        # シンプルに「ベスト保持」で最後に返す方が堅牢。
        # ここではそのまま進める。

    return best_puzzle, solution, best_score


# ---------------------------
# 表示
# ---------------------------
def print_grid(g: Grid) -> None:
    for r in range(9):
        row = []
        for c in range(9):
            v = g[r][c]
            row.append(str(v) if v else ".")
            if c in (2, 5):
                row.append("|")
        print(" ".join(row))
        if r in (2, 5):
            print("-" * 21)


if __name__ == "__main__":
    puzzle, solution, score = generate_puzzle(
        seed=42,
        difficulty=HARD,
        score_trials=1,   # 3にすると難易度評価が安定（遅くなる）
        symmetry=True
    )
    print("Puzzle (score nodes =", score, ")")
    print_grid(puzzle)
    print("\nSolution")
    print_grid(solution)
