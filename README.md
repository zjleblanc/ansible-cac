# ansible-cac

Configuration as Code for Ansible Automation Platform.

## Repository structure

Configuration is organized by **domain** under `config/`. Shared fundamentals live in `config/common/`; domain folders hold resources exclusive to that domain. Wildcard variable suffixes (e.g. `controller_templates_cloud`) are merged by `infra.aap_configuration.dispatch` when `dispatch_include_wildcard_vars` is enabled. See [config/README.md](./config/README.md) for domain descriptions and per-domain apply instructions.

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
│   ├── servicenow/   # ServiceNow ITSM
│   ├── apps/         # SSL/ACME, Kasa, CyberArk, Vault, security demos
│   ├── aap/          # AAP self-management (EE builds, backups, PAH)
│   └── hub/          # Private Automation Hub
├── vars/
├── pb_aap_config.yml
```

- **config/common/** — Resources referenced by multiple domains (always applied unless skipped).
- **config/\<domain\>/** — Domain-specific resources; no cross-dependencies between domains.
- **vars/** — Vaulted variables and in-repo `*_secrets.redacted.yml` examples (see [Secrets](#secrets)).
- `pb_aap_config.yml` — Component-agnostic playbook; select domains via Ansible tags.

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

`common` is tagged `always` and loads on every run. Domain folders are opt-in via `--tags` (each domain tag is paired with `never`). Resource-specific tags from `infra.aap_configuration` (e.g. `projects`, `credentials`, `job_templates`) still work as a second layer of filtering.

```bash
# Apply only common fundamentals
ansible-playbook pb_aap_config.yml

# Apply common + networking
ansible-playbook pb_aap_config.yml --tags networking

# Apply common + multiple domains
ansible-playbook pb_aap_config.yml --tags networking,cloud

# Apply common + networking, but only projects and credentials
ansible-playbook pb_aap_config.yml --tags networking,projects,credentials

# Apply everything
ansible-playbook pb_aap_config.yml \
  --tags cloud,networking,linux,windows,hashi,aiops,servicenow,apps,aap,hub
```

If `ANSIBLE_VAULT_PASSWORD_FILE` (or another vault config) is not set, add `--ask-vault-pass` or `--vault-password-file <path>` when encrypted `vars/` files are required.

### Pre-commit

This repository includes a [pre-commit](https://pre-commit.com/) configuration with [Gitleaks](https://gitleaks.io/) to reduce the risk of committing secrets. After installing pre-commit: `pre-commit install`.

## Secrets

Sensitive values used to populate credentials and other configuration details are supplied from vaulted files.

```text
vars
├── controller_secrets.yml
├── eda_secrets.yml
└── platform_secrets.yml
```

Each file is encrypted with `ansible-vault`. `pb_aap_config.yml` loads all three by default. Real secret files are not included in this public repository (they are ignored via `.gitignore` as `vars/*secrets.yml`). Redacted examples (`*_secrets.redacted.yml`) are included only as shape/documentation for the variables you need to define locally.
