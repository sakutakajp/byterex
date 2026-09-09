export default defineNuxtRouteMiddleware((to) => {
  if (to.path === "/") {
    return navigateTo({ path: "/ja", query: to.query, hash: to.hash }, { redirectCode: 302, replace: true });
  }
});
