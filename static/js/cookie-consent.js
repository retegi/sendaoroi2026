(function () {
  const CONSENT_KEY = "sendaoroiCookieConsent";
  const ANALYTICS_KEY = "sendaoroiAnalyticsCookies";

  function showBanner() {
    const banner = document.getElementById("cookie-banner");
    if (!banner) return;

    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) {
      banner.classList.remove("hidden");
    }
  }

  function hideBanner() {
    const banner = document.getElementById("cookie-banner");
    if (banner) {
      banner.classList.add("hidden");
    }
  }

  function saveConsent(value, analyticsAllowed) {
    localStorage.setItem(CONSENT_KEY, value);
    localStorage.setItem(ANALYTICS_KEY, analyticsAllowed ? "true" : "false");
    hideBanner();

    if (analyticsAllowed) {
      window.dispatchEvent(new CustomEvent("sendaoroi:cookies:analytics-accepted"));
    }
  }

  function bindCookieActions() {
    document.addEventListener("click", function (event) {
      const button = event.target.closest("[data-cookie-action]");
      if (!button) return;

      const action = button.getAttribute("data-cookie-action");
      const settings = document.getElementById("cookie-settings");
      const analyticsCheckbox = document.getElementById("analytics-cookies-checkbox");

      if (action === "accept") {
        saveConsent("accepted", true);
      }

      if (action === "reject") {
        saveConsent("rejected", false);
      }

      if (action === "configure") {
        if (settings) {
          settings.classList.toggle("hidden");
        }
      }

      if (action === "save-settings") {
        saveConsent("configured", Boolean(analyticsCheckbox && analyticsCheckbox.checked));
      }
    });
  }

  function bindResetFromCookiesPage() {
    document.addEventListener("click", function (event) {
      const button = event.target.closest("[data-cookie-reset]");
      if (!button) return;

      localStorage.removeItem(CONSENT_KEY);
      localStorage.removeItem(ANALYTICS_KEY);

      const banner = document.getElementById("cookie-banner");
      if (banner) {
        banner.classList.remove("hidden");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    showBanner();
    bindCookieActions();
    bindResetFromCookiesPage();
  });
})();
