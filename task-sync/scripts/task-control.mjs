#!/usr/bin/env node

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const employeesRoot = path.resolve(here, "../..");
const command = process.argv[2] || "status";
const argument = process.argv[3] || "";

const records = await scanRecords();
const tasks = records.filter((item) => item.type === "task");

if (command === "status") printStatus(tasks, records);
else if (command === "check") process.exitCode = printChecks(tasks);
else if (command === "json") console.log(JSON.stringify(buildPayload(tasks), null, 2));
else if (command === "find") findTask(tasks, argument);
else if (command === "outputs") await printOutputAudit();
else {
  console.error("用法: node task-control.mjs status|check|json|find <task-id>|outputs");
  process.exitCode = 2;
}

async function scanRecords() {
  const employeeDirs = (await readdir(employeesRoot, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory() && /^0\d-/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
  const output = [];
  for (const employee of employeeDirs) {
    for (const bucket of ["inbox", "done"]) {
      const dir = path.join(employeesRoot, employee, bucket);
      let names = [];
      try { names = await readdir(dir); } catch { continue; }
      for (const name of names.sort()) {
        if (!name.endsWith(".md") || name === "README.md") continue;
        const absolutePath = path.join(dir, name);
        const content = await readFile(absolutePath, "utf8");
        const frontmatter = parseFrontmatter(content);
        output.push({
          employee,
          bucket,
          file: name,
          path: absolutePath,
          relativePath: path.relative(employeesRoot, absolutePath),
          type: frontmatter.type || inferType(name),
          taskId: frontmatter["task-id"] || "",
          title: firstHeading(content) || name.replace(/\.md$/, ""),
          priority: frontmatter.priority || "",
          status: normalizeStatus(frontmatter.status || (bucket === "done" ? "done" : "pending")),
          deadline: frontmatter.deadline || "",
          owner: frontmatter.owner || frontmatter.to || "",
          reviewed: frontmatter.reviewed || "",
          aligned: frontmatter.aligned || "",
          decision: frontmatter.decision || "",
          closed: frontmatter.closed || ""
        });
      }
    }
  }
  return output;
}

function parseFrontmatter(content) {
  if (!content.startsWith("---\n")) return {};
  const end = content.indexOf("\n---", 4);
  if (end === -1) return {};
  const result = {};
  for (const line of content.slice(4, end).split("\n")) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;
    result[match[1]] = match[2].trim().replace(/^(["'])(.*)\1$/, "$2");
  }
  return result;
}

function firstHeading(content) {
  return content.split("\n").find((line) => line.startsWith("# "))?.slice(2).trim() || "";
}

function inferType(name) {
  if (name.startsWith("report_")) return "report";
  if (name.startsWith("handoff_")) return "handoff";
  if (name.startsWith("info-request_")) return "info-request";
  return name.startsWith("task_") ? "task" : "unknown";
}

function normalizeStatus(value) {
  return { completed: "done", active: "doing" }[value] || value || "pending";
}

function buildPayload(items) {
  const counts = { total: items.length, inbox: 0, doing: 0, waiting: 0, blocked: 0, pending: 0, done: 0, cancelled: 0 };
  for (const task of items) {
    if (task.bucket === "inbox") counts.inbox += 1;
    counts[task.status] = (counts[task.status] || 0) + 1;
  }
  return {
    generatedAt: new Date().toISOString(),
    source: "digital-employees/0X-*/{inbox,done}/*.md",
    authority: "01-coordination",
    counts,
    tasks
  };
}

function printStatus(items, allRecords) {
  const employees = [...new Set(items.map((item) => item.employee))].sort();
  console.log("706 数字员工任务实时状态");
  console.log(`来源: ${employeesRoot}/0X-*/{inbox,done}/*.md`);
  console.log("");
  console.log("员工\tinbox\tdoing\twaiting\tblocked\tdone\t总计");
  for (const employee of employees) {
    const own = items.filter((item) => item.employee === employee);
    const count = (status) => own.filter((item) => item.status === status).length;
    console.log(`${employee}\t${own.filter((item) => item.bucket === "inbox").length}\t${count("doing")}\t${count("waiting")}\t${count("blocked")}\t${count("done")}\t${own.length}`);
  }
  const inbox = items.filter((item) => item.bucket === "inbox").length;
  const reports = allRecords.filter((item) => item.type === "report" && item.bucket === "inbox").length;
  console.log("");
  console.log(`任务: inbox ${inbox} / 全部 ${items.length}; 01 待处理 report ${reports}`);
}

function printChecks(items) {
  const errors = [];
  const warnings = [];
  const ids = new Map();
  for (const task of items) {
    if (!task.taskId) warnings.push(`${task.relativePath}: 缺少 task-id`);
    else {
      const previous = ids.get(task.taskId);
      if (previous) errors.push(`重复 task-id ${task.taskId}: ${previous} / ${task.relativePath}`);
      else ids.set(task.taskId, task.relativePath);
    }
    if (task.bucket === "inbox" && ["done", "cancelled"].includes(task.status)) errors.push(`${task.relativePath}: ${task.status} 任务仍在 inbox`);
    if (task.bucket === "done" && !["done", "cancelled"].includes(task.status)) errors.push(`${task.relativePath}: done 目录中的状态是 ${task.status}`);
    if (!task.priority) warnings.push(`${task.relativePath}: 缺少 priority`);
    if (!task.reviewed && !task.aligned) warnings.push(`${task.relativePath}: 尚未经过 2026-08-03 内容审阅或全库归属对齐`);
  }
  console.log(`检查 ${items.length} 个任务：${errors.length} errors, ${warnings.length} warnings`);
  for (const item of errors) console.log(`ERROR ${item}`);
  for (const item of warnings) console.log(`WARN  ${item}`);
  return errors.length ? 1 : 0;
}

function findTask(items, query) {
  if (!query) {
    console.error("find 需要 task-id 或标题关键词");
    process.exitCode = 2;
    return;
  }
  const matches = items.filter((item) => item.taskId === query || item.title.includes(query));
  if (!matches.length) {
    console.error(`未找到任务: ${query}`);
    process.exitCode = 1;
    return;
  }
  for (const item of matches) console.log(`${item.taskId || "(no-id)"}\t${item.status}\t${item.relativePath}\t${item.title}`);
}

async function printOutputAudit() {
  const employeeDirs = (await readdir(employeesRoot, { withFileTypes: true }))
    .filter((entry) => entry.isDirectory() && /^0[2-9]-/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
  const rows = [];
  const errors = [];
  for (const employee of employeeDirs) {
    const root = path.join(employeesRoot, employee, "outputs");
    const files = await walkFiles(root);
    const meaningful = files.filter((file) => path.basename(file) !== ".DS_Store");
    const reviews = meaningful.filter((file) => file.endsWith(".review.md"));
    let approved = 0;
    for (const review of reviews) {
      const data = parseFrontmatter(await readFile(review, "utf8"));
      if (data["review-status"] === "approved") {
        approved += 1;
        if (!data.reviewer || !data.target || !data["reviewed-at"]) {
          errors.push(`${path.relative(employeesRoot, review)}: approved 缺 reviewer / target / reviewed-at`);
        }
      }
    }
    rows.push({
      employee,
      files: meaningful.length,
      index: meaningful.some((file) => file === path.join(root, "INDEX.md")),
      reviews: reviews.length,
      approved
    });
  }
  console.log("员工产出工作区审核状态");
  console.log("员工\t文件\tINDEX\treview sidecar\tapproved");
  for (const row of rows) console.log(`${row.employee}\t${row.files}\t${row.index ? "yes" : "no"}\t${row.reviews}\t${row.approved}`);
  console.log("");
  console.log(`合计: ${rows.reduce((n, row) => n + row.files, 0)} files; ${rows.filter((row) => row.index).length}/8 INDEX; ${rows.reduce((n, row) => n + row.reviews, 0)} review sidecars; ${errors.length} errors`);
  for (const error of errors) console.log(`ERROR ${error}`);
  if (errors.length) process.exitCode = 1;
}

async function walkFiles(root) {
  const found = [];
  let entries = [];
  try { entries = await readdir(root, { withFileTypes: true }); } catch { return found; }
  for (const entry of entries) {
    const target = path.join(root, entry.name);
    if (entry.isDirectory()) found.push(...await walkFiles(target));
    else if (entry.isFile()) found.push(target);
  }
  return found;
}
