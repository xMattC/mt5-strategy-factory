![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![YAML](https://img.shields.io/badge/YAML-Configuration_CB171E?logo=yaml)
![Testing](https://img.shields.io/badge/Testing-pytest-0A9EDC)
![Architecture](https://img.shields.io/badge/Architecture-Modular-success)
![CI](https://img.shields.io/badge/Workflow-Automation-orange)
![MT5](https://img.shields.io/badge/MT5-Research_Framework-green)

# MT5 Strategy Factory

A Python-based framework for automated generation, transformation and evaluation of modular strategy configurations.

The project focuses on workflow orchestration, configuration-driven architecture, automated processing pipelines, and research automation through reusable software components.

While the domain is quantitative strategy research, the primary engineering focus is on building scalable and maintainable software systems.

---

## 🔍 Domain Context

MetaTrader 5 (MT5) is a multi-asset trading platform widely used for developing and executing automated trading strategies. [Learn more](https://www.metatrader5.com/en)

In this project, MT5 acts as the execution environment for optimisation and evaluation workflows, while the primary software focus is on orchestration, configuration management, and research automation.

---

## 🎯 Engineering Focus

This project was built to demonstrate:

- Configuration-driven application design
- Modular pipeline architecture
- Workflow orchestration
- Dynamic branch generation
- YAML validation and parsing
- Manifest and lineage tracking
- Structured output generation
- Research workflow automation
- Large-scale processing pipelines
- Separation of concerns and reusable components

---

## 🛠️ Tech Stack

- **Language:** Python
- **Configuration:** YAML
- **Data Processing:** Pandas
- **Architecture:** Modular pipelines
- **Automation:** MT5 CLI integration
- **Validation:** Custom validation framework
- **Development:** Git

---

## 🔑 Key Features

- Multi-stage optimisation pipelines
- Dynamic branch generation
- Candidate lineage tracking
- Manifest-driven workflow state management
- Automatic YAML generation and validation
- Structured output generation
- Modular stage processing
- Automated compilation and execution workflows
- In-sample / out-of-sample evaluation support

---

## 🧱 Engineering Practices

This project evolved iteratively while exploring workflow automation and strategy research concepts. Development focused on improving maintainability and reducing complexity as the project grew.

Key practices include:

- Modular application design
- Separation of concerns
- Reusable software components
- Configuration-driven behaviour
- Validation layers
- Incremental refactoring and improvement
- Structured outputs for reproducibility

---

## 📈 Architecture

A key focus of this project was designing a modular pipeline architecture that allows independent processing stages while maintaining full traceability between generated results.

<p align="center">
<img src="docs/images/architecture.png" width="800">
</p>

This architecture provides:

- Independent stage execution
- Candidate lineage tracking
- Reproducible workflows
- Modular configuration systems
- Structured outputs
- Scalable processing

Full architecture documentation:

[Architecture Document](docs/architecture.md)

---

## 🔄 Processing Workflow

The currently implemented pipeline progressively builds complete systems using staged processing.

Example workflow:

```text
Trigger
    ↓
Confirmation
    ↓
Trendline
    ↓
Volume
    ↓
Exit
    ↓
Results
    ↓
Resolved Configuration
```
---

## 📂 Example Output Structure

```text
outputs/
└── Example_Run/
    ├── Trigger/
    │   └── branch_0001/
    │       ├── results.yaml
    │       └── .resolved.yaml
    │
    ├── Confirmation/
    ├── Trendline/
    ├── Volume/
    └── Exit/
```

---

## ⚙️ Running Locally
Prerequisites

Before running:

- Python 3.8+, MetaTrader 5, Git
- [MyLibs dependency](https://github.com/xMattC/mt5-quant-lib)

```Bash
# Clone repository:

git clone https://github.com/xMattC/mt5-strategy-factory.git
cd mt5-strategy-factory

# Create virtual environment:
python -m venv .venv

# Activate:
.venv\Scripts\activate

# Install requirements:
pip install -r requirements.txt

```
## 📚 Documentation

Additional documentation:

| Document | Description |
|-----------|-------------|
| `architecture.md` | System architecture and workflow design |
| `configuration.md` | YAML configuration system |
| `strategy-pipeline.md` | Pipeline stages and processing |
| `manifest-system.md` | Manifest and lineage tracking |
| `testing.md` | Testing strategy |
| `roadmap.md` | Future development plans |
| `examples.md` | Example workflows and outputs |
examples.md	Example workflows and outputs

---

## ⚠️ Current Limitations
- Test coverage currently focuses on critical components and core workflows
- Integration testing remains limited
- Full execution currently requires a local MT5 installation
- Workflow execution is research-oriented rather than cloud-native
- Distributed processing is not implemented

---

## 🚀 Future Improvements
- Expanded automated testing coverage
- Improved visualisation tooling
- Distributed execution support
- Additional processing pipelines
- Dashboard and reporting system
- Improved configuration tooling
