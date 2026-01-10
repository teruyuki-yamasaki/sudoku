# %%
import os
import csv
import json
from tqdm import tqdm
from datetime import datetime
from dataclasses import dataclass
from generator import generate_puzzle, PRESETS, EASY, MEDIUM, HARD, EXPERT

@dataclass
class Config:
    n_problems_generate: int = 60
    n_problems_printout: int = 60
    seed_start: int = 1000
    diff: str = MEDIUM
    data_dir: str = "./data/"
    output_dir: str = "./output/"

    @property
    def basename(self) -> str:
        return f"{self.diff}_seed{int(self.seed_start)}"
    
    @property
    def json_path(self) -> str:
        return os.path.join(self.data_dir, f"{self.basename}.json")
    
    @property
    def csv_path(self) -> str:
        return os.path.join(self.data_dir, f"{self.basename}.csv")
    
    @property
    def problems_pdf(self) -> str:
        return os.path.join(self.output_dir, f"{self.basename}_problems.pdf")
    
    @property
    def answers_pdf(self) -> str:
        return os.path.join(self.output_dir, f"{self.basename}_answers.pdf")

def grid_to_string(grid) -> str:
    """9x9 -> 81文字（0は .）"""
    return "".join(str(v) if v != 0 else "." for row in grid for v in row)

def save_json(records: list[dict], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def save_csv(records: list[dict], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

def generate_dataset(
    n=100,
    difficulty=MEDIUM,
    seed_start=0
) -> list[dict]:
    
    records = []
    desc = f"Generating {difficulty} problems ..."
    for i in tqdm(range(n), desc=desc):
        seed = seed_start + i
        puzzle, solution, score = generate_puzzle(
            seed=seed,difficulty=difficulty
        )
        records.append({
            "id": f"{difficulty}_{i:04d}",
            "difficulty": difficulty,
            "seed": seed,
            "score": score,
            "puzzle": grid_to_string(puzzle),
            "solution": grid_to_string(solution),
            "created_at": datetime.utcnow().isoformat()
        })

    return records

def generate_dataset_cfg(cfg: Config) -> list[dict]:
    records = generate_dataset(
        n=cfg.n_problems_generate,
        difficulty=cfg.diff,
        seed_start=cfg.seed_start,
    )
    return records

if __name__ == "__main__":
    cfg = Config()
    for diff in PRESETS.keys():
        cfg.diff = str(diff)
        records = generate_dataset_cfg(cfg)
        save_json(records, cfg.json_path)
        save_csv(records, cfg.csv_path)
        msg = f'Genaration of {diff} problems is done!' 
        msg += f"Saved in:\n - {cfg.json_path}\n - {cfg.csv_path}"
        print(msg)
    print("✔ データベース生成完了")
