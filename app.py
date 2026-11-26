# kaomojimaker - かおもじメーカー
# パーツ（輪郭・目・口・頬・腕・装飾）を選んで顔文字を組み立てる単一ファイルアプリ。
# 組み立て・ランダム・コピー・お気に入り保存はすべてブラウザ側（JavaScript）で行い、
# サーバー側に状態は持たない。お気に入りは localStorage にのみ保存される。

from flask import Flask, render_template_string

app = Flask(__name__)

CSS = """
* { box-sizing: border-box;}
body {
margin: 0;
font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans",
"Noto Sans JP", "Yu Gothic", sans-serif;
background: #fff7f0;
color: #333;
}
main { max-width: 720px; margin: 0 auto; padding: 16px;}
h1 { font-size: 1.5rem; text-align: center; margin: 12px 0 4px;}
.sub { text-align: center; color: #888; font-size: 0.85rem; margin: 0 0 16px;}
.preview {
background: #fff;
border: 2px solid #ffb59e;
border-radius: 16px;
padding: 28px 12px;
text-align: center;
font-size: 2rem;
min-height: 96px;
word-break: break-all;
box-shadow: 0 2px 8px rgba(255, 150, 110, 0.15);
}
.actions { display: flex; gap: 8px; justify-content: center; margin: 14px 0 4px; flex-wrap: wrap;}
button.act {
border: none; border-radius: 999px; padding: 10px 18px;
font-size: 0.95rem; cursor: pointer; color: #fff; background: #ff8c66;
}
button.act.sub2 { background: #ffa98f;}
button.act:active { transform: scale(0.97);}
.feedback { text-align: center; color: #e0653a; font-size: 0.85rem; min-height: 1.2em; margin: 4px 0 0;}
section { margin-top: 20px;}
h2 { font-size: 1rem; margin: 0 0 8px; color: #b3542e;}
.chips { display: flex; flex-wrap: wrap; gap: 6px;}
.chip {
border: 2px solid #ffd9c9; background: #fff; border-radius: 999px;
padding: 6px 12px; font-size: 1rem; cursor: pointer; line-height: 1.4;
}
.chip.selected { border-color: #ff8c66; background: #ffe9df; font-weight: bold;}
.chip.fav { display: inline-flex; align-items: center; gap: 6px;}
.chip.del {
border: none; background: #ffb59e; color: #fff; border-radius: 50%;
width: 20px; height: 20px; line-height: 1; cursor: pointer; font-size: 0.8rem;
}
.note { color: #999; font-size: 0.8rem; margin-top: 6px;}
.empty { color: #bbb; font-size: 0.9rem;}
footer { text-align: center; color: #bbb; font-size: 0.75rem; margin: 28px 0 8px;}
"""

SCRIPT = """
var PARTS = {
frame: [
{ label: "()", open: "(", close: ")"},
{ label: "（ ）", open: "（", close: "）"},
{ label: "[]", open: "[", close: "]"},
{ label: "{}", open: "{", close: "}"},
{ label: "| |", open: "|", close: "|"},
{ label: "", open: ""},
{ label: "〔 〕", open: "〔", close: "〕"},
{ label: "ʕ ʔ", open: "ʕ", close: "ʔ"},
{ label: "< >", open: "<", close: ">"},
{ label: "なし", open: "", close: ""}
],
eyes: [
{ label: "・ ・", l: "・", r: "・"},
{ label: "＾ ＾", l: "＾", r: "＾"},
{ label: "◕ ◕", l: "◕", r: "◕"},
{ label: "¬ ¬", l: "¬", r: "¬"},
{ label: "＞ ＜", l: "＞", r: "＜"},
{ label: "> <", l: ">", r: "<"},
{ label: "´ `", l: "´", r: "`"},
{ label: "● ●", l: "●", r: "●"},
{ label: "╥ ╥", l: "╥", r: "╥"},
{ label: "⊙ ⊙", l: "⊙", r: "⊙"},
{ label: "￣ ￣", l: "￣", r: "￣"},
{ label: "T T", l: "T", r: "T"},
{ label: "★ ★", l: "★", r: "★"}
],
mouth: [
{ label: "ω", v: "ω"},
{ label: "▽", v: "▽"},
{ label: "∀", v: "∀"},
{ label: "‿", v: "‿"},
{ label: "◡", v: "◡"},
{ label: "︵", v: "︵"},
{ label: "Д", v: "Д"},
{ label: "□", v: "□"},
{ label: "ｏ", v: "ｏ"},
{ label: "へ", v: "へ"},
{ label: "ε", v: "ε"},
{ label: "３", v: "３"},
{ label: "ᴥ", v: "ᴥ"}
],
cheek: [
{ label: "なし", l: "", r: ""},
{ label: "＊ ＊", l: "＊", r: "＊"},
{ label: "// //", l: "//", r: "//"},
{ label: "/// ///", l: "///", r: "///"},
{ label: "♡ ♡", l: "♡", r: "♡"},
{ label: "✿ ✿", l: "✿", r: "✿"},
{ label: "# #", l: "#", r: "#"},
{ label: "＠ ＠", l: "＠", r: "＠"},
{ label: "✧ ✧", l: "✧", r: "✧"}
],
arm: [
{ label: "なし", l: "", r: ""},
{ label: "ヽ ﾉ", l: "ヽ", r: "ﾉ"},
{ label: "＼ ／", l: "＼", r: "／"},
{ label: "⊂ ⊃", l: "⊂", r: "⊃"},
{ label: "ᕦ ᕤ", l: "ᕦ", r: "ᕤ"},
{ label: "╰ ╯", l: "╰", r: "╯"},
{ label: "٩ و", l: "٩", r: "و"},
{ label: "o o", l: "o", r: "o"}
],
deco: [
{ label: "なし", v: ""},
{ label: "✧", v: "✧"},
{ label: "♪", v: "♪"},
{ label: "♫", v: "♫"},
{ label: "♡", v: "♡"},
{ label: "★", v: "★"},
{ label: "☆", v: "☆"},
{ label: "✿", v: "✿"},
{ label: "❀", v: "❀"},
{ label: "+", v: "+"}
]
};

var PRESETS = [
{ name: "(・∀・)", sel: { frame: 0, eyes: 0, mouth: 2, cheek: 0, arm: 0, deco: 0}},
{ name: "(´ω`)", sel: { frame: 0, eyes: 6, mouth: 0, cheek: 0, arm: 0, deco: 0}},
{ name: "(＾▽＾)", sel: { frame: 0, eyes: 1, mouth: 1, cheek: 0, arm: 0, deco: 0}},
{ name: "ヽ(・∀・)ﾉ", sel: { frame: 0, eyes: 0, mouth: 2, cheek: 0, arm: 1, deco: 0}},
{ name: "(//・ω・//)", sel: { frame: 0, eyes: 0, mouth: 0, cheek: 2, arm: 0, deco: 0}},
{ name: "ʕ・ᴥ・ʔ", sel: { frame: 7, eyes: 0, mouth: 12, cheek: 0, arm: 0, deco: 0}},
{ name: "(╥□╥)", sel: { frame: 0, eyes: 8, mouth: 7, cheek: 0, arm: 0, deco: 0}},
{ name: "(★ω★)", sel: { frame: 0, eyes: 12, mouth: 0, cheek: 0, arm: 0, deco: 0}},
{ name: "⊂(・∀・)⊃", sel: { frame: 0, eyes: 0, mouth: 2, cheek: 0, arm: 3, deco: 0}},
{ name: "(⊙□⊙)", sel: { frame: 0, eyes: 9, mouth: 7, cheek: 0, arm: 0, deco: 0}}
];

var CATEGORIES = [
{ key: "frame", title: "輪郭"},
{ key: "eyes", title: "目"},
{ key: "mouth", title: "口"},
{ key: "cheek", title: "頬・照れ"},
{ key: "arm", title: "腕・手"},
{ key: "deco", title: "装飾"}
];

var sel = { frame: 0, eyes: 0, mouth: 0, cheek: 0, arm: 0, deco: 0};
var current = "";
var FAV_KEY = "kaomojimaker-favorites";

function assemble() {
var f = PARTS.frame[sel.frame];
var e = PARTS.eyes[sel.eyes];
var m = PARTS.mouth[sel.mouth];
var c = PARTS.cheek[sel.cheek];
var a = PARTS.arm[sel.arm];
var d = PARTS.deco[sel.deco];
return d.v + a.l + f.open + c.l + e.l + m.v + e.r + c.r + f.close + a.r;
}

function render() {
current = assemble();
document.getElementById("preview").textContent = current;
CATEGORIES.forEach(function (cat) {
var box = document.getElementById("chips-" + cat.key);
var chips = box.children;
for (var i = 0; i < chips.length; i++) {
if (i === sel[cat.key]) chips[i].classList.add("selected");
else chips[i].classList.remove("selected");
}
});
}

function buildChips() {
CATEGORIES.forEach(function (cat) {
var box = document.getElementById("chips-" + cat.key);
PARTS[cat.key].forEach(function (opt, idx) {
var b = document.createElement("button");
b.type = "button";
b.className = "chip";
b.textContent = opt.label;
b.addEventListener("click", function () {
sel[cat.key] = idx;
render();
});
box.appendChild(b);
});
});
}

function buildPresets() {
var box = document.getElementById("presets");
PRESETS.forEach(function (p) {
var b = document.createElement("button");
b.type = "button";
b.className = "chip";
b.textContent = p.name;
b.addEventListener("click", function () {
Object.keys(p.sel).forEach(function (k) { sel[k] = p.sel[k];});
render();
});
box.appendChild(b);
});
}

function showFeedback(msg) {
var el = document.getElementById("feedback");
el.textContent = msg;
setTimeout(function () { el.textContent = "";}, 2000);
}

function randomize() {
CATEGORIES.forEach(function (cat) {
sel[cat.key] = Math.floor(Math.random() * PARTS[cat.key].length);
});
render();
}

function copyCurrent() {
function done() { showFeedback("コピーした！");}
if (navigator.clipboard && navigator.clipboard.writeText) {
navigator.clipboard.writeText(current).then(done, function () { fallbackCopy(done);});
} else {
fallbackCopy(done);
}
}

function fallbackCopy(done) {
var ta = document.createElement("textarea");
ta.value = current;
ta.style.position = "fixed";
ta.style.opacity = "0";
document.body.appendChild(ta);
ta.select();
try { document.execCommand("copy");} catch (e) {}
document.body.removeChild(ta);
done();
}

function loadFavorites() {
try {
var raw = localStorage.getItem(FAV_KEY);
var arr = raw? JSON.parse(raw): [];
return Array.isArray(arr)? arr: [];
} catch (e) {
return [];
}
}

function saveFavorites(arr) {
try { localStorage.setItem(FAV_KEY, JSON.stringify(arr));} catch (e) {}
}

function renderFavorites() {
var box = document.getElementById("favorites");
box.innerHTML = "";
var favs = loadFavorites();
if (favs.length === 0) {
var span = document.createElement("span");
span.className = "empty";
span.textContent = "まだ保存されていません";
box.appendChild(span);
return;
}
favs.forEach(function (text, idx) {
var chip = document.createElement("span");
chip.className = "chip fav";
var label = document.createElement("span");
label.textContent = text;
label.addEventListener("click", function () {
document.getElementById("preview").textContent = text;
current = text;
});
var del = document.createElement("button");
del.type = "button";
del.className = "del";
del.textContent = "×";
del.title = "削除";
del.addEventListener("click", function () {
var arr = loadFavorites();
arr.splice(idx, 1);
saveFavorites(arr);
renderFavorites();
});
chip.appendChild(label);
chip.appendChild(del);
box.appendChild(chip);
});
}

function addFavorite() {
var arr = loadFavorites();
if (arr.indexOf(current) >= 0) {
showFeedback("もう保存されているよ");
return;
}
arr.push(current);
saveFavorites(arr);
renderFavorites();
showFeedback("お気に入りに保存した！");
}

document.getElementById("btn-random").addEventListener("click", randomize);
document.getElementById("btn-copy").addEventListener("click", copyCurrent);
document.getElementById("btn-fav").addEventListener("click", addFavorite);

buildChips();
buildPresets();
renderFavorites();
render();
"""

PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>かおもじメーカー | kaomojimaker</title>
<style>{{ css|safe}}</style>
</head>
<body>
<main>
<h1>かおもじメーカー</h1>
<p class="sub">パーツを選んで、自分だけの顔文字を組み立てよう</p>

<div class="preview" id="preview"></div>

<div class="actions">
<button type="button" class="act" id="btn-random">ランダム</button>
<button type="button" class="act" id="btn-copy">コピー</button>
<button type="button" class="act sub2" id="btn-fav">お気に入りに保存</button>
</div>
<p class="feedback" id="feedback"></p>

<section>
<h2>輪郭</h2>
<div class="chips" id="chips-frame"></div>
</section>
<section>
<h2>目</h2>
<div class="chips" id="chips-eyes"></div>
</section>
<section>
<h2>口</h2>
<div class="chips" id="chips-mouth"></div>
</section>
<section>
<h2>頬・照れ</h2>
<div class="chips" id="chips-cheek"></div>
</section>
<section>
<h2>腕・手</h2>
<div class="chips" id="chips-arm"></div>
</section>
<section>
<h2>装飾</h2>
<div class="chips" id="chips-deco"></div>
</section>

<section>
<h2>プリセット</h2>
<div class="chips" id="presets"></div>
</section>

<section>
<h2>お気に入り</h2>
<div class="chips" id="favorites"></div>
<p class="note">お気に入りはこのブラウザの中だけに保存されます（サーバーには送られません）。クリックで読み込み、×で削除できます。</p>
</section>

<footer>kaomojimaker</footer>
</main>
<script>{{ script|safe}}</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE, css=CSS, script=SCRIPT)


@app.route("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
