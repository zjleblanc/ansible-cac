# ansible-cac

Configuration as Code for Ansible Automation Platform.

## Repository structure

Configuration is organized by **domain** under `config/`. Shared fundamentals live in `config/common/`; domain folders hold resources exclusive to that domain. Wildcard variable suffixes (e.g. `controller_templates_cloud`) are merged by `infra.aap_configuration.dispatch` when `dispatch_include_wildcard_vars` is enabled. Domains are selected with the `domains` extra-var. See [config/README.md](./config/README.md) for domain descriptions and per-domain apply instructions.

```text
.
├── config/
│   ├── common/       # Orgs, users, shared projects/credentials/inventories, EEs, labels
│   ├── cloud/        # AWS, Azure, GCP, VMware
│   ├── networking/   # Cisco, Palo Alto
│   ├── linux/        # Linux/RHEL management and patching
│   ├── windows/      # Windows, AD, Proxmox
│   ├── hashi/        # HashiCorp Terraform/HCP + Vault
│   ├── aiops/        # EDA + AIOps (controller JTs + EDA component)
│   ├── business/     # Business process automation (BPA)
│   ├── itsm/         # ServiceNow ITSM + OpenFlake CMDB
│   ├── apps/         # SSL/ACME, Kasa, CyberArk, Vault, security demos
│   ├── aap/          # AAP self-management (EE builds, backups, PAH)
│   └── hub/          # Private Automation Hub
├── vars/
├── pb_aap_config.yml
```

- **config/common/** — Resources referenced by multiple domains (always applied unless skipped).
- **config/\<domain\>/** — Domain-specific resources; no cross-dependencies between domains.
- **vars/** — Vaulted variables and in-repo `*_secrets.redacted.yml` examples (see [Secrets](#secrets)).
- `pb_aap_config.yml` — Component-agnostic playbook; select domains via the `domains` extra-var.

## AI-Powered Configuration-as-Code Lifecycle

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'edgeLabelBackground': '#e0f0ff',
    'lineColor': '#e0f0ff',
    'tertiaryTextColor': '#151515'
  },
  'themeCSS': '.edgeLabel .labelBkg { background-color: #e0f0ff !important; border: 1px solid #0066cc; border-radius: 4px; padding: 4px 10px; } .edgeLabel span, .edgeLabel p { background-color: transparent !important; color: #003366 !important; margin: 0; }'
}}%%
flowchart TD
    AAP[AAP Environment]:::aap
    MCP:::ai@{ shape: console, label: "AAP MCP Server" }
    Skills:::ai@{ shape: subproc, label: "Agent Skills" }
    Git:::git@{ shape: docs, label: "Comprehensive AAP CaC"}
    Collection:::collection@{ shape: subproc, label: "infra.aap_configuration --> apply" }

    AAP -->|"&nbsp;1. Prototype in UI&nbsp;"| MCP
    MCP <-->|"&nbsp;2. Extract & Format&nbsp;"| Skills
    Skills -->|"&nbsp;3. Commit Changes&nbsp;"| Git
    Git -->|"&nbsp;4. Trigger GitOps&nbsp;"| Collection
    Collection -->|"&nbsp;5. Idempotent Push&nbsp;"| AAP

    linkStyle default stroke:#e0f0ff,stroke-width:2px;

    classDef aap fill:#5f0000,stroke:#f9a8a8,stroke-width:2px,color:#ffffff;
    classDef ai fill:#21134d,stroke:#b6a6e9,stroke-width:2px,color:#ffffff;
    classDef git fill:#732e00,stroke:#f8ae54,stroke-width:2px,color:#ffffff;
    classDef collection fill:#004d4d,stroke:#9ad8d8,stroke-width:2px,color:#ffffff;
```

## Usage

### Prerequisites

- Python 3 with `venv`
- Network access to the target AAP gateway / controller (and hub / EDA if you apply those resources)

### Local environment (venv and API env vars)

Create and activate a virtualenv, then install Ansible and the collections this repo uses:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install ansible-core
ansible-galaxy collection install -r collections/requirements.yml
```

`.venv/` is gitignored. Reactivate the venv in each new shell before running playbooks.

Authenticate to AAP with environment variables (preferred for local runs). Use a token **or** username/password:

```bash
export AAP_HOSTNAME="https://aap.example.com"
export AAP_VALIDATE_CERTS=true

# Option A — OAuth token (preferred)
export AAP_TOKEN="your-token"

# Option B — username / password
export AAP_USERNAME="admin"
export AAP_PASSWORD="your-password"

# Vault password file (if not set in ansible.cfg or elsewhere)
export ANSIBLE_VAULT_PASSWORD_FILE="$HOME/.ansible/ansible-cac-vault-pass"
```

| Variable | Purpose |
|----------|---------|
| `AAP_HOSTNAME` | AAP gateway / platform URL |
| `AAP_TOKEN` | OAuth2 token (preferred over password) |
| `AAP_USERNAME` / `AAP_PASSWORD` | Basic auth when not using a token |
| `AAP_VALIDATE_CERTS` | TLS verification (`true` / `false`) |
| `ANSIBLE_VAULT_PASSWORD_FILE` | Path to a file containing the vault password for `vars/*_secrets.yml` (skip if you already configure vault via `ansible.cfg`, `--vault-password-file`, or another mechanism) |

The underlying collections also accept legacy `CONTROLLER_*` and `GATEWAY_*` names as fallbacks; `AAP_*` works across controller and gateway modules. Do not commit real tokens, passwords, or vault password files—keep them in your shell, a private path outside the repo, or a secrets manager.

Vaulted values under `vars/` (credential inputs, etc.) are separate from these API login variables—see [Secrets](#secrets).

### Apply configuration

`common` loads on every run by default; set `skip_common=true` to omit it. Domain folders are opt-in via the
`domains` extra-var (a comma-separated string or a YAML/JSON list). Resource-specific tags from
`infra.aap_configuration` (e.g. `projects`, `credentials`, `job_templates`) are a fully independent second layer
of filtering — pass them via `--tags` and they compose with any `domains` selection without conflict.

```bash
# Apply only common fundamentals
ansible-playbook pb_aap_config.yml

# Apply common + networking
ansible-playbook pb_aap_config.yml -e "domains=networking"

# Apply common + multiple domains
ansible-playbook pb_aap_config.yml -e "domains=networking,cloud"

# Apply common + networking, but only projects and credentials
ansible-playbook pb_aap_config.yml -e "domains=networking" --tags projects,credentials

# Apply everything
ansible-playbook pb_aap_config.yml \
  -e "domains=cloud,networking,linux,windows,hashi,aiops,business,itsm,apps,aap,hub"
```

If `ANSIBLE_VAULT_PASSWORD_FILE` (or another vault config) is not set, add `--ask-vault-pass` or `--vault-password-file <path>` when encrypted `vars/` files are required.

### Pre-commit

This repository includes a [pre-commit](https://pre-commit.com/) configuration with [Gitleaks](https://gitleaks.io/) to reduce the risk of committing secrets. After installing pre-commit: `pre-commit install`.

## Secrets

Sensitive values used to populate credentials and other configuration details are supplied from vaulted files.

```text
vars/
├── controller_secrets.yml      # always loaded
├── eda_secrets.yml
└── platform_secrets.yml

config/<domain>/
├── vault.yml                   # optional; loaded only when that domain is selected
└── vault.redacted.yml          # committed shape/docs (mock values only)
```

Global `vars/*_secrets.yml` files are encrypted with `ansible-vault` and loaded on every apply. Optional `config/<domain>/vault.yml` (and `config/common/vault.yml`) are loaded only when that domain is selected (`common` unless `skip_common=true`). Domain vault keys use the `<domain>_var_<name>` convention (e.g. `business_var_support_case_accounts`). Real secret files are gitignored (`**/*secrets.yml`, `**/vault.yml`). Redacted counterparts (`*_secrets.redacted.yml`, `vault.redacted.yml`) document expected variable names with mock placeholders (`"secret"`, `["user@example.com"]`, …) — never production-looking secrets.
