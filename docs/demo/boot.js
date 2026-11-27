/* Starts the Lythe UI on sample data for the website and moves it to a scene when the page asks. */
(function () {
  var lang = /\/ja\/[^/]*$/.test(location.pathname) ? "ja" : "en";
  var ja = lang === "ja";
  var FIXED = Date.parse("2026-08-26T12:00:00+09:00");
  var Real = Date;
  var off = FIXED - Real.now();
  class DemoDate extends Real {
    constructor() {
      if (arguments.length === 0) super(Real.now() + off);
      else super(...arguments);
    }
    static now() { return Real.now() + off; }
  }
  window.Date = DemoDate;

  var PR = "acme/storefront#103";
  var HEAD = "0000000000000000000000000000000000000067";
  var chat = {};
  chat[PR] = [
    { role: "me", text: ja ? "タイムアウトの既定値は妥当？" : "Is the default timeout reasonable?", head: HEAD },
    { role: "agent", text: ja ? "5 秒は妥当です。ただし `src/http/retry.ts` で 0 を渡すと待たずに失敗します。" : "5 seconds is reasonable. But passing 0 in `src/http/retry.ts` fails without waiting.", agent: "claude", model: "opus", head: HEAD },
  ];
  chat[PR + "/2"] = [
    { role: "me", text: ja ? "別の AI の答えを確かめて: 「0 を渡すと待たずに失敗する」" : "Check another AI's answer: \"passing 0 fails without waiting\"", head: HEAD },
    { role: "agent", text: ja ? "確かめました。0 は「タイムアウトなし」ではなく即時の失敗になります。`timeoutMs > 0` のときだけ AbortSignal を付けるのが安全です。" : "Confirmed. 0 means an immediate failure, not \"no timeout\". Attach the AbortSignal only when `timeoutMs > 0`.", agent: "codex", model: "gpt-5", head: HEAD },
  ];
  chat[PR + "/auto"] = [
    { role: "me", text: "review", head: HEAD },
    { role: "agent", text: ja ? "判定: 修正推奨\n" : "Verdict: changes\n", agent: "claude", model: "opus", head: HEAD },
  ];
  window.__TAURI_INTERNALS__ = {};
  window.__LYTHE_DEMO__ = true;
  window.__LYTHE_DEMO_ANSWER__ = ja
    ? "これはサイト上のデモなので、決まった答えを返しています。アプリでは、手元の Claude Code や Codex がこの PR を読んで答えます。"
    : "This is the website demo, so it gives a fixed answer. In the app, your own Claude Code or Codex reads the pull request and answers here.";
  window.__LYTHE_E2E__ = {
    fixture: "semantic",
    config: {
      language: lang,
      theme: "dark",
      layout: { aboutSide: "left", chatShown: false },
      autoReview: { agent: "", model: "", effort: "", auto: true },
    },
    chat: chat,
    autoReviews: [{
      key: PR, head: HEAD, agent: "claude", model: "opus", at: 0,
      reading: {
        verdict: "changes",
        reasons: ja
          ? ["タイムアウトの既定値が 0 のとき、待たずに失敗する `src/http/retry.ts`", "再試行の試験が無い"]
          : ["With a timeout of 0 the request fails without waiting `src/http/retry.ts`", "No test covers the retry"],
        rest: ja
          ? "## 全文\nタイムアウトを足す方向は良い。ただし既定値が 0 の分岐で、待たずに失敗する。"
          : "## Full review\nAdding a timeout is the right direction, but with a timeout of 0 the request fails without waiting.",
      },
    }],
  };

  function all(sel) { return Array.prototype.slice.call(document.querySelectorAll(sel)); }
  function byText(sel, re) { return all(sel).filter(function (el) { return re.test((el.textContent || "").trim()); })[0] || null; }
  function until(fn, ms) {
    return new Promise(function (resolve) {
      var t0 = Real.now();
      (function tick() {
        var v = null;
        try { v = fn(); } catch (e) { v = null; }
        if (v) return resolve(v);
        if (Real.now() - t0 > (ms || 6000)) return resolve(null);
        setTimeout(tick, 60);
      })();
    });
  }
  function pressed(sel) { var b = document.querySelector(sel); return !!b && b.getAttribute("aria-pressed") === "true"; }
  async function set(sel, on) {
    var b = await until(function () { return document.querySelector(sel); }, 3000);
    if (!b || pressed(sel) === on) return;
    b.click();
    await until(function () { return pressed(sel) === on; }, 2000);
  }
  async function pick103() {
    var cur = document.querySelector("main.detail[data-pr]");
    if (cur && /#103$/.test(cur.dataset.pr || "")) return;
    var row = await until(function () { return byText("nav.rail button", /#103/); });
    if (row) row.click();
    await until(function () { var d = document.querySelector("main.detail[data-pr]"); return d && /#103$/.test(d.dataset.pr || ""); });
  }
  async function tab(re) {
    var t = await until(function () { return byText('.view-tabs [role="tab"]', re); });
    if (t && t.getAttribute("aria-selected") !== "true") t.click();
  }
  async function chatTab(n) {
    var t = await until(function () { return all(".chat-tabs .chat-tab-pick")[n]; });
    if (t && t.getAttribute("aria-selected") !== "true") t.click();
  }
  var style = document.createElement("style");
  style.textContent = "@keyframes demo-hint{0%,100%{box-shadow:0 0 0 2px rgba(85,194,201,.9),0 0 0 2px rgba(85,194,201,.35)}50%{box-shadow:0 0 0 2px rgba(85,194,201,.9),0 0 0 9px rgba(85,194,201,0)}}.demo-hint{animation:demo-hint 1.4s ease-in-out infinite;border-radius:6px;position:relative;z-index:1}";
  document.addEventListener("DOMContentLoaded", function () { document.head.appendChild(style); });
  function unhint() { all(".demo-hint").forEach(function (el) { el.classList.remove("demo-hint"); }); }
  document.addEventListener("pointerdown", unhint, true);
  async function hint(fn) {
    unhint();
    var el = await until(fn, 4000);
    if (el) el.classList.add("demo-hint");
  }
  var scenes = {
    list: async function () {
      await set("button.activity-graph", false); await set("button.activity-chat", false);
      var all_ = await until(function () { return byText(".rail-tab", ja ? /^全部/ : /^All/); });
      if (all_) all_.click();
      unhint();
    },
    graph: async function () {
      await set("button.activity-chat", false); await set("button.activity-graph", true); unhint();
    },
    semantic: async function () {
      await set("button.activity-graph", false); await set("button.activity-chat", false);
      await pick103(); await tab(/^Semantic diff/);
      hint(function () { var n = all(".sem-crow-name").filter(function (el) { return /^Orders$/.test((el.textContent || "").trim()); })[0]; return n ? n.closest(".sem-crow") : null; });
    },
    reorder: async function () {
      await set("button.activity-graph", false); await set("button.activity-chat", false);
      await pick103(); await tab(ja ? /^差分/ : /^Diff/);
      hint(function () { return byText("button", ja ? /^AI で並べ替え$/ : /^Reorder with AI$/); });
    },
    auto: async function () {
      await set("button.activity-graph", false); await pick103(); await set("button.activity-chat", true);
      await chatTab(0); unhint();
    },
    chat: async function () {
      await set("button.activity-graph", false); await pick103(); await set("button.activity-chat", true);
      await chatTab(2); unhint();
    },
  };
  var busy = Promise.resolve();
  window.addEventListener("message", function (e) {
    var d = e.data;
    if (e.source !== parent || !d || d.type !== "lythe-demo" || !scenes[d.scene]) return;
    busy = busy.then(function () { return scenes[d.scene](); }).then(function () {
      parent.postMessage({ type: "lythe-demo-at", scene: d.scene }, "*");
    });
  });
  window.addEventListener("DOMContentLoaded", function () {
    until(function () { return byText("nav.rail button", /#103/); }, 15000).then(function (ok) {
      if (parent !== window) parent.postMessage({ type: "lythe-demo-ready", ok: !!ok }, "*");
    });
  });
})();
