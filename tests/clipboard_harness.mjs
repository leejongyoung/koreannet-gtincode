// web.py 의 페이지 스크립트를 최소한의 가짜 DOM 위에서 실행해 클립보드 동작을 확인한다.
// 입력(stdin): {"script": "...", "secure": bool, "clipboard": "ok"|"deny"|"none"}
// 출력(stdout): JSON 결과
import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(0, "utf8"));

class El {
  constructor(tag) {
    this.tag = tag; this.children = []; this.listeners = {}; this.attrs = {};
    this.value = ""; this.textContent = ""; this.className = ""; this.disabled = false;
    this.hidden = false; this.title = ""; this.placeholder = ""; this.onclick = null; this.focused = false; this.selected = false;
  }
  append(...n) { this.children.push(...n); }
  replaceChildren(...n) { this.children = [...n]; }
  addEventListener(type, fn) { this.listeners[type] = fn; }
  setAttribute(k, v) { this.attrs[k] = v; }
  focus() { this.focused = true; }
  select() { this.selected = true; }
  remove() {}
  find(pred, out = []) { if (pred(this)) out.push(this); for (const c of this.children) c.find && c.find(pred, out); return out; }
}

const ids = {};
const document = {
  getElementById(id) { return ids[id] || (ids[id] = new El("#" + id)); },
  createElement(tag) { return new El(tag); },
};
const writes = [];
const clipboard = input.clipboard === "none" ? undefined : {
  writeText: async (t) => { if (input.clipboard === "deny") throw new Error("NotAllowedError"); writes.push(t); },
  readText: async () => { if (input.clipboard === "deny") throw new Error("NotAllowedError"); return "8801045759296"; },
};
const product = { gtin: "8801045759296", name: "테스트 상품", image_url: "" };
globalThis.window = { isSecureContext: input.secure };
globalThis.document = document;
Object.defineProperty(globalThis, "navigator", { value: { clipboard }, configurable: true, writable: true });
globalThis.fetch = async () => ({ ok: true, json: async () => product });

new Function(input.script)();

document.getElementById("q").value = "8801045759296";
await ids.f.listeners.submit({ preventDefault() {} });
const out = ids.out;
const card = out.children[0];
const buttons = card.find((e) => e.tag === "button");
const jsonButton = buttons.find((b) => b.textContent === "JSON 복사");
const nameButton = buttons.find((b) => b.textContent === "상품명 복사");
await jsonButton.onclick();
const manual = card.find((e) => e.className === "manual")[0];
const area = manual.find((e) => e.tag === "textarea")[0];
const afterJson = { manualHidden: manual.hidden, area: area ? area.value : null, msg: ids.msg.textContent, msgClass: ids.msg.className, writes: [...writes] };
await nameButton.onclick();
const afterName = { manualHidden: manual.hidden, writes: [...writes], msg: ids.msg.textContent };
console.log(JSON.stringify({
  pasteDisabled: ids.paste.disabled, pastePlaceholder: ids.q.placeholder, afterJson, afterName,
  jsonText: JSON.stringify(product, null, 2),
}));
