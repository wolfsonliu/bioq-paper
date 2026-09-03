#!/usr/bin/env bash
# Throughput scaling — run commands.
#
# 1) 先激活 venv
# 2) 一条条执行下面的命令
#
# 可以并行跑不同的服务（不同终端），同一服务的不同 N 建议顺序跑。
# 跑完后执行 offline 看结果。
set -euo pipefail
cd "$(dirname "$0")"

case "${1:-help}" in
  fetch)
    echo "# === 1. 输入文件 ==="
    echo "bash fetch_inputs.sh"
    ;;

  bioq)
    svc="${2:-}"
    n="${3:-}"
    rep="${4:-}"
    if [[ -n "$svc" ]]; then
      extra=" --svc $svc"
      [[ -n "$n" ]] && extra+=" --N $n"
      [[ -n "$rep" ]] && extra+=" --rep $rep"
      echo "python3 collect_bioq.py$extra"
    else
      echo "# === 2. bioq 臂（一个终端跑一个服务，并行）==="
      echo ""
      for s in dockq plip mmseqs2 reinvent proteinmpnn rfdiffusion rfdiffusion2 boltz boltzgen alphafold; do
        echo "python3 collect_bioq.py --svc $s"
      done
    fi
    ;;

  offline)
    echo "# === 3. 分析 + 绘图 ==="
    echo "bash run_offline.sh"
    echo "# 结果在 data/ 和 figures/"
    ;;

  mock)
    echo "# === 模拟数据测试（不需要云）==="
    echo "python3 make_mock.py && bash run_offline.sh"
    ;;

  plan)
    echo "# 时间预估（bioq 臂，并行跑，全部 3 N × 3 重复，FC 配额 ≤50）"
    echo ""
    echo "  dockq         ~5min       # CPU, 5s/job, 并发~30"
    echo "  plip          ~10min      # CPU, 10s/job, 并发~20"
    echo "  mmseqs2       ~30min      # GPU, 60s/job, 并发~12"
    echo "  reinvent      ~1h         # GPU, 60s/job, 并发~6"
    echo "  rfdiffusion   ~1h         # GPU, 120s/job, 并发~6"
    echo "  proteinmpnn   ~1.5h       # GPU, 150s/job, 并发~8"
    echo "  boltz         ~6h         # GPU, 300s/job, 并发~4"
    echo "  boltzgen      ~6h         # GPU, 300s/job, 并发~4"
    echo "  rfdiffusion2  ~6h         # GPU, 480s/job, 并发~4"
    echo "  alphafold     ~12h        # GPU, 600s/job, 并发~2"
    echo ""
    echo "推荐顺序：先跑 dockq 验证流程"
    ;;

    *)
    echo "用法:"
    echo "  source ~/bioagent/.venv/bin/activate"
    echo ""
    echo "  ./run_experiment.sh fetch     # 打印 fetch 命令"
    echo "  ./run_experiment.sh bioq      # 打印所有服务的 bioq 命令"
    echo "  ./run_experiment.sh bioq dockq       # 打印单个服务的命令"
    echo "  ./run_experiment.sh bioq dockq 10 2  # N=10, rep=2"
    echo "  ./run_experiment.sh offline   # 分析 + 绘图"
    echo "  ./run_experiment.sh mock      # 模拟测试"
    echo "  ./run_experiment.sh plan      # 时间预估"
    ;;
esac