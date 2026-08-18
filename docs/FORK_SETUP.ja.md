# himiyosh/cc-switch フォーク セットアップガイド

このフォークは [farion1231/cc-switch](https://github.com/farion1231/cc-switch) に
**Codex（ChatGPT Desktop App）を OpenRouter などのカスタムプロバイダーと安全に往復させるための修正**を
重ねたものです。作業ブランチは `himiyosh/local-customizations`（`main` は upstream のまま）。

このガイドは 2 部構成です。

- **A. リポジトリに入っているもの** — クローンすれば手に入る（ビルドするだけ）
- **B. リポジトリに入っていないもの** — 各マシンで 1 回だけ行う環境構築（Keychain / config.toml / OpenRouter）

> 💡 自分でビルドしたくない場合は、このフォークの
> [Releases](https://github.com/himiyosh/cc-switch/releases) にビルド済み DMG（Apple Silicon・無署名）がある。
> 公証していないため、初回のみ `xattr -dr com.apple.quarantine "/Applications/CC Switch.app"`
> で隔離属性を外すか、.app を右クリック →「開く」で起動する。

---

## A-1. フォークに含まれる変更

| コミット | 内容 |
|---|---|
| `b1592cd3` | **config.toml 保護マージ** — cc-switch は本来プロバイダー切り替え時に config.toml 全体をスナップショットで上書きし、手書きの `[projects.*]` `[plugins.*]` `[model_providers.*]` 等が消える（upstream 既知バグ #4254/#3700 ほか）。3 系統ある書き込み経路すべてをマージ関数経由にし、cc-switch が管理するキーだけを更新するよう変更。あわせて **メモリ抽出/統合モデルのピン**（カスタムプロバイダー時は `[memories].extract_model` / `consolidation_model` をアクティブモデルに固定し、GPT-5.6 Luna/Terra への裏課金を防止。公式復帰時は削除して既定に戻す）と、**公式⇄カスタム切り替え時の確認ダイアログ**（en/ja/zh/zh-TW）を追加 |
| `286cb6bf` | カスタム判定を `category` ではなく config 内の **`model_provider`** で行うよう修正（インポート品はすべて `official` になり判定が壊れていた） |
| `fa886d65` | **インポート分類の修正** — コマンド式 auth（キーがファイルに現れない）+ ChatGPT の auth.json 残留という構成が `official` 誤分類 → ChatGPT OAuth 誤紐付け → 公式へ戻れなくなる問題の根治。あわせて b1592cd3 のリグレッション 2 件（テイクオーバー復元のマージ誤適用 / 離脱プロバイダーブロックの残留）を修復 |
| `82cf3023` | **OTA アップデーター無効化** — upstream の署名付きリリースが検証を通ってフォークを上書きするのを防ぐ。更新は「upstream を merge して再ビルド」で意図的に行う |

テスト: `cargo test --lib` 2590 件パス / clippy・rustfmt クリーン。

## A-2. クローンとビルド（macOS / Apple Silicon で検証済み）

前提: Xcode Command Line Tools、Rust（rustup, cargo 1.94+）、Node 20+、pnpm。

```sh
git clone https://github.com/himiyosh/cc-switch.git
cd cc-switch
git checkout himiyosh/local-customizations
git remote add upstream https://github.com/farion1231/cc-switch.git   # 追従用

pnpm install
pnpm tauri build        # 初回 15〜25 分 / 2 回目以降は数分
```

### ビルドの罠（実際に踏んだもの）

- **corepack の pnpm シムに注意**。Homebrew の node が入れる `pnpm` は corepack シムで、
  `package.json` の `packageManager` 指定を registry.npmjs.org から取りに行き、
  社内プロキシ環境では ENOTCONN で死ぬ。本物の pnpm（`brew install pnpm`）を PATH 先頭に置き、
  自動バージョン切替も止める:

  ```sh
  export PATH=/opt/homebrew/Cellar/pnpm/<ver>/bin:$PATH
  export npm_config_manage_package_manager_versions=false
  # 社内プロキシ利用時のみ:
  export npm_config_registry=https://<your-internal-npm-proxy>/npm/
  ```

- 成果物: `src-tauri/target/release/bundle/macos/CC Switch.app`（+ .dmg）。
  82cf3023 以降はビルドが exit 0 で完走する（以前は updater 署名鍵が無い旨のエラーで終わっていた）。

### インストール

```sh
rm -rf "/Applications/CC Switch.app"
ditto "src-tauri/target/release/bundle/macos/CC Switch.app" "/Applications/CC Switch.app"
codesign --force -s - "/Applications/CC Switch.app"   # アドホック署名
open -a "CC Switch"
```

### テスト実行

```sh
cd src-tauri
cargo test --lib
```

### リリース（タグ push で自動）

`.github/workflows/release.yml` はフォーク用に書き換えてあり、`v*` タグを push すると
GitHub Actions が **macOS (Apple Silicon) の無署名ビルド**を作成して Releases に
DMG / zip を公開する。upstream 版と違い、updater 署名鍵や Apple Developer ID は不要。

```sh
git tag v3.19.2-himiyosh.2
git push fork v3.19.2-himiyosh.2
```

---

## B. リポジトリに入っていない環境構築（各マシンで 1 回）

ここから先は **git 管理外**。API キー・個人設定・サーバー側設定なので、クローンしただけでは動かない。

### B-1. OpenRouter API キーを macOS Keychain に登録

環境変数（`launchctl setenv`）は**再起動で消える**ため使わない。Keychain が正解。

```sh
security add-generic-password -U -a "$USER" -s openrouter-api -T /usr/bin/security -w
# ↑ 最後の -w に値を付けないと対話プロンプトになり、シェル履歴にキーが残らない
```

`-T /usr/bin/security` を付けることで、後述の auth コマンドがプロンプトなしで読める。

動作確認（キーを表示せずステータスだけ見る）:

```sh
sh -c 'security find-generic-password -s openrouter-api -w' >/dev/null; echo rc=$?
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer $(security find-generic-password -s openrouter-api -w)" \
  https://openrouter.ai/api/v1/key        # 200 なら OK
```

### B-2. `~/.codex/config.toml` にプロバイダーを手書き

キー本体はファイルに書かない。Keychain から**リクエスト時に**読ませる:

```toml
model = "deepseek/deepseek-v4-pro"
model_provider = "openrouter"
model_catalog_json = "/Users/<you>/.codex/model-catalog.json"   # B-3 参照（任意）

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"

[model_providers.openrouter.auth]
command = "sh"
args = ["-c", "security find-generic-password -s openrouter-api -w"]
```

この「コマンド式 auth + ChatGPT ログイン残留」の組み合わせを cc-switch が誤って
公式扱いしてしまう問題は、このフォークの `fa886d65` で修正済み。

### B-3. model-catalog.json（任意 / **絶対に公開しないこと**）

Codex のモデル選択プルダウンに「DeepSeek V4 Pro」等の名前を出すための仕組み。
`codex debug models` で内蔵カタログをダンプし、既存エントリを複製して `slug` / 表示名を
サードパーティモデルに書き換えたものを `model_catalog_json` で指す。

> ⚠️ 生成物には OpenAI 独自の `base_instructions`（モデルごと約 20KB のシステムプロンプト）が
> 含まれる。**リポジトリにコミットしたり公開したりしてはならない**。各マシンで再生成する。

### B-4. OpenRouter サーバー側の設定（Web ダッシュボード）

1. **API キー作成** + **週次などの利用上限**。上限は**キー単位**なのでキーを作り直したら再設定
2. **Guardrail を「Only Allow」（許可リスト）で作成**し、使うモデルだけを登録して対象キーに割り当てる。
   デナイリストにしないこと — Codex は `gpt-5.6-luna` / `gpt-5.6-terra` などを裏で呼ぶことがあり、
   将来の新 GPT はデナイリストをすり抜ける。許可リストなら**未知のモデルは既定で遮断**される
3. 検証: GPT 系スラッグへのリクエストが 404（"No endpoints available matching your guardrail
   restrictions"、課金なし）、許可モデルが 200 になること

### B-5. cc-switch 初回起動

初回起動時、cc-switch は live の config.toml を `default` プロバイダーとして取り込み、
「OpenAI Official」カードを播種する。`fa886d65` により、OpenRouter へルーティングしている
config は正しく **custom** として取り込まれる（誤って ChatGPT アカウントに紐付かない）。

推奨設定: General → Codex App Enhancements → **「Keep official login for direct switches」を ON**
（カスタムへ切り替えても `auth.json` の ChatGPT ログインを温存する）。

---

## upstream への追従

OTA を切ってあるので、更新は明示的に行う:

```sh
git fetch upstream
git merge upstream/main          # コンフリクトは自コミットの範囲に限られる
cd src-tauri && cargo test --lib # 全件パスを確認してから
cd .. && pnpm tauri build        # 再ビルド → A-2 の手順で再インストール
```

## 免責

個人利用目的のフォークです。upstream へ還元する場合は各コミットメッセージに
経緯・再現手順・テストを記載してあるので、そのまま PR の説明に流用できます。
