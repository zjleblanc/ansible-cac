# Changelog

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
