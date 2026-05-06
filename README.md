# 数独生成ツール

数独の問題データ生成、JSON / CSV 出力、問題集 PDF / 解答集 PDF 生成、PySide6 ベースの GUI 操作に対応したローカル向けツールです。

## できること

- 数独の問題と解答を難易度別に生成
- JSON / CSV 形式で保存
- 問題集 PDF と解答集 PDF を生成
- GUI から保存先、難易度、シード、件数を指定して実行
- GUI の `PDF設定` タブからページサイズや配置を調整
- GUI の `PDF設定` タブで簡易プレビュー確認
- GUI の `PDF設定` タブで設定の保存 / 復元

## フォルダ構成

```text
.
├─ gui/
│  ├─ app.py
│  ├─ main_window.py
│  ├─ models.py
│  ├─ workers.py
│  └─ tabs/
│     ├─ generation_tab.py
│     ├─ log_tab.py
│     └─ pdf_settings_tab.py
├─ scripts/
│  ├─ export_dataset.py
│  ├─ generate_sample.py
│  ├─ launch_gui.py
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

## 主な役割

- `sudoku/solver.py`: 盤面操作とソルバー
- `sudoku/puzzle.py`: 難易度定義と問題生成
- `sudoku/dataset.py`: JSON / CSV 用データ生成
- `sudoku/pdf.py`: PDF レイアウトと描画
- `sudoku/config.py`: 入出力設定
- `gui/`: PySide6 ベースのデスクトップ GUI
- `scripts/`: 人が直接実行する入口

## 環境構築

```sh
setup_venv.bat
activate_venv.bat
pip install -r requirements.txt
```

## 使い方

### GUI を使う

```sh
python scripts/launch_gui.py
```

GUI では次の操作ができます。

- 保存先フォルダの選択
- 難易度、シード開始値、生成件数、PDF 出力件数の指定
- JSON / CSV、問題 PDF、解答 PDF の出力有無の切り替え
- `PDF設定` タブでページサイズ、配置方式、行数、列数、余白、間隔、タイトル表示の調整

### スクリプトで使う

問題データ生成:

```sh
python scripts/export_dataset.py
```

PDF 生成:

```sh
python scripts/render_pdfs.py
```

単体の動作確認:

```sh
python scripts/generate_sample.py
```

## 保存先

- GUI の既定保存先は `デスクトップ/sudoku_data`
- 生成データは `デスクトップ/sudoku_data/data`
- PDF は `デスクトップ/sudoku_data/output`

## PDF 設定タブ

`PDF設定` タブでは次の内容を調整できます。

- ページサイズ: `A5`, `A4`
- 配置方式: `中央配置`, `最大化配置`
- 1ページあたりの行数と列数
- 横間隔、縦間隔
- 左右余白、上下余白
- タイトル表示の有無
- タイトル文字サイズ

また、次の補助機能があります。

- 現在のレイアウトの簡易プレビュー
- 設定の保存
- 保存済み設定の復元
- 初期値へのリセット

## 補足

- GUI の実行には `PySide6` が必要です
- PDF 生成には `reportlab` が必要です
- 実装本体は `sudoku/` パッケージ配下に分離されています
