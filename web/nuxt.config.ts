import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/content", "@nuxt/eslint", "@nuxt/test-utils"],
  devtools: { enabled: true },
  css: ["@fortawesome/fontawesome-svg-core/styles.css", "~/assets/css/main.css"],
  app: {
    head: {
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    },
  },
  runtimeConfig: {
    public: {
      xUrl: "https://x.com/sakutakajp",
      githubUrl: "https://github.com/sakutakajp",
      gtmId: "process.env.GTM_ID",
    },
  },
  nitro: {
    prerender: {
      crawlLinks: true,
      routes: [
        "/ja",
        "/ja/about",
        "/ja/docs",
        "/ja/docs/todo",
        "/ja/docs/architecture",
        "/en",
        "/en/about",
        "/en/docs",
        "/en/docs/todo",
        "/en/docs/architecture",
        "/ja/blog",
        "/en/blog",
      ],
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  compatibilityDate: "2024-04-03",
});
