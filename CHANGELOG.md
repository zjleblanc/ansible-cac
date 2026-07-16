# Changelog

## 2026-07-16 — Add Vault OIDC demo CaC to hashi

### Added
- Hashi credentials `Vault OIDC Lookup`, `Vault OIDC Allow`, and `Vault OIDC Deny`
- `config/hashi/credential_input_sources.yml` wiring Allow/Deny tokens from the OIDC Vault lookup
- Job template `Vault // OIDC // Demo` (Zero Trust project) with credential prompt on launch
- Canonical key order and cac-parser resource map for credential input sources

### Changed
- Documented `credential_input_sources` in AGENTS.md resource-tag examples and the hashi README file table

### Fixed
- Restored corrupted machine credential name on `Terraform // HCP // AWS Web Demo Configure`

## 2026-07-16 — Document local venv and AAP env vars in README

### Added
- README "Local environment" section for creating a `.venv`, installing `ansible-core` and `collections/requirements.yml`, and setting `AAP_*` API auth variables plus optional `ANSIBLE_VAULT_PASSWORD_FILE`

### Changed
- Apply examples assume vault is configured via env/`ansible.cfg`; document `--ask-vault-pass` / `--vault-password-file` as fallbacks

### Removed
- Controller export pointer from the README (still covered in `README_EXPORT.md`)

## 2026-07-16 — Refine docs breadcrumbs and var page presentation

### Added
- Path-based navbar breadcrumbs (`ansible-cac / …`) via header overrides, with links only for directories that have an index page
- Autodotes red (`#b31b1b`) accordion styling for Full definition on generated config var pages

### Changed
- Default palette to dark mode; glass header only in slate, solid primary in light
- Compact heading spacing; brighter dark-mode section and side-nav headers
- Removed Home and the site title from the primary side nav (logo still links home)
- Full definition opens by default, has a TOC heading, and keeps YAML syntax highlighting
- Breadcrumb links match navbar text until hover (soft gold accent)
- Tightened Pygments highlight settings (`pygments_lang_class`, `inlinehilite`)
- Dropped obsolete export playbooks from the README tree diagram

## 2026-07-16 — Polish docs site chrome and side nav

### Added
- `docs/mkdocs/assets/extra.js` to show sidebar scrollbars only while scrolling

### Changed
- Replaced tinted/bordered sidebars with transparent chrome and left/right content shadows
- Applied a frosted glass effect to the Material header
- Dropped `navigation.expand` so nested side nav starts collapsed and only the active section opens

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
