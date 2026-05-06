# 数独生成

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
python exporter.py
```

2. PDF生成

```sh
python printer.py
```

## 補足

- `generator.py` は単体の問題生成と動作確認用です
- `exporter.py` は JSON / CSV の問題データを生成します
- `printer.py` は生成済みの JSON をもとに問題集 PDF と解答集 PDF を作成します
