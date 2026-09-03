# OpenADMET Anvil Skill

A [Claude Code](https://claude.ai/code) skill for designing, writing, and running OpenADMET Anvil workflows. Covers recipe authoring, component selection, hyperparameter guidance, inference, and production (no-split) model training.

## What this skill does

When active, Claude understands the full Anvil recipe format and will:

- Ask the right questions before writing a recipe (task type, dataset columns, compute, evaluation needs)
- Select compatible components (featurizer + model + trainer + splitter must all match)
- Enforce the validation rules that cause hard `ValueError`s at runtime (val_size constraints, n_tasks matching, ensemble/CV exclusivity, etc.)
- Write complete, runnable recipe YAML with correct structure
- Provide deep learning hyperparameter guidance and point to [optimus-prime](https://github.com/OpenADMET/optimus-prime) canonical recipes
- Cover inference (`openadmet predict`) including active learning acquisition functions
- Guide production no-split model training

## Requirements

- [Claude Code](https://claude.ai/code) CLI or IDE extension
- Skills support (available in current Claude Code releases)

---

## Installation

### Option 1 — Project-level (recommended for OpenADMET repos)

The skill will be available only when Claude Code is opened inside that project directory.

```bash
git clone https://github.com/OpenADMET/openadmet-anvil-skill /tmp/openadmet-anvil-skill
mkdir -p .claude/skills/openadmet-anvil
cp /tmp/openadmet-anvil-skill/*.md .claude/skills/openadmet-anvil/
```

Commit the `.claude/skills/` directory so the whole team gets the skill automatically:

```bash
git add .claude/skills/openadmet-anvil/
git commit -m "Add OpenADMET Anvil Claude Code skill"
```

### Option 2 — Global (available in all your projects)

```bash
git clone https://github.com/OpenADMET/openadmet-anvil-skill /tmp/openadmet-anvil-skill
mkdir -p ~/.claude/skills/openadmet-anvil
cp /tmp/openadmet-anvil-skill/*.md ~/.claude/skills/openadmet-anvil/
```

Global skills are not committed to any repository — they live only on your machine.

### Keeping the skill up to date

```bash
# Pull latest and re-copy to whichever location you installed to
git -C /tmp/openadmet-anvil-skill pull
cp /tmp/openadmet-anvil-skill/*.md ~/.claude/skills/openadmet-anvil/
# or for project-level:
# cp /tmp/openadmet-anvil-skill/*.md .claude/skills/openadmet-anvil/
```

---

## Usage

Once installed, Claude Code picks up the skill automatically. You can invoke it explicitly with the slash command:

```
/openadmet-anvil
```

Or just describe what you want — Claude will trigger the skill when the request is clearly Anvil-related:

> "Write me an Anvil recipe for pIC50 regression on this CSV using LGBM"

> "Set up a ChemProp multitask recipe for four CYP targets"

> "How do I run inference on a trained Anvil model?"

> "I want a production no-split model for deployment"

---

## Skill structure

```
openadmet-anvil-skill/
├── SKILL.md                # main skill — entry point
├── dl_hyperparameters.md   # ChemPropModel / LightningTrainer params + optimus-prime fetch
├── fine_tuning.md          # param_path/serial_path and from_foundation fine-tuning
├── production_models.md    # no-split training for deployment
├── inference.md            # openadmet predict CLI and Python API
├── model_comparison.md     # training multiple variants and openadmet compare
├── docker.md               # running in the official Docker image
└── README.md               # this file
```

---

## What the skill covers

| Section | Topics |
|---------|--------|
| Requirements gathering | Task type, dataset columns, split strategy, compute |
| Component selection | All featurizers, models, splitters, trainers, evaluators, ensembles, transforms |
| Compatibility rules | val_size constraints, n_tasks matching, ensemble/CV exclusivity, driver matching |
| Recipe templates | Full annotated YAML skeleton + 6 canonical patterns |
| Running workflows | CLI (`openadmet anvil`) and Python API |
| DL hyperparameters | All `ChemPropModel` and `LightningTrainer` params, LR scheduling, weight freezing, CheMeleon fine-tuning |
| Inference | `openadmet predict` CLI and Python API, output column naming, acquisition functions (UCB/EI/PI) |
| Production models | No-split training, two-stage workflow, DL `max_epochs` selection |
| Common mistakes | The runtime `ValueError`s that are easy to hit |
