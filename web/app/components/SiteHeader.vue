<script setup lang="ts">
const { locale, labels, homePath, blogPath, aboutPath, languagePath } = useSiteLocale();
const route = useRoute();
const menuOpen = ref(false);
const menuButton = ref<HTMLButtonElement | null>(null);

watch(() => route.fullPath, () => {
  menuOpen.value = false;
});

function closeMenu() {
  if (!menuOpen.value) return;
  menuOpen.value = false;
  menuButton.value?.focus();
}

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
  <header class="border-b border-neutral-200 bg-white" @keydown.esc="closeMenu">
    <div class="mx-auto flex max-w-[960px] flex-wrap items-center justify-between gap-x-6 gap-y-3 px-6 py-5 max-[600px]:px-5">
      <NuxtLink :to="homePath" class="inline-flex items-center gap-2 rounded-sm font-[Ubuntu,sans-serif] text-2xl font-bold tracking-tight text-neutral-900 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-neutral-700" @click="menuOpen = false">
        <img src="/icon.png" alt="" width="32" height="32" class="size-8 shrink-0 object-contain">
        Byterex
      </NuxtLink>
      <button
        ref="menuButton"
        type="button"
        class="inline-flex size-11 items-center justify-center rounded-lg border border-neutral-200 hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700 md:hidden"
        :aria-label="menuOpen ? labels.closeMenu : labels.menu"
        :aria-expanded="menuOpen"
        aria-controls="header-navigation"
        @click="menuOpen = !menuOpen"
      >
        <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
          <path v-if="menuOpen" d="m6 6 12 12M6 18 18 6" />
          <path v-else d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <div
        id="header-navigation"
        :class="menuOpen ? 'flex' : 'hidden'"
        class="w-full flex-col items-stretch gap-3 border-t border-neutral-200 pt-3 md:flex md:w-auto md:flex-row md:items-center md:gap-x-6 md:border-0 md:pt-0"
      >
        <nav :aria-label="labels.navigation" class="flex flex-col gap-1 text-sm font-medium md:flex-row md:items-center">
          <NuxtLink :to="homePath" exact-active-class="bg-neutral-100 text-neutral-900" class="rounded-lg px-3 py-2.5 transition-colors hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-neutral-700" @click="menuOpen = false">
            {{ labels.home }}
          </NuxtLink>
          <NuxtLink :to="blogPath" active-class="text-neutral-900" class="rounded-lg px-3 py-2.5 hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700" @click="menuOpen = false">{{ labels.blog }}</NuxtLink>
          <NuxtLink :to="aboutPath" exact-active-class="bg-neutral-100 text-neutral-900" class="rounded-lg px-3 py-2.5 transition-colors hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-neutral-700" @click="menuOpen = false">
            {{ labels.about }}
          </NuxtLink>
        </nav>
        <nav :aria-label="labels.language" class="flex items-center gap-1 self-start rounded-xl border border-neutral-200 p-1 text-xs font-medium md:self-auto">
          <NuxtLink v-for="language in (['ja', 'en'] as const)" :key="language" :to="languagePath(language)" :lang="language" :hreflang="language" :aria-current="locale === language ? 'true' : undefined" :class="locale === language ? 'bg-neutral-900 text-white' : 'text-neutral-600 hover:bg-neutral-50'" class="rounded-lg px-3 py-2.5 transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700" @click="menuOpen = false">
            {{ language === 'ja' ? '日本語' : 'English' }}
          </NuxtLink>
        </nav>
      </div>
    </div>
  </header>
</template>
