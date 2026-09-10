export default defineNuxtPlugin(() => {
  const { gtmId } = useRuntimeConfig().public;

  if (import.meta.dev || !/^GTM-[A-Z0-9]+$/.test(gtmId)) return;

  useHead({
    script: [{
      key: "gtm",
      tagPosition: "head",
      tagPriority: "high",
              innerHTML: `(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                      new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                      j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                      'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                      })(window,document,'script','dataLayer','${gtmId}');`,
    }],
    noscript: [{
      key: "gtm-noscript",
      tagPosition: "bodyOpen",
      innerHTML: `<iframe src="https://www.googletagmanager.com/ns.html?id=${gtmId}" height="0" width="0" style="display:none;visibility:hidden"></iframe>`,
    }],
  });
});
