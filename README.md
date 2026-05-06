# 数独生成

## フォルダ構成

```text
.
├─ scripts/
│  ├─ export_dataset.py
│  ├─ generate_sample.py
│  └─ render_pdfs.py
├─ sudoku/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ dataset.py
│  ├─ pdf.py
│  ├─ puzzle.py
│  └─ solver.py
├─ requirements.txt
├─ setup_venv.bat
└─ activate_venv.bat
```

- `sudoku/solver.py`: 盤面操作とソルバー
- `sudoku/puzzle.py`: 難易度定義と問題生成
- `sudoku/dataset.py`: JSON / CSV 用データ生成
- `sudoku/pdf.py`: PDF レイアウトと描画
- `sudoku/config.py`: 入出力設定
- `scripts/`: 人が直接実行する入口をまとめた場所です

## 環境構築

```sh
$ setup_venv.bat
```

```sh
$ activate_venv.bat
```

```sh
(sdk)$ pip install -r requirements.txt
```

## 使用方法

1. 問題データ生成

```sh
python scripts/export_dataset.py
```

2. PDF生成

```sh
python scripts/render_pdfs.py
```

## 補足

- `scripts/generate_sample.py` は単体の問題生成と動作確認用です
- `scripts/export_dataset.py` は JSON / CSV の問題データを生成します
- `scripts/render_pdfs.py` は生成済みの JSON をもとに問題集 PDF と解答集 PDF を作成します
- 実装本体は `sudoku/` パッケージ配下に分離してあります
