# DevOps MCP + RAG Agent

AI-powered DevOps monitoring platform combining:
- **MCP Server** — 38 tools for live cluster monitoring (kubectl, Prometheus, GitHub, AWS)
- **RAG** — Semantic search over project docs to answer "how did we fix X?"
- **Ansible** — Configuration management for Jenkins agent + cluster bootstrap

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  You: "Is anything broken? How did we fix this last time?"      │
│                     ↓                                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         MCP Server (mcp_server.py)                      │    │
│  │                                                         │    │
│  │  LIVE TOOLS (35+):          RAG TOOLS (3):              │    │
│  │  ├── kubectl ops            ├── search_runbook          │    │
│  │  ├── prometheus queries     ├── search_troubleshooting  │    │
│  │  ├── github operations      └── search_deployment_steps │    │
│  │  └── aws cli                                            │    │
│  └────────────┬──────────────────────────┬─────────────────┘    │
│               ↓                          ↓                      │
│  ┌────────────────────┐    ┌──────────────────────────┐         │
│  │  Live EKS Cluster  │    │  ChromaDB Vector Store   │         │
│  │  (kubectl/prom)    │    │  (Your docs indexed)     │         │
│  └────────────────────┘    └──────────────────────────┘         │
│                                                                 │
│  Ansible Playbooks:                                             │
│  ├── setup-jenkins-agent.yml   ← Provision agent (idempotent)   │
│  └── bootstrap-cluster.yml     ← Full cluster setup             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
.
├── mcp-server/
│   ├── mcp_server.py          ← MCP server (38 tools)
│   ├── requirements.txt
│   └── rag/
│       ├── ingest.py          ← Index docs into ChromaDB
│       ├── query.py           ← Semantic search engine
│       └── requirements.txt
├── ansible/
│   ├── playbooks/
│   │   ├── setup-jenkins-agent.yml
│   │   └── bootstrap-cluster.yml
│   ├── inventory/hosts.ini
│   ├── group_vars/jenkins_agents.yml
│   └── templates/jenkins-agent.service.j2
├── app/                       ← 3 Python microservices
├── charts/                    ← Helm chart
├── kubernetes/                ← K8s manifests
├── scripts/                   ← Cluster install scripts
├── Terraform/                 ← IaC (EKS, VPC, ECR)
├── MCP-RAG-SETUP.md           ← MCP + RAG setup guide
└── DEPLOYMENT-GUIDE.md        ← Platform deployment guide
```

---

## Quick Start

```bash
# 1. Install MCP + RAG dependencies
cd mcp-server
pip install -r requirements.txt

# 2. Index your docs (RAG)
python rag/ingest.py

# 3. Start MCP server
python mcp_server.py

# 4. Setup Jenkins agent via Ansible
cd ../ansible
ansible-playbook playbooks/setup-jenkins-agent.yml

# 5. Bootstrap full cluster
ansible-playbook playbooks/bootstrap-cluster.yml
```

---

## Documentation

| Document | What It Covers |
|---|---|
| `MCP-RAG-SETUP.md` | MCP server + RAG setup, all 38 tools, usage examples |
| `DEPLOYMENT-GUIDE.md` | Full platform deployment (Terraform → EKS → services) |
| `ansible/README.md` | Ansible playbook usage and configuration |

---

## Tech Stack

| Component | Technology |
|---|---|
| MCP Server | FastMCP (Python) |
| RAG | ChromaDB + SentenceTransformers |
| Configuration Mgmt | Ansible |
| Infrastructure | Terraform + AWS EKS |
| CI/CD | Jenkins + ArgoCD |
| Monitoring | Prometheus + Grafana |
| App | Python Flask microservices |
