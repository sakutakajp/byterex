<script setup lang="ts">
const route = useRoute();
const contentPath = computed(() => route.path.replace(/\/+$/, "") || "/");

const { data: page } = await useAsyncData(() => "page-" + contentPath.value, () => {
  return queryCollection("content").path(contentPath.value).first();
});

if (!page.value) {
  throw createError({
    statusCode: 404,
    statusMessage: "Page not found",
    fatal: true,
  });
}

const { locale } = useSiteLocale();
const title = computed(() => page.value?.title || "Byterex");
const description = computed(() => page.value?.description || "");
const canonicalUrl = computed(() => `https://byterex.ai${contentPath.value}`);

useSeoMeta({
  title: () => title.value,
  description: () => description.value,
  ogTitle: () => title.value,
  ogDescription: () => description.value,
  ogImage: "https://byterex.ai/ogp.png",
  ogType: "website",
  ogSiteName: "Byterex",
  ogUrl: () => canonicalUrl.value,
  ogLocale: () => locale.value === "ja" ? "ja_JP" : "en_US",
  twitterCard: "summary_large_image",
  twitterImage: "https://byterex.ai/ogp.png",
  twitterTitle: () => title.value,
  twitterDescription: () => description.value,
});

useHead(() => ({
  link: [{ rel: "canonical", href: canonicalUrl.value }],
}));
</script>

<template>
  <main
    class="mx-auto w-[calc(100%_-_48px)] max-w-[960px] py-[clamp(32px,6vw,80px)] max-[600px]:w-[calc(100%_-_24px)] max-[600px]:pt-5 max-[600px]:pb-8"
  >
    <ContentRenderer
      v-if="page"
      :value="page"
      class="
        prose prose-neutral max-w-none rounded-[20px] border border-neutral-200 bg-white
        p-[clamp(24px,5vw,64px)] text-base leading-[1.95] wrap-anywhere
        shadow-[0_8px_32px_rgb(0_0_0/0.03)]
        prose-headings:text-neutral-900 prose-strong:text-neutral-800
        prose-h1:mb-[1.1em] prose-h1:text-[clamp(1.9rem,4vw,2.75rem)]
        prose-h1:leading-[1.3] prose-h1:tracking-[-0.035em]
        prose-h2:mt-[2.5em] prose-h2:mb-[1em] prose-h2:border-b
        prose-h2:border-neutral-200 prose-h2:pb-[0.65em] prose-h2:text-[1.4rem] prose-h2:leading-normal
        [&>:first-child]:mt-0 [&>:last-child]:mb-0 prose-p:my-[1.4em]
        prose-a:text-neutral-700 prose-a:decoration-1 prose-a:underline-offset-4
        hover:prose-a:text-neutral-800 focus-visible:prose-a:rounded-xs
        focus-visible:prose-a:outline-2 focus-visible:prose-a:outline-offset-4
        focus-visible:prose-a:outline-neutral-700
        prose-table:w-full prose-table:text-sm prose-table:leading-[1.7]
        prose-th:bg-neutral-100 prose-th:px-[18px] prose-th:py-3.5 prose-th:align-middle
        prose-th:font-semibold prose-th:whitespace-nowrap prose-th:text-neutral-700
        prose-td:px-[18px] prose-td:py-3.5 prose-td:align-middle
        [&_th:first-child]:whitespace-nowrap [&_td:first-child]:whitespace-nowrap
        [&_th:last-child]:text-center [&_td:last-child]:text-center
        [&_tbody_tr:nth-child(even)]:bg-neutral-50 prose-li:my-[0.5em]
        [&_li>ul]:mt-[0.5em] [&_li>ul]:mb-[1em]
        max-[600px]:rounded-[14px] max-[600px]:px-5 max-[600px]:py-7
        max-[600px]:text-[0.9375rem] max-[600px]:leading-[1.9]
        max-[600px]:prose-th:min-w-16 max-[600px]:prose-th:py-3
        max-[600px]:prose-td:min-w-16 max-[600px]:prose-td:py-3
        max-[600px]:[&_th:nth-child(2)]:min-w-[260px]
        max-[600px]:[&_td:nth-child(2)]:min-w-[260px]
      "
    />
  </main>
</template>
