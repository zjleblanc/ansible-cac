# Changelog

## 2026-09-11 — Add GitHub EDA webhook integration for Lightwell Demo

Sets up an Event-Driven Ansible pipeline to receive and route GitHub webhooks for the Lightwell Demo application. This includes a new EDA project for the webhook rulebook, a GitHub HMAC credential for signature verification, an event stream to ingest the webhooks, and a rulebook activation to process them.

### Added
- `vars/eda_secrets.redacted.yml`: added `eda_credential_github_hmac_secret` placeholder.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Credential | GitHub HMAC Credential | HMAC-SHA256 signature verification for GitHub webhooks | aiops | [🕵️](config/aiops/eda_credentials.yml#L71-L81) |
| Event stream | GitHub Event Stream | Ingests GitHub webhooks with header preservation | aiops | [🕵️](config/aiops/eda_event_streams.yml#L16-L19) |
| Project | Lightwell Demo | SCM sync for Lightwell app webhook rulebooks | aiops | [🕵️](config/aiops/eda_projects.yml#L8-L10) |
| Rulebook activation | Lightwell Patch Pipeline Router | Processes GitHub webhooks via the Lightwell webhook rulebook | aiops | [🕵️](config/aiops/eda_rulebook_activations.yml#L54-L68) |

## 2026-09-10 — Add Lightwell Demo project and wire AAP URL to templates

Adds the missing SCM project for the Lightwell demo app and injects the AAP controller URL into the build and deploy job templates so they can report status back to the platform.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Project | Lightwell Demo | SCM sync for the Lightwell demo app playbooks | aiops | [🕵️](config/aiops/projects.yml#L7-L16) |

### Changed
- `config/aiops/job_templates.yml`: added `aap_controller_url` to `Lightwell // Build & Test` and `Lightwell // Deploy Prod` extra_vars.

## 2026-09-09 — Add Lightwell demo app CaC resources and enforce extra_vars dict format

Captures the Lightwell demo app CI/CD job templates and container registry credential in `config/aiops/`, and closes an apply-breaking bug where `extra_vars` was written as a block-scalar string rather than a YAML dict (the `ansible.controller.job_template` module requires a mapping).

### Added
- `config/aiops/credentials.yml`: `Lightwell Demo App Registry` — Container Registry Auth File credential for `quay.io`; injects auth for Lightwell app builds and deploys. New vault var `controller_credential_lightwell_registry_auth` required.
- `config/aiops/job_templates.yml`: `Lightwell // Build & Test` — CI build/test JT against Cloud Inventory using the Lightwell Demo project; attaches registry credential, `GitHub Status Token`, and `Lightwell Network Service Account`.
- `config/aiops/job_templates.yml`: `Lightwell // Deploy Prod` — production deploy JT targeting `env_prod` hosts; attaches registry credential and `GitHub Status Token`.
- `.cursor/rules/extra-vars-dict.mdc`: new rule scoped to `job_templates*.yml` / `workflow_job_templates*.yml` requiring `extra_vars` to always be a YAML mapping, never a string or block scalar.

### Fixed
- `.cursor/skills/cac-parser/resource-map.md`: documented that `extra_vars` must be a YAML dict when converting API payloads; drop `#`-prefixed comment lines that cannot appear as dict keys.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Credential | Lightwell Demo App Registry | Container registry auth for quay.io Lightwell demo app via Container Registry Auth File type | aiops | [🕵️](config/aiops/credentials.yml#L4-L9) |
| Job template | Lightwell // Build & Test | Build and test the Lightwell demo app on Cloud Inventory | aiops | [🕵️](config/aiops/job_templates.yml#L210-L226) |
| Job template | Lightwell // Deploy Prod | Deploy the Lightwell demo app to production (limit: env_prod) | aiops | [🕵️](config/aiops/job_templates.yml#L227-L244) |

## 2026-09-09 — Add container registry auth file credential type for auth.json injection

Adds a generic Container Registry Auth File credential type that materializes a standard `auth.json` (host + base64 `user:pass` auth token) and sets `REGISTRY_AUTH_FILE`, so any job template can authenticate to a container registry via Podman's `auth_file` param or other OCI-compliant tooling (Buildah, Skopeo, Docker) without registry-specific playbook logic. Named distinctly from AAP's built-in "Container Registry" credential type to avoid a naming collision. Takes a pre-encoded base64 auth token (rather than separate username/password) since AAP's credential injector renders templates in a sandboxed Jinja2 environment that has no `b64encode` filter.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Credential type | Container Registry Auth File | Injects auth.json for container registry authentication compatible with Podman, Buildah, Skopeo, and Docker. Sets REGISTRY_AUTH_FILE so tools discover the credentials automatically. | common | [🕵️](config/common/credential_types.yml#L247-L285) |

## 2026-09-09 — Add rhlw group and environment keyed group to AWS EC2 inventory source

Extends the AWS EC2 Instances inventory source with a static `rhlw` group for hosts whose `tags.Name` starts with `rhlw` and a new `env`-prefixed keyed group derived from `tags.environment`, improving host classification in Cloud Inventory.

### Changed
- `config/common/inventory_sources.yml`: added `rhlw` group filter and `tags.environment` keyed group to the AWS EC2 Instances source vars.

## 2026-08-28 — Add EDA rulebook activation refresh utility

Adds a standalone script to fully refresh an EDA rulebook activation after its project is updated — syncing the project, disabling the activation, detaching and rebuilding event stream mappings against the freshly synced rulebook, re-enabling, and validating startup — since `restart_on_project_update` alone only reloads rulebook logic and does not rebind event streams.

### Added
- `utils/refresh_eda_activation.py`: Python (stdlib-only) CLI that resolves a rulebook activation by name and runs the full 10-step refresh flow, handling the EDA API's dedicated enable/disable action endpoints and recomputing `source_mappings` (including `rulebook_hash`) against the synced rulebook.

### Changed
- `config/aiops/eda_rulebook_activations.yml`: set `restart_on_project_update: true` on all three existing activations so they auto-restart with fresh rulebook logic after a project sync.
- `.cursor/skills/eda-parser/SKILL.md`, `resource-map.md`, `key_ordering.md`: documented that `enabled` and `restart_on_project_update` are always explicit but track the live platform value when reconciling an existing activation (defaulting to `true` only for brand-new entries with no live reference); added `restart_on_project_update` to the canonical key order and cross-referenced `utils/refresh_eda_activation.py` for event stream rebinding.

## 2026-08-26 — Expand and refactor eda-parser skill

Adds a dedicated `key_ordering.md` and `api-reference.md` to the `eda-parser` skill, moves EDA key ordering out of the shared `cac-parser` doc, and extends `SKILL.md` with direct API export patterns so the agent can pull EDA resources itself rather than waiting for a pasted payload.

### Added
- `.cursor/skills/eda-parser/key_ordering.md`: EDA-only canonical key ordering (all seven resource types), extracted from `cac-parser/key_ordering.md` so the eda-parser skill is self-contained.
- `.cursor/skills/eda-parser/api-reference.md`: EDA API endpoint catalog — export patterns, auth, pagination, list vs retrieve, and dependency-first export order.

### Changed
- `.cursor/skills/eda-parser/SKILL.md`: updated all `key_ordering.md` references to point to the local copy; added "Exporting from the EDA API" section with quick export patterns and env-var prerequisites; added `api-reference.md` as required reading and an additional resource.
- `.cursor/skills/cac-parser/key_ordering.md`: removed EDA section (now lives in `eda-parser/key_ordering.md`).

## 2026-08-26 — Prevent agent write operations against AAP

Adds a project rule that prohibits agents from performing write operations against the Ansible Automation Platform API via raw curl, MCP tools, or playbook execution, ensuring all changes are applied by humans via the configuration-as-code playbook.

### Added
- `.cursor/rules/aap-read-only.mdc`: Global rule enforcing read-only status for agents when interacting with AAP.

## 2026-08-25 — Add EDA parser skill

Adds a `.cursor/skills/eda-parser/` skill that mirrors cac-parser but is scoped to Event-Driven Ansible API resources, since no EDA MCP server is available in this workspace. Heuristics (ref-object/`_id` unwrap rules, `ansible.eda` module defaults, `source_mappings` decoding) were derived from the EDA OpenAPI spec before deleting it.

### Changed
- Added `.cursor/skills/eda-parser/SKILL.md` and `resource-map.md`, covering EDA projects, credentials, credential types, credential input sources, decision environments, event streams, and rulebook activations
- Added `eda_credential_types_*`, `eda_credential_input_sources_*`, and `eda_decision_environments_*` sections to `.cursor/skills/cac-parser/key_ordering.md`
- Added an "EDA Parser" nav entry under AI > Skills in `mkdocs.yml`

### Removed
- Deleted `.cursor/skills/eda-parser/openapi.spec.json` now that its heuristics are captured in the skill files

## 2026-08-25 — Move Support Analyzer to business domain

Moves existing Support Analyzer credential resources from the `aap` domain to `business` and codifies the project, job template, and schedule from the platform.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Credential type | Ansible Support Analyzer | LLM endpoint, Google Sheets, and Red Hat API settings | business | [🕵️](config/business/credential_types.yml#L33-L110) |
| Credential | Support Analyzer (zleblanc) | Staged vault secrets for LLM and Google integration | business | [🕵️](config/business/credentials.yml#L22-L37) |
| Project | Support Analyzer | SCM sync for the support case analyzer playbooks | business | [🕵️](config/business/projects.yml#L9-L14) |
| Job template | BPA // Support Case Analyzer | Automated summarization of open support cases | business | [🕵️](config/business/job_templates.yml#L21-L66) |
| Schedule | BPA // Support Case Analyzer // Weekly | Weekly Friday night run of the analyzer | business | [🕵️](config/business/schedules.yml#L8-L12) |

### Changed
- Updated `config/business/README.md` to include Support Analyzer resources in the domain summary.

### Removed
- `Ansible Support Analyzer` credential type and `Support Analyzer (zleblanc)` credential from the `aap` domain.

## 2026-08-21 — Fix OpenFlake workflow node credential overrides

The OpenFlake disk-space remediation workflow was applying successfully but never attaching the OpenFlake ServiceNow credential to its nodes, because `ansible.controller.workflow_job_template` only honors node-level credential/label/instance-group associations under `related` as `- name: X` dicts.

### Fixed
- Nested OpenFlake credential overrides under each ServiceNow-related node’s `related.credentials` (dict form) on [EDA // Remediation Workflow // Disk Space // OpenFlake](config/aiops/workflow_job_templates.yml#L71-L146)

### Changed
- Documented the workflow-node `related.credentials` / `labels` / `instance_groups` shape (and the silent top-level bare-string no-op) in the cac-parser skill and resource map

## 2026-08-21 — Publish Cursor skills and rules in MkDocs

Moves canonical key ordering into the cac-parser skill and adds an AI section to the docs site so skills and agent rules ship with GitHub Pages instead of living as a standalone `docs/` reference.

### Changed
- Moved `docs/key_ordering.md` into `.cursor/skills/cac-parser/` and updated skill / AGENTS.md references
- Added MkDocs `AI` nav: nested CaC Parser skill pages, plus CaC Schedules and Changelog; Rules auto-discovered from `.cursor/rules/*.mdc`
- Added `docs/mkdocs/gen_agent_pages.py` to render rule pages from `.mdc` frontmatter; hooks populate the Rules nav
- Noted in AGENTS.md that new skills need a manual `mkdocs.yml` nav entry (rules do not)

## 2026-08-20 — Add OpenFlake variant of disk space remediation workflow

Clones the EDA disk-space remediation workflow so its ServiceNow incident and enrichment steps run against the OpenFlake ServiceNow instance instead of West ServiceNow, letting either backend service the same remediation without duplicating the underlying job templates.

### Resources

| Type | Name | Description | Domain | |
|------|------|-------------|--------|------------|
| Workflow job template | EDA // Remediation Workflow // Disk Space // OpenFlake | Disk space remediation workflow using the OpenFlake credential for ServiceNow steps. | aiops | [🕵️](config/aiops/workflow_job_templates.yml#L71-L145) |

### Changed
- Enabled `ask_credential_on_launch` on `Service Now // Create Incident`, `Service Now // Update Incident`, `AIOps // Ticket Enrichment // RHEL`, and `EDA // Resize EBS Volume` so the new workflow's nodes can override their default `West ServiceNow (ven07621)` credential with `OpenFlake`.

## 2026-08-15 — Refactor domain selection to use extra-vars instead of tags

Decouple domain loading from Ansible tags to ensure resource-type tags (like `job_templates` or `credentials`)
compose correctly during dynamic inclusion. Domain inclusion is now controlled by the `domains` list and
`skip_common` boolean, while `--tags` remains reserved for filtering `dispatch` resource types.

### Changed
- `pb_aap_config.yml`: replaced tag-based domain inclusions with `when` conditions gated by the `domains` list and `skip_common` variable.
- Updated 85 files across `config/` folders to reflect the new `ansible-playbook` invocation pattern in READMEs and one-liner file headers.
- Updated `AGENTS.md`, `README.md`, and the `cac-parser` agent skill to reflect domain selection via extra-vars.

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
