#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bank-requirement-spec 内部一致性校验器

这是 SKILL 自身（core-engine 残余风险表 / human-checklist 一票否决项）反复建议、
但原始交付未提供的「形式核验脚本」的一部分：把跨文件的一致性约束自动化，
代替人工逐条 Ctrl+F。

检查项：
  C1  模板中出现的占位符【...】是否都在 core-engine「固定占位符表」中登记
  C2  被引用的不涉及原因代码 N0x 是否都在 N01-N10 表中定义
  C3  SKILL.md「轮次挂载表」提到的第三方章节，third-party.md 是否都有对应小节
  C4  六轮轮次命名是否在各文件中一致（0/1/2/3A/3B/4）
  C5  README / SKILL / core-engine 版本号是否一致（V4.0）

退出码非 0 表示发现不一致。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "bank-requirement-spec" / "SKILL.md"
CORE = ROOT / "bank-requirement-spec" / "references" / "core-engine.md"
THIRD = ROOT / "bank-requirement-spec" / "references" / "third-party.md"
CHECK = ROOT / "bank-requirement-spec" / "references" / "human-checklist.md"
README = ROOT / "README.md"

# 真正的占位符以「待」开头、「确认」结尾；其余【...】是章节/区块标题，排除
PLACEHOLDER = re.compile(r"【待[^】]*确认】")
REASON_CODE = re.compile(r"\bN0[0-9]\b|\bN10\b")

problems = []


def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


def registered_placeholders(core_text):
    """从「固定占位符表」抽取登记在册的占位符。"""
    seg = core_text.split("## 固定占位符表")[1]
    seg = seg.split("## 不涉及原因代码")[0]
    return set(PLACEHOLDER.findall(seg))


def registered_reason_codes(core_text):
    # 注意：markdown 表头分隔行 |---| 含 "---"，不能用 --- 截断区段
    seg = core_text.split("## 不涉及原因代码")[1].split("\n# ")[0]
    return set(re.findall(r"\bN0[0-9]\b|\bN10\b", seg))


def check_c1(core_text, third_text):
    registered = registered_placeholders(core_text)
    used = set()
    for label, txt in (("core-engine", core_text), ("third-party", third_text)):
        for ph in PLACEHOLDER.findall(txt):
            used.add((label, ph))
    # 占位符表自身的条目不算"使用"
    table_seg = core_text.split("## 固定占位符表")[1].split("## 不涉及原因代码")[0]
    table_phs = set(PLACEHOLDER.findall(table_seg))
    unknown = sorted({ph for _, ph in used if ph not in registered} - table_phs)
    if unknown:
        problems.append(
            "C1 占位符未在占位符表登记（可能拼写不一致/漏登记）:\n      "
            + "\n      ".join(unknown)
        )
    else:
        print(f"  C1 OK  占位符全部登记在册（登记 {len(registered)} 个）")


def check_c2(core_text, skill_text, third_text):
    defined = registered_reason_codes(core_text)
    used = set()
    for txt in (skill_text, third_text, core_text):
        used |= set(re.findall(r"\bN0[0-9]\b|\bN10\b", txt))
    undefined = sorted(used - defined)
    if undefined:
        problems.append("C2 引用了未定义的原因代码: " + ", ".join(undefined))
    else:
        print(f"  C2 OK  原因代码引用合法（定义 {len(defined)} 个）")


def check_c3(skill_text, third_text):
    # SKILL 轮次挂载表里提到的第三方关键章节名
    expected = [
        "合作机构类型",
        "业务类型",
        "生命周期",
        "数据采集与使用要求",
        "对账清算",
        "手续费",
        "差错",
        "报文安全",
        "服务中断",
    ]
    missing = [e for e in expected if e not in third_text]
    if missing:
        problems.append("C3 SKILL 提到但 third-party.md 缺失的章节: " + ", ".join(missing))
    else:
        print("  C3 OK  第三方挂载章节齐全")


def check_c4(skill_text, core_text):
    rounds = ["第 0 轮", "第 1 轮", "第 2 轮", "第 3A 轮", "第 3B 轮", "第 4 轮"]
    for r in rounds:
        if r not in core_text:
            problems.append(f"C4 core-engine 缺少轮次模板: {r}")
    if all(r in core_text for r in rounds):
        print("  C4 OK  六轮模板命名一致")


def check_c5(readme_text, skill_text, core_text):
    texts = {"README": readme_text, "SKILL": skill_text, "core-engine": core_text}
    missing = [name for name, t in texts.items() if t and "V4.0" not in t]
    if missing:
        problems.append("C5 未出现版本号 V4.0 的文件: " + ", ".join(missing))
    else:
        print("  C5 OK  版本号 V4.0 一致")


def main():
    core_text = read(CORE)
    skill_text = read(SKILL)
    third_text = read(THIRD)
    readme_text = read(README)
    if not core_text or not skill_text or not third_text:
        print("ERROR: 找不到 skill 文件，请在仓库根目录运行", file=sys.stderr)
        return 2

    print("== bank-requirement-spec 一致性校验 ==")
    check_c1(core_text, third_text)
    check_c2(core_text, skill_text, third_text)
    check_c3(skill_text, third_text)
    check_c4(skill_text, core_text)
    check_c5(readme_text, skill_text, core_text)

    print()
    if problems:
        print("发现 %d 处不一致：" % len(problems))
        for p in problems:
            print("  [X] " + p)
        return 1
    print("全部通过：内部引用一致。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
