// Copy buttons, screenshots shown at their natural size, and the live demo.
document.addEventListener("click", (e) => {
  const copy = e.target.closest(".copy");
  if (copy) {
    const code = copy.previousElementSibling;
    const label = copy.textContent;
    const select = () => getSelection().selectAllChildren(code);
    const done = () => {
      copy.textContent = copy.dataset.copied;
      setTimeout(() => (copy.textContent = label), 1400);
    };
    if (navigator.clipboard) navigator.clipboard.writeText(code.textContent).then(done, select);
    else select();
    return;
  }
});

// Screenshots are taken at 2x; never show them larger than their CSS size.
const fit = (img) => img.style.setProperty("--iw", img.naturalWidth / 2 + "px");
document.querySelectorAll("img[data-fit]").forEach((img) => {
  if (img.complete) fit(img);
  else img.addEventListener("load", () => fit(img));
});

// The live demo: the real UI on sample data in an iframe, moved to a scene by the tabs.
// Narrow screens and failed starts keep the screenshot.
(() => {
  const root = document.querySelector(".try");
  if (!root) return;
  const W = 1600, H = 900;
  const tabs = [...root.querySelectorAll('[role="tab"]')];
  const view = root.querySelector(".demo-view");
  const still = root.querySelector(".demo-still");
  const note = root.querySelector(".demo-note");
  const wide = matchMedia("(min-width: 900px) and (pointer: fine)");
  let frame = null, ready = false, current = tabs[0].dataset.scene;

  const fit = () => {
    if (!frame) return;
    const scale = Math.min(1, view.clientWidth / W);
    frame.style.width = W + "px";
    frame.style.height = H + "px";
    frame.style.transform = `scale(${scale})`;
    if (ready) view.style.height = Math.round(H * scale) + "px";
  };
  const send = () => { if (frame && ready) frame.contentWindow.postMessage({ type: "lythe-demo", scene: current }, "*"); };
  const show = (scene) => {
    current = scene;
    tabs.forEach((t) => {
      const on = t.dataset.scene === scene;
      t.setAttribute("aria-selected", String(on));
      t.tabIndex = on ? 0 : -1;
    });
    root.querySelectorAll("[data-panel]").forEach((p) => (p.hidden = p.dataset.panel !== scene));
    still.src = `${root.dataset.up}shots/${root.dataset.lang}/${scene}.webp`;
    send();
  };
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => show(t.dataset.scene));
    t.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      const n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
      n.focus();
      show(n.dataset.scene);
    });
  });
  addEventListener("message", (e) => {
    const d = e.data;
    if (!frame || e.source !== frame.contentWindow || !d || d.type !== "lythe-demo-ready" || !d.ok) return;
    ready = true;
    root.classList.add("live");
    fit();
    send();
  });
  const start = () => {
    if (frame) return;
    if (!wide.matches) { note.textContent = root.dataset.narrow; return; }
    frame = document.createElement("iframe");
    frame.title = "Lythe demo";
    frame.src = `${root.dataset.up}demo/${root.dataset.lang}/`;
    view.appendChild(frame);
    fit();
    setTimeout(() => { if (!ready) note.textContent = root.dataset.fail; }, 12000);
  };
  addEventListener("resize", fit);
  wide.addEventListener("change", start);
  // Start loading once the section is close, so the hero is not slowed down.
  new IntersectionObserver((es, io) => {
    if (es.some((x) => x.isIntersecting)) { io.disconnect(); start(); }
  }, { rootMargin: "400px" }).observe(root);
})();
