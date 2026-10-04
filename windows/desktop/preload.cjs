const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('pet', {
  onPointer: handler => ipcRenderer.on('pet:pointer', (_event, point) => handler(point)),
  onGreeting: handler => ipcRenderer.on('pet:greet', () => handler()),
  menu: () => ipcRenderer.send('pet:menu'),
  greet: () => ipcRenderer.send('pet:greet'),
  dragStart: () => ipcRenderer.send('pet:drag-start'),
  dragEnd: () => ipcRenderer.send('pet:drag-end'),
  resize: direction => ipcRenderer.send('pet:resize', direction),
  ready: () => ipcRenderer.send('pet:ready'),
  diagnostic: state => ipcRenderer.send('pet:diagnostic', state)
});
