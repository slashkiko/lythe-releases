#!/usr/bin/env python3
"""Builds the GitHub Pages site into docs/ from content.json and style.css.

    python3 site/build.py

Pages: docs/index.html and docs/guide/ in English, docs/ja/ and docs/ja/guide/ in
Japanese. Both languages come from the same content.json so the two stay in step.
Screenshots live in docs/shots/<lang>/ and are not generated here.
"""
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT.parent / "docs"
SITE = "https://slashkiko.github.io/lythe-releases/"
RELEASES = "https://github.com/slashkiko/lythe-releases/releases"
INSTALL = "curl -fsSL https://slashkiko.github.io/lythe-releases/install.sh | sh"
VERSION = "0.1.0"

C = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))

LOGO = (
    '<svg viewBox="100 100 824 824" aria-hidden="true"><rect x="100" y="100" width="824" height="824" rx="185" '
    'fill="#12161c" stroke="#2a323b" stroke-width="12"/><g transform="translate(212 212) scale(9.375)"><g fill="#e4ebf0">'
    '<rect x="12" y="6.5" width="30" height="9" rx="4.5"/><rect x="12" y="20.5" width="30" height="9" rx="4.5"/>'
    '<rect x="12" y="48.5" width="30" height="9" rx="4.5"/></g>'
    '<rect x="12" y="34.5" width="44" height="9" rx="4.5" fill="#55c2c9"/></g></svg>'
)
FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700'
    '&family=JetBrains+Mono:wght@400;500&family=LINE+Seed+JP:wght@400;700&display=swap">'
)


def path_of(lang, page):
    """Site-relative path of a page, e.g. "ja/guide/"."""
    return ("ja/" if lang == "ja" else "") + ("guide/" if page == "guide" else "")


def cmd(text, t):
    return (
        f'<div class="term"><div class="cmd"><code>{html.escape(text)}</code>'
        f'<button class="copy" type="button" data-copied="{t["copied"]}">{t["copy"]}</button></div></div>'
    )


def shot(lang, name, alt, up):
    return (
        f'<div class="shot"><img src="{up}shots/{lang}/{name}.webp" alt="{html.escape(alt)}" '
        f'loading="lazy" data-fit></div>'
    )


def home(lang, up):
    t = C[lang]
    scenes = "".join(
        f'<button type="button" role="tab" id="sc-{img}" data-scene="{img}" aria-controls="try-panel" '
        f'aria-selected="{str(i == 0).lower()}"{"" if i == 0 else " tabindex=\"-1\""}>{h}</button>'
        for i, (h, _, img) in enumerate(t["feats"])
    )
    panels = "".join(
        f'<div class="tryp" data-panel="{img}"{"" if i == 0 else " hidden"}>'
        f'<div class="say"><h3>{h}</h3><p>{p}</p></div>'
        f'<div class="do"><span class="lab">{t["tryH"]}</span><ol>'
        + "".join(f"<li><span>{x}</span></li>" for x in t["tries"][img][0])
        + "</ol>"
        + (f'<p class="donote">{t["tries"][img][1]}</p>' if t["tries"][img][1] else "")
        + "</div></div>"
        for i, (h, p, img) in enumerate(t["feats"])
    )
    first = t["feats"][0][2]
    steps = ""
    for i, s in enumerate(t["steps"]):
        h, p, c1, p2, c2 = (s + [None] * 5)[:5]
        steps += (
            f'<li class="step"><span class="n">{i + 1}</span><div><h3>{h}</h3><p>{p}</p>'
            + (cmd(c1, t) if c1 else "")
            + (f'<p style="margin-top:10px">{p2}</p>' if p2 else "")
            + (cmd(c2, t) if c2 else "")
            + "</div></li>"
        )
    trouble = "".join(f"<dt>{d}</dt><dd>{e}</dd>" for d, e in t["trouble"][1])
    alt = t["installAlt"].replace('href="#install"', 'href="#install"')
    return f"""
<div class="wrap">
  <div class="hero">
    <div>
      <h1>{t["h1"]}</h1>
      <p class="lead">{t["lead"]}</p>
      <p class="req">{t["req"]}</p>
    </div>
    <div class="install">
      <div class="hd"><span>{t["installHd"]}</span><span class="mono" style="font-size:12px">v{VERSION}</span></div>
      <div class="cmd"><code>{INSTALL}</code><button class="copy" type="button" data-copied="{t["copied"]}">{t["copy"]}</button></div>
      <div class="alt">{alt}</div>
    </div>
  </div>
  <div class="shot hero-shot"><img src="{up}shots/{lang}/window.webp" alt="Lythe" width="1600" height="960"></div>
</div>
<section class="wrap feat" id="try">
  <h2>{t["featH"]}</h2>
  <p class="sub">{t["featSub"]}</p>
  <div class="try" data-lang="{lang}" data-up="{up}" data-narrow="{html.escape(t["demoNarrow"])}" data-fail="{html.escape(t["demoFail"])}">
    <div class="scenes" role="tablist">{scenes}</div>
    <div id="try-panel" role="tabpanel">{panels}</div>
    <div class="demo">
      <div class="demo-bar"><span class="demo-note">{t["demoNote"]}</span><a href="{up}demo/{lang}/" target="_blank" rel="noopener">{t["demoOpen"]} ↗</a></div>
      <div class="demo-view"><img class="demo-still" src="{up}shots/{lang}/{first}.webp" alt=""></div>
    </div>
  </div>
</section>
<section class="wrap gs" id="install">
  <h2>{t["gsH"]}</h2>
  <p class="sub">{t["gsSub"]}</p>
  <ol class="steps">{steps}</ol>
  <p style="margin-top:4px;color:var(--fg-2);font-size:14px">{t["update"]}</p>
  <details class="trouble"><summary>{t["trouble"][0]}</summary><dl>{trouble}</dl></details>
  <p style="margin-top:28px">{t["toGuide"].replace("{guide}", "guide/")}</p>
</section>"""


def guide(lang, up):
    t = C[lang]
    side = f'<span class="lab">{t["gLabel"]}</span>' + "".join(
        f'<a href="#g{i + 1}">{i + 1}. {h}</a>' for i, (h, _, _) in enumerate(t["guide"])
    ) + f'<span class="lab">{t["moreLabel"]}</span>' + "".join(
        f'<a href="#{k}">{h}</a>' for k, h, _ in t["more"]
    ) + f'<a href="#keys">{t["keysH"]}</a>'
    steps = "".join(
        f'<section class="gstep" id="g{i + 1}"><div class="hd"><span class="num">{i + 1}</span><h2>{h}</h2></div>'
        f'<div class="txt">{"".join(f"<p>{p}</p>" for p in ps)}</div>'
        f'{shot(lang, img, h, up) if img else ""}</section>'
        for i, (h, ps, img) in enumerate(t["guide"])
    )
    para = lambda p: p if p.startswith(("<pre", "<table")) else f"<p>{p}</p>"  # noqa: E731
    more = "".join(
        f'<section class="gstep more" id="{k}"><div class="hd"><span class="num"></span><h2>{h}</h2></div>'
        f'<div class="txt">{"".join(para(p) for p in ps)}</div></section>'
        for k, h, ps in t["more"]
    )
    keys = "".join(f"<tr><td><kbd>{k}</kbd></td><td>{d}</td></tr>" for k, d in t["keys"])
    return f"""
<div class="wrap guide">
  <nav class="side">{side}</nav>
  <div>
    <h1>{t["gH"]}</h1>
    <p class="intro">{t["gIntro"]}</p>
    {steps}
    <h1 class="moreh">{t["moreH"]}</h1>
    {more}
    <section class="gstep" id="keys"><div class="hd"><span class="num"></span><h2>{t["keysH"]}</h2></div>
      <div class="txt"><table class="keys">{keys}</table></div></section>
  </div>
</div>"""


def page(lang, which):
    t = C[lang]
    here = path_of(lang, which)
    up = "../" * here.count("/")
    other = "ja" if lang == "en" else "en"
    title = "Lythe" if which == "home" else f'{t["gH"]} · Lythe'
    desc = html.escape(t["lead"]) if which == "home" else html.escape(t["gIntro"])
    nav = lambda p, label: (  # noqa: E731
        f'<a href="{up}{path_of(lang, p)}"{" class=\"on\" aria-current=\"page\"" if p == which else ""}>{label}</a>'
    )
    body = home(lang, up) if which == "home" else guide(lang, up)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}{here}">
<link rel="alternate" hreflang="en" href="{SITE}{path_of("en", which)}">
<link rel="alternate" hreflang="ja" href="{SITE}{path_of("ja", which)}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}shots/{lang}/window.webp">
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
{FONTS}
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header class="snav"><div class="wrap">
  <a class="brand" href="{up}{path_of(lang, "home")}">{LOGO}Lythe</a>
  <div class="navr">
    <nav>{nav("home", t["navHome"])}{nav("guide", t["navGuide"])}<a href="{RELEASES}">{t["navReleases"]}</a></nav>
    <div class="lang"><a href="{up}{path_of("en", which)}" hreflang="en"{" aria-current=\"true\"" if lang == "en" else ""}>EN</a><a href="{up}{path_of("ja", which)}" hreflang="ja"{" aria-current=\"true\"" if lang == "ja" else ""}>日本語</a></div>
  </div>
</div></header>
<main>{body}</main>
<footer class="sfoot"><div class="wrap"><span>Lythe {VERSION}</span><a href="{RELEASES}">{t["notes"]}</a><a href="https://github.com/slashkiko/lythe-releases/issues">{t["issue"]}</a></div></footer>
<script src="{up}site.js" defer></script>
</body>
</html>
"""


def main():
    for lang in ("en", "ja"):
        for which in ("home", "guide"):
            out = DOCS / path_of(lang, which) / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page(lang, which), encoding="utf-8")
            print("wrote", out.relative_to(DOCS.parent))
    (DOCS / "style.css").write_text((ROOT / "style.css").read_text(encoding="utf-8"), encoding="utf-8")
    (DOCS / "site.js").write_text((ROOT / "site.js").read_text(encoding="utf-8"), encoding="utf-8")
    (DOCS / "favicon.svg").write_text(LOGO.replace(' aria-hidden="true"', ' xmlns="http://www.w3.org/2000/svg"'), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    # The demo itself (docs/demo/en, docs/demo/ja) is a build of the app's UI on sample data
    # and is copied in by hand; only its start-up script lives here.
    (DOCS / "demo" / "boot.js").write_text((ROOT / "demo-boot.js").read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    main()
