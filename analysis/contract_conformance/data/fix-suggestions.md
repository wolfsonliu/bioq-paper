# Contract-conformance 审计 — bioq-services 修复实施指南

> **结果(2026-08-21):** 本指南的修复已落地(framework C/A1 + 服务端 A2/B
> 注解,网关改为静态 manifest 服务),重跑本审计得到:task endpoints 全通过
> **98.5%**、服务 ≥0.9 **96.7%**(中位数 1.0),`docs_text`/`file_fields`/
> 结构项全部 100%。唯一残余:chembounce `scaffold_hop` 的 `input_smiles_uri`
> 未加 `bioq_default` 注解(见附录)。

来源:uniform-contract conformance 审计(2026-08-20,28 个已审计服务、
65 个 task endpoints;数据见本目录 `conformance.csv` / `summary.json`)。
目标仓库:`bioq-services`。按本文档修改后,重跑本审计验证(见文末)。

## 修复优先级总览

| 修复 | 位置 | 改动量 | 影响 |
|------|------|--------|------|
| **C** `array[file]` 文件识别 | framework `manifest.py` | 1 个函数 + 1 个测试 | openadmet `file_fields` 转正 |
| **A1** `register_task_endpoint` 支持 summary | framework `task_endpoint.py` | 1 个函数签名 | 解锁 9 个 endpoint 的 A2 修复 |
| **A2** 补 endpoint summary | 12 个服务 | 25 个 task endpoint(+5 reinvent legacy) | `docs_text` 61.5% → 100% |
| **B** defaults | 各服务 `models.py`(B3 可选框架) | 多 | 真正的瓶颈,见专项说明 |

预期效果(同一 checklist 复算):

| 场景 | 中位数 | 服务 ≥0.9 | 全通过 task endpoints |
|------|--------|-----------|------------------------|
| 现状 | 0.80 | 3/28 (11%) | 7/65 (11%) |
| C + A 完成 | 0.80 | 4/28 (14%) | 11/65 (17%) |
| C + A + B 完成 | 1.00 | 28/28 (100%) | 65/65 (100%) |

> 结构契约(`typed_params` / `machine_view`)已 100%,无需改动。

---

## C. 框架:`array[file]` 输入识别为文件(1 行修复)

**问题**:openadmet `/api/tasks/compare` 的 `model_stats_files` 声明为
`array[file]` 但 `is_file=false`,对 `bioq run --file` 上传面不可见。根因是
`_is_file_schema` 只认标量 binary。

**文件**:`framework/src/bioq_service/manifest.py`

当前代码:

```python
def _is_file_schema(schema: dict[str, Any]) -> bool:
    """Multipart file uploads show up as either format=binary or contentMediaType=...octet-stream."""
    if schema.get("type") != "string":
        return False
    return (
        schema.get("format") == "binary"
        or schema.get("contentMediaType") == "application/octet-stream"
    )
```

替换为(增加 array 递归;`_format_type` 已能把 array[binary] 渲染成
`array[file]`,此处只补 `is_file`):

```python
def _is_file_schema(schema: dict[str, Any]) -> bool:
    """Multipart file uploads: format=binary / octet-stream, scalar or array of them."""
    if schema.get("type") == "array":
        return _is_file_schema(schema.get("items") or {})
    if schema.get("type") != "string":
        return False
    return (
        schema.get("format") == "binary"
        or schema.get("contentMediaType") == "application/octet-stream"
    )
```

**测试**:`framework/tests/test_manifest.py`,仿照已有的
`test_extract_fields_marks_file_uploads_by_schema_shape` 追加:

```python
def test_extract_fields_marks_file_arrays_as_files() -> None:
    """list[UploadFile] (array of binary) must come out is_file=True / type='array[file]'."""
    from bioq_service.manifest import _extract_fields

    body_schema = {
        "type": "object",
        "properties": {
            "model_stats_files": {
                "type": "array",
                "items": {"type": "string", "format": "binary"},
                "title": "Model Stats Files",
            },
        },
    }
    fields = {f.name: f for f in _extract_fields(body_schema)}
    assert fields["model_stats_files"].is_file is True
    assert fields["model_stats_files"].type == "array[file]"
```

**跨仓库跟进(非本仓库改动)**:修复后 `bioq describe openadmet` 会把
`model_stats_files` 列进 `files:` 区;需确认 bioq CLI 的 `--file` 上传路径
支持同名多文件(array 语义),如不支持则在 bioq 仓库补上传侧处理。

---

## A. docs_text:补 endpoint summary

### A1. 框架:`register_task_endpoint` 透传 summary/description

**问题**:9 个无上传 task endpoint 通过 `register_task_endpoint` 注册,
该 helper 的 `app.add_api_route(...)` 不带 summary,服务侧无法提供文案。

**文件**:`framework/src/bioq_service/task_endpoint.py`(约 L216)

签名增加两个可选参数并透传:

```python
def register_task_endpoint(
    app: FastAPI,
    *,
    path: str,
    label: str,
    request_model: type[BaseModel],
    build_argv: BuildArgvForTask,
    save_inputs: Optional[Callable[[BaseModel, Path], None]] = None,
    summary: Optional[str] = None,          # 新增
    description: Optional[str] = None,      # 新增
) -> None:
    ...
    app.add_api_route(
        path,
        _task_handler,
        methods=["POST"],
        response_model=JobInfo,
        summary=summary,                    # 新增
        description=description,            # 新增
    )
```

(`summary=None` 时行为与现状完全一致,不影响未改动的服务。)

### A2. 各服务补 summary(可直接粘贴)

规则:显式 `@app.post` 的,在装饰器加 `summary="..."`;
`register_task_endpoint(...)` 的,在调用里加 `summary="..."`(依赖 A1)。
文案按"legacy 孪生端点措辞 + task 语义"拟定;`(single atomic task)` 表示
阻塞式一次完成,区别于 submit/poll。

**显式 @app.post(16 个):**

| 服务 | endpoint | 文件:行 | summary= |
|------|----------|---------|----------|
| diffdock | `/api/tasks/dock` | `services/diffdock-server/app.py:233` | `"Protein-ligand docking (single atomic task)."` |
| drughive | `/api/tasks/generate` | `services/drughive-server/app.py:351` | `"De novo ligand generation (single atomic task)."` |
| drughive | `/api/tasks/generate_spatial` | `services/drughive-server/app.py:392` | `"Substructure modification / scaffold hopping (single atomic task)."` |
| drughive | `/api/tasks/optimize` | `services/drughive-server/app.py:445` | `"Multi-cycle QVina2 property optimization (single atomic task; long-running)."` |
| openadmet | `/api/tasks/compare` | `services/openadmet-server/app.py:397` | `"Post-hoc comparison of pre-trained models (Mode A) or their stats JSON (Mode B; single atomic task)."` |
| pocketxmol | `/api/tasks/dock` | `services/pocketxmol-server/app.py:502` | `"Molecular docking, small-molecule or peptide (single atomic task)."` |
| pocketxmol | `/api/tasks/sbdd` | `services/pocketxmol-server/app.py:533` | `"De novo structure-based drug design (single atomic task)."` |
| pocketxmol | `/api/tasks/linking` | `services/pocketxmol-server/app.py:557` | `"Fragment linking / growing / PROTAC linker design (single atomic task)."` |
| pocketxmol | `/api/tasks/optimize` | `services/pocketxmol-server/app.py:585` | `"Molecular optimization: local refinement of an input ligand (single atomic task)."` |
| pocketxmol | `/api/tasks/pepdesign` | `services/pocketxmol-server/app.py:613` | `"Peptide design: linear/cyclic de novo, inverse folding, sc-packing (single atomic task)."` |
| pocketxmol | `/api/tasks/confidence` | `services/pocketxmol-server/app.py:644` | `"Tuned-ranker confidence scoring on a previously completed job (single atomic task)."` |
| reinvent | `/api/tasks/sampling` | `services/reinvent-server/app.py:262` | `"De novo sampling from a Reinvent generator (single atomic task)."` |
| reinvent | `/api/tasks/scoring` | `services/reinvent-server/app.py:277` | `"Score SMILES with a scoring function (single atomic task)."` |
| reinvent | `/api/tasks/enumeration` | `services/reinvent-server/app.py:292` | `"Peptide enumeration with pepinvent (single atomic task)."` |
| reinvent | `/api/tasks/transfer-learning` | `services/reinvent-server/app.py:310` | `"Fine-tune a generative prior on target molecules (single atomic task; long-running)."` |
| reinvent | `/api/tasks/staged-learning` | `services/reinvent-server/app.py:330` | `"Staged learning: RL / curriculum over multiple stages (single atomic task; long-running)."` |

装饰器改法示例(diffdock L233):

```python
@app.post("/api/tasks/dock", response_model=JobInfo,
          summary="Protein-ligand docking (single atomic task).")
```

**register_task_endpoint(9 个,依赖 A1):**

| 服务 | endpoint | 文件:行 | summary= |
|------|----------|---------|----------|
| flowmol | `/api/tasks/generate` | `services/flowmol-server/app.py:146` | `"Unconditional molecule generation (single atomic task)."` |
| immunebuilder | `/api/tasks/predict_antibody` | `services/immunebuilder-server/app.py:194` | `"Predict antibody structure from heavy + light chain sequences (single atomic task)."` |
| immunebuilder | `/api/tasks/predict_nanobody` | `services/immunebuilder-server/app.py:201` | `"Predict nanobody structure from heavy chain sequence (single atomic task)."` |
| immunebuilder | `/api/tasks/predict_tcr` | `services/immunebuilder-server/app.py:208` | `"Predict TCR structure from alpha + beta chain sequences (single atomic task)."` |
| megalodon | `/api/tasks/generate` | `services/megalodon-server/app.py:154` | `"Unconditional generation (single atomic task)."` |
| ppiflow | `/api/tasks/sample/monomer` | `services/ppiflow-server/app.py:328` | `"Unconditional monomer generation at the requested lengths (single atomic task)."` |
| rfdiffusion | `/api/tasks/generate/unconditional` | `services/rfdiffusion-server/app.py:310` | `"Unconditional monomer, or macrocycle with cyclic=true (single atomic task)."` |
| rfdiffusion | `/api/tasks/generate/symmetry` | `services/rfdiffusion-server/app.py:317` | `"Symmetric oligomer: cyclic / dihedral / tetrahedral (single atomic task)."` |
| semlaflow | `/api/tasks/generate` | `services/semlaflow-server/app.py:153` | `"Unconditional generation (single atomic task)."` |

**reinvent 附加项**:它的 5 个 legacy 端点同样没有文档(本审计 "all
endpoints" 口径下也失败),建议一并补(去掉 task 措辞即可):

| endpoint | 文件:行 | summary= |
|----------|---------|----------|
| `/api/sampling` | `services/reinvent-server/app.py:191` | `"De novo sampling from a Reinvent generator."` |
| `/api/scoring` | `services/reinvent-server/app.py:202` | `"Score SMILES with a scoring function."` |
| `/api/enumeration` | `services/reinvent-server/app.py:213` | `"Peptide enumeration with pepinvent."` |
| `/api/transfer-learning` | `services/reinvent-server/app.py:227` | `"Fine-tune a generative prior on target molecules (long-running)."` |
| `/api/staged-learning` | `services/reinvent-server/app.py:243` | `"Staged learning: RL / curriculum over multiple stages (long-running)."` |

---

## B. defaults:可选参数默认值不可见(真正的瓶颈)

**根因**(已验证):54/65 task endpoint 失败,全部是 `Optional[X] = None`
参数。FastAPI 的 OpenAPI 对 None 默认值**不输出 `default` 键**(抽查
dockq/alphafold/rfdiffusion/reinvent:112 个非空默认值正常输出、0 个显式
null、66 个无键),manifest 因此显示 `default: null` = "未声明"。服务代码
普遍只透传参数,有效默认值在**上游工具内部**,无法从服务代码机械推导。

### B1(推荐):把确有默认行为的参数改成具体默认值

- 方法:对每个 `Optional[X] = None` 参数,查上游工具的 CLI/config 文档,
  若"省略时工具实际用某值",就在 `models.py` 里声明它,例如
  `mapping: str = "auto"`、`seed: int = 42`。
- 已有好样板:多数服务的 `name: str = "run"`。
- **不要批量臆造**:错误默认值比缺失更糟。拿不准的走 B2。
- 优先级:reinvent(5 端点)、pocketxmol(6 端点)、rfdiffusion、drughive。

### B2:None 即"未提供"的,在 description 写明

约定文案:`"Default: unset — only used when explicitly provided."`
(或该 None 的真实语义,如 device 的 `"Default: auto-select CUDA if
available."`)。本审计检查仍会诚实失败,但 agent 可用性立即改善;范围以
`conformance.csv` 中 `defaults=0` 的 endpoint 为准。

### B3(可选,框架级):区分"显式 null"与"未声明"

FastAPI 在 schema 层丢失了该信息,如需结构化区分,需要模型层约定 +
manifest 透传,草图:

```python
# 服务 models.py:显式声明"默认值就是 None"
device: Optional[str] = Field(default=None, json_schema_extra={"default_declared": True})

# manifest.py FieldInfo 增加
has_explicit_default: bool = Field(default=False, ...)

# _extract_fields 中
has_explicit_default=("default" in fschema
                      or bool(fschema.get("default_declared")))
```

随后本审计的 `defaults` 检查可改为"default != null 或 has_explicit_default"。
这是契约变更,建议与 B1/B2 落地后视剩余缺口再决定。

---

## 验证

1. **框架测试**:
   ```bash
   cd framework && uv run pytest tests/test_manifest.py tests/test_task_endpoint.py -v
   ```
2. **受影响服务离线测试**(示例):
   ```bash
   uv run python -m pytest services/openadmet-server/tests -v
   uv run python -m pytest services/reinvent-server/tests -v
   ```
3. **重跑本审计**(本分析文件夹):
   ```bash
   cd .
   BIOQ=/path/to/bioq ./run_all.sh        # live:重新采集 + 评分 + 出图
   ```
   注意:需先重新部署改动过的服务镜像,`describe` 取到的才是新 manifest。
4. **抽查**:`bioq describe reinvent` 应显示每个 endpoint 的 summary 行;
   `bioq describe openadmet` 的 `compare` 应把 `model_stats_files` 列入
   `files:` 区。
5. **目标数字**:`docs_text` task 通过率 61.5% → 100%;`file_fields`
   98.5% → 100%;B 完成后 `defaults` 16.9% → 100%,服务 ≥0.9 达 28/28。

## 附:现状快照(2026-08-20 审计)

- 注册 31 服务;`ensemble` 为 legacy /v1 API,不在 uniform contract 范围,
  已排除;`esmfold2` / `promera` 审计时不可达(冷启动/运维问题),列为
  未审计、不计分。
- 28 个已审计服务,135 endpoints(65 task)。
- 结构项:`typed_params` 100%、`machine_view` 100%(task)、
  `file_fields` 98.5%;元数据项:`docs_text` 61.5%、`defaults` 16.9%。
- 另有全舰队已知现象:`operation_id` 在 manifest 中未填充(审计仅作信息
  列记录,不计分),如需修复属框架 `manifest.py::_service_endpoints`。
