<script setup lang="ts">
const { locale, blogPath } = useSiteLocale();
const { data: posts } = await useAsyncData(
  () => `blog-${locale.value}`,
  () => queryCollection("content")
    .where("path", "LIKE", `${blogPath.value}/%`)
    .order("date", "DESC")
    .order("path", "ASC")
    .select("path", "title", "description", "date")
    .all(),
);
</script>

<template>
  <div class="not-prose">
    <ul v-if="posts?.length" class="divide-y divide-neutral-200">
      <li v-for="post in posts" :key="post.path" class="py-6 first:pt-0">
        <time v-if="post.date" :datetime="post.date" class="text-sm text-neutral-500">{{ post.date }}</time>
        <h2 class="mt-2 text-xl font-semibold text-neutral-900">
          <NuxtLink :to="post.path" class="rounded-sm underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-neutral-700">{{ post.title }}</NuxtLink>
        </h2>
        <p v-if="post.description" class="mt-3 leading-relaxed text-neutral-600">{{ post.description }}</p>
      </li>
    </ul>
    <p v-else class="rounded-xl bg-neutral-50 p-6 text-neutral-600">
      {{ locale === "ja" ? "記事はまだありません。" : "No posts yet." }}
    </p>
  </div>
</template>
