<script setup lang="ts">
const { locale } = useSiteLocale();

useHead(() => ({ htmlAttrs: { lang: locale.value } }));
</script>

<template>
  <NuxtRouteAnnouncer />
  <div
    class="flex min-h-screen flex-col bg-neutral-50 font-[-apple-system,BlinkMacSystemFont,'Segoe_UI','Noto_Sans_JP','Hiragino_Kaku_Gothic_ProN','Yu_Gothic',sans-serif] text-neutral-700 antialiased [font-synthesis:none]"
  >
    <SiteHeader />
    <NuxtPage />
    <SiteFooter />
  </div>
</template>
