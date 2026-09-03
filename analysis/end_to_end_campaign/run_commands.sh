#!/usr/bin/env bash
# ============================================================
# rfantibody — bioq 命令编排器（支持串行 / 分批 / 打印计划）
#
# 用法:
#   运行单个靶标:   bash run_commands.sh HIV_Env
#   运行全部靶标:   bash run_commands.sh
#   打印计划(不运行): bash run_commands.sh print
#   分批(每批 50 designs): BATCH_SIZE=50 bash run_commands.sh HIV_Env
#
# 链式调用说明 — 与 run_batched.sh 一致:
#   rfantibody-server 的 proteinmpnn/rf2 输入端已从 `input_uri` 改名为
#   `input_quiver_uri`（配合 `--file input_quiver=<path>` 上传）。本脚本
#   直接把上一步下载到本地的 .qv 文件作为文件路径重新上传，实现三步串联。
# ============================================================
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
INPUTS="$HERE/inputs"
RESULTS="$HERE/results"
BIOQ="bioq --profile ecs"
SVC="rfantibody"

# --- 激活 venv（run_batched.sh 同款，避免手动 source) ---
BIOAGENT_VENV="${BIOAGENT_VENV:-$HOME/bioagent/.venv}"
if [ -f "$BIOAGENT_VENV/bin/activate" ]; then
  source "$BIOAGENT_VENV/bin/activate"
fi

# BATCH_SIZE 环境变量: 每批的 designs 数 (默认 0 = 不分批)
BATCH_SIZE="${BATCH_SIZE:-0}"

# ---------------------------------------------------------------
# 靶标定义: name|pdb|framework|hotspots|loops|num_designs|diffuser_t
# ---------------------------------------------------------------
# VHH 靶标 (Table 5)
TARGETS=(
  "HIV_Env|2NY7.pdb|vhh_nbbcII10.pdb|G371,G375,G435,G475|H1:7,H2:6,H3:5-13|1000|100"
  "SARS_CoV2_RBD|6M0J.pdb|vhh_nbbcII10.pdb|E492,E493,E494,E495,E496,E497|H1:7,H2:6,H3:5-13|1000|50"
  "RSV_Site_I|7LVW.pdb|vhh_nbbcII10.pdb|D469,D384|H1:7,H2:6,H3:5-13|1000|50"
  "RSV_Site_III|rsv_site3.pdb|vhh_nbbcII10.pdb|T305,T456|H1:7,H2:6,H3:5-13|1000|50"
  "Influenza_HA|flu_HA.pdb|vhh_nbbcII10.pdb|B146,B170,B177|H1:7,H2:6,H3:5-13|1000|50"
  "TcdB|6C0B.pdb|vhh_nbbcII10.pdb|A1433,A1435,A1437,A1438,A1493|H1:7,H2:6,H3:5-13|1000|50"
  "IL7R_alpha|3DI3.pdb|vhh_nbbcII10.pdb|B81,B139,B192|H1:7,H2:6,H3:5-13|1000|50"
)
# scFv 靶标 (Table 7)
SCFV_TARGETS=(
  "TcdB_scFv_unique|7ML7.pdb|hu-4D5-8_Fv.pdb|A1816,A1818,A1819,A1823,A1831|H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13|1000|50"
  "TcdB_scFv_combinatorial|6C0B.pdb|hu-4D5-8_Fv.pdb|A1433,A1435,A1437,A1438,A1493|H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13|1000|50"
)
ALL_TARGETS=("${TARGETS[@]}" "${SCFV_TARGETS[@]}")

# ---------------------------------------------------------------
# 辅助: 解析靶标定义
# ---------------------------------------------------------------
parse_target() {
  local IFS='|'
  local parts=($1)
  echo "${parts[0]} ${parts[1]} ${parts[2]} ${parts[3]} ${parts[4]} ${parts[5]} ${parts[6]}"
}

# ================================================================
# 辅助: 解析某一步输出的 quiver 文件路径
# ================================================================

# bioq 下载后是扁平路径（无 output/ 前缀），兜底检查 output/ 子目录
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

# ---------------------------------------------------------------
# 打印单条 bioq 命令
# ---------------------------------------------------------------
_bioq_cmd() {
  echo "$BIOQ run $SVC" "$@"
}

# ---------------------------------------------------------------
# 打印单个 batch 的三步命令（后两步用 --file input_quiver 上传上一步本地输出）
# ---------------------------------------------------------------
_print_batch() {
  local name="$1" pdb="$2" framework="$3" hotspots="$4" loops="$5" batch_size="$6" T="$7" batch_out="$8"
  local batch_dir="$(dirname "$batch_out")"   # e.g. results/HIV_Env/batch_00
  local mpnn_out="$batch_dir/proteinmpnn"
  local rf2_out="$batch_dir/rf2"

  echo "# rfdiffusion"
  _bioq_cmd rfdiffusion \
    "--file target=$INPUTS/$pdb" \
    "--file framework=$INPUTS/$framework" \
    "--set num_designs=$batch_size" \
    "--set design_loops=$loops" \
    "--set hotspots=$hotspots" \
    "--set diffuser_t=$T" \
    "--set deterministic=false" \
    "--wait -o $batch_out"
  echo ""

  echo "# proteinmpnn — uploads the local rfdiffusion quiver"
  _bioq_cmd proteinmpnn \
    "--file input_quiver=$batch_out/1_rfdiffusion.qv" \
    "--set seqs_per_struct=8" \
    "--set temperature=0.2" \
    "--wait -o $mpnn_out"
  echo ""

  echo "# rf2 — uploads the local proteinmpnn quiver"
  _bioq_cmd rf2 \
    "--file input_quiver=$mpnn_out/2_proteinmpnn.qv" \
    "--set num_recycles=10" \
    "--wait -o $rf2_out"
  echo ""
}

# ---------------------------------------------------------------
# 打印所有命令（不执行）—— 仅作计划预览，直接运行请用 run 模式
# ---------------------------------------------------------------
print_commands() {
  echo "# ============================================================"
  echo "# 端到端设计流程 — 所有靶标的 bioq 命令(计划预览)"
  echo "#"
  echo "# 注意: proteinmpnn / rf2 用 --file input_quiver= 直接把上一步"
  echo "# 下载到本地的 .qv 文件重新上传。上一步必须先运行成功:"
  echo "#   bash run_commands.sh <target>"
  echo "#   BATCH_SIZE=50 bash run_commands.sh <target>"
  echo "# ============================================================"
  echo ""

  for raw in "${ALL_TARGETS[@]}"; do
    read -r name pdb framework hotspots loops num T <<< "$(parse_target "$raw")"

    echo "# --------------------------------------------------"
    echo "# $name  (total=${num})"
    echo "# --------------------------------------------------"
    echo ""

    if [ "$BATCH_SIZE" -gt 0 ] && [ "$num" -gt "$BATCH_SIZE" ]; then
      local n_batches=$(( (num + BATCH_SIZE - 1) / BATCH_SIZE ))
      local remaining=$num
      local batch_i=0
      while [ $remaining -gt 0 ]; do
        local this_batch=$BATCH_SIZE
        [ $remaining -lt $BATCH_SIZE ] && this_batch=$remaining
        local batch_name=$(printf "batch_%02d" $batch_i)
        local batch_out="$RESULTS/$name/$batch_name/rfdiffusion"

        echo "# ----- batch ${batch_i}/${n_batches} (${this_batch} designs) -----"
        _print_batch "$name" "$pdb" "$framework" "$hotspots" "$loops" \
          "$this_batch" "$T" "$batch_out"
        remaining=$(( remaining - this_batch ))
        batch_i=$(( batch_i + 1 ))
      done

      echo "# 合并所有 batch 的 rf2 结果"
      echo "python3 $HERE/merge_quivers.py" \
        "$RESULTS/$name/batch_*/rf2/3_rf2.qv" \
        "-o $RESULTS/$name/merged/3_rf2.qv"
      echo ""
    else
      _print_batch "$name" "$pdb" "$framework" "$hotspots" "$loops" \
        "$num" "$T" "$RESULTS/$name/rfdiffusion"
    fi
    echo ""
  done
}

# ---------------------------------------------------------------
# 运行单个 batch 的三步（本地 quiver 上传 + 断点续跑）
# ---------------------------------------------------------------
_run_one_batch() {
  local name="$1" pdb="$2" framework="$3" hotspots="$4" loops="$5" batch_size="$6" T="$7" batch_out="$8"
  local batch_dir="$(dirname "$batch_out")"   # e.g. results/HIV_Env/batch_00
  local mpnn_out="$batch_dir/proteinmpnn"
  local rf2_out="$batch_dir/rf2"
  local rfd_qv mpnn_qv rc

  # ---- Step 1: rfdiffusion ----
  rfd_qv="$(find_quiver "$batch_out" "1_rfdiffusion.qv")"
  if [ -n "$rfd_qv" ]; then
    echo "  [SKIP] ${name} rfdiffusion 输出已存在: $rfd_qv"
  else
    echo ""
    echo "  [${name} rfdiffusion] ${batch_size} designs..."
    mkdir -p "$batch_out"
    $BIOQ run $SVC rfdiffusion \
      --file "target=$INPUTS/$pdb" \
      --file "framework=$INPUTS/$framework" \
      --set "num_designs=$batch_size" \
      --set "design_loops=$loops" \
      --set "hotspots=$hotspots" \
      --set "diffuser_t=$T" \
      --set "deterministic=false" \
      --wait -o "$batch_out" 2>&1 | tee "$batch_out/_run.log"
    rc=${PIPESTATUS[0]}
    [ $rc -ne 0 ] && echo "  !! rfdiffusion 失败 (rc=$rc)" && return 1
    rfd_qv="$(find_quiver "$batch_out" "1_rfdiffusion.qv")"
    [ -z "$rfd_qv" ] && echo "  !! rfdiffusion 输出 quiver 缺失" && return 1
    echo "  [${name} rfdiffusion] 完成"
  fi
  # ---- Step 2: proteinmpnn (上传 rfdiffusion 输出的本地 quiver) ----
  mpnn_qv="$(find_quiver "$mpnn_out" "2_proteinmpnn.qv")"
  if [ -n "$mpnn_qv" ]; then
    echo "  [SKIP] ${name} proteinmpnn 输出已存在: $mpnn_qv"
  else
    echo ""
    echo "  [${name} proteinmpnn] input_quiver=$rfd_qv"
    mkdir -p "$mpnn_out"
    $BIOQ run $SVC proteinmpnn \
      --file "input_quiver=$rfd_qv" \
      --set "seqs_per_struct=8" \
      --set "temperature=0.2" \
      --wait -o "$mpnn_out" 2>&1 | tee "$mpnn_out/_run.log"
    rc=${PIPESTATUS[0]}
    [ $rc -ne 0 ] && echo "  !! proteinmpnn 失败 (rc=$rc)" && return 1
    mpnn_qv="$(find_quiver "$mpnn_out" "2_proteinmpnn.qv")"
    [ -z "$mpnn_qv" ] && echo "  !! proteinmpnn 输出 quiver 缺失" && return 1
    echo "  [${name} proteinmpnn] 完成"
  fi
  # ---- Step 3: rf2 (上传 proteinmpnn 输出的本地 quiver) ----
  if [ -n "$(find_quiver "$rf2_out" "3_rf2.qv")" ]; then
    echo "  [SKIP] ${name} rf2 输出已存在: $(find_quiver "$rf2_out" "3_rf2.qv")"
  else
    echo ""
    echo "  [${name} rf2] input_quiver=$mpnn_qv"
    mkdir -p "$rf2_out"
    $BIOQ run $SVC rf2 \
      --file "input_quiver=$mpnn_qv" \
      --set "num_recycles=10" \
      --wait -o "$rf2_out" 2>&1 | tee "$rf2_out/_run.log"
    rc=${PIPESTATUS[0]}
    [ $rc -ne 0 ] && echo "  !! rf2 失败 (rc=$rc)" && return 1
    [ -z "$(find_quiver "$rf2_out" "3_rf2.qv")" ] && echo "  !! rf2 输出 quiver 缺失" && return 1
    echo "  [${name} rf2] 完成"
  fi
  return 0
}

# ---------------------------------------------------------------
# 运行单个靶标的所有三步（支持分批）
# ---------------------------------------------------------------
run_target() {
  local raw="$1"
  read -r name pdb framework hotspots loops num T <<< "$(parse_target "$raw")"

  echo ""
  echo "============================================================"
  echo "=== $name"
  echo "    target:    $pdb"
  echo "    framework: $framework"
  echo "    hotspots:  $hotspots"
  echo "    loops:     $loops"
  echo "    designs:   $num"
  echo "    diffuser_t: $T"
  echo "============================================================"

  local out="$RESULTS/$name"

  if [ "$BATCH_SIZE" -gt 0 ] && [ "$num" -gt "$BATCH_SIZE" ]; then
    # -----------------------------------------------------------
    # 分批模式: 三步一起拆分，每个 batch 独立运行
    # -----------------------------------------------------------
    local n_batches=$(( (num + BATCH_SIZE - 1) / BATCH_SIZE ))
    local remaining=$num
    local batch_i=0
    local rf2_qvs=()

    while [ $remaining -gt 0 ]; do
      local this_batch=$BATCH_SIZE
      [ $remaining -lt $BATCH_SIZE ] && this_batch=$remaining
      local batch_name=$(printf "batch_%02d" $batch_i)
      local batch_out="$out/$batch_name/rfdiffusion"
      rf2_qvs+=("$out/$batch_name/rf2/3_rf2.qv")

      echo ""
      echo "  >>> batch ${batch_i}/${n_batches} (${this_batch} designs) <<<"
      _run_one_batch "$name" "$pdb" "$framework" "$hotspots" "$loops" \
        "$this_batch" "$T" "$batch_out" || return 1

      remaining=$(( remaining - this_batch ))
      batch_i=$(( batch_i + 1 ))
    done

    # 合并所有 batch 的 rf2 Quiver
    echo ""
    echo "  [${name} merge] 合并 ${#rf2_qvs[@]} 个 batch 的 rf2 结果..."
    python3 "$HERE/merge_quivers.py" "${rf2_qvs[@]}" \
      -o "$out/merged/3_rf2.qv"
  else
    # -----------------------------------------------------------
    # 不分批模式: 三步串行
    # -----------------------------------------------------------
    _run_one_batch "$name" "$pdb" "$framework" "$hotspots" "$loops" \
      "$num" "$T" "$out/rfdiffusion" || return 1
  fi

  echo ""
  echo "  >>> $name 完成"
}

# ---------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------
main() {
  local target_filter="${1:-}"

  if [ "$target_filter" = "print" ]; then
    print_commands
    return
  fi

  # 选择要运行的靶标
  local selected=()
  if [ -n "$target_filter" ]; then
    for raw in "${ALL_TARGETS[@]}"; do
      read -r name _ <<< "$(parse_target "$raw")"
      if [ "$name" = "$target_filter" ]; then
        selected+=("$raw")
      fi
    done
    if [ ${#selected[@]} -eq 0 ]; then
      echo "未知靶标: $target_filter"
      echo "可用靶标:"
      for raw in "${ALL_TARGETS[@]}"; do
        read -r name _ <<< "$(parse_target "$raw")"
        echo "  $name"
      done
      exit 1
    fi
  else
    selected=("${ALL_TARGETS[@]}")
  fi

  # 确保 inputs 存在
  if [ ! -f "$INPUTS/vhh_nbbcII10.pdb" ]; then
    echo "缺少 inputs — 请先运行 bash fetch_inputs.sh"
    exit 1
  fi

  mkdir -p "$RESULTS"

  for raw in "${selected[@]}"; do
    run_target "$raw"
  done
}

main "$@"