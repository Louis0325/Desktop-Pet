# Phy 桌寵 — JavaScript 動畫版 1.1.2

執行 `dist/PhyDesktopPet.exe`，或使用 `dist/PhyDesktopPet-Setup.exe` 安裝。
角色透明、固定在其他視窗上方，滑鼠移動時眼睛和頭部會跟著看。

## 操作

- 左鍵拖曳：自由擺放，可以拖到螢幕最底部；放開後不會強制往上拉。
- 雙擊：即時播放 1.5 秒小跳躍、搖尾巴、耳朵與開心表情，之後回到待機；再次雙擊可以重播。
- 滑鼠滾輪：調整大小。
- 右鍵：大小、工作列貼齊、結束。選單依 Windows 顯示語言自動選擇 41 種翻譯，未收錄時使用英文。

## 即時動畫

`desktop/renderer.js` 透過 `requestAnimationFrame` 計算姿勢，直接更新 SVG 元素。
角色規格位於 `vendor/phy.js`，繪圖引擎是 `vendor/phyfriends.js`，動作函數是 `vendor/anim.js`。
`desktop/character-adapter.js` 處理新角色規格與繪圖引擎的相容性。
動畫不載入 PNG、WebP 或 GIF 影格，也不需要預先產生影格。

程式使用 Electron；需要 Node.js 22.12 以上重建。`assets/phy.ico` 僅用於 EXE 和安裝程式圖示。
`desktop/languages.json` 包含右鍵選單翻譯。`desktop/window-position.cjs` 透過 Koffi 呼叫 Windows 原生定位，使用實際視窗座標避開工作列限制；角色繪圖靠底對齊。

## 重建與同步

主要編輯位置：`C:\Users\yumin\OneDrive\Desktop\其他\桌面寵物`。
同步位置：`C:\Users\yumin\OneDrive\Documents\GitHub\Desktop-Pet\windows`。

- `npm ci`，再執行 `node node_modules/electron/install.js`：安裝開發依賴與 Electron。
- `npm start`：啟動開發版。
- `powershell -ExecutionPolicy Bypass -File .\build-release.ps1`：安裝依賴、重建便攜 EXE 和 Inno Setup 安裝檔，成功後完整同步並核對 SHA-256。
- `powershell -ExecutionPolicy Bypass -File .\sync-to-github.ps1`：單獨同步專案及發行檔。會移除目標 `windows` 資料夾中已淘汰的檔案，保留 GitHub 專案根目錄。
- `dist\win-unpacked\PhyDesktopPet.exe --verify-animation`：驗證即時動畫、雙擊、回到待機、底部位置、大→小→中選單切換及實際繪圖尺寸與零點陣動畫資源。測試結束後自行關閉。

`node_modules` 是可由 `package-lock.json` 還原的本機依賴快取，不會同步或提交。
同步不會自動提交或推送 GitHub。後續更新同步規則記錄在 `AGENTS.md`。

位置與大小仍儲存在 `%APPDATA%\PhyDesktopPet\settings.json`，沿用舊版本設定。
診斷紀錄是 `%APPDATA%\PhyDesktopPet\pet-js.log`，動畫測試報告是 `js-animation-check.json`。
程式不會自行開機啟動；繪圖程序異常退出時會嘗試恢復。
