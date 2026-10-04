(() => {
const PF = window.PhyFriends;
// Adapt the supplied newer character schema to the bundled renderer.
const spec = PF.get('phy');
function color(role, seen = new Set()) {
  if (role.startsWith('#')) return role;
  if (seen.has(role)) throw new Error(`Circular palette role: ${role}`);
  seen.add(role);
  if (spec.palette[role]) return color(spec.palette[role], seen);
  if (role.endsWith('Shade')) return PF.shadeOf(color(role.slice(0, -5), seen));
  throw new Error(`Unknown palette role: ${role}`);
}
for (const role of Object.keys(spec.palette)) spec.palette[role] = color(role);
spec.eyes.color = 'iris';
spec.head.color = 'head';
spec.body.color = 'body';
spec.tail.color = 'tail';
spec.ears.color = 'ear';
spec.extras = spec.extras.map(extra => extra.on === 'scarf' ? { ...extra, on: 'body' } : extra);
if (spec.stand?.seat) {
  for (const [part, shape] of Object.entries(spec.stand.seat)) {
    for (const side of [-1, 1]) {
      spec.extras.push({ ...shape, cx: side * shape.cx, on: 'body', fill: part === 'paw' ? 'paw' : 'foot' });
      for (const extra of spec.extras.filter(e => e.on === `${part}${side < 0 ? 'L' : 'R'}`)) {
        spec.extras.push({ ...extra, on: 'body', polys: extra.polys.map(([x, y, ...rest]) =>
          [side * shape.cx - side * x, shape.cy + y, ...rest]) });
      }
    }
  }
}


})();
