// =========================================================
// Auto EDA Analytics — UI Enhancement JavaScript
// Tidak mengubah data processing. Hanya interaksi tampilan.
// =========================================================

(function () {
  function ready(fn) {
    if (document.readyState !== "loading") {
      fn();
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  ready(function () {
    document.body.classList.add("loaded");
    enableSmoothScroll();
    addCopyButtons();
    polishHoverCards();
    observeStreamlitRerun();
  });

  function enableSmoothScroll() {
    try {
      document.documentElement.style.scrollBehavior = "smooth";
      setTimeout(function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      }, 120);
    } catch (e) {}
  }

  function addCopyButtons() {
    const boxes = document.querySelectorAll(
      ".interpretation-content, .interpretation-list-box, .insight-box"
    );

    boxes.forEach(function (box) {
      if (box.querySelector(".copy-interpretation-btn")) return;

      const btn = document.createElement("button");
      btn.className = "copy-interpretation-btn";
      btn.innerHTML = "📋";
      btn.title = "Salin interpretasi";
      btn.setAttribute("type", "button");

      btn.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();

        const text = (box.innerText || "")
          .replace("📋", "")
          .replace("✅", "")
          .trim();

        if (!text) return;

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(function () {
            showCopied(btn);
          });
        } else {
          fallbackCopy(text);
          showCopied(btn);
        }
      });

      box.style.position = "relative";
      box.appendChild(btn);
    });
  }

  function showCopied(btn) {
    btn.innerHTML = "✅";
    setTimeout(function () {
      btn.innerHTML = "📋";
    }, 1200);
  }

  function fallbackCopy(text) {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.left = "-9999px";
    document.body.appendChild(area);
    area.focus();
    area.select();
    try {
      document.execCommand("copy");
    } catch (e) {}
    document.body.removeChild(area);
  }

  function polishHoverCards() {
    const selector = [
      ".member-card",
      ".compact-card",
      ".upload-card",
      ".clean-card",
      ".empty-kpi",
      ".empty-feature-card",
      ".identity-item"
    ].join(",");

    document.querySelectorAll(selector).forEach(function (card) {
      if (card.dataset.jsHoverReady === "1") return;
      card.dataset.jsHoverReady = "1";

      card.addEventListener("mouseenter", function () {
        card.style.transform = "translateY(-4px)";
      });

      card.addEventListener("mouseleave", function () {
        card.style.transform = "";
      });
    });
  }

  function observeStreamlitRerun() {
    const root = document.body;

    const observer = new MutationObserver(function () {
      addCopyButtons();
      polishHoverCards();
    });

    observer.observe(root, {
      childList: true,
      subtree: true
    });
  }
})();
