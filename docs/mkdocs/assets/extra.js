/* Show sidebar scrollbars only while the user is scrolling. */
(function () {
  const timers = new WeakMap();

  function bindScrollwrap(el) {
    if (el.dataset.adScrollBound) return;
    el.dataset.adScrollBound = "1";

    el.addEventListener(
      "scroll",
      () => {
        el.classList.add("is-scrolling");
        const prev = timers.get(el);
        if (prev) clearTimeout(prev);
        timers.set(
          el,
          setTimeout(() => el.classList.remove("is-scrolling"), 700)
        );
      },
      { passive: true }
    );
  }

  function init() {
    document
      .querySelectorAll(".md-sidebar__scrollwrap")
      .forEach(bindScrollwrap);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
