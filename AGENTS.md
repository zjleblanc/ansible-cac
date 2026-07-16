# Agent instructions — ansible-cac

This repository is Ansible Automation Platform (AAP) Configuration as Code. Configuration is applied with `infra.aap_configuration.dispatch` and **wildcard vars** so the same resource type can be split across domain folders.

Prefer [README.md](./README.md) and [config/README.md](./config/README.md) for human-oriented usage. This file is for agents editing or extending the repo.

## Mental model

```text
config/<domain>/*.yml  →  include_vars (by tag)  →  dispatch_include_wildcard_vars: true
                                                    merges controller_*_<suffix> → controller_*
```

- Domains are **logical product areas**, not AAP components (controller vs hub vs eda).
- `config/common/` holds fundamentals and anything referenced by **more than one** domain.
- Each other domain depends only on **itself + common**. No cross-domain references to definitions that live in another domain folder.
- Entry playbook: [`pb_aap_config.yml`](./pb_aap_config.yml).

## Domains

| Folder | Tag | Contents |
|--------|-----|----------|
| `common` | `always` + `common` (omit with `--skip-tags common`) | Orgs, users, teams, authenticators, EEs, labels, notifications, multi-domain projects/credentials/inventories/sources |
| `cloud` | `cloud` | AWS / Azure / GCP / VMware exclusive resources |
| `networking` | `networking` | Cisco / Palo Alto / Summit Connect |
| `linux` | `linux` | Linux/RHEL, lockdown, satellite-related exclusive resources |
| `windows` | `windows` | Windows / AD / Proxmox exclusive resources |
| `hashi` | `hashi` | HashiCorp Terraform / HCP / Vault |
| `aiops` | `aiops` | EDA controller JTs/workflows + EDA component vars (`eda_*_aiops`) |
| `servicenow` | `servicenow` | ServiceNow / Selenium JTs (deps usually in common) |
| `apps` | `apps` | SSL/ACME, Kasa, CyberArk, policy demos |
| `aap` | `aap` | AAP self-mgmt, EE builds, PAH sync templates |
| `hub` | `hub` | Private Automation Hub (`hub_*` / `ah_*` vars) |

Domain docs:

- [config/README.md](./config/README.md) — index of domains with short descriptions and links
- `config/<domain>/README.md` — how to apply that domain and file-scoped tag examples

## Wildcard variable naming (required)

Every list variable **must** use a domain suffix matching the folder:

```yaml
# ansible-playbook pb_aap_config.yml --tags cloud,job_templates --skip-tags common
---
controller_templates_cloud:
  - name: AWS // Create VM
    ...
```

Dispatch merges `controller_templates_cloud` + `controller_templates_networking` + … into `controller_templates`.

Use the same pattern for other resource keys, for example:

- `controller_projects_<domain>`
- `controller_credentials_<domain>`
- `controller_credential_types_<domain>`
- `controller_inventories_<domain>`
- `controller_inventory_sources_<domain>`
- `controller_groups_<domain>`
- `controller_workflows_<domain>`
- `controller_schedules_<domain>`
- `aap_organizations_common`, `gateway_authenticators_common`, …
- `eda_projects_aiops`, `eda_credentials_aiops`, …
- `hub_ee_registries_hub`, `ah_groups_hub`, …

Do **not** define the unsuffixed base list (e.g. `controller_templates:`) in config files when using wildcards.

## Placement rules (no cross-dependencies)

Before adding or moving a resource, ask: **is this definition referenced by job templates / workflows / inventory sources in more than one domain?**

| Answer | Place in |
|--------|----------|
| Yes (2+ domains) | `config/common/` with `_common` suffix |
| No (one domain only) | That domain folder with `_<domain>` suffix |

Examples of common (shared) definitions:

- Projects used by multiple domains (e.g. Cloud Mgmt, Linux Mgmt, Windows Mgmt, Autodotes)
- Credentials used across domains (e.g. Controller Credential, West ServiceNow, AWS Sandbox, machine SSH keys)
- Inventories used across domains (e.g. Autodotes Lab, Cloud Inventory)

Examples of domain-local definitions:

- Network Mgmt project → `networking`
- Terraform Mgmt project → `hashi`
- HashiCorp Vault credentials / Vault // job templates → `hashi`
- Event-Driven Demos project → `aiops`

**Schedules are not global.** A schedule belongs in the same domain as the job template (or workflow) it targets (`unified_job_template`).

**Inventory sources / groups** belong with the inventory they attach to (or in `common` if that inventory is shared). Prefer keeping groups next to the domain that owns the use case when the inventory itself is shared (e.g. Proxmox groups under `windows`).

## Var file one-liners (required)

Every YAML var file under `config/` must start with a comment one-liner for applying that file’s resource type.

**Domain files** (not `common`):

```yaml
# ansible-playbook pb_aap_config.yml --tags <domain>,<resource_tag> --skip-tags common
```

**Common files** (do not use a `common` tag in `--tags`; other domains already use `never`):

```yaml
# ansible-playbook pb_aap_config.yml --tags <resource_tag>
```

Rules:

- Do **not** put `--ask-vault-pass` on var-file one-liners. Domain / config READMEs may mention vault flags as optional.
- `--skip-tags common` on domain file one-liners skips loading `config/common` for that scoped run (common `include_vars` is tagged `[always, common]`).
- Keep the one-liner in sync when renaming files or changing resource tags.
- When adding/removing YAML files in a domain, update that domain’s `README.md` file table.

Resource tags match `infra.aap_configuration.dispatch` (examples: `projects`, `credentials`, `credential_types`, `job_templates`, `workflow_job_templates`, `inventories`, `inventory_sources`, `host_groups`, `schedules`, `organizations`, `users`, `teams`, `authenticators`, `authenticator_maps`, `execution_environments`, `labels`, `notification_templates`, EDA `project` / `credential` / `event_stream` / `rulebook_activation`, Hub `registries` / `repos` / `collectionremote`).

## Applying configuration

```bash
# common only
ansible-playbook pb_aap_config.yml

# common + one domain
ansible-playbook pb_aap_config.yml --tags networking

# domain file scope (matches var-file one-liners)
ansible-playbook pb_aap_config.yml --tags networking,job_templates --skip-tags common

# compose domain + resource tags (common still loaded)
ansible-playbook pb_aap_config.yml --tags networking,projects,credentials
```

Vault is optional at the CLI: add `--ask-vault-pass` or `--vault-password-file <path>` when secrets in `vars/` are required.

Tag layers:

1. **Domain tags** — which folders’ vars are loaded (`never` = opt-in; `common` is `always` unless skipped).
2. **Resource tags** — which dispatch roles run (`projects`, `credentials`, `job_templates`, …).

`dispatch` is tagged `always` so it runs after the selected vars are loaded.

## Adding a new resource (checklist)

1. Choose the correct domain (or `common` if shared).
2. Add the object to the matching file under `config/<domain>/`, using the suffixed variable name.
3. Ensure the file has the correct one-liner comment at the top (see above).
4. Ensure any **referenced** project, credential, credential type, inventory, EE, and label already exist in that domain or in `common`.
5. If a dependency is missing and would be used only here, add it in the same domain. If other domains already need it, put the definition in `common` instead of duplicating.
6. For `aiops` job templates and workflows, include `labels` containing `AIOps`. Keep the `AIOps` label definition in `config/common/labels.yml`.
7. Do not put secrets in config YAML. Reference vaulted vars from `vars/*_secrets.yml` (see redacted examples). Never commit real `*secrets.yml` files.
8. If you add a **new domain folder**:
   - Add `include_vars` in `pb_aap_config.yml` with `tags: [<domain>, never]`
   - Add `config/<domain>/README.md` (apply instructions + file table)
   - Link it from [config/README.md](./config/README.md)
9. If you add/remove a YAML file in an existing domain, update that domain’s README file table.

## What not to do

- Do not reintroduce flat `controller/`, `eda/`, `hub/`, `platform/` layouts or component-specific apply playbooks as the primary path; use `config/` + `pb_aap_config.yml`.
- Do not put a shared project/credential/inventory only in one domain if another domain’s templates reference it by name — that creates a silent apply-order / missing-object dependency. Move the definition to `common`.
- Do not invent or hardcode secret values; use `{{ controller_credential_* }}` (or the appropriate vault var) and document new vars in the matching `*_secrets.redacted.yml`.
- Do not omit or drift var-file one-liners / domain README tables when changing config layout.
- Do not edit the plan file under `.cursor/plans/` unless the user asks.

## Related files

- [`pb_aap_config.yml`](./pb_aap_config.yml) — apply playbook
- [`config/README.md`](./config/README.md) — domain index
- [`config/<domain>/README.md`](./config/README.md) — per-domain apply docs
- [`README.md`](./README.md) — repo overview
- [`README_EXPORT.md`](./README_EXPORT.md) — export/normalize into CaC
- [`scripts/migrate_to_wildcard_config.py`](./scripts/migrate_to_wildcard_config.py) — one-time migration reference (historical)
- [redhat-cop/aap_configuration_template](https://github.com/redhat-cop/aap_configuration_template) — upstream pattern for wildcard vars + `dispatch_include_wildcard_vars`
