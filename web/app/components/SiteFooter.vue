<script setup lang="ts">
import { faGithub, faXTwitter } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

const { labels, homePath, blogPath, docsPath, aboutPath } = useSiteLocale();
const config = useRuntimeConfig();
const socialLinks = computed(() => [
  { name: "X", url: config.public.xUrl, icon: faXTwitter },
  { name: "GitHub", url: config.public.githubUrl, icon: faGithub },
].filter(link => link.url));
</script>

<template>
  <footer class="mt-auto border-t border-neutral-200 bg-white">
    <div class="mx-auto flex max-w-[960px] flex-col gap-6 px-6 py-8 sm:flex-row sm:items-center sm:justify-between max-[600px]:px-5">
      <div class="space-y-2">
        <p class="text-sm font-semibold text-neutral-900">Byterex Project</p>
        <p class="text-sm leading-relaxed text-neutral-500">{{ labels.description }}</p>
        <div v-if="socialLinks.length" class="flex flex-wrap gap-2">
          <a
            v-for="link in socialLinks"
            :key="link.name"
            :href="link.url"
            class="inline-flex min-h-11 items-center gap-2 rounded-lg px-3 text-sm text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700"
          >
            <FontAwesomeIcon :icon="link.icon" class="size-5" aria-hidden="true" />
            <span>{{ link.name }}</span>
          </a>
        </div>
        <p class="text-xs text-neutral-500">&copy; Byterex Project</p>
      </div>
      <nav :aria-label="labels.footerNavigation" class="flex flex-wrap gap-x-6 gap-y-2 text-sm">
        <NuxtLink :to="homePath" class="rounded-sm py-2 hover:text-neutral-700 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-neutral-700">{{ labels.home }}</NuxtLink>
        <NuxtLink :to="blogPath" active-class="text-neutral-900" class="rounded-lg px-3 py-2.5 hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700">{{ labels.blog }}</NuxtLink>
        <NuxtLink :to="docsPath" active-class="text-neutral-900" class="rounded-lg px-3 py-2.5 hover:bg-neutral-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-neutral-700">{{ labels.docs }}</NuxtLink>
        <NuxtLink :to="aboutPath" class="rounded-sm py-2 hover:text-neutral-700 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-neutral-700">{{ labels.about }}</NuxtLink>
      </nav>
    </div>
  </footer>
</template>
