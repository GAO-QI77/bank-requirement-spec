# bank-requirement-spec

> 银行业务需求转技术需求说明书生成器（V4.0.1）— 一个 Claude / Agent Skill

把银行业务人员提交的业务需求，转化为科技人员可直接执行的《需求说明书》。面向国有大行（以中国交通银行金融科技部为蓝本）、由行内自有大模型（智能水平有限）驱动、需真正投产的场景。

## 它解决什么问题

行内弱模型直接写需求书，典型失败是"结构完整但内容失真"：编造交易码/系统名、把不确定写成确定、漏判账务、差错只写"转人工"、越权做技术选型。本 skill 用一套工程化方法把这些堵住：

- **分级路由** A/B/C：流程重量匹配需求风险，简单需求不走重流程
- **分轮生成** 0/1/2/3A/3B/4：弱模型短任务可靠性远高于长任务，每轮间有人工确认
- **固定占位符**：把"不要编造"从需要自律的开放要求，变成只能复制粘贴的封闭动作
- **冻结基线 + 举证式自检**：防偷改、防"自检全填是"
- **高敏感概念边界框架**：反向交易/客户主体状态等只输出"待确认问题"，不下定性结论
- **业务条线对照表**：覆盖 11 个条线，反过拟合，不只适用代收付
- **第三方合作业务域扩展包**：代收付/代付/批量扣款/签约代扣/数据回盘/对账清算/手续费/差错处理等全生命周期

## 目录结构

```
.
├── bank-requirement-spec/            可安装 skill 的源
│   ├── SKILL.md                      路由总控：档位判定、何时加载扩展包、工作流
│   └── references/
│       ├── core-engine.md            V4.0 核心引擎（所有需求都走）
│       ├── third-party.md            第三方合作业务域扩展包（命中时加载）
│       └── human-checklist.md        人工确认 Checklist（把关人用，不投喂模型）
├── tools/
│   ├── consistency_check.py          内部一致性形式核验脚本
│   ├── build_split_md.py             生成交行内部模型可导入的拆分版 .md
│   └── build_skill.sh                校验 + 生成拆分版 .md + 打包为 .skill
├── dist/
│   ├── bank-requirement-spec-split/  拆分版 Markdown skills（交行内部模型导入）
│   └── bank-requirement-spec.skill   构建产物（可直接安装）
└── EVALUATION.md                     测评报告（评估方法、发现、修复）
```

## 怎么用

### 作为 Skill 安装
把 `dist/bank-requirement-spec.skill` 安装到支持 Skill 的客户端（Claude.ai / Claude Code / Cowork）。

### 作为交行内部模型 Markdown 导入
把 `dist/bank-requirement-spec-split/*.md` 按编号全部上传到内部模型的技能/知识导入入口。每个文件都控制在 5500 字以内，并通过 `00-router.md` 串成整体：

- A/B/C 档通用：`00 + 01 + 02 + 03 + 04 + 07`
- 第三方合作类：在通用文件基础上额外导入并启用 `05 + 06`

### 作为方法论手动使用
1. 读 `bank-requirement-spec/SKILL.md` 判定档位、是否第三方合作类
2. 每轮调用时投喂：`core-engine.md` 第一部分模型规则 + 本轮模板 +（第三方时）`third-party.md` 对应章节 + 上一轮冻结基线
3. 把关人对照 `human-checklist.md` 核验，先过一票否决项

### 自行构建与校验
```bash
python3 tools/consistency_check.py     # 跑内部一致性核验
python3 tools/build_split_md.py        # 单独生成 dist/bank-requirement-spec-split/*.md
./tools/build_skill.sh                 # 校验通过后生成拆分版 .md 并打包 dist/*.skill
```

`consistency_check.py` 校验五类跨文件约束（占位符闭合、原因代码合法、第三方挂载章节齐全、六轮命名一致、版本号一致），落实了 skill 自身在残余风险表与一票否决项中长期建议、但原始交付缺失的"形式核验脚本"。

## 重要边界（请勿期待过高）

- 业务原文本身写错的，本 skill 兜不住（垃圾进垃圾出）
- 行内会计/合规口径不下结论，必须条线确认
- 弱模型在 C 档长基线下可能静默丢内容，试点首要任务是实测基线承载上限
- **没有人工 Checklist 兜底，不允许投产**

## 版本

- **V4.0.1** — 闭合占位符集合（登记 3 个此前散落在 third-party / human-checklist 的未注册变体）；新增 `tools/consistency_check.py` 形式核验脚本与 `build_skill.sh` 构建流程。
- **V4.0** — 判定树→高敏感概念框架（反过拟合）、业务条线对照表、待确认密度告警、Q 模糊化防取巧、强弱触发分级、第三方合作业务域扩展包。

详见 [EVALUATION.md](EVALUATION.md) 与 core-engine 末尾「版本变更说明」。

## License

[MIT](LICENSE)
