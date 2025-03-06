# 議事録作成ツール

**本ツールは会議録画の音声を解析し、議事録作成を支援するツールです。**<br/>
**mp4またはwav形式のファイルをアップロードするだけで、要約された議事録を生成してくれます。**<br>
**生成された議事録ファイルはSharepointへ格納することができ、ローカルにダウンロードすることもできます。**<br>
**いずれもワードファイル形式での保存となります。**<br>

---

## 使用技術スタック

| 分類 | 技術・ツール |
|------|-------------|
| フロントエンド | React（Material UI） |
| バックエンド | FastAPI |
| クラウドサービス | Azure Speech Service, Azure OpenAI |
| ストレージ | Azure Blob Storage |
| コンテナ技術 | Docker（docker-compose） |

---

## 環境構築

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
docker-compose build
```

---

## 3. アプリケーションの起動と使用方法

1. フロントエンドのサーバーを起動。
```bash
cd client
yarn start
```

2. バックエンドのサーバーを起動
```bash
cd api
docker-compose up -d
```

3. ブラウザで以下のURLにアクセスし、音声ファイルをアップロードしてください。
```
http://localhost:3000
```

4. 議事録の生成後、ワードファイルとしてダウンロードすることができます。

---

## 注意事項と前提条件
- 本ツールのご利用には、AzureアカウントおよびAPIキーが必要です。
- APIキーや環境変数の設定方法については、各サービスの公式ドキュメントを参照してください。

