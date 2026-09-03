#!/usr/bin/env bash
cd "$(dirname "$0")"
# ============================================================
# 端到端设计流程 — 所有靶标的 bioq 命令(计划预览)
#
# 注意: proteinmpnn / rf2 用 --file input_quiver= 直接把上一步
# 下载到本地的 .qv 文件重新上传。上一步必须先运行成功:
#   bash run_commands.sh <target>
#   BATCH_SIZE=50 bash run_commands.sh <target>
# ============================================================

# --------------------------------------------------
# HIV_Env  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/2NY7.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=G371,G375,G435,G475 --set diffuser_t=100 --set deterministic=false --wait -o ./results/HIV_Env/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/HIV_Env/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/HIV_Env/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/HIV_Env/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/HIV_Env/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/HIV_Env/batch_*/rf2/3_rf2.qv -o ./results/HIV_Env/merged/3_rf2.qv


# --------------------------------------------------
# SARS_CoV2_RBD  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6M0J.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=E492,E493,E494,E495,E496,E497 --set diffuser_t=50 --set deterministic=false --wait -o ./results/SARS_CoV2_RBD/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/SARS_CoV2_RBD/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/SARS_CoV2_RBD/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/SARS_CoV2_RBD/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/SARS_CoV2_RBD/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/SARS_CoV2_RBD/batch_*/rf2/3_rf2.qv -o ./results/SARS_CoV2_RBD/merged/3_rf2.qv


# --------------------------------------------------
# RSV_Site_I  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7LVW.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=D469,D384 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_I/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_I/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_I/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_I/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_I/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/RSV_Site_I/batch_*/rf2/3_rf2.qv -o ./results/RSV_Site_I/merged/3_rf2.qv


# --------------------------------------------------
# RSV_Site_III  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/rsv_site3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=T305,T456 --set diffuser_t=50 --set deterministic=false --wait -o ./results/RSV_Site_III/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/RSV_Site_III/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/RSV_Site_III/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/RSV_Site_III/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/RSV_Site_III/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/RSV_Site_III/batch_*/rf2/3_rf2.qv -o ./results/RSV_Site_III/merged/3_rf2.qv


# --------------------------------------------------
# Influenza_HA  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/flu_HA.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B146,B170,B177 --set diffuser_t=50 --set deterministic=false --wait -o ./results/Influenza_HA/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/Influenza_HA/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/Influenza_HA/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/Influenza_HA/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/Influenza_HA/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/Influenza_HA/batch_*/rf2/3_rf2.qv -o ./results/Influenza_HA/merged/3_rf2.qv


# --------------------------------------------------
# TcdB  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/TcdB/batch_*/rf2/3_rf2.qv -o ./results/TcdB/merged/3_rf2.qv


# --------------------------------------------------
# IL7R_alpha  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/3DI3.pdb --file framework=./inputs/vhh_nbbcII10.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13 --set hotspots=B81,B139,B192 --set diffuser_t=50 --set deterministic=false --wait -o ./results/IL7R_alpha/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/IL7R_alpha/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/IL7R_alpha/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/IL7R_alpha/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/IL7R_alpha/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/IL7R_alpha/batch_*/rf2/3_rf2.qv -o ./results/IL7R_alpha/merged/3_rf2.qv


# --------------------------------------------------
# TcdB_scFv_unique  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/7ML7.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1816,A1818,A1819,A1823,A1831 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_unique/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_unique/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_unique/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_unique/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_unique/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/TcdB_scFv_unique/batch_*/rf2/3_rf2.qv -o ./results/TcdB_scFv_unique/merged/3_rf2.qv


# --------------------------------------------------
# TcdB_scFv_combinatorial  (total=1000)
# --------------------------------------------------

# ----- batch 0/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_00/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_00/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_00/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_00/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_00/rf2

# ----- batch 1/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_01/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_01/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_01/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_01/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_01/rf2

# ----- batch 2/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_02/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_02/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_02/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_02/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_02/rf2

# ----- batch 3/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_03/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_03/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_03/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_03/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_03/rf2

# ----- batch 4/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_04/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_04/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_04/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_04/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_04/rf2

# ----- batch 5/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_05/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_05/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_05/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_05/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_05/rf2

# ----- batch 6/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_06/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_06/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_06/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_06/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_06/rf2

# ----- batch 7/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_07/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_07/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_07/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_07/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_07/rf2

# ----- batch 8/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_08/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_08/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_08/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_08/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_08/rf2

# ----- batch 9/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_09/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_09/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_09/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_09/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_09/rf2

# ----- batch 10/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_10/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_10/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_10/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_10/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_10/rf2

# ----- batch 11/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_11/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_11/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_11/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_11/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_11/rf2

# ----- batch 12/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_12/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_12/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_12/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_12/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_12/rf2

# ----- batch 13/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_13/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_13/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_13/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_13/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_13/rf2

# ----- batch 14/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_14/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_14/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_14/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_14/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_14/rf2

# ----- batch 15/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_15/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_15/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_15/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_15/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_15/rf2

# ----- batch 16/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_16/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_16/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_16/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_16/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_16/rf2

# ----- batch 17/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_17/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_17/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_17/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_17/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_17/rf2

# ----- batch 18/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_18/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_18/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_18/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_18/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_18/rf2

# ----- batch 19/20 (50 designs) -----
# rfdiffusion
bioq --profile ecs run rfantibody rfdiffusion --file target=./inputs/6C0B.pdb --file framework=./inputs/hu-4D5-8_Fv.pdb --set num_designs=50 --set design_loops=H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13 --set hotspots=A1433,A1435,A1437,A1438,A1493 --set diffuser_t=50 --set deterministic=false --wait -o ./results/TcdB_scFv_combinatorial/batch_19/rfdiffusion

# proteinmpnn — uploads the local rfdiffusion quiver
bioq --profile ecs run rfantibody proteinmpnn --file input_quiver=./results/TcdB_scFv_combinatorial/batch_19/rfdiffusion/1_rfdiffusion.qv --set seqs_per_struct=8 --set temperature=0.2 --wait -o ./results/TcdB_scFv_combinatorial/batch_19/proteinmpnn

# rf2 — uploads the local proteinmpnn quiver
bioq --profile ecs run rfantibody rf2 --file input_quiver=./results/TcdB_scFv_combinatorial/batch_19/proteinmpnn/2_proteinmpnn.qv --set num_recycles=10 --wait -o ./results/TcdB_scFv_combinatorial/batch_19/rf2

# 合并所有 batch 的 rf2 结果
python3 ./merge_quivers.py ./results/TcdB_scFv_combinatorial/batch_*/rf2/3_rf2.qv -o ./results/TcdB_scFv_combinatorial/merged/3_rf2.qv


