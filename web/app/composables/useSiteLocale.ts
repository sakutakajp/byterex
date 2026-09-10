const messages = {
  ja: {
    home: "ホーム",
    blog: "ブログ",
    about: "私について",
    navigation: "メインナビゲーション",
    footerNavigation: "フッターナビゲーション",
    language: "言語",
    description: "洗濯機の次は、AIが片付ける。",
  },
  en: {
    home: "Home",
    blog: "Blog",
    about: "About",
    navigation: "Main navigation",
    footerNavigation: "Footer navigation",
    language: "Language",
    description: "After washing, AI puts the laundry away.",
  },
};

export function useSiteLocale() {
  const route = useRoute();
  const locale = computed(() =>
    route.path.split("/")[1] === "en" ? "en" : "ja",
  );
  const labels = computed(() => messages[locale.value]);
  const homePath = computed(() => `/${locale.value}`);
  const blogPath = computed(() => `/${locale.value}/blog`);
  const aboutPath = computed(() => `/${locale.value}/about`);
  const languagePath = (language: "ja" | "en") => ({
    path: `/${language}${route.path.replace(/^\/(ja|en)(?=\/|$)/, "").replace(/\/$/, "")}`,
    query: route.query,
    hash: route.hash,
  });

  return { locale, labels, homePath, aboutPath, blogPath, languagePath };
}
