# Changelog

## 2026-08-15 — Add OpenFlake AWS provision and decommission CaC

AWS lifecycle demos that create or tear down EC2 instances and register or remove matching CMDB CIs in OpenFlake (ServiceNow-compatible), then sync inventory from the OpenFlake CMDB for patch and agent steps.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Credential | OpenFlake | for integrating with ServiceNow using servicenow.itsm collection | common | [🕵️](config/common/credentials.yml#L174-L181) |
| Inventory | OpenFlake Inventory | OpenFlake CMDB via servicenow.itsm.now inventory plugin | cloud | [🕵️](config/cloud/inventories.yml#L9-L13) |
| Inventory source | openflake.servicenow.itsm.now | SCM sync of OpenFlake CMDB hosts via servicenow.itsm.now | cloud | [🕵️](config/cloud/inventory_sources.yml#L24-L32) |
| Job template | OpenFlake // Create CIs | Create cmdb_ci_vm_instance items in OpenFlake | servicenow | [🕵️](config/servicenow/job_templates.yml#L68-L94) |
| | OpenFlake // Delete CIs | Delete cmdb_ci_vm_instance items in OpenFlake | servicenow | [🕵️](config/servicenow/job_templates.yml#L121-L146) |
| Workflow job template | AWS // Decommission Workflow // OpenFlake | AWS decommission using the OpenFlake ServiceNow credential | cloud | [🕵️](config/cloud/workflow_job_templates.yml#L51-L98) |
| | AWS // Provisioning Workflow // OpenFlake | AWS provisioning using the OpenFlake ServiceNow credential | cloud | [🕵️](config/cloud/workflow_job_templates.yml#L212-L325) |

### Secrets

| Component | Variable | Credential |
|-----------|----------|------------|
| Controller | controller_credential_servicenow_openflake | [OpenFlake](config/common/credentials.yml#L174-L181) |

## 2026-07-16 — Add Vault OIDC demo CaC to hashi

Zero Trust demo that authenticates against HashiCorp Vault via OIDC and issues an allow or deny credential token to AAP based on the org identity, using credential input sources to feed the looked-up client ID into the target credential.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Credential | Vault OIDC Allow | Generic token credential that receives the Vault OIDC allow-path client ID | hashi | [🕵️](config/hashi/credentials.yml#L119-L121) |
| | Vault OIDC Deny | Generic token credential that receives the Vault OIDC deny-path client ID | hashi | [🕵️](config/hashi/credentials.yml#L122-L124) |
| | Vault OIDC Lookup | Vault lookup for OIDC integration | hashi | [🕵️](config/hashi/credentials.yml#L110-L118) |
| Credential input source | Vault OIDC Lookup → Vault OIDC Allow | Feeds the Autodotes org client ID from Vault OIDC Lookup into Vault OIDC Allow | hashi | [🕵️](config/hashi/credential_input_sources.yml#L4-L10) |
| | Vault OIDC Lookup → Vault OIDC Deny | Feeds the Default org client ID from Vault OIDC Lookup into Vault OIDC Deny | hashi | [🕵️](config/hashi/credential_input_sources.yml#L11-L17) |
| Job template | Vault // OIDC // Demo | Demonstrate the Vault integration with AAP as an OIDC provider. Choose a credential based on expect… | hashi | [🕵️](config/hashi/job_templates.yml#L307-L318) |

### Changed
- Documented `credential_input_sources` in AGENTS.md resource-tag examples and the hashi README file table
- Added canonical key order and cac-parser resource map entries for credential input sources

### Fixed
- Restored corrupted machine credential name on `Terraform // HCP // AWS Web Demo Configure`

## 2026-07-16 — Document local venv and AAP env vars in README

Documents how to stand up a local development environment: creating a `.venv`, installing `ansible-core` and `collections/requirements.yml`, and setting the `AAP_*` API auth variables (plus optional `ANSIBLE_VAULT_PASSWORD_FILE`) needed to run playbooks against a live controller.

### Changed
- Apply examples assume vault is configured via env/`ansible.cfg`; document `--ask-vault-pass` / `--vault-password-file` as fallbacks

### Removed
- Controller export pointer from the README (still covered in `README_EXPORT.md`)

## 2026-07-16 — Refine docs breadcrumbs and var page presentation

Adds path-based navbar breadcrumbs (`ansible-cac / …`) that link to directory index pages, and Autodotes red (`#b31b1b`) accordion styling for the "Full definition" section on generated config var pages.

### Changed
- Default palette to dark mode; glass header only in slate, solid primary in light
- Compact heading spacing; brighter dark-mode section and side-nav headers
- Removed Home and the site title from the primary side nav (logo still links home)
- Full definition opens by default, has a TOC heading, and keeps YAML syntax highlighting
- Breadcrumb links match navbar text until hover (soft gold accent)
- Tightened Pygments highlight settings (`pygments_lang_class`, `inlinehilite`)
- Dropped obsolete export playbooks from the README tree diagram

## 2026-07-16 — Polish docs site chrome and side nav

Cleans up the docs site chrome: transparent sidebars with content-edge shadows, a frosted glass header effect, and a small script (`docs/mkdocs/assets/extra.js`) so side-nav scrollbars only appear while actively scrolling.

### Changed
- Replaced tinted/bordered sidebars with transparent chrome and left/right content shadows
- Applied a frosted glass effect to the Material header
- Dropped `navigation.expand` so nested side nav starts collapsed and only the active section opens

## 2026-07-16 — Auto-generate docs pages for domain config vars

Generates a docs page per `config/<domain>/*.yml` at build time (`docs/mkdocs/gen_var_pages.py` via `mkdocs-gen-files`) with the apply one-liner, variable name, resource summary table, and collapsible full YAML, discovering domains straight from `config/` (`docs/mkdocs/domains.py` / `hooks.py`) so nav and README links stay in sync with the repo layout.

### Changed
- Moved MkDocs hooks/assets under `docs/mkdocs/`
- Widened the content grid to 70rem and tinted/ bordered sidebars so nav and TOC read apart from main content
- Docs workflow installs `mkdocs-gen-files` and `pyyaml`, and rebuilds when `config/**` changes

## 2026-07-16 — Align docs site styling with Autodotes brand

Restyles the generated docs site to match autodotes.com: Dosis/Roboto Mono fonts and an Autodotes navy (`#001157` / `#002d62`), gold accent (`#e2c044`), soft background (`#faf9fe`) palette in `docs/mkdocs/assets/extra.css`.

## 2026-07-16 — Publish repo docs to GitHub Pages with MkDocs

Publishes this repo's READMEs and `docs/` as a GitHub Pages site: a `mkdocs.yml` Material theme config with Red Hat fonts/colors and the Autodotes logo, brand styling assets (`docs/mkdocs/assets/extra.css`, `logo.png`), and a `.github/workflows/docs.yml` workflow that builds and deploys on pushes to `main` (or manual dispatch).

## 2026-07-16 — Add ansible-lint pre-commit hook with production profile

Adds an `ansible-lint` pre-commit hook (v26.6.0, `ansible-core>=2.16`) running the `production` profile, with `yaml_extra_tags: ["!unsafe"]` support for credential type injectors, and fixes the lint violations the stricter profile surfaced across existing config files.

### Changed
- Bumped `.ansible-lint` profile from `shared` to `production`

### Fixed
- `yaml[line-length]` violations in `config/aap/job_templates.yml`, `config/networking/inventory_groups.yml`, `config/networking/workflow_job_templates.yml`, and `config/windows/credential_types.yml` using `>-` folded scalars
- `yaml[colons]` extra-space violation in `config/aiops/credentials.yml`
- Comment indentation in `config/linux/job_templates.yml`

## 2026-07-16 — Add cac-parser skill for API-to-CaC conversion

Adds a `.cursor/skills/cac-parser` agent skill that maps AAP API export payloads into the correct domain vars file, normalizes references, omits role/module defaults (`infra.aap_configuration` and `ansible.*`, tracked instead in a new `collections/requirements.yml`), and applies canonical key ordering.

### Removed
- `filter_plugins/core.py` export/normalize filters (no longer part of the apply path)

## 2026-07-16 — Standardize config YAML key ordering

Defines a canonical key order (identity fields first, then classification, behavior, and complex nested structures last) for every config variable type, backed by a `docs/key_ordering.md` reference and a one-time `scripts/reorder_keys.py` helper, then reorders existing `config/` entries to match.

### Changed
- Reordered keys on list entries in domain config YAML so ordering is consistent within and across domains (properties unchanged; order only)

## 2026-07-16 — Reorganize CaC into domain folders with wildcard vars

Restructures Configuration as Code from flat `controller/`, `eda/`, `hub/`, and `platform/` trees into logical `config/<domain>/` folders merged via `dispatch_include_wildcard_vars`, applied through a single tag-driven `pb_aap_config.yml` (common always-on, domains opt-in via `never`) instead of per-component playbooks, with `AGENTS.md` and per-domain/`config/` READMEs documenting the new placement rules, wildcard naming, and apply conventions (including var-file one-liner comments for resource-scoped applies).

### Domains

- [common](config/common/README.md) — Platform fundamentals and multi-domain shared resources.
- [cloud](config/cloud/README.md) — AWS, Azure, GCP, VMware.
- [networking](config/networking/README.md) — Cisco, Palo Alto, Summit Connect.
- [linux](config/linux/README.md) — Linux/RHEL management and patching.
- [windows](config/windows/README.md) — Windows, AD, Proxmox.
- [hashi](config/hashi/README.md) — HashiCorp Terraform/HCP and Vault.
- [aiops](config/aiops/README.md) — AIOps + Event-Driven Ansible.
- [servicenow](config/servicenow/README.md) — ServiceNow ITSM and Selenium demos.
- [apps](config/apps/README.md) — SSL/ACME, Kasa, CyberArk, policy demos.
- [aap](config/aap/README.md) — AAP self-management and EE builds.
- [hub](config/hub/README.md) — Private Automation Hub.

### Changed
- Merged HashiCorp Terraform/HCP and Vault resources into the `hashi` domain
- Updated root README, export docs, and ansible-lint to target `config/`

### Removed
- `pb_controller_cac.yml`, `pb_eda_cac.yml`, and `pb_platform_cac.yml`
