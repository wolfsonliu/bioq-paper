# 1. 激活环境
source "${BIOAGENT_VENV}/bin/activate"
export BIOQ_PROFILE=ecs

# 2. 输入文件
# bash fetch_inputs.sh

# 3. 并行跑 bioq 臂（开 6 个终端，每个跑一个服务）
python3 collect_bioq.py --svc dockq         &  # ~30min
python3 collect_bioq.py --svc plip          &  # ~1h
python3 collect_bioq.py --svc mmseqs2       &  # ~5h
python3 collect_bioq.py --svc reinvent      &  # ~10h
python3 collect_bioq.py --svc proteinmpnn   &  # ~15h
python3 collect_bioq.py --svc rfdiffusion2  &  # ~80h
wait

# 4. 分析 + 绘图
bash run_offline.sh
