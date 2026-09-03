#!/usr/bin/env bash
# ============================================================
# 端到端设计流程 — HIV_Env 精简调试版 (5 designs × 1 batch)
#
# 用法:
#   bash run_batched.sh            # 直接运行
#   bash run_batched.sh 2>&1 | tee run.log  # 运行并保存日志
#
# ⚠️ 链式调用说明 (job:// workaround):
#   rfantibody-server 的 proteinmpnn/rf2 端点把 URI 字段命名成了 `input_uri`
#   （而 bioq 的 `--file input_quiver` 映射成 `input_quiver_uri`，两者不匹配，
#   会触发 422）。所以在服务端修复之前，本脚本改用 `--set input_uri=job://...`
#   直接引用上一步在共享 NAS 上的输出，实现零拷贝链式调用。
#
#   job:// 格式: job://<account_id>-<上游 job_id>/<文件名>
#     - account_id 从 ~/.config/bioq/tokens/ecs.json 的 JWT `sub` 解出
#     - 上游 job_id 从该步 _run.log 的 "job_id: <id>" 提取
#   （依赖部署开启共享 NAS；若报 404 "File not found in job" 说明 NAS 未共享）
# ============================================================
set -euo pipefail

# --- 激活 venv ---
BIOAGENT_VENV="${BIOAGENT_VENV:-$HOME/bioagent/.venv}"
if [ -f "$BIOAGENT_VENV/bin/activate" ]; then
  source "$BIOAGENT_VENV/bin/activate"
else
  echo "ERROR: venv 未找到: $BIOAGENT_VENV"
  exit 1
fi

# --- 路径定义 ---
HERE="$(cd "$(dirname "$0")" && pwd)"
INPUTS="$HERE/inputs"
RESULTS="$HERE/results"

TARGET_NAME="HIV_Env"
BATCH_DIR="$RESULTS/$TARGET_NAME/batch_00"
RFD_OUT="$BATCH_DIR/rfdiffusion"
MPNN_OUT="$BATCH_DIR/proteinmpnn"
RF2_OUT="$BATCH_DIR/rf2"

BIOQ="bioq --profile ecs"
SVC="rfantibody"

# --- 解出 account_id（JWT sub），job:// 链式调用需要 ---
derive_account_id() {
  local token_file="$HOME/.config/bioq/tokens/ecs.json"
  [ -f "$token_file" ] || return 0
  python3 - "$token_file" 2>/dev/null <<'PY'
import json, base64, sys
try:
    t = json.load(open(sys.argv[1]))
    p = t["access_token"].split(".")[1]
    p += "=" * (-len(p) % 4)
    print(json.loads(base64.urlsafe_b64decode(p)).get("sub", ""))
except Exception:
    pass
PY
}
ACCOUNT_ID="$(derive_account_id)"

# --- 辅助函数 ---

# 从某一步的 _run.log 提取 bioq job_id（bioq --wait 会打印 "job_id: <id>"）
step_job_id() {
  grep -oP 'job_id:\s*\K\S+' "$1" 2>/dev/null | head -1 || true
}

# 构造 job:// URI: job://<account_id>-<job_id>/<filename>
job_uri() {
  local upstream_job_id="$1" filename="$2"
  echo "job://${ACCOUNT_ID}-${upstream_job_id}/${filename}"
}

# 解析某一步输出的 quiver 文件路径（bioq 下载后是扁平路径，无 output/ 前缀）
find_quiver() {
  local out_dir="$1" basename="$2"
  if [ -f "$out_dir/$basename" ]; then
    echo "$out_dir/$basename"
  elif [ -f "$out_dir/output/$basename" ]; then
    echo "$out_dir/output/$basename"
  else
    echo ""
  fi
}

# --- 确保输入文件存在 ---
REQUIRED_INPUTS=("$INPUTS/2NY7.pdb" "$INPUTS/vhh_nbbcII10.pdb")
for f in "${REQUIRED_INPUTS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "ERROR: 缺少输入文件: $f"
    echo "  请先运行: bash fetch_inputs.sh"
    exit 1
  fi
done

if [ -z "$ACCOUNT_ID" ]; then
  echo "WARN: 无法从 ~/.config/bioq/tokens/ecs.json 解出 account_id，job:// 链式调用将失败"
fi

# ============================================================
# Step 1: RFdiffusion
# ============================================================
RFD_QUIVER="$(find_quiver "$RFD_OUT" "1_rfdiffusion.qv")"

if [ -n "$RFD_QUIVER" ]; then
  echo ""
  echo "  [SKIP] RFdiffusion 输出已存在，跳过: $RFD_QUIVER"
else
  echo ""
  echo "============================================================"
  echo "  Step 1/3: RFdiffusion — $TARGET_NAME (5 designs)"
  echo "  started at: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "============================================================"

  mkdir -p "$RFD_OUT"
  $BIOQ run $SVC rfdiffusion \
    --file "target=$INPUTS/2NY7.pdb" \
    --file "framework=$INPUTS/vhh_nbbcII10.pdb" \
    --set num_designs=5 \
    --set "design_loops=H1:7,H2:6,H3:5-13" \
    --set "hotspots=G371,G375,G435,G475" \
    --set diffuser_t=100 \
    --set deterministic=false \
    --wait -o "$RFD_OUT" 2>&1 | tee "$RFD_OUT/_run.log"
  RC=${PIPESTATUS[0]}
  if [ $RC -ne 0 ]; then
    echo "FATAL: RFdiffusion 失败 (exit code=$RC)"
    exit $RC
  fi
  echo "  RFdiffusion 完成: $(date '+%Y-%m-%d %H:%M:%S')"

  RFD_QUIVER="$(find_quiver "$RFD_OUT" "1_rfdiffusion.qv")"
  if [ -z "$RFD_QUIVER" ]; then
    echo "FATAL: RFdiffusion 输出 quiver 不存在"
    find "$RFD_OUT" -type f 2>&1 || true
    exit 1
  fi
fi
echo "  rfdiffusion quiver: $RFD_QUIVER"

RFD_JOB_ID="$(step_job_id "$RFD_OUT/_run.log")"
if [ -z "$RFD_JOB_ID" ]; then
  echo "FATAL: 无法从 $RFD_OUT/_run.log 提取 rfdiffusion job_id"
  exit 1
fi
echo "  rfdiffusion job_id: $RFD_JOB_ID"

# ============================================================
# Step 2: ProteinMPNN  (job:// 链式引用 rfdiffusion 输出)
# ============================================================
MPNN_QUIVER="$(find_quiver "$MPNN_OUT" "2_proteinmpnn.qv")"

if [ -n "$MPNN_QUIVER" ]; then
  echo ""
  echo "  [SKIP] ProteinMPNN 输出已存在，跳过: $MPNN_QUIVER"
else
  echo ""
  echo "============================================================"
  echo "  Step 2/3: ProteinMPNN — $TARGET_NAME"
  echo "  started at: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "============================================================"

  mpnn_input_uri="$(job_uri "$RFD_JOB_ID" "1_rfdiffusion.qv")"
  echo "  input_uri: $mpnn_input_uri"

  mkdir -p "$MPNN_OUT"
  $BIOQ run $SVC proteinmpnn \
    --set "input_uri=$mpnn_input_uri" \
    --set seqs_per_struct=4 \
    --set temperature=0.2 \
    --wait -o "$MPNN_OUT" 2>&1 | tee "$MPNN_OUT/_run.log"
  RC=${PIPESTATUS[0]}
  if [ $RC -ne 0 ]; then
    echo "FATAL: ProteinMPNN 失败 (exit code=$RC)"
    exit $RC
  fi
  echo "  ProteinMPNN 完成: $(date '+%Y-%m-%d %H:%M:%S')"

  MPNN_QUIVER="$(find_quiver "$MPNN_OUT" "2_proteinmpnn.qv")"
  if [ -z "$MPNN_QUIVER" ]; then
    echo "FATAL: ProteinMPNN 输出 quiver 不存在"
    find "$MPNN_OUT" -type f 2>&1 || true
    exit 1
  fi
fi
echo "  proteinmpnn quiver: $MPNN_QUIVER"

MPNN_JOB_ID="$(step_job_id "$MPNN_OUT/_run.log")"
if [ -z "$MPNN_JOB_ID" ]; then
  echo "FATAL: 无法从 $MPNN_OUT/_run.log 提取 proteinmpnn job_id"
  exit 1
fi
echo "  proteinmpnn job_id: $MPNN_JOB_ID"

# ============================================================
# Step 3: RF2  (job:// 链式引用 proteinmpnn 输出)
# ============================================================
RF2_QUIVER="$(find_quiver "$RF2_OUT" "3_rf2.qv")"

if [ -n "$RF2_QUIVER" ]; then
  echo ""
  echo "  [SKIP] RF2 输出已存在，跳过: $RF2_QUIVER"
else
  echo ""
  echo "============================================================"
  echo "  Step 3/3: RF2 — $TARGET_NAME"
  echo "  started at: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "============================================================"

  rf2_input_uri="$(job_uri "$MPNN_JOB_ID" "2_proteinmpnn.qv")"
  echo "  input_uri: $rf2_input_uri"

  mkdir -p "$RF2_OUT"
  $BIOQ run $SVC rf2 \
    --set "input_uri=$rf2_input_uri" \
    --set num_recycles=10 \
    --wait -o "$RF2_OUT" 2>&1 | tee "$RF2_OUT/_run.log"
  RC=${PIPESTATUS[0]}
  if [ $RC -ne 0 ]; then
    echo "FATAL: RF2 失败 (exit code=$RC)"
    exit $RC
  fi
  echo "  RF2 完成: $(date '+%Y-%m-%d %H:%M:%S')"

  RF2_QUIVER="$(find_quiver "$RF2_OUT" "3_rf2.qv")"
  if [ -z "$RF2_QUIVER" ]; then
    echo "FATAL: RF2 输出 quiver 不存在"
    find "$RF2_OUT" -type f 2>&1 || true
    exit 1
  fi
fi
echo "  rf2 quiver: $RF2_QUIVER"

# ============================================================
# 完成
# ============================================================
echo ""
echo "============================================================"
echo "  ALL DONE — $TARGET_NAME"
echo "  finished at: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "  结果目录: $BATCH_DIR/"
echo "  rfdiffusion log : $RFD_OUT/_run.log"
echo "  proteinmpnn log : $MPNN_OUT/_run.log"
echo "  rf2 log         : $RF2_OUT/_run.log"
echo "  rf2 quiver      : $RF2_QUIVER"
echo "============================================================"