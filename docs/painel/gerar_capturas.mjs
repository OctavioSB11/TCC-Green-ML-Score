// Capturas em alta resolução do GreenML Dashboard (T8), via Chrome headless e CDP.
// Reproduz o estado de cada tela do roteiro (docs/painel/roteiro_demonstracao.md) e
// salva PNGs de 3200x1800 (1600x900 com densidade 2). Usa só o Chrome instalado e o
// Node 22 (WebSocket nativo), sem pacotes extras. Com o painel aberto em
// http://localhost:8501 (de preferência com --client.toolbarMode viewer):
//   node docs\painel\gerar_capturas.mjs "C:\Program Files\Google\Chrome\Application\chrome.exe" docs\painel\slides %TEMP%\chrome-capturas
import { spawn } from "node:child_process";
import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";

const [chromePath, outDir, profileDir, baseUrl] = process.argv.slice(2);
const BASE = baseUrl || "http://localhost:8501"; // 4º argumento opcional
const PORT = 9333;
const W = 1600, H = 900, DSF = 2;
mkdirSync(outDir, { recursive: true });

const chrome = spawn(chromePath, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profileDir}`,
  `--window-size=${W},${H}`, "--hide-scrollbars", "--no-first-run", "--lang=pt-BR",
  "about:blank",
], { stdio: "ignore" });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, seq = 0;
const pending = new Map();

async function connect() {
  for (let i = 0; i < 50; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
      const page = list.find((t) => t.type === "page");
      if (page) {
        ws = new WebSocket(page.webSocketDebuggerUrl);
        await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
        ws.onmessage = (ev) => {
          const msg = JSON.parse(ev.data);
          if (msg.id && pending.has(msg.id)) {
            const { resolve, reject } = pending.get(msg.id);
            pending.delete(msg.id);
            msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
          }
        };
        return;
      }
    } catch { /* Chrome ainda abrindo */ }
    await sleep(200);
  }
  throw new Error("Chrome não respondeu");
}

function send(method, params = {}) {
  const id = ++seq;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
}

async function js(expression) {
  const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " " + expression);
  return r.result.value;
}

const HELPERS = `
window.__vis = (e) => e && e.offsetParent !== null;
window.__byText = (sel, text) => [...document.querySelectorAll(sel)]
  .filter((e) => __vis(e) && e.innerText && e.innerText.trim() === text).pop();
window.__label = (text) => [...document.querySelectorAll('[data-testid="stWidgetLabel"]')]
  .filter((e) => __vis(e) && e.innerText && e.innerText.trim().startsWith(text)).pop();
window.__center = (e) => { const r = e.getBoundingClientRect();
  return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; };
window.__scrollParent = (e) => { let c = e.parentElement;
  while (c && !(c.scrollHeight > c.clientHeight + 2 &&
    /(auto|scroll)/.test(getComputedStyle(c).overflowY))) c = c.parentElement;
  return c || document.scrollingElement; };
`;

async function waitText(text, timeout = 60000) {
  const t0 = Date.now();
  while (Date.now() - t0 < timeout) {
    const ok = await js(`document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
    if (ok) return;
    await sleep(300);
  }
  throw new Error("Texto não apareceu: " + text);
}

async function settle(ms = 2500) {
  // Espera o Streamlit terminar de rodar o script e os gráficos desenharem.
  const t0 = Date.now();
  while (Date.now() - t0 < 60000) {
    const running = await js(`!!document.querySelector('[data-testid="stStatusWidget"]')`);
    if (!running) break;
    await sleep(300);
  }
  await sleep(ms);
}

async function clickAt({ x, y }) {
  for (const type of ["mouseMoved", "mousePressed", "mouseReleased"]) {
    await send("Input.dispatchMouseEvent", { type, x, y, button: "left", clickCount: 1 });
  }
}

async function clickExpr(expr, what) {
  const c = await js(`(() => { ${HELPERS}; const e = (${expr}); if (!e) return null;
    e.scrollIntoView({ block: "center" }); return __center(e); })()`);
  if (!c) throw new Error("Elemento não encontrado: " + what);
  await sleep(300);
  await clickAt(c);
}

async function nav(path, title) {
  await clickExpr(`[...document.querySelectorAll('[data-testid="stSidebarNav"] a')]
    .find((a) => new URL(a.href).pathname === "/${path}")`, "menu " + path);
  await waitText(title);
  await settle();
}

async function choose(label, option) {
  await clickExpr(`(__label(${JSON.stringify(label)}) || {closest: () => null})
    .closest('[data-testid="stSelectbox"]')?.querySelector('button[aria-haspopup="listbox"], [role="combobox"]')`, "seletor " + label);
  await sleep(500);
  await clickExpr(`__byText('[role="option"]', ${JSON.stringify(option)})`, "opção " + option);
  await settle();
}

async function scrollTo(text, sel = "h1, h2, h3, p, button", offset = 90) {
  const ok = await js(`(() => { ${HELPERS}; const e = __byText(${JSON.stringify(sel)}, ${JSON.stringify(text)});
    if (!e) return false; e.scrollIntoView({ block: "start" });
    __scrollParent(e).scrollTop -= ${offset}; return true; })()`);
  if (!ok) throw new Error("Âncora não encontrada: " + text);
  await sleep(1500);
}

async function scrollTop() {
  await js(`(() => { ${HELPERS}; const h = document.querySelector("h1");
    if (h) __scrollParent(h).scrollTop = 0; })()`);
  await sleep(800);
}

async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(join(outDir, name), Buffer.from(r.data, "base64"));
  console.log("ok", name);
}

try {
  await connect();
  await send("Page.enable");
  await send("Runtime.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: DSF, mobile: false });
  await send("Page.navigate", { url: BASE + "/" });
  await waitText("GreenML Dashboard");
  await settle();
  await shot("00_inicio.png");

  // Conjunto de dados do roteiro: Covertype (barra lateral; vale para todas as telas).
  await choose("Conjunto de dados", "Covertype");

  // 1. Visão geral
  await nav("visao_geral", "Visão geral: Covertype");
  await scrollTop();
  await shot("01_visao_geral_cartoes.png");
  await scrollTo("Rankings por critério", '[role="tab"], [role="tab"] p', 70);
  await shot("02_visao_geral_rankings.png");

  // 2. Qualidade × custo
  await nav("qualidade_custo", "Qualidade × custo: Covertype");
  await scrollTop();
  await scrollTo("Mostrar as dez sementes", "label p, p", 70);
  await shot("03_qualidade_custo_pareto.png");
  await scrollTo("Custo em relação à Regressão Logística", "h3", 40);
  await shot("04_qualidade_custo_custo_marginal.png");

  // 3. Simulador com todo o peso no carbono
  await nav("simulador", "Simulador de contexto: Covertype");
  await clickExpr(`__byText('button', 'Só carbono')`, "perfil Só carbono");
  await waitText("O contexto mudou a escolha do modelo");
  await settle(4000);
  await scrollTop();
  await shot("05_simulador_so_carbono.png");
  await scrollTo("Regiões no mapa", "h3", 40);
  await sleep(4000); // fundo do mapa vem da internet
  await shot("06_simulador_mapa.png");
  await scrollTo("GMS de cada modelo em cada região", "h3", 40);
  await shot("07_simulador_mapa_de_calor.png");

  // 4. Cartão ambiental: XGBoost em Estocolmo, só carbono
  await nav("cartao", "Cartão ambiental: Covertype");
  await choose("Região de execução", "AWS-Stockholm");
  await choose("Perfil de pesos do GMS", "Só carbono");
  await waitText("XGBoost em AWS-Stockholm");
  await scrollTop();
  await scrollTo("Modelo", '[data-testid="stWidgetLabel"] p', 70);
  await shot("08_cartao_ambiental.png");
  await scrollTo("Baixar o cartão", "h3", 40);
  await shot("09_cartao_downloads.png");

  // 5. Avalie seu modelo (dados de exemplo do Covertype)
  await nav("avalie", "Avalie seu modelo");
  await scrollTo("3. Resultado", "h3", 40);
  await shot("10_avalie_seu_modelo.png");
} catch (err) {
  console.error("ERRO:", err.message);
  try { console.error(await js(`(() => { ${HELPERS}; return [...document.querySelectorAll('[data-testid="stWidgetLabel"]')].map((e) => JSON.stringify(e.innerText) + " vis=" + __vis(e) + " label=" + !!__label("Conjunto")); })()`)); } catch (e2) { console.error("diag", e2.message); }
  try { await shot("erro.png"); } catch { /* sem conexão */ }
  process.exitCode = 1;
} finally {
  try { ws?.close(); } catch { /* ignorar */ }
  chrome.kill();
}
