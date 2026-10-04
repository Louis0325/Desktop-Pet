const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = path.join(__dirname, 'vendor');
const PF = require(path.join(source, 'phyfriends.js'));
vm.runInNewContext(fs.readFileSync(path.join(source, 'phy.js'), 'utf8'), { PhyFriends: PF });
require(path.join(source, 'anim.js'));

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

const output = path.join(__dirname, 'build', 'svg');
fs.mkdirSync(output, { recursive: true });
for (const file of fs.readdirSync(output)) {
  if (file.endsWith('.svg')) fs.unlinkSync(path.join(output, file));
}

for (let y = 0; y < 3; y++) {
  for (let x = 0; x < 5; x++) {
    const lookX = (x - 2) / 2;
    const lookY = y - 1;
    const gaze = { lookX, lookY, turnX: lookX * 0.5, turnY: lookY * 0.5 };
    const idle = PF.anim.make.idle({ energy: 1.6 });
    for (let frame = 0; frame < 24; frame++) {
      const pose = PF.anim.sample(idle, frame / 3);
      Object.assign(pose, gaze);
      const svg = PF.render('phy', { bg: false, pencil: false, pose });
      fs.writeFileSync(path.join(output, `g${x}${y}_${frame}.svg`), svg);
    }
    fs.writeFileSync(path.join(output, `blink_${x}${y}.svg`), PF.render('phy', {
      bg: false, pencil: false, pose: { ...gaze, blink: 1 },
    }));
    fs.writeFileSync(path.join(output, `happy_${x}${y}.svg`), PF.render('phy', {
      bg: false, pencil: false,
      pose: { ...gaze, tilt: 8, tail: -12, eyes: 'happy', mouth: 'open' },
    }));
  }
}
