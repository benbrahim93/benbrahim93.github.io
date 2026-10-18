/* Shared behaviours: theme toggle, nav, mobile menu, reveal, progress. */
(function () {
  var d = document.documentElement;
  d.dataset.js = "ok";

  /* ---- theme + progress + nav shadow on scroll ---- */
  function setTheme(t, persist) {
    d.dataset.theme = t;
    var metas = document.querySelectorAll('meta[name="theme-color"]');
    for (var i = 0; i < metas.length; i++) {
      metas[i].setAttribute("content", t === "light" ? "#f7f9fc" : "#05070c");
    }
    if (persist) { try { localStorage.setItem("theme", t); } catch (e) {} }
  }
  var tBtn = document.getElementById("themeToggle");
  if (tBtn) {
    tBtn.addEventListener("click", function () {
      setTheme(d.dataset.theme === "light" ? "dark" : "light", true);
    });
  }

  var nav = document.getElementById("siteNav");
  var progress = null;
  function onScroll() {
    var y = window.scrollY || document.documentElement.scrollTop || 0;
    if (nav) nav.classList.toggle("scrolled", y > 8);
    if (progress) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + "%";
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ---- mobile menu ---- */
  var burger = document.getElementById("burger");
  var menu = document.getElementById("mobileMenu");
  function closeMenu() {
    menu.classList.remove("open");
    burger.classList.remove("open");
    burger.setAttribute("aria-expanded", "false");
  }
  if (burger && menu) {
    burger.addEventListener("click", function () {
      var open = menu.classList.toggle("open");
      burger.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    menu.addEventListener("click", function (e) {
      if (e.target && e.target.tagName === "A") closeMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("open")) closeMenu();
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 820) closeMenu();
    });
  }

  /* ---- reading progress (article pages only) ---- */
  if (document.querySelector("article") && !document.getElementById("progress")) {
    progress = document.createElement("div");
    progress.id = "progress";
    document.body.appendChild(progress);
  }

  /* ---- scroll reveal ---- */
  var els = Array.prototype.slice.call(document.querySelectorAll(".reveal"));
  if ("IntersectionObserver" in window && els.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("in");
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    els.forEach(function (el) { io.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add("in"); });
  }

  onScroll();
})();