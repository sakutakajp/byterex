import tailwindcss from "@tailwindcss/vite";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/content", "@nuxt/eslint", "@nuxt/test-utils"],
  devtools: { enabled: true },
  css: ["~/assets/css/main.css"],
  app: {
    head: {
      link: [{ rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    },
  },
  // runtimeConfig: {
  //   public: {
  //     gtmId: "",
  //   },
  // },
  nitro: {
    prerender: {
      routes: ["/ja", "/ja/about", "/en", "/en/about"],
    },
  },
  vite: {
    plugins: [tailwindcss()],
  },
  compatibilityDate: "2024-04-03",
});
