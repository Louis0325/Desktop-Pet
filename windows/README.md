# Phy 桌寵

直接執行 `dist/PhyDesktopPet.exe`。角色會固定顯示在其他視窗上方。
也可以執行 `dist/PhyDesktopPet-Setup.exe`，透過繁體中文安裝程式加入開始功能表捷徑與解除安裝項目。

- 左鍵拖曳：移動角色
- 眼睛和頭部會跟著滑鼠位置移動
- 動作與追視以平滑影格播放
- 雙擊：打招呼
- 滑鼠滾輪：調整大小
- 右鍵：選擇大小、工作列貼齊或結束；選單依 Windows 顯示語言自動切換（41 種語言，未收錄時使用英文）
- 可以拖到螢幕最底部；手動拖曳後取消自動貼齊，不會強制往上拉

位置和大小儲存在 `%APPDATA%/PhyDesktopPet/settings.json`。程式不會自行開機啟動。
顯示器配置改變時，視窗會回到可見桌面範圍。異常紀錄在 `%APPDATA%/PhyDesktopPet/pet.log` 與 `crash.log`。

要從原始碼重建：先執行 `py -3.14 build_assets.py`，再執行
`py -3.14 -m PyInstaller --noconfirm --clean --onefile --windowed --name PhyDesktopPet --icon assets/phy.ico --add-data "assets;assets" phy_pet.py`。
影格由 `vendor` 內的 phy_friends 原始角色定義產生。
安裝檔可用 Inno Setup 的 `ISCC.exe PhyDesktopPet.iss` 重新編譯。

## 同步到 GitHub 專案

主要編輯位置：`C:\Users\yumin\OneDrive\Desktop\其他\桌面寵物`。
每次更新後，完整同步到 `C:\Users\yumin\OneDrive\Documents\GitHub\Desktop-Pet\windows`。

- 執行 `powershell -ExecutionPolicy Bypass -File .\sync-to-github.ps1`：同步全部專案檔案、動畫影格、預覽、EXE 與安裝檔，並逐檔核對 SHA-256。
- 執行 `powershell -ExecutionPolicy Bypass -File .\build-release.ps1`：重新編譯 EXE 與安裝檔，兩者成功後自動同步。
- 修改角色規格或影格產生流程時，先執行 `py -3.14 build_assets.py`，再執行發行版打包流程。
- 同步只更新本機 GitHub 專案資料夾，不會自動提交或推送。

`AGENTS.md` 記錄後續工作必須同步的規則；在 GitHub 副本工作時也應先修改主要專案，再同步過去。
