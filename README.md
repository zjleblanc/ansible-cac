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

- Ansible with collections that provide `infra.aap_configuration.dispatch` (and related modules/roles used by your AAP version).
- Access to the target controller / platform / EDA / hub APIs (typically via environment variables or credentials configured for those roles—see your collection documentation).

### Apply configuration

`common` is tagged `always` and loads on every run. Domain folders are opt-in via `--tags` (each domain tag is paired with `never`). Resource-specific tags from `infra.aap_configuration` (e.g. `projects`, `credentials`, `job_templates`) still work as a second layer of filtering.

```bash
# Apply only common fundamentals
ansible-playbook pb_aap_config.yml --ask-vault-pass

# Apply common + networking
ansible-playbook pb_aap_config.yml --tags networking --ask-vault-pass

# Apply common + multiple domains
ansible-playbook pb_aap_config.yml --tags networking,cloud --ask-vault-pass

# Apply common + networking, but only projects and credentials
ansible-playbook pb_aap_config.yml --tags networking,projects,credentials --ask-vault-pass

# Apply everything
ansible-playbook pb_aap_config.yml \
  --tags cloud,networking,linux,windows,hashi,aiops,servicenow,apps,aap,hub \
  --ask-vault-pass
```

Use `--vault-password-file` instead of `--ask-vault-pass` in CI or scripted runs.

### Controller export

To pull configuration from a source controller, normalize it, and turn it into YAML you can commit under `config/` for `pb_aap_config.yml` on a destination instance, see [Export Documentation](./README_EXPORT.md).

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
