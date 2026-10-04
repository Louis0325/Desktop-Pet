/* Animate the SVG rig directly; no raster frames or image interpolation. */
const PF = window.PhyFriends;
const rig = PF.mount(document.getElementById('pet'), 'phy', { bg: false, pencil: false });
const idle = PF.anim.make.idle({ energy: 1.6 });
const greeting = PF.anim.make.happy({ duration: 1.5, bounces: 2, height: 18, wags: 3 });
const api = window.pet;
const start = performance.now();
let last = start, greetingStart = -Infinity;
let pointer = { x: innerWidth / 2, y: innerHeight / 2 }, lookX = 0, lookY = 0;
let frames = 0, greetings = 0, changes = 0, previousTransform = '';

// Fit the live rig and leave space for ears, tail swishes and jumps.
rig.setPose(PF.anim.sample(idle, 0), true);
const root = rig.svg.querySelector('[data-pf="root"]');
const bounds = root.getBBox();
const matrix = rig.svg.getScreenCTM().inverse().multiply(root.getScreenCTM());
const corners = [[bounds.x, bounds.y], [bounds.x + bounds.width, bounds.y],
  [bounds.x, bounds.y + bounds.height], [bounds.x + bounds.width, bounds.y + bounds.height]]
  .map(([x, y]) => new DOMPoint(x, y).matrixTransform(matrix));
const boundsLeft = Math.min(...corners.map(p => p.x)), boundsTop = Math.min(...corners.map(p => p.y));
const boundsRight = Math.max(...corners.map(p => p.x)), boundsBottom = Math.max(...corners.map(p => p.y));
rig.svg.setAttribute('preserveAspectRatio', 'xMidYMax meet');
rig.svg.setAttribute('viewBox', `${boundsLeft - 8} ${boundsTop - 22} ${boundsRight - boundsLeft + 16} ${boundsBottom - boundsTop + 24}`);

function greet() { greetingStart = performance.now(); greetings++; }
api.onPointer(point => { pointer = point; });
api.onGreeting(greet);
const petElement = document.getElementById('pet');
petElement.addEventListener('dblclick', () => { greet(); api.greet(); });
petElement.addEventListener('contextmenu', event => { event.preventDefault(); api.menu(); });
petElement.addEventListener('pointerdown', event => {
  if (event.button !== 0) return;
  petElement.setPointerCapture(event.pointerId);
  api.dragStart();
});
for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) {
  petElement.addEventListener(event, () => api.dragEnd());
}
petElement.addEventListener('wheel', event => {
  event.preventDefault(); api.resize(event.deltaY < 0 ? 1 : -1);
}, { passive: false });

function animate(now) {
  const elapsed = Math.min((now - last) / 1000, 0.1);
  last = now;
  const dx = pointer.x - innerWidth * 0.45, dy = pointer.y - innerHeight * 0.42;
  const distance = Math.max(Math.hypot(dx, dy), innerWidth * 0.6);
  const ease = 1 - Math.exp(-elapsed * 7);
  lookX += (dx / distance - lookX) * ease;
  lookY += (dy / distance - lookY) * ease;
  const greetingTime = (now - greetingStart) / 1000;
  const pose = PF.anim.sample(greetingTime < 1.5 ? greeting : idle,
    greetingTime < 1.5 ? greetingTime : (now - start) / 1000);
  Object.assign(pose, { lookX, lookY, turnX: lookX * 0.5, turnY: lookY * 0.5 });
  rig.setPose(pose, true);
  const transform = ['root', 'head', 'earL', 'earR', 'tail'].map(
    part => rig.parts[part]?.getAttribute('transform') || '').join('|');
  if (transform !== previousTransform) changes++;
  previousTransform = transform;
  frames++;
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
setInterval(() => api.diagnostic({ frames, changes, greetings,
  greetingActive: performance.now() - greetingStart < 1500 }), 1000);
api.ready();
