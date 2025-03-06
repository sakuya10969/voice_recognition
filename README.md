# 議事録作成ツール

会議録画の音声を解析し、議事録作成を支援するツールです。
**mp4またはwav形式のファイルをアップロードするだけで、要約された議事録を生成してくれます。**

---

## 特徴

- **高精度な音声文字起こし**  
  Azure Speech Serviceを活用し、録音ファイルからテキストデータを生成してくれます。

- **AIによるスマートな要約機能**  
  Azure OpenAIのを利用して、わかりやすい要約を提供します。

- **議事録の簡単出力**  
  要約された議事録はワードファイル形式で簡単にダウンロードすることができます。
  また、本ツールでは生成された議事録ファイルをSharepointへ格納することもできます。

---

## 🛠 使用技術スタック

| 分類 | 技術・ツール |
|------|-------------|
| フロントエンド | React（Material UI） |
| バックエンド | FastAPI |
| クラウドサービス | Azure Speech Service, Azure OpenAI |
| ストレージ | Azure Blob Storage |
| コンテナ技術 | Docker（docker-compose） |

---

## 環境構築ガイド

### 1. リポジトリをクローン

```bash
git clone https://github.com/sakuya10969/voice_recognition.git
cd voice_recognition
```

### 2. 依存関係のセットアップ

**フロントエンド (React)**

```bash
cd client
yarn install
```

**バックエンド (FastAPI)**

```bash
cd ../api
docker-compose up -d --build
```

---

## アプリケーションの起動と使用方法

1. フロントエンドを起動します。

```bash
cd client
yarn start
```

2. ブラウザで以下のURLにアクセスし、音声ファイルをアップロードしてください。

```
http://localhost:3000
```

3. 議事録の生成後、ワードファイルとしてダウンロードできます。会議後すぐに活用できます。

---

## ⚠注意事項と前提条件
- 本ツールのご利用には、AzureアカウントおよびAPIキーが必要です。
- APIキーや環境変数の設定方法については、各サービスの公式ドキュメントを参照してください。

