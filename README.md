# タツユキ産後ケア

結婚記念日特別イベント用の一枚ものサイト。産後ケア施設のコーポレートサイト風に作った、**2026年9月20日（日）一日限り開設**の架空施設の案内ページ。

**公開URL**: https://tatsuyukitakashima-hub.github.io/tatsuyuki-sango-care/ （合言葉 `sekai-de-ichiban-erina-to-nanako`）

## 合言葉は本物の鍵

このリポジトリは public だが、**サイト本文と写真は暗号化された状態でしか置かれていない**。

- 合言葉から **PBKDF2-HMAC-SHA256（60万回）** で256bitの鍵を導出
- サイト本文（写真を data URI で埋め込んだHTML全体）を **AES-256-GCM** で暗号化
- 暗号文を base64 にして `index.html` に埋め込む
- ブラウザ側で `crypto.subtle` を使って復号し、`document.write()` でページを差し替える

したがって `index.html` を直接読んでも、リポジトリを clone しても、合言葉なしでは写真1枚取り出せない。GCMの認証タグが復号可否をそのまま判定するので、合言葉の照合そのものが暗号化に一体化している。

一度入館すると合言葉が `localStorage` に保存され、次回以降は自動で解錠される。

合言葉は `sekai-de-ichiban-erina-to-nanako`（32文字）。申込フォームのQuestion 05「辰幸が世界でいちばん好きなものは？」の正解と同じ文言になっている。

32文字の未知のパスフレーズを60万回のPBKDF2越しに総当たりするのは現実的でない。ただし文言のパターンを知っている相手には強度が落ちるので、他所で使い回さないこと。

## ファイル構成

| パス | 内容 | Git |
| --- | --- | --- |
| `src/page.html` | **サイト本体のソース。編集するのはここ** | ✅ |
| `src/shell.html` | 解錠ゲート。`__PAYLOAD__` と `__ITER__` を埋める | ✅ |
| `build.py` | ビルドスクリプト | ✅ |
| `index.html` | 生成物。GitHub Pages が配信する | ✅ |
| `assets/*.jpg` | 平文の写真（ビフォーアフター） | ❌ gitignore |
| `dist/artifact.html` | Artifact 用の平文ビルド | ❌ gitignore |

`assets/` は Git に入れていないので、clone しただけではビルドできない。元写真は `~/Downloads/IMG_8458.HEIC`（before）と `IMG_8273.JPG`（after）から作った。

```sh
mkdir -p assets
sips -s format jpeg -s formatOptions 72 --resampleHeightWidthMax 900 ~/Downloads/IMG_8458.HEIC --out assets/before.jpg
sips -s format jpeg -s formatOptions 72 --resampleHeightWidthMax 900 ~/Downloads/IMG_8273.JPG  --out assets/after.jpg
```

## ビルドと更新

```sh
python3 build.py          # index.html と dist/artifact.html を生成
git add -A && git commit -m "..." && git push    # Pages に反映（1〜2分）
```

`src/page.html` を直接ブラウザで開けば、ゲートなしで見た目を確認できる（写真は `assets/` を参照）。生成後の `index.html` はローカルの `file://` では復号できない（`crypto.subtle` が安全なコンテキストを要求するため）。確認するなら:

```sh
python3 -m http.server 8000   # → http://localhost:8000/
```

## 申込フォームの採点

全9問・満点165点のクライアントサイド採点。判定は6段階。

| 満点比 | スコア | 判定印 | 結果 |
| ---: | ---: | --- | --- |
| 100% | 165 | 特別受付 | 満点。審査不要で受付 |
| 88% | 145–164 | 受付 | 「溢れる愛を確認することができました」 |
| 70% | 116–144 | 受付 | 受付するが、当日口頭で補足説明を要求される |
| 48% | 79–115 | 保留 | 再審査。辰幸を3秒見つめてから再記入 |
| 24% | 40–78 | 不受理 | 「厳正なる審査をするまでもなく」 |
| — | 0–39 | 別人 | 「あなた、瑛里奈様のそっくりさんですね？」 |

配点は `src/page.html` の `QUESTIONS` 配列、判定文は `TIERS` 配列にまとまっている。

- 設問番号（Question 01…）と満点は配列から自動計算されるので、設問を足しても他をいじる必要はない
- 判定しきい値は絶対値ではなく満点比（`at`）で持たせてあるため、配点を変えてもバランスが崩れない
- 低スコアの選択肢には `r`（審査員所見）を持たせてあり、結果画面の下部に表示される
