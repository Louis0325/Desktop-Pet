const { app, BrowserWindow, Menu, ipcMain, screen } = require('electron');
const fs = require('fs');
const path = require('path');
const translations = require('./languages.json');
const nativePosition = require('./window-position.cjs');
const getBounds = () => nativePosition.getBounds(win, screen);
const setBounds = bounds => {
  const current = getBounds();
  if (current.width !== bounds.width || current.height !== bounds.height) {
    // Electron must update its fixed-size constraints before Win32 can resize it.
    win.setResizable(true);
    try { win.setSize(bounds.width, bounds.height); }
    finally { win.setResizable(false); }
  }
  nativePosition.setBounds(win, screen, bounds);
};
app.setName('PhyDesktopPet');
app.setPath('userData', path.join(app.getPath('appData'), 'PhyDesktopPet'));
const folder = app.getPath('userData');
fs.mkdirSync(folder, { recursive: true });
const log = message => fs.appendFileSync(path.join(folder, 'pet-js.log'), `${new Date().toISOString()} ${message}\n`);
const settingsFile = path.join(folder, 'settings.json');
let settings = {};
try { settings = JSON.parse(fs.readFileSync(settingsFile, 'utf8')); } catch {}
const sizes = [180, 240, 320];
let win, drag = null, pointerTimer, dock = !!settings.dock_taskbar;
let language, text, latestDiagnostic, restarting = false, failures = 0;
const verify = process.argv.includes('--verify-animation');

function chooseLanguage(tags) {
  for (const tag of tags) {
    const parts = tag.toLowerCase().replaceAll('_', '-').split('-');
    let key = parts[0];
    if (key === 'zh') key = parts.some(p => ['hant', 'tw', 'hk', 'mo'].includes(p)) ? 'zh-Hant' : 'zh-Hans';
    else key = ({ no: 'nb', nn: 'nb', tl: 'fil', iw: 'he' })[key] || key;
    if (translations[key]) return [key, translations[key]];
  }
  return ['en', translations.en];
}
function save() {
  if (!win || win.isDestroyed() || verify) return;
  const bounds = getBounds();
  fs.writeFileSync(settingsFile, JSON.stringify({ x: bounds.x, y: bounds.y,
    height: bounds.height, dock_taskbar: dock }));
}
function safeBounds(x, y, height) {
  const width = Math.round(height * 1.15);
  const area = screen.getDisplayNearestPoint({ x, y }).bounds;
  return { x: Math.max(area.x, Math.min(x, area.x + area.width - width)),
    y: Math.max(area.y, Math.min(y, area.y + area.height - height)), width, height };
}
function alignDock() {
  if (!dock || !win || win.isDestroyed() || drag) return;
  const b = getBounds();
  const area = screen.getDisplayMatching(b).workArea;
  setBounds({ ...b, y: area.y + area.height - b.height });
}
function resize(height) {
  const b = getBounds();
  setBounds(safeBounds(b.x, b.y + b.height - height, height));
  alignDock(); save();
}
function menu() {
  return Menu.buildFromTemplate([
    { label: text[0], submenu: sizes.map((height, i) => ({ label: text[i + 1],
      type: 'radio', checked: getBounds().height === height, click: () => resize(height) })) },
    { label: text[4], type: 'checkbox', checked: dock, click: item => { dock = item.checked; alignDock(); save(); } },
    { type: 'separator' }, { label: text[5], click: () => app.quit() }
  ]);
}
function bFromSettings() {
  const b = getBounds();
  return safeBounds(Number.isFinite(settings.x) ? settings.x : b.x,
    Number.isFinite(settings.y) ? settings.y : b.y, b.height);
}
function createWindow() {
  const primary = screen.getPrimaryDisplay().bounds;
  const height = sizes.includes(settings.height) ? settings.height : 240;
  const b = safeBounds(Number.isFinite(settings.x) ? settings.x : primary.x + primary.width - 260,
    Number.isFinite(settings.y) ? settings.y : primary.y + primary.height - height, height);
  win = new BrowserWindow({ ...b, title: 'Phy 桌寵', frame: false,
    transparent: true, backgroundColor: '#00000000', alwaysOnTop: true,
    skipTaskbar: true, resizable: false, maximizable: false, minimizable: false,
    show: false, webPreferences: { preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true, nodeIntegration: false, sandbox: true, backgroundThrottling: false } });
  win.setAlwaysOnTop(true, 'screen-saver');
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.webContents.on('will-navigate', event => event.preventDefault());
  win.webContents.on('console-message', (_event, level, message) => { if (level >= 2) log(`renderer: ${message}`); });
  win.webContents.on('render-process-gone', (_event, details) => {
    log(`Renderer exited: ${details.reason}`);
    if (++failures <= 3 && !restarting) {
      restarting = true;
      setTimeout(() => { if (!win.isDestroyed()) win.reload(); restarting = false; }, 1000);
    }
  });
  win.on('close', save);
  win.on('closed', () => clearInterval(pointerTimer));
  win.loadFile(path.join(__dirname, 'index.html'));
  pointerTimer = setInterval(() => {
    if (win.isDestroyed()) return;
    const point = screen.getCursorScreenPoint();
    if (drag) {
      const x = point.x - drag.dx, y = point.y - drag.dy;
      const b = getBounds();
      if (x !== b.x || y !== b.y) { drag.moved = true; dock = false; setBounds({ ...b, x, y }); }
    }
    const b = getBounds();
    win.webContents.send('pet:pointer', { x: point.x - b.x, y: point.y - b.y });
  }, 16);
}
function fromPet(event) { return win && !win.isDestroyed() && event.sender === win.webContents; }
ipcMain.on('pet:ready', event => {
  if (!fromPet(event)) return;
  win.showInactive(); setBounds(bFromSettings()); alignDock(); log(`Ready: live JS animation, menu=${language}`);
});
ipcMain.on('pet:menu', event => { if (fromPet(event)) menu().popup({ window: win }); });
ipcMain.on('pet:greet', event => { if (fromPet(event)) log('Double-click: live JS greeting'); });
ipcMain.on('pet:drag-start', event => {
  if (!fromPet(event)) return;
  const point = screen.getCursorScreenPoint(), b = getBounds();
  drag = { dx: point.x - b.x, dy: point.y - b.y, moved: false };
});
function finishDrag() {
  if (!drag) return;
  if (drag.moved) {
    dock = false;
    const b = getBounds(); setBounds(safeBounds(b.x, b.y, b.height));
  }
  drag = null; save();
}
ipcMain.on('pet:drag-end', event => { if (fromPet(event)) finishDrag(); });
ipcMain.on('pet:resize', (event, direction) => {
  if (!fromPet(event) || ![-1, 1].includes(direction)) return;
  resize(sizes[Math.max(0, Math.min(2, sizes.indexOf(getBounds().height) + direction))]);
});
ipcMain.on('pet:diagnostic', (event, state) => {
  if (!fromPet(event)) return;
  latestDiagnostic = state;
  if (state.frames < 300 || state.greetingActive) log(`Animation: ${JSON.stringify(state)}`);
});

async function verifyAnimation() {
  const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
  try {
    await delay(2200);
    const idle = latestDiagnostic;
    if (!idle || idle.frames < 30 || idle.changes < 30) throw Error('Idle animation did not advance');
    await win.webContents.executeJavaScript("document.getElementById('pet').dispatchEvent(new MouseEvent('dblclick', {bubbles:true}))");
    await delay(1000);
    const greeting = latestDiagnostic;
    if (!greeting || greeting.greetings !== 1 || !greeting.greetingActive) throw Error('Double-click did not animate');
    const preview = await win.webContents.capturePage();
    fs.writeFileSync(path.join(folder, 'phy-js-greeting-preview.png'), preview.toPNG());
    await delay(1600);
    if (latestDiagnostic.greetingActive) throw Error('Greeting did not return to idle');
    const resources = await win.webContents.executeJavaScript("performance.getEntriesByType('resource').map(r=>r.name)");
    if (resources.some(r => /\.(png|webp|gif)(?:$|\?)/i.test(r))) throw Error('Raster animation loaded');
    const b = getBounds(), display = screen.getDisplayMatching(b).bounds;
    dock = true;
    drag = { moved: true };
    setBounds(safeBounds(b.x, display.y + display.height - b.height, b.height));
    finishDrag();
    await delay(4000);
    const bottom = getBounds();
    if (dock) throw Error('Dragging did not disable taskbar docking');
    if (bottom.y + bottom.height !== display.y + display.height) throw Error('Window was pulled up from the screen bottom');
    const sizeChecks = [];
    for (const index of [2, 0, 1]) {
      menu().items[0].submenu.items[index].click();
      await delay(300);
      const actual = getBounds();
      const viewport = await win.webContents.executeJavaScript('({ width: innerWidth, height: innerHeight })');
      if (actual.height !== sizes[index] || viewport.height !== sizes[index] || actual.width !== viewport.width) {
        throw Error(`Size menu failed: expected ${sizes[index]}, window=${JSON.stringify(actual)}, viewport=${JSON.stringify(viewport)}`);
      }
      if (actual.y + actual.height !== display.y + display.height) throw Error('Size change lost screen-bottom placement');
      if (!menu().items[0].submenu.items[index].checked) throw Error('Size menu selection not updated');
      sizeChecks.push({ height: sizes[index], viewport, bottom: actual.y + actual.height });
    }
    const idlePreview = await win.webContents.capturePage();
    fs.writeFileSync(path.join(folder, 'phy-js-idle-preview.png'), idlePreview.toPNG());
    const report = { version: app.getVersion(), language, idle, greeting, final: latestDiagnostic,
      sizeChecks, rasterResources: 0, bottomPlacement: true, windowBottom: bottom.y + bottom.height, screenBottom: display.y + display.height, alwaysOnTop: win.isAlwaysOnTop(),
      menuLabels: menu().items.filter(i => i.label).map(i => i.label) };
    fs.writeFileSync(path.join(folder, 'js-animation-check.json'), JSON.stringify(report, null, 2));
    log('Live JavaScript animation verification passed'); app.exit(0);
  } catch (error) { log(`Verification failed: ${error.stack}`); app.exit(1); }
}
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on('second-instance', () => {
    if (!win || win.isDestroyed()) return;
    const point = screen.getCursorScreenPoint(), b = getBounds();
    setBounds(safeBounds(point.x - b.width / 2 | 0, point.y - b.height / 2 | 0, b.height));
    win.showInactive();
  });
  app.whenReady().then(() => {
    [language, text] = chooseLanguage(app.getPreferredSystemLanguages());
    log(`Starting PhyDesktopPet ${app.getVersion()} pid=${process.pid}`);
    createWindow();
    screen.on('display-metrics-changed', () => {
      if (!drag && win && !win.isDestroyed()) { const b = getBounds(); setBounds(safeBounds(b.x, b.y, b.height)); alignDock(); }
    });
    if (verify) win.webContents.once('did-finish-load', verifyAnimation);
  });
  app.on('window-all-closed', () => app.quit());
}
