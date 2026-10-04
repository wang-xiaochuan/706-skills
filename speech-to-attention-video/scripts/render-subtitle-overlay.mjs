#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

function parseArgs(argv) {
  const values = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) throw new Error(`Unexpected argument: ${token}`);
    const key = token.slice(2);
    if (key === 'single-line') values[key] = true;
    else {
      const value = argv[index + 1];
      if (!value || value.startsWith('--')) throw new Error(`Missing value for --${key}`);
      values[key] = value;
      index += 1;
    }
  }
  return values;
}

function run(command, args, options = {}) {
  const result = spawnSync(command, args, { encoding: 'utf8', stdio: options.inherit ? 'inherit' : ['ignore', 'pipe', 'pipe'] });
  if (result.status !== 0) throw new Error(`${command} failed (${result.status})\n${result.stderr || result.stdout || ''}`);
  return result.stdout || '';
}

function timestampSeconds(value) {
  const match = value.match(/^(\d+):(\d+):(\d+)[,.](\d+)$/);
  if (!match) throw new Error(`Invalid SRT timestamp: ${value}`);
  return Number(match[1]) * 3600 + Number(match[2]) * 60 + Number(match[3]) + Number(match[4].padEnd(3, '0').slice(0, 3)) / 1000;
}

const args = parseArgs(process.argv.slice(2));
for (const name of ['input', 'srt', 'output', 'font']) {
  if (!args[name]) throw new Error(`Required: --${name}`);
}
for (const file of [args.input, args.srt, args.font]) {
  if (!fs.existsSync(file)) throw new Error(`File not found: ${file}`);
}

const probe = JSON.parse(run('ffprobe', [
  '-v', 'error', '-select_streams', 'v:0',
  '-show_entries', 'stream=width,height:format=duration', '-of', 'json', args.input,
]));
const width = Number(probe.streams?.[0]?.width);
const height = Number(probe.streams?.[0]?.height);
const sourceDuration = Number(probe.format?.duration);
if (!(width > 0 && height > 0 && sourceDuration > 0)) throw new Error('Could not probe input dimensions or duration');

const singleLine = Boolean(args['single-line']);
const overlayHeight = Number(args['overlay-height'] || (singleLine ? 44 : 88));
const bottomMargin = Number(args['bottom-margin'] || 10);
const x = Number(args.x || 0);
const y = args.y === undefined ? height - overlayHeight - bottomMargin : Number(args.y);
const maxPointSize = Number(args['font-size'] || (singleLine ? 24 : 30));
const minPointSize = Number(args['min-font-size'] || 16);
const maxTextWidth = Math.floor(width * Number(args['max-width-ratio'] || 0.94));
const requestedLimit = args['limit-seconds'] === undefined ? sourceDuration : Number(args['limit-seconds']);
const renderDuration = Math.min(sourceDuration, requestedLimit);
if (!(overlayHeight > 0 && y >= 0 && y + overlayHeight <= height)) throw new Error('Overlay geometry is outside the source frame');

const outputPath = path.resolve(args.output);
const workDir = path.resolve(args['work-dir'] || `${outputPath}.overlay-work`);
const assetDir = path.join(workDir, 'png');
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.mkdirSync(assetDir, { recursive: true });

const entries = fs.readFileSync(args.srt, 'utf8').trim().split(/\r?\n\s*\r?\n/).map((block) => {
  const lines = block.split(/\r?\n/);
  const [start, end] = lines[1].split(/\s+-->\s+/);
  const rawText = lines.slice(2).join(singleLine ? ' ' : '\n');
  return {
    start: timestampSeconds(start),
    end: timestampSeconds(end),
    text: rawText.replace(singleLine ? /\s+/g : /[ \t]+/g, ' ').trim(),
  };
}).filter((entry) => entry.end > entry.start && entry.start < renderDuration);
if (!entries.length) throw new Error('No subtitle cues overlap the render duration');

function measuredWidth(text, pointSize) {
  const lines = text.split('\n');
  return Math.max(...lines.map((line) => Number(run('magick', [
    '-font', args.font, '-pointsize', String(pointSize), `label:${line}`,
    '-format', '%w', 'info:',
  ]).trim())));
}

function fittedPointSize(text) {
  for (let size = maxPointSize; size >= minPointSize; size -= 1) {
    if (measuredWidth(text, size) <= maxTextWidth) return size;
  }
  return minPointSize;
}

function renderPng(file, text) {
  if (!text) {
    run('magick', ['-size', `${width}x${overlayHeight}`, 'xc:rgba(0,0,0,0)', '-alpha', 'on', '-depth', '8', '-define', 'png:color-type=6', file]);
    return;
  }
  const pointSize = String(fittedPointSize(text));
  run('magick', [
    '(', '-size', `${width}x${overlayHeight}`, 'xc:none', '-font', args.font,
    '-pointsize', pointSize, '-interline-spacing', '3', '-gravity', 'south',
    '-stroke', 'rgba(0,0,0,0.96)', '-strokewidth', '3', '-fill', 'rgba(0,0,0,0.96)',
    '-annotate', '+1+3', text, '-blur', '0x1', ')',
    '(', '-size', `${width}x${overlayHeight}`, 'xc:none', '-font', args.font,
    '-pointsize', pointSize, '-interline-spacing', '3', '-gravity', 'south',
    '-stroke', 'none', '-fill', '#FFFFFF', '-annotate', '+0+2', text, ')',
    '-compose', 'over', '-composite', '-alpha', 'on', '-depth', '8',
    '-define', 'png:color-type=6', file,
  ]);
}

const blank = path.join(assetDir, 'blank.png');
renderPng(blank, '');
const timeline = [];
let cursor = 0;
for (const [index, entry] of entries.entries()) {
  const start = Math.max(0, entry.start);
  const end = Math.min(renderDuration, entry.end);
  if (end <= start) continue;
  if (start > cursor + 0.001) timeline.push({ file: blank, duration: start - cursor });
  const file = path.join(assetDir, `subtitle-${String(index + 1).padStart(4, '0')}.png`);
  renderPng(file, entry.text);
  timeline.push({ file, duration: end - start });
  cursor = end;
}
if (cursor < renderDuration) timeline.push({ file: blank, duration: renderDuration - cursor });

const concatPath = path.join(workDir, 'overlay.ffconcat');
const trackPath = path.join(workDir, 'overlay.mov');
const concat = ['ffconcat version 1.0'];
for (const item of timeline) {
  concat.push(`file '${item.file.replaceAll("'", "'\\''")}'`);
  concat.push(`duration ${Math.max(0.001, item.duration).toFixed(6)}`);
}
concat.push(`file '${timeline.at(-1).file.replaceAll("'", "'\\''")}'`);
fs.writeFileSync(concatPath, `${concat.join('\n')}\n`);

run('ffmpeg', [
  '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', concatPath,
  '-vf', 'format=argb', '-t', renderDuration.toFixed(3), '-fps_mode', 'vfr',
  '-c:v', 'qtrle', '-pix_fmt', 'argb', trackPath,
]);

run('ffmpeg', [
  '-hide_banner', '-loglevel', 'error', '-y', '-t', renderDuration.toFixed(3), '-i', args.input, '-i', trackPath,
  '-filter_complex', `[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[ov];[v0][ov]overlay=${x}:${y}:eof_action=pass:repeatlast=1,format=yuv420p[vout]`,
  '-map', '[vout]', '-map', '0:a:0?', '-t', renderDuration.toFixed(3),
  '-c:v', 'libx264', '-preset', args.preset || 'medium', '-crf', args.crf || '20',
  '-c:a', args.audio || 'copy', '-movflags', '+faststart', outputPath,
], { inherit: true });

console.log(JSON.stringify({
  output: outputPath,
  work_dir: workDir,
  subtitle_cues: entries.length,
  source_dimensions: `${width}x${height}`,
  output_dimensions: `${width}x${height}`,
  overlay_geometry: `${width}x${overlayHeight}+${x}+${y}`,
  duration_seconds: renderDuration,
}));
