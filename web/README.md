# Nuxt Content Starter

## ブログ記事の追加

ブログ一覧は `/ja/blog` と `/en/blog` です。
`content/ja/blog/記事名.md` に記事を追加すると、一覧に日付の新しい順で表示されます。
英語版は同じファイル名で `content/en/blog/` に追加してください。言語切り替えで対応する記事に移動します。
両言語の記事を用意してから公開してください。

```markdown
---
title: 記事のタイトル
description: 記事の概要
date: '2026-09-10'
---

# 記事のタイトル

ここに本文を書きます。
```

日付は `YYYY-MM-DD` 形式です。保存した記事はすべて公開対象になります。
`npm run generate` で一覧とリンク先の記事が静的生成されます。

Look at the [Nuxt Content documentation](https://content.nuxt.com) to learn more.

## Setup

Make sure to install dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm preview

# yarn
yarn preview

# bun
bun run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.
