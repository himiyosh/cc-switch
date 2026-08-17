import json, io, sys, os

BLOCKS = {
  "en": {
    "title": "Switch Codex provider?",
    "toCustom": "Switching to \"{{provider}}\" moves Codex onto a custom provider.\n\nYou gain: cheaper models, and no ChatGPT weekly quota usage.\n\nYou lose, until you switch back: Sites, the Usage and sign-out menu entries, cloud projects, and voice input. These are tied to your ChatGPT account login, so they disappear while a custom provider is active.\n\nCodex must be restarted for the change to take effect.",
    "toOfficial": "Switching to \"{{provider}}\" returns Codex to your ChatGPT account.\n\nYou gain: Sites, the Usage and sign-out menu entries, cloud projects, and voice input.\n\nYou lose: cheaper third-party models. Requests will consume your ChatGPT plan quota again.\n\nCodex must be restarted for the change to take effect.",
    "confirm": "Switch",
    "dontAskAgain": "Don't ask again"
  },
  "ja": {
    "title": "Codex のプロバイダーを切り替えますか？",
    "toCustom": "「{{provider}}」に切り替えると、Codex はカスタムプロバイダーを使う状態になります。\n\n得られるもの: 安価なモデルを使えます。ChatGPT の週次上限も消費しません。\n\n失うもの（戻すまでの間）: Sites、メニュー内の Usage とログアウト、クラウドプロジェクト、音声入力。これらは ChatGPT アカウントのログインに紐づいているため、カスタムプロバイダー使用中は表示されなくなります。\n\n反映には Codex の再起動が必要です。",
    "toOfficial": "「{{provider}}」に切り替えると、Codex は ChatGPT アカウントに戻ります。\n\n得られるもの: Sites、メニュー内の Usage とログアウト、クラウドプロジェクト、音声入力が使えるようになります。\n\n失うもの: 安価な外部モデル。リクエストは再び ChatGPT プランの上限を消費します。\n\n反映には Codex の再起動が必要です。",
    "confirm": "切り替える",
    "dontAskAgain": "次回から確認しない"
  },
  "zh": {
    "title": "切换 Codex 供应商？",
    "toCustom": "切换到「{{provider}}」后，Codex 将使用自定义供应商。\n\n获得：更便宜的模型，且不消耗 ChatGPT 的每周额度。\n\n失去（切回前）：Sites、菜单中的 Usage 与退出登录、云端项目、语音输入。这些功能绑定 ChatGPT 账号登录，使用自定义供应商期间不会显示。\n\n需要重启 Codex 才能生效。",
    "toOfficial": "切换到「{{provider}}」后，Codex 将恢复使用 ChatGPT 账号。\n\n获得：Sites、菜单中的 Usage 与退出登录、云端项目、语音输入。\n\n失去：更便宜的第三方模型。请求将重新消耗 ChatGPT 套餐额度。\n\n需要重启 Codex 才能生效。",
    "confirm": "切换",
    "dontAskAgain": "不再提示"
  },
  "zh-TW": {
    "title": "切換 Codex 供應商？",
    "toCustom": "切換至「{{provider}}」後，Codex 將使用自訂供應商。\n\n獲得：更便宜的模型，且不消耗 ChatGPT 的每週額度。\n\n失去（切回前）：Sites、選單中的 Usage 與登出、雲端專案、語音輸入。這些功能綁定 ChatGPT 帳號登入，使用自訂供應商期間不會顯示。\n\n需要重新啟動 Codex 才會生效。",
    "toOfficial": "切換至「{{provider}}」後，Codex 將恢復使用 ChatGPT 帳號。\n\n獲得：Sites、選單中的 Usage 與登出、雲端專案、語音輸入。\n\n失去：更便宜的第三方模型。請求將重新消耗 ChatGPT 方案額度。\n\n需要重新啟動 Codex 才會生效。",
    "confirm": "切換",
    "dontAskAgain": "不再提示"
  },
}

base = sys.argv[1]
for lang, block in BLOCKS.items():
    p = os.path.join(base, f"{lang}.json")
    with io.open(p, encoding="utf-8") as f:
        data = json.load(f)
    data["codexSwitchConfirm"] = block
    with io.open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("patched", lang)
