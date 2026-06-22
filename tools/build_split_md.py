#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成交行内部模型可导入的拆分版 Markdown skills。

银行内部平台单个 skill 有 6000 字限制；这里按 5500 个 Unicode 字符做
硬上限，给平台解析、标题和后续微调留余量。源文件仍按目录型 skill 维护。
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "bank-requirement-spec" / "references" / "core-engine.md"
THIRD = ROOT / "bank-requirement-spec" / "references" / "third-party.md"
CHECK = ROOT / "bank-requirement-spec" / "references" / "human-checklist.md"
OUTPUT_DIR = ROOT / "dist" / "bank-requirement-spec-split"
LEGACY_SINGLE = ROOT / "dist" / "bank-requirement-spec.md"
MAX_CHARS = 5500


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def remove_section(text: str, heading: str) -> str:
    before, sep, _after = text.partition(heading)
    return before.rstrip() if sep else text


def slice_between(text: str, start: str, end: str | None = None) -> str:
    start_pos = text.find(start)
    if start_pos < 0:
        raise ValueError(f"找不到章节起点: {start}")
    if end is None:
        return text[start_pos:].strip()
    end_pos = text.find(end, start_pos)
    if end_pos < 0:
        raise ValueError(f"找不到章节终点: {end}")
    return text[start_pos:end_pos].strip()


def normalize_common(text: str) -> str:
    replacements = {
        "core-engine.md": "核心引擎章节",
        "third-party.md": "第三方合作扩展章节",
        "human-checklist.md": "模型自检与人工核验清单",
        "core-engine": "核心引擎章节",
        "third-party": "第三方合作扩展章节",
        "human-checklist": "模型自检与人工核验清单",
        "每轮 prompt 必须原样前置": "每轮生成必须遵守",
        "prompt 无法纠正": "本文规则无法纠正",
        "本 prompt": "本文规则",
        "prompt 的价值": "本文规则的价值",
        "投喂模型": "提供给模型执行",
        "不投喂模型": "用于模型输出后的人工核验",
        "人工 Checklist": "模型自检与人工核验清单",
        "加载条件": "启用条件",
        "加载": "启用",
        "挂载": "并入",
        "挂在": "并入",
        "挂到": "并入",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    cleanup = {
        "模型自检与人工核验清单 的": "模型自检与人工核验清单的",
        "本文规则 不允许": "本文规则不允许",
        "本文规则 的价值": "本文规则的价值",
    }
    for old, new in cleanup.items():
        text = text.replace(old, new)
    return text


def normalize_core(text: str) -> str:
    text = remove_section(text, "# 版本变更说明")
    replacements = {
        "# 中国交通银行金融科技部\n# 业务需求转化为技术需求 AI Prompt V4.0": "# 核心引擎：模型规则、占位符、原因代码与分轮模板",
        "> 配套要求：必须搭配《人工确认 Checklist V4.0》使用": "> 配套要求：必须执行 07-review-checklist.md 的模型自检与人工核验要求",
        "# 第零部分　使用者必读（此部分不投喂模型）": "# 执行前约束",
        "## 0.4 调用编排（人工操作流程）": "## 0.4 分轮执行编排",
        "每轮模板均**继承第一部分模型规则**，由人工在调用时一并粘贴。": "每轮模板均**自动继承 01-core-rules.md 的模型规则**。生成任一轮输出时，必须同时遵守硬禁令、硬义务、占位符和原因代码规则。",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return normalize_common(text)


def normalize_third_party(text: str) -> str:
    text = normalize_common(text)
    replacements = {
        "# 第三方合作业务域扩展包（V4.0）": "# 第三方合作业务域扩展规则（V4.0）",
        "> 启用条件：第 0 轮判定为「第三方合作类需求」时启用。": "> 启用条件：第 0 轮判定为「第三方合作类需求」时，自动启用本部分全部规则。",
        "> 用法：本扩展包的各章节，按下表并入 核心引擎章节 的对应轮次模板上，与核心引擎共同提供给模型执行。": "> 用法：命中第三方合作类需求后，将本部分对应规则并入相应轮次输出；不得要求用户另行提供材料。",
        "## 目录": "## 轮次并入目录",
        "第 1 轮输出模板（并入 核心引擎章节 第 1 轮\"需求基本信息\"之后）：": "第 1 轮输出时，在\"需求基本信息\"之后增加以下内容：",
        "第三方合作的数据需求不能只写\"接口查询\"。并入 核心引擎章节 第 2 轮功能明细之后，作为独立章节。": "第三方合作的数据需求不能只写\"接口查询\"。第 2 轮输出时，在功能明细之后增加本节，作为独立章节。",
        "按银行系统视角，不写互联网 RESTful。并入 核心引擎章节 第 3A 轮\"系统交互\"，逐系统说明。": "按银行系统视角，不写互联网 RESTful。第 3A 轮输出时，在\"系统交互\"中逐系统说明。",
        "仅当涉及资金流时填写。并入 核心引擎章节 第 3A 轮\"账务处理\"与\"对账清算\"。": "仅当涉及资金流时填写。第 3A 轮输出时，在\"账务处理\"与\"对账清算\"中增加本节。",
        "★ 金额构成（本金/手续费/税费）涉及时，按 核心引擎章节 高敏感概念 D 类输出 Cxx 问题清单。借贷方向、科目、内部户、清算账户、手续费比例、清算周期一律禁止写死。": "★ 金额构成（本金/手续费/税费）涉及时，按 02-risk-boundaries.md 高敏感概念 D 类输出 Cxx 问题清单。借贷方向、科目、内部户、清算账户、手续费比例、清算周期一律禁止写死。",
        "第三方合作的差错远多于单机构场景。并入 核心引擎章节 第 3B 轮差错矩阵，并继承其客户主体状态维度。": "第三方合作的差错远多于单机构场景。第 3B 轮输出时，并入差错矩阵，并继承其客户主体状态维度。",
        "并入 核心引擎章节 第 3B 轮\"数据安全\"之后。": "第 3B 轮输出时，在\"数据安全\"之后增加本节。",
        "★ 反洗钱、反欺诈、大额/可疑识别、客户授权沿用 核心引擎章节 第 3B 风控章节，此处补第三方特有的报文安全与数据边界。": "★ 反洗钱、反欺诈、大额/可疑识别、客户授权沿用第 3B 轮风控章节，此处补第三方特有的报文安全与数据边界。",
        "第三方合作类需求的终稿，在 核心引擎章节 第 4 轮正文章节基础上，增加以下专属章节（编号顺延，不重排）：": "第三方合作类需求的终稿，在第 4 轮正文章节基础上，增加以下专属章节（编号顺延，不重排）：",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def normalize_checklist(text: str) -> str:
    text = normalize_common(text)
    replacements = {
        "# 人工确认 Checklist（V4.0）": "# 模型自检与辅助人工核验清单（V4.0）",
        "> 这份文件给**把关人/评审者**用，用于模型输出后的人工核验。": "> 本清单用于模型在每轮输出后辅助人工核验。模型不得替代人工放行，但必须保留可核验证据、待确认问题和自检摘抄。",
        "> 这份文件给**把关人/评审者**用，不提供给模型执行。": "> 本清单用于模型在每轮输出后辅助人工核验。模型不得替代人工放行，但必须保留可核验证据、待确认问题和自检摘抄。",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def file_header(filename: str, role: str, trigger: str, prev_file: str, next_file: str) -> str:
    return f"""# {filename}

> 系列：交通银行业务需求转技术需求说明书生成
> 职责：{role}
> 配套：必须同时导入并遵守 `00-router.md`；按编号顺序共同使用。
> 启用：{trigger}
> 前后关系：上一份 `{prev_file}`；下一份 `{next_file}`。
"""


def router() -> str:
    return """# 00-router.md

> 系列：交通银行业务需求转技术需求说明书生成
> 职责：总控路由、角色、输入协议、A/B/C 档、第三方识别、文件使用顺序。
> 配套：本系列所有文件必须与本文件一起导入；不得只导入单个子文件。
> 启用：任何银行业务需求转技术需求说明书任务。
> 前后关系：这是第 1 份；下一份 `01-core-rules.md`。

## 角色与总原则

你是中国交通银行金融科技部的资深需求分析师。你的任务是把业务条线提交的业务需求，转化为科技人员可直接执行的《需求说明书》。

本系列是完整 skill。不得要求用户再提供其他技能包、目录、文件、说明书或外部提示词。所有输出必须遵守 `01-core-rules.md` 的硬禁令、硬义务、占位符和原因代码。

## 输入协议

用户通常提供：业务需求原文、已有人工确认结论、期望执行轮次、上一轮冻结基线。若未指定轮次，从第 0 轮开始。第 1 轮以后如缺少上一轮冻结基线，停止并要求补齐。

若业务原文明显缺少目标、范围、参与方、资金/账务边界、系统边界或处理时点，第 0 轮必须先拦截并输出缺口，不得直接生成终稿。

## 文件使用顺序

| 文件 | 用途 |
|---|---|
| `00-router.md` | 总控路由与系列说明 |
| `01-core-rules.md` | 硬禁令、硬义务、固定占位符、不涉及原因代码 |
| `02-risk-boundaries.md` | 分级路由、业务条线、高敏感概念、样例与残余风险 |
| `03-rounds-0-2.md` | 第 0/1/2 轮模板 |
| `04-rounds-3a-4.md` | 第 3A/3B/4 轮模板 |
| `05-third-party-foundation.md` | 第三方基础规则：机构、业务类型、生命周期、数据、系统边界、账务清算 |
| `06-third-party-risk.md` | 第三方风险规则：差错、安全、服务中断、参数、终稿专章 |
| `07-review-checklist.md` | 模型自检与辅助人工核验清单 |

## 按档位启用

| 档位 | 适用需求 | 必用文件 |
|---|---|---|
| A 档 | 纯页面、字段、文案、查询、性能优化；无资金、无账务、无第三方、无授权、无敏感信息 | `00 + 01 + 02 + 03 + 04 + 07` |
| B 档 | 业务规则、参数、接口、渠道流程、状态流转；不直接涉核心账务 | `00 + 01 + 02 + 03 + 04 + 07` |
| C 档 | 资金、账户、核心账务、反向交易、远程授权、对账清算、风控、监管、敏感信息 | `00 + 01 + 02 + 03 + 04 + 07` |
| 第三方合作类 | 命中第三方/代收付/对账/清算/回盘/手续费等 | 在对应档位基础上额外使用 `05 + 06` |

## 分轮流程

| 档位 | 执行轮次 |
|---|---|
| A 档 | 第 0 轮 → 第 1+2 合并轮 → 第 4 轮 |
| B 档 | 第 0 轮 → 第 1 轮 → 第 2 轮 → 第 3A 或 3B 轮（按需）→ 第 4 轮 |
| C 档 | 第 0 轮 → 第 1 轮 → 第 2 轮 → 第 3A 轮 → 第 3B 轮 → 第 4 轮 |

C 档不得合并轮次。C 档第 3A 轮涉及账务、清算、内部户、科目或手续费时，必须先输出需财会/运营确认的事项，再继续后续轮次。

## 第三方合作类自动识别

读业务原文，命中以下任一信号词，即按第三方合作类处理，并自动启用 `05-third-party-foundation.md` 与 `06-third-party-risk.md`：

> 第三方、外部机构、合作机构、代收、代付、代扣、批量扣款、批量入账、代发、归集、签约、协议、对账、回盘、清算、清分、手续费、分润、委托单位、商户、平台方、供应链、水电燃气、社保医保公积金、税务财政、保险公司、基金公司、证券公司、缴费、扣费、退费、数据报送、账户验证、身份核验、数据采集、数据回传

第三方合作类需求几乎必然落入 B 或 C 档。纯第三方查询展示且不涉资金的，最低也是 B 档；涉及代收付、扣款、入账、退款、清算、对账、手续费、分润、回盘差错的，按 C 档处理。
"""


def build_files() -> dict[str, str]:
    core = normalize_core(read(CORE))
    third = normalize_third_party(read(THIRD))
    check = normalize_checklist(read(CHECK))

    files = {
        "00-router.md": router(),
        "01-core-rules.md": file_header(
            "01-core-rules.md",
            "硬禁令、硬义务、固定占位符表、不涉及原因代码。",
            "所有档位、所有轮次均启用。",
            "00-router.md",
            "02-risk-boundaries.md",
        )
        + "\n"
        + slice_between(core, "# 执行前约束", "# 第二部分　分级路由"),
        "02-risk-boundaries.md": file_header(
            "02-risk-boundaries.md",
            "分级路由细则、业务条线对照表、高敏感概念边界、样例和残余风险。",
            "第 0 轮档位判定、任何敏感/资金/账户/第三方/监管场景均启用。",
            "01-core-rules.md",
            "03-rounds-0-2.md",
        )
        + "\n"
        + slice_between(core, "# 第二部分　分级路由", "# 第五部分　六轮模板")
        + "\n\n"
        + slice_between(core, "# 第六部分　Few-shot 标准样例"),
        "03-rounds-0-2.md": file_header(
            "03-rounds-0-2.md",
            "第 0 轮、第 1 轮、第 2 轮生成模板。",
            "启动需求分析、识别澄清、功能规则梳理时启用。",
            "02-risk-boundaries.md",
            "04-rounds-3a-4.md",
        )
        + "\n"
        + slice_between(core, "# 第五部分　六轮模板", "## 第 3A 轮"),
        "04-rounds-3a-4.md": file_header(
            "04-rounds-3a-4.md",
            "第 3A 轮、第 3B 轮、第 4 轮生成模板。",
            "系统交互、账务、差错、安全、非功能、终稿整合时启用。",
            "03-rounds-0-2.md",
            "05-third-party-foundation.md",
        )
        + "\n"
        + slice_between(core, "## 第 3A 轮", "# 第六部分　Few-shot 标准样例"),
        "05-third-party-foundation.md": file_header(
            "05-third-party-foundation.md",
            "第三方合作基础规则：机构类型、业务类型、生命周期、数据、系统边界、账务对账清算。",
            "第 0 轮判定为第三方合作类需求时启用。",
            "04-rounds-3a-4.md",
            "06-third-party-risk.md",
        )
        + "\n"
        + slice_between(third, "# 第三方合作业务域扩展规则", "## 7. 第三方差错处理矩阵"),
        "06-third-party-risk.md": file_header(
            "06-third-party-risk.md",
            "第三方合作风险规则：差错、安全、服务中断、参数库、终稿专属章节。",
            "第三方合作类需求进入第 3B 轮或第 4 轮时启用。",
            "05-third-party-foundation.md",
            "07-review-checklist.md",
        )
        + "\n"
        + slice_between(third, "## 7. 第三方差错处理矩阵"),
        "07-review-checklist.md": file_header(
            "07-review-checklist.md",
            "模型自检与辅助人工核验清单。",
            "每轮输出后、终稿放行前均启用。",
            "06-third-party-risk.md",
            "00-router.md",
        )
        + "\n"
        + check,
    }
    return files


def validate(files: dict[str, str]) -> None:
    expected = [
        "00-router.md",
        "01-core-rules.md",
        "02-risk-boundaries.md",
        "03-rounds-0-2.md",
        "04-rounds-3a-4.md",
        "05-third-party-foundation.md",
        "06-third-party-risk.md",
        "07-review-checklist.md",
    ]
    if list(files) != expected:
        raise ValueError("拆分文件清单与预期不一致")

    forbidden = [
        "SKILL.md",
        "references/",
        "core-engine.md",
        "third-party.md",
        "human-checklist.md",
        "不投喂模型",
        "Claude / Agent Skill",
    ]
    for filename, content in files.items():
        char_count = len(content)
        if char_count > MAX_CHARS:
            raise ValueError(f"{filename} 超过 {MAX_CHARS} 字: {char_count}")
        for token in forbidden:
            if token in content:
                raise ValueError(f"{filename} 含陌生环境禁用词: {token}")

    router_text = files["00-router.md"]
    for filename in expected:
        if filename not in router_text:
            raise ValueError(f"00-router.md 未列出 {filename}")


def main() -> int:
    files = build_files()
    validate(files)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if LEGACY_SINGLE.exists():
        LEGACY_SINGLE.unlink()

    for filename, content in files.items():
        (OUTPUT_DIR / filename).write_text(content.rstrip() + "\n", encoding="utf-8")

    print(f"完成：{OUTPUT_DIR.relative_to(ROOT)}")
    for filename, content in files.items():
        print(f"  {filename}: {len(content)} 字")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
