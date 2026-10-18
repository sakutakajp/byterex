# Byterex CPU テキストチャット（初期実装）

Raspberry Pi 5 16GB 上で、Gemma 4 E2B の短い日本語応答を逐次表示するための端末アプリです。
既存の `web/` から独立した実験用ランタイムです。

**状態:** Python標準ライブラリの単体テストで制御処理を確認済みです。
Pi実機・ネイティブ推論・日本語の応答品質・速度・メモリ使用量は未検証です。
モデル本体や実行環境は同梱していません。

## 今回の範囲

- LiteRT-LMのCPUバックエンドを明示して使用（4スレッド）
- 日本語、短い応答、逐次表示、履歴リセット、Ctrl-Cで中断後に終了
- 初期値: コンテキスト2,048トークン、出力128トークン、入力400文字、4往復
- 「thinking」を無効化し、回答テキストだけを表示
- 生成時間を任意で計測。モデルの初期ロード時間と回答待ち時間を分離
- ランタイムの差し替え境界は `byterex_chat/backend.py` の `ChatBackend`

ネットワーク待受、クラウド推論への切替、音声・カメラ入力、Hailo使用、
ロボットの操作やツール呼び出しは実装していません。会話をファイルに保存しません。
依存ライブラリのインストールとモデル取得には通信が必要ですが、
アプリにはダウンロード・通信処理を設けていません。

## 前提条件

- Raspberry Pi 5 / 64-bit Linux（`uname -m` が `aarch64`）
- Python 3.10以上、glibc 2.27以上。32-bit OSやmusl環境は対象外
- 冷却と安定した電源。初回は他の重い処理を止める
- モデル本体は約2.59 GB。作業用の空きを含め8 GB以上の空き容量を推奨
- 標準の `venv` / `pip` と、ダウンロード用 `curl`

```sh
uname -m
python3 --version
ldd --version | head -n 1
df -h .
```

この実装は `litert-lm-api==0.18.0` のLinux ARM64 wheelに固定しています。
Python APIのパッケージ名は `litert-lm-api`、import名は `litert_lm` です。
ブログで紹介されている別の `litert-cli` を追加インストールする必要はありません。

## Piでの初回セットアップ

リポジトリ直下にこの `runtime/` を配置してから、Pi上の端末で実行します。
以下は手順です。この成果物の作成時点では実行していません。

```sh
cd runtime
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --only-binary=:all: --require-hashes -r requirements.txt
```

`venv` がない場合は、利用中のOSの公式手順でPythonのvenvを導入してください。
対応wheelがない場合はその場で止め、別ランタイムへ自動で切り替えないでください。

次に、CPU用の正しいモデルを取得します。`-gpu` / `-web` / NPU専用版ではありません。
取得先とリビジョン、SHA256を固定しています。
認証が要求される場合はHugging Faceの公式画面でアクセス条件を確認してください。
トークンをこのリポジトリ、チャット、コマンド引数、ログへ書かないでください。

```sh
mkdir -p models
curl --fail --location --continue-at - \
  'https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/resolve/b3ca0d2f076785a8f4b2219ddbd2bdb99954eae1/gemma-4-E2B-it.litertlm' \
  --output models/gemma-4-E2B-it.litertlm
python -m byterex_chat \
  --model models/gemma-4-E2B-it.litertlm \
  --check --verify-model
```

モデルのSHA256:

```text
181938105e0eefd105961417e8da75903eacda102c4fce9ce90f50b97139a63c
```

`--check` はプラットフォーム、依存パッケージのバージョンとネイティブライブラリのロード、モデルの存在を確認します。
`--verify-model` はモデル全体を読み、固定SHA256と比較します。大きなファイルなので時間がかかります。
この確認だけではモデルのロードや推論の成功を意味しません。
以後も、モデルを置き換えた場合はハッシュを再確認してください。

## 最初の1回

```sh
python -m byterex_chat \
  --model models/gemma-4-E2B-it.litertlm \
  --prompt 'こんにちは。自己紹介を一文でお願いします。' \
  --metrics
```

回答は標準出力、診断情報とJSONの計測値は標準エラーに出ます。
モデルの生成結果をロボットの命令として実行しないでください。

対話モード:

```sh
python -m byterex_chat --model models/gemma-4-E2B-it.litertlm --metrics
```

- `/reset`: モデルを再ロードせず会話履歴を消去
- `/quit` または入力待ちのCtrl-D: 終了
- 生成中のCtrl-C: ネイティブ処理をキャンセルし、残りのストリームを破棄して終了
- 4往復後: `/reset` を案内。履歴を黙って破棄しない

## 計測の読み方と注意点

- `load.elapsed_ms`: エンジン・最初の会話作成にかかった実行時間
- `response.first_text_ms`: 送信開始から最初に表示できる回答テキストまでの時間
- `response.elapsed_ms`: 送信開始からストリーム終了までの時間
- `response.output_characters`: 文字数。トークン数でもtokens/secでもない

初回/2回目の差、モデルやディスクのキャッシュ、冷却、電源、同時実行処理によって結果は変わります。
公式ベンチマークの値をこの実装の実測値として扱わないでください。

出力128トークンに達すると、文の途中で終わる場合があります。
LiteRT-LM 0.18.0のストリームには、正常な文末とトークン上限を確実に区別できる
終了理由がありません。空の回答はエラーとして扱います。
入力の文字数と会話回数の制限は、2,048トークン以内を保証するものではありません。
送信前に既存履歴と新しい入力のトークン数、出力上限、32トークンの余裕を合計して確認し、
足りなければ生成せず入力の短縮か `/reset` を案内します。この見積もりはSDKの保証ではありません。
ネイティブ側で履歴が原因のエラーになった場合は新しく起動してください。
推論エラーは表示して終了し、同じ質問の自動再送や別モデルへの切替はしません。

キャンセルは公式CLIと同じ「キャンセル要求→ストリームを読み捨て」の順です。
ネイティブAPIにタイムアウト保証はないため、中断処理が必ず即時完了するとは限りません。
実機で中断を確認してから、今後のUIや常駐サービスに接続してください。

CPUだけを使い、vision/audioバックエンドは未指定、投機的デコードは無効です。
将来のHailo・カメラ・音声対応は別の実装・検証が必要です。
ロボット制御を追加する場合は、会話生成から独立した検証・許可・停止の経路が必要です。

## テスト

モデルやLiteRT-LMのインストールなしで、制御処理の単体テストを実行できます。

```sh
cd runtime
python3 -m unittest discover -s tests -v
python3 -m compileall -q byterex_chat tests
```

テストでは厳密な引数を持つ偽SDKを使い、CPU設定、出力制限、回答だけの抽出、
キャンセル、リセット、初期化失敗時の片付け、異常時に自動再試行しないことを検証します。
これはネイティブSDKやPi上での推論の結合テストではありません。

### Pi実機で完了させる確認

1. `--check --verify-model` 成功
2. 1回の日本語入力で空でない回答が逐次表示される
3. 同じ対話内の2回目の応答、`/reset` 後に履歴が消えることを確認
4. 生成中のCtrl-Cで停止・終了し、再起動できる
5. 冷却、温度、メモリ、初回と2回目の時間を記録
6. 通信なしで同じ手順が動くことを確認

## 確認した一次資料（2026-10-18）

- [LiteRT-LM v0.18.0](https://github.com/google-ai-edge/LiteRT-LM/releases/tag/v0.18.0)
- [Python API](https://developers.google.com/edge/litert-lm/python)
- [固定版Engine API](https://github.com/google-ai-edge/LiteRT-LM/blob/v0.18.0/python/litert_lm/engine.py)
- [固定版Conversation API](https://github.com/google-ai-edge/LiteRT-LM/blob/v0.18.0/python/litert_lm/conversation.py)
- [公式CLIのキャンセル処理](https://github.com/google-ai-edge/LiteRT-LM/blob/v0.18.0/python/litert_lm_cli/commands/run.py#L84-L129)
- [PyPI 0.18.0](https://pypi.org/project/litert-lm-api/0.18.0/)
- [Gemma 4 E2Bモデルカード](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm)
- [モデルファイルとSHA256](https://huggingface.co/litert-community/gemma-4-E2B-it-litert-lm/blob/main/gemma-4-E2B-it.litertlm)
- [GoogleのRaspberry Pi記事](https://developers.googleblog.com/en/mastering-edge-ai-on-raspberry-pi-with-litert-and-gemma/)
