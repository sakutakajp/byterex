# Repository Guidelines

## Project Structure & Module Organization

This repository is a Nuxt 4 site using Vue 3, TypeScript, Nuxt Content, and Tailwind CSS 4.

- `app/app.vue` provides the application shell.
- `app/pages/[...slug].vue` queries content by route path, renders Markdown, and handles missing pages.
- `app/components/` contains reusable Vue components such as `Alert.vue` and `Counter.vue`.
- `content/ja/` contains Japanese Markdown pages; collection configuration lives in `content.config.ts`.
- `app/assets/css/main.css` loads Tailwind and its typography plugin. `public/` holds static assets.
- `.nuxt/`, `.output/`, and `.data/` are generated directories; do not edit them manually.

## Build, Test, and Development Commands

Use npm with the committed `package-lock.json`.

- `npm ci`: install locked dependencies.
- `npm run dev`: start local development, normally at `http://localhost:3000`.
- `npm run build`: produce the production server build.
- `npm run preview`: preview the production build locally.
- `npm run generate`: generate static output in `.output/public`, the Firebase Hosting directory.
- `npx nuxt prepare`: generate Nuxt configuration and types when needed.
- `npx eslint .`: run the Nuxt ESLint configuration after preparation.

## Coding Style & Naming Conventions

Use two-space indentation and Vue single-file components with `<script setup lang="ts">`. Use PascalCase component filenames and preserve Nuxt route naming conventions. Match surrounding quote and semicolon styles; existing files vary.

Use Tailwind utility classes and typography variants for new layout and styling changes instead of custom CSS or inline styles. Keep Markdown content in `content/` and shared presentation in Vue components. ESLint is configured in `eslint.config.mjs`; no dedicated formatter is configured.

## Testing Guidelines

`@nuxt/test-utils` is installed, but there are no committed tests, test script, or coverage thresholds. Run `npm run build` for application changes. Manually check affected content routes, missing-page handling, mobile spacing, table scrolling, and keyboard focus. If adding automated tests, document the runner command and use descriptive `*.spec.ts` filenames.

## Commit & Pull Request Guidelines

Recent commits use short Japanese or English summaries, such as `レイアウト修正` and `Update README.md`; no enforced prefix convention is evident. Keep commits focused and describe the concrete change.

PRs should explain the change, reference related issues when applicable, and list validation performed. Include desktop and mobile screenshots for visual changes. Keep secrets and local `.env` files out of commits.
