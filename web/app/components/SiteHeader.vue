<script setup lang="ts">
const { locale, labels, homePath, aboutPath, languagePath } = useSiteLocale();

useHead({
  link: [
    { rel: "preconnect", href: "https://fonts.googleapis.com" },
    { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "anonymous" },
    {
      rel: "stylesheet",
      href: "https://fonts.googleapis.com/css2?family=Ubuntu:wght@700&display=swap&text=Byterex",
    },
  ],
});
</script>

<template>
  <header class="border-b border-neutral-200 bg-white">
    <div class="mx-auto flex max-w-[960px] flex-wrap items-center justify-between gap-x-6 gap-y-3 px-6 py-5 max-[600px]:px-5">
      <NuxtLink :to="homePath" class="rounded-sm font-[Ubuntu,sans-serif] text-2xl font-bold tracking-tight text-neutral-900 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-neutral-700">
        Byterex
      </NuxtLink>
      <div class="flex flex-wrap items-center gap-x-6 gap-y-3">
        <nav :aria-label="labels.navigation" class="flex items-center gap-1 text-sm font-medium">
          <NuxtLink :to="homePath" exact-active-class="bg-neutral-100 text-neutral-900" class="rounded-lg px-3 py-2.5 transition-colors hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-neutral-700">
            {{ labels.home }}
          </NuxtLink>
          <NuxtLink :to="aboutPath" exact-active-class="bg-neutral-100 text-neutral-900" class="rounded-lg px-3 py-2.5 transition-colors hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-neutral-700">
            {{ labels.about }}
          </NuxtLink>
        </nav>
        <nav :aria-label="labels.language" class="flex items-center gap-1 rounded-xl border border-neutral-200 p-1 text-xs font-medium">
          <NuxtLink v-for="language in (['ja', 'en'] as const)" :key="language" :to="languagePath(language)" :lang="language" :hreflang="language" :aria-current="locale === language ? 'true' : undefined" :class="locale === language ? 'bg-neutral-900 text-white' : 'text-neutral-600 hover:bg-neutral-50'" class="rounded-lg px-3 py-2.5 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700">
            {{ language === 'ja' ? '日本語' : 'English' }}
          </NuxtLink>
        </nav>
      </div>
    </div>
  </header>
</template>
