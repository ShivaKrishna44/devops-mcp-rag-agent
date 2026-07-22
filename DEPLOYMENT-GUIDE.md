# Deployment Guide — MCP + RAG + Ansible Platform

---

## Overview

This repo adds three layers on top of the base microservices platform:
1. **MCP Server** — AI agent that monitors the cluster via kubectl, Prometheus, GitHub, AWS
2. **RAG** — Searches your docs to answer "how did we fix this before?"
3. **Ansible** — Replaces manual bash scripts with idempotent playbooks

---

## Step 1: Provision Infrastructure (Terraform)

```bash
cd Terraform
terraform init -backend-config=tfvars/dev/backend.tfvars
terraform apply -var-file=tfvars/dev/dev.tfvars
```

Creates: VPC, EKS cluster, ECR repos, IAM roles.

---

## Step 2: Bootstrap Cluster (Ansible)

```bash
cd ansible
ansible-playbook playbooks/bootstrap-cluster.yml \
  -e "jenkins_admin_password=YourPass123" \
  -e "grafana_admin_password=GrafanaPass456"
```

**What it does (in order):**
1. Verifies cluster connectivity
2. Creates all namespaces
3. Creates secrets FIRST (prevents Init:0/2 stuck pods)
4. Installs ALB Controller
5. Installs Jenkins (waits for ready)
6. Installs ArgoCD
7. Installs Monitoring
8. Installs SonarQube
9. Installs Argo Rollouts
10. Applies ingresses + ArgoCD apps

---

## Step 3: Setup Jenkins Agent (Ansible)

```bash
vim ansible/inventory/hosts.ini   # Update agent IP
ansible-playbook playbooks/setup-jenkins-agent.yml \
  -e "jenkins_agent_secret=SECRET_FROM_JENKINS_UI"
```

Installs: Java, Docker, kubectl, Helm, Terraform, sonar-scanner, agent.jar + systemd service.

---

## Step 4: Setup MCP Server

```bash
cd mcp-server
pip install -r requirements.txt
export GITHUB_TOKEN="ghp_your_token"
export AWS_REGION="us-east-1"
export PROMETHEUS_URL="http://localhost:9090"
```

---

## Step 5: Index Documents (RAG)

```bash
python rag/ingest.py
```

Indexes all `.md`, `.yaml`, `.sh` files into ChromaDB for semantic search.

---

## Step 6: Start MCP Server

```bash
python mcp_server.py
```

38 tools available: kubectl, prometheus, github, aws, rag.

---

## Step 7: Connect to Kiro

Already configured in `.kiro/settings/mcp.json`. Ask questions like:
- "Is anything broken in the cluster?"
- "How did we fix Jenkins Init:0/2 before?"
- "Show deployment steps for ArgoCD"

---

## URLs (After Deployment)

| Service | URL |
|---|---|
| Jenkins | https://jenkins.vosukula.online |
| ArgoCD | https://argocd.vosukula.online |
| Grafana | https://grafana.vosukula.online |
| SonarQube | https://sonar.vosukula.online |
| Application | https://app.vosukula.online |
