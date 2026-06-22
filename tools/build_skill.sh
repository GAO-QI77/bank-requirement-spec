#!/usr/bin/env bash
# 从源文件构建可安装的 bank-requirement-spec.skill 包。
# 构建前先跑一致性校验；校验不过则拒绝打包。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/3] 运行一致性校验 ..."
python3 tools/consistency_check.py

echo "[2/3] 生成拆分版 Markdown skills ..."
python3 tools/build_split_md.py

echo "[3/3] 打包 dist/bank-requirement-spec.skill ..."
mkdir -p dist
rm -f dist/bank-requirement-spec.skill
# .skill 即 zip：根目录下含 bank-requirement-spec/ 目录
zip -r -q dist/bank-requirement-spec.skill bank-requirement-spec \
  -x '*.DS_Store'
echo "完成："
unzip -l dist/bank-requirement-spec.skill
