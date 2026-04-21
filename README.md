# ansible-cac

Configuration as Code for Ansible Automation Platform.

## Repository structure

Core directories and playbooks for applying configuration as code to the Ansible Automation Platform components.

```text
.
├── controller/
├── eda/
├── hub/
├── platform/
├── vars/
├── pb_controller_cac.yml
├── pb_eda_cac.yml
└── pb_platform_cac.yml
```

- **controller/** — Automation Controller configuration as YAML.
- **eda/** — Event-Driven Ansible (projects, activations, streams, credentials).
- **hub/** — Private automation hub (EEs, collections, users, groups).
- **platform/** — Gateway / platform (organizations, users, teams, authenticators).
- **vars/** — Vaulted variables and in-repo `*_secrets.redacted.yml` examples (see [Secrets](#secrets)).
- `pb_controller_cac.yml` — Apply controller CaC (`controller/` + `vars/controller_secrets.yml`).
- `pb_eda_cac.yml` — Apply EDA CaC (`eda/` + `vars/eda_secrets.yml`).
- `pb_platform_cac.yml` — Apply platform CaC (`platform/` + `vars/platform_secrets.yml`).

## Usage

### Prerequisites

- Ansible with collections that provide `infra.aap_configuration.dispatch` (and related modules/roles used by your AAP version).
- Access to the target controller / platform / EDA APIs (typically via environment variables or credentials configured for those roles—see your collection documentation).

### Apply configuration

Run the playbook for the component you are updating from the repository root. Each CaC playbook loads YAML from its directory and merges in vaulted variables from `vars/`:

```bash
ansible-playbook pb_controller_cac.yml --ask-vault-pass
ansible-playbook pb_platform_cac.yml --ask-vault-pass
ansible-playbook pb_eda_cac.yml --ask-vault-pass
```

Use `--vault-password-file` instead of `--ask-vault-pass` in CI or scripted runs.

### Controller export

To pull configuration from a source controller, normalize it, and turn it into YAML you can commit under `controller/` for `pb_controller_cac.yml` on a destination instance, see [Controller export process](#controller-export-process).

### Pre-commit

This repository includes a [pre-commit](https://pre-commit.com/) configuration with [Gitleaks](https://github.com/gitleaks/gitleaks) to reduce the risk of committing secrets. After installing pre-commit: `pre-commit install`.

## Secrets

Sensitive values used to populate credentials and other configuration details are supplied from vaulted files.

```text
vars
├── controller_secrets.yml
├── eda_secrets.yml
└── platform_secrets.yml
```

Each file is encrypted with `ansible-vault`, and you will see references to them in each `pb_{component}_cac.yml` playbook. Since these playbooks are run locally for now, the real secret files are not included in this public repository (they are also ignored via `.gitignore` as `vars/*secrets.yml`). If you were looking for them and do not see them, that is why. Redacted examples (`*_secrets.redacted.yml`) are included only as shape/documentation for the variables you need to define locally.
