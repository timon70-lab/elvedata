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
  // url gir siden en ekte origin – uten den kaster localStorage (brukt av admin) SecurityError.
  url: "https://elvesona.no/",
  runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
  beforeParse(w) {
    w.fetch = () => Promise.resolve({ ok: true, json: async () => ({}), text: async () => "" });
    // get-fellen må gi primitiver for koersjon — ellers:
    // "TypeError: Cannot convert object to primitive value" så snart sidekoden
    // string-koerserer en stub-verdi (f.eks. i en template-streng).
    const stub = new Proxy(function () { return stub; }, {
      get: (t, k) => {
        if (k === Symbol.toPrimitive || k === "toString" || k === "valueOf") return () => "[stub]";
        if (k === Symbol.toStringTag) return "stub";
        if (k === "then") return undefined;   // ikke thenable — ellers henger await på stub
        return stub;
      },
    });
    w.L = stub; w.Chart = stub;           // Leaflet / Chart.js
    w.scrollTo = () => {}; w.HTMLElement.prototype.scrollIntoView = () => {};
    w.matchMedia = () => ({ matches: false, addListener() {}, removeListener() {}, addEventListener() {} });
  },
});
setTimeout(() => {
  if (errors.length) { console.log(errors.slice(0, 10).join("\n")); process.exit(1); }
  console.log("jsdom-røyktest uten JS-feil"); dom.window.close(); process.exit(0);
}, 1500);
