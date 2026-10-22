"""Inlines CSS/JS into single-file HTML previews (with a fake Tauri bridge, sample pages
and sample settings) so the UI can be checked in any browser without building.

  python3 tools/build_preview.py [out_dir]"""
import html, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "preview")
os.makedirs(OUT, exist_ok=True)

NAV = '<header class="site"><nav><a href="/">Home</a> <a href="/about">About</a> <a href="/shop">Shop</a></nav><div class="cookie">We use cookies. <button>OK</button></div></header>'
FOOT = '<footer><p>Copyright Dot Widgets. <a href="/privacy">Privacy</a></p></footer><script>alert("never runs")</script>'
PAGES = {
    "https://dotwidgets.example/how-dot-matrix-works": """<html><head><title>How dot-matrix displays work | Dot Widgets</title>
<meta property="og:title" content="How dot-matrix displays work"><meta property="og:site_name" content="Dot Widgets"><meta name="author" content="The Dot Team"></head>
<body>%s<main><article><h1>How dot-matrix displays work</h1>
<p>Before high-resolution screens, almost every sign, clock and calculator drew its letters from a grid of tiny lights. Each character is a small pattern, usually five dots wide and seven tall, and the trick is choosing which dots to switch on.</p>
<h2>Why five by seven?</h2>
<p>A 5×7 grid is the smallest size where every capital letter is still easy to tell apart. Lower case needs a little more room, because letters like g, j, p, q and y hang below the line. That is why this reader uses nine rows: seven for the letter and two for the tail.</p>
<blockquote>The best dot fonts look simple, but every dot has been argued over.</blockquote>
<h2>Where you still see them</h2>
<ul><li>Departure boards at stations and airports</li><li>Bus fronts and motorway signs</li><li>Old receipt printers and pagers</li><li>This family of desktop widgets</li></ul>
<figure><img src="board.jpg" alt="Departure board"><figcaption>A station departure board at night</figcaption></figure>
<p>Read more about the <a href="/history">history of the 5×7 font</a>, or see how the <a href="/colours">colours were chosen</a>.</p>
<h2>Making text readable</h2>
<p>Spacing matters more than the letters themselves. One empty column between letters and four between words keeps lines tidy, and a little extra space between paragraphs lets your eye find its place again after scrolling.</p>
<ol><li>Headings glow in full colour</li><li>Body text sits a step softer</li><li>Links are blue so you can spot them</li></ol>
<p>That's all there is to it. Café, naïve and “smart quotes” all come out cleanly.</p>
</article></main>%s</body></html>""" % (NAV, FOOT),
    "https://dotwidgets.example/history": """<html><head><title>A short history of the 5×7 font</title></head><body>%s<article><h1>A short history of the 5×7 font</h1>
<p>Early electronic displays had very little memory, so every character had to fit in a handful of bytes. Seven rows of five dots fits neatly into five columns of seven bits each.</p>
<p>Designers soon learned which shapes survived the grid. Round letters became octagons, diagonals became staircases, and the letter M lost a little dignity.</p>
<p>Back to <a href="/how-dot-matrix-works">How dot-matrix displays work</a>.</p></article>%s</body></html>""" % (NAV, FOOT),
    "https://dotwidgets.example/colours": """<html><head><title>Choosing the colours</title></head><body>%s<article><h1>Choosing the colours</h1>
<p>Amber is warm and easy on the eyes at night, which is why so many older displays used it. Green came from early computer terminals, and white is the modern choice.</p>
<p>Try another colour preset in settings, then head <a href="/how-dot-matrix-works">back to the article</a>.</p></article>%s</body></html>""" % (NAV, FOOT),
}
STATE = {"home": "https://dotwidgets.example/how-dot-matrix-works", "rememberLast": False, "W": 180, "H": 130}


def shim():
    return """<script>
window.__PREVIEW__ = true;
window.__SAMPLE_PAGES__ = %s;
var __state = %s;
window.__TAURI__ = {
  core: { invoke: async (cmd, args) => {
    if (cmd === 'load_state') return __state;
    if (cmd === 'save_state') { __state = args.json; return; }
  } },
  event: { listen: async () => () => {} },
  window: { getCurrentWindow: () => ({ setSize: async () => {}, setAlwaysOnTop: async () => {}, startDragging: async () => {} }) },
  dpi: { LogicalSize: function (w, h) { this.width = w; this.height = h; } },
};
</script>""" % (json.dumps(PAGES).replace("</", "<\\/"), json.dumps(json.dumps(STATE)))


def inline(name, head=""):
    src = open(os.path.join(ROOT, "src", name), encoding="utf-8").read()
    src = re.sub(r'<link rel="stylesheet" href="([^"]+)">',
                 lambda m: "<style>" + open(os.path.join(ROOT, "src", m.group(1)), encoding="utf-8").read() + "</style>", src)
    src = re.sub(r'<script src="([^"]+)"></script>',
                 lambda m: "<script>" + open(os.path.join(ROOT, "src", m.group(1)), encoding="utf-8").read()
                 .replace("</script", "<\\/script") + "</script>", src)
    return src.replace("</head>", head + "</head>", 1)


DESK = "<style>body{min-height:100vh;padding:24px;background:linear-gradient(135deg,#3a6186,#89253e)!important}</style>"
widget = inline("index.html", DESK + shim())
open(os.path.join(OUT, "reader-widget-preview.html"), "w", encoding="utf-8").write(widget)
open(os.path.join(OUT, "reader-settings-preview.html"), "w", encoding="utf-8").write(inline("settings.html", shim()))
print("previews written to", os.path.abspath(OUT))
