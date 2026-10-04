// Use physical Win32 bounds so taskbar work-area constraints cannot lift the pet.
const koffi = require('koffi');
const user32 = koffi.load('user32.dll');
const Rect = koffi.struct('PetRect', { left: 'long', top: 'long', right: 'long', bottom: 'long' });
const getRect = user32.func('bool __stdcall GetWindowRect(void *hwnd, _Out_ PetRect *rect)');
const setPosition = user32.func('bool __stdcall SetWindowPos(void *hwnd, void *after, int x, int y, int width, int height, uint flags)');
const handle = win => win.getNativeWindowHandle().readBigUInt64LE();
exports.getBounds = (win, screen) => {
  const rect = {};
  if (!getRect(handle(win), rect)) throw Error('GetWindowRect failed');
  return screen.screenToDipRect(win, { x: rect.left, y: rect.top,
    width: rect.right - rect.left, height: rect.bottom - rect.top });
};
exports.setBounds = (win, screen, bounds) => {
  const rect = screen.dipToScreenRect(win, bounds);
  if (!setPosition(handle(win), null, rect.x, rect.y, rect.width, rect.height, 0x14)) {
    throw Error('SetWindowPos failed');
  }
};
