const fs = require('fs');
const path = require('path');
const vm = require('vm');

const source = path.join(__dirname, 'vendor');
const PF = require(path.join(source, 'phyfriends.js'));
vm.runInNewContext(fs.readFileSync(path.join(source, 'phy.js'), 'utf8'), { PhyFriends: PF });
require(path.join(source, 'anim.js'));

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
    for (let frame = 0; frame < 8; frame++) {
      const pose = PF.anim.sample(PF.anim.clips.idle, frame);
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
