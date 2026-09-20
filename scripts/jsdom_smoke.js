// Røyktest: laster HTML i jsdom, kjører inline-script, feiler på JS-unntak.
// Nettverkskall (fetch/NVE) stubbes; eksterne script (Leaflet/Chart.js) lastes ikke.
let JSDOM, VirtualConsole;
try { ({ JSDOM, VirtualConsole } = require("jsdom")); } catch { process.exit(3); }
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const errors = [];
const vc = new VirtualConsole();
vc.on("jsdomError", e => { if (!/Could not load|Not implemented/.test(e.message)) errors.push(e.message); });
const dom = new JSDOM(html, {
  runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
  beforeParse(w) {
    w.fetch = () => Promise.resolve({ ok: true, json: async () => ({}), text: async () => "" });
    const stub = new Proxy(function () { return stub; }, { get: () => stub });
    w.L = stub; w.Chart = stub;           // Leaflet / Chart.js
    w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = () => {};
    w.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {} });
  },
});
setTimeout(() => {
  if (errors.length) { console.log(errors.slice(0, 10).join("\n")); process.exit(1); }
  console.log("jsdom-røyktest uten JS-feil"); dom.window.close(); process.exit(0);
}, 1500);
