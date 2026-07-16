# Changelog

## 2026-07-16 — Auto-generate docs pages for domain config vars

### Added
- `docs/mkdocs/gen_var_pages.py` (via `mkdocs-gen-files`) to render each `config/<domain>/*.yml` as a docs page with apply one-liner, variable name, resource summary table, and collapsible full YAML
- `docs/mkdocs/domains.py` and `docs/mkdocs/hooks.py` to discover domains from `config/`, expand Configuration nav with generated var pages, and linkify domain README file tables at build time (repo READMEs stay GitHub-safe)

### Changed
- Moved MkDocs hooks/assets under `docs/mkdocs/`
- Widened the content grid to 70rem and tinted/ bordered sidebars so nav and TOC read apart from main content
- Docs workflow installs `mkdocs-gen-files` and `pyyaml`, and rebuilds when `config/**` changes

## 2026-07-16 — Align docs site styling with Autodotes brand

### Changed
- Switched MkDocs fonts to Dosis and Roboto Mono to match autodotes.com
- Updated `docs/mkdocs/assets/extra.css` palette to Autodotes navy (`#001157` / `#002d62`), gold accent (`#e2c044`), and soft background (`#faf9fe`)

## 2026-07-16 — Publish repo docs to GitHub Pages with MkDocs

### Added
- `mkdocs.yml` with Material theme, Red Hat fonts/colors, Autodotes logo, and nav over root/config READMEs plus `docs/`
- `docs/mkdocs/assets/extra.css` and `docs/mkdocs/assets/logo.png` for brand styling
- `.github/workflows/docs.yml` to build and deploy Pages on `main` (and `workflow_dispatch`)

## 2026-07-16 — Add ansible-lint pre-commit hook with production profile

### Added
- `ansible-lint` hook in `.pre-commit-config.yaml` (v26.6.0 with `ansible-core>=2.16`)
- `yaml_extra_tags: ["!unsafe"]` in `.ansible-lint` to support credential type injectors

### Changed
- Bumped `.ansible-lint` profile from `shared` to `production`
- Fixed `yaml[line-length]` violations in `config/aap/job_templates.yml`, `config/networking/inventory_groups.yml`, `config/networking/workflow_job_templates.yml`, and `config/windows/credential_types.yml` using `>-` folded scalars
- Fixed `yaml[colons]` extra-space violation in `config/aiops/credentials.yml`
- Fixed comment indentation in `config/linux/job_templates.yml`

## 2026-07-16 — Add cac-parser skill for API-to-CaC conversion

### Added
- `.cursor/skills/cac-parser` agent skill to map AAP API payloads into the correct domain vars file, normalize refs, omit role/module defaults (`infra.aap_configuration` and `ansible.*` from `collections/requirements.yml`), and apply canonical key ordering
- `collections/requirements.yml` listing Automation Platform collections used by this repo

### Removed
- `filter_plugins/core.py` export/normalize filters (no longer part of the apply path)

## 2026-07-16 — Standardize config YAML key ordering

### Added
- `docs/key_ordering.md` with canonical key order for every config variable type
- Key ordering rule in `AGENTS.md` (identity first: name, organization, description)
- `scripts/reorder_keys.py` to apply the canonical order across `config/` (directory is gitignored; keep or force-add locally as needed)

### Changed
- Reordered keys on list entries in domain config YAML so ordering is consistent within and across domains (properties unchanged; order only)

## 2026-07-16 — Reorganize CaC into domain folders with wildcard vars

### Added
- Domain-based `config/` layout (`common`, `cloud`, `networking`, `linux`, `windows`, `hashi`, `aiops`, `servicenow`, `apps`, `aap`, `hub`) using `dispatch_include_wildcard_vars`
- Component-agnostic `pb_aap_config.yml` with tag-based domain selection (`common` always-on; domains opt-in via `never`)
- Per-domain and `config/` READMEs describing scope and apply commands
- Var-file one-liner comments for resource-scoped applies (`--tags` / `--skip-tags common`)
- `AGENTS.md` documenting placement rules, wildcard naming, and apply conventions

### Changed
- Replaced flat `controller/`, `eda/`, `hub/`, and `platform/` trees and component playbooks with the domain layout above
- Merged HashiCorp Terraform/HCP and Vault resources into the `hashi` domain
- Updated root README, export docs, and ansible-lint to target `config/`

### Removed
- `pb_controller_cac.yml`, `pb_eda_cac.yml`, and `pb_platform_cac.yml`
