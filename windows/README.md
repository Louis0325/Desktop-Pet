# Phy 桌寵

直接執行 `dist/PhyDesktopPet.exe`。角色會固定顯示在其他視窗上方。
也可以執行 `dist/PhyDesktopPet-Setup.exe`，透過繁體中文安裝程式加入開始功能表捷徑與解除安裝項目。

- 左鍵拖曳：移動角色
- 眼睛和頭部會跟著滑鼠位置移動
- 動作與追視以平滑影格播放
- 雙擊：打招呼
- 滑鼠滾輪：調整大小
- 右鍵：選擇大小或結束

位置和大小儲存在 `%APPDATA%/PhyDesktopPet/settings.json`。程式不會自行開機啟動。
顯示器配置改變時，視窗會回到可見桌面範圍。異常紀錄在 `%APPDATA%/PhyDesktopPet/pet.log` 與 `crash.log`。

要從原始碼重建：先執行 `py -3.14 build_assets.py`，再執行
`py -3.14 -m PyInstaller --noconfirm --clean --onefile --windowed --name PhyDesktopPet --icon assets/phy.ico --add-data "assets;assets" phy_pet.py`。
影格由 `vendor` 內的 phy_friends 原始角色定義產生。
安裝檔可用 Inno Setup 的 `ISCC.exe PhyDesktopPet.iss` 重新編譯。
