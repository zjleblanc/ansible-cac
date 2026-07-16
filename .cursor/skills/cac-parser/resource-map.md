# Resource map: API → config file / variable / omit defaults

Paths are under `config/<domain>/`. Variable suffix is always `_<domain>` (`_common`, `_cloud`, …).

## Type → file → variable prefix

| API / export type (hints) | File | Variable prefix | Key-order section in docs/key_ordering.md |
|---------------------------|------|-----------------|-------------------------------------------|
| `job_template` | `job_templates.yml` | `controller_templates` | Job Templates |
| `workflow_job_template` | `workflow_job_templates.yml` | `controller_workflows` | Workflow Job Templates |
| `project` (Controller) | `projects.yml` | `controller_projects` | Projects |
| `credential` (Controller) | `credentials.yml` | `controller_credentials` | Credentials |
| `credential_type` (Controller) | `credential_types.yml` | `controller_credential_types` | Credential Types |
| `inventory` | `inventories.yml` | `controller_inventories` | Inventories |
| `inventory_source` | `inventory_sources.yml` | `controller_inventory_sources` | Inventory Sources |
| `group` | `inventory_groups.yml` | `controller_groups` | Groups |
| `schedule` | `schedules.yml` | `controller_schedules` | Schedules |
| `execution_environment` | `execution_environments.yml` | `controller_execution_environments` | Execution Environments |
| `label` | `labels.yml` | `controller_labels` | Labels |
| `notification_template` | `notifications.yml` | `controller_notifications` | Notification Templates |
| `organization` | `organizations.yml` | `aap_organizations` | Organizations |
| `user` (platform/gateway) | `users.yml` | `aap_user_accounts` | Users |
| `team` | `teams.yml` | `aap_teams` | Teams |
| authenticator (`gateway`) | `authenticators.yml` | `gateway_authenticators` | Authenticators |
| authenticator map | `authenticator_maps.yml` | `gateway_authenticator_maps` | Authenticator Maps |
| EDA `project` | `eda_projects.yml` | `eda_projects` | EDA Projects |
| EDA `credential` | `eda_credentials.yml` | `eda_credentials` | EDA Credentials |
| EDA `event_stream` | `eda_event_streams.yml` | `eda_event_streams` | EDA Event Streams |
| EDA `rulebook_activation` | `eda_rulebook_activations.yml` | `eda_rulebook_activations` | EDA Rulebook Activations |
| Hub EE registry | `ee_registries.yml` | `hub_ee_registries` | Hub EE Registries |
| Hub EE repository | `ee_repositories.yml` | `hub_ee_repositories` | Hub EE Repositories |
| Hub collection remote | `collection_remotes.yml` | `hub_collection_remotes` | Hub Collection Remotes |
| Hub / AH group | `groups.yml` | `ah_groups` | Hub Groups |
| Hub / AH role | `roles.yml` | `ah_roles` | Hub Roles |
| Hub / AH user | `users.yml` | `ah_users` | Hub Users |

Most platform/gateway fundamentals live only under `common` today. Hub resources live under `hub`. EDA resources live under `aiops` in this repo.

If the target file does not exist in that domain yet: create it with the correct one-liner comment (see AGENTS.md), add the suffixed list variable, and update that domain’s README file table.

## Nested API unwrap cheat sheet

| API shape | CaC field |
|-----------|-----------|
| `organization: {name: Autodotes}` or `summary_fields.organization.name` | `organization: Autodotes` |
| `project: {name: Cloud Mgmt}` | `project: Cloud Mgmt` |
| `inventory: {name: Cloud Inventory}` | `inventory: Cloud Inventory` |
| `execution_environment: {name: ee-default}` | `execution_environment: ee-default` |
| `credential_type: {name: Machine}` | `credential_type: Machine` |
| `credentials: [{name: A}, …]` / related credentials | `credentials: [A, …]` |
| `labels: [{name: Cloud}, …]` | `labels: [Cloud, …]` |
| `unified_job_template: {name: X}` (schedule) | `unified_job_template: X` |
| `source_project: {name: Autodotes}` | `source_project: Autodotes` |
| survey in `related.survey_spec` | `survey_spec: …` |

## Defaults to omit

Drop the key when the payload value equals a documented default (or a falsey empty that restates “unset”). Keep the key when the value differs.

**Sources of truth** (installed under `~/.ansible/collections/ansible_collections/` unless vendored elsewhere):

| Layer | Where to look | Collections |
|-------|---------------|-------------|
| CaC dispatch roles | `infra/aap_configuration/roles/<role>/tasks/main.yml` | `infra.aap_configuration` |
| Module defaults | `ansible/<name>/plugins/modules/<module>.py` (`DOCUMENTATION` / argument spec) | Every **`ansible.*`** entry in [collections/requirements.yml](../../../collections/requirements.yml): `ansible.controller`, `ansible.platform`, `ansible.hub`, `ansible.eda` |

Map resource → module roughly as: Controller JT → `ansible.controller.job_template`; workflow → `workflow_job_template`; project/credential/inventory/… → matching `ansible.controller.*`; orgs/users/teams/authenticators → `ansible.platform.*`; Hub → `ansible.hub.*`; EDA → `ansible.eda.*`. Prefer the module the `infra.aap_configuration` role actually invokes when both define a default.

### `controller_job_templates` → `controller_templates_*` (`ansible.controller.job_template`)

| Key | Omit when |
|-----|-----------|
| `job_type` | `run` |
| `job_slice_count` | `1` |
| `verbosity` | `0` |
| `forks` | `0` |
| `timeout` | `0` |
| `ask_*_on_launch` (all) | `false` |
| `allow_simultaneous` | `false` |
| `use_fact_cache` | `false` |
| `survey_enabled` | `false` |
| `diff_mode`, `force_handlers`, `become_enabled` | `false` |
| `limit`, `job_tags`, `skip_tags`, `start_at_task`, `host_config_key`, `scm_branch`, `webhook_service`, `description` | `""` (empty) |
| `extra_vars` | `{}` |
| `labels`, `credentials`, `instance_groups`, notification lists | `[]` |
| `survey_spec` | `{}` or empty when `survey_enabled` is false/absent |

Always keep meaningful identity/refs: `name`, `project`, `playbook`, `inventory`, non-empty `credentials` / `labels`, non-default ask flags, real surveys.

### `controller_projects` → `controller_projects_*` (`ansible.controller.project`)

| Key | Omit when |
|-----|-----------|
| `scm_type` | only if you intentionally rely on role default `manual` — prefer keeping real scm type (`git`, …) |
| `scm_clean`, `scm_delete_on_update`, `scm_track_submodules`, `scm_update_on_launch`, `allow_override`, `update_project` | `false` |
| `scm_update_cache_timeout`, `timeout` | `0` |
| `scm_url`, `scm_branch`, `scm_refspec`, `local_path`, `description` | `""` |
| notification lists | `[]` |

Keep `scm_type`, `scm_url`, and any non-default branch/update/credential/EE fields used by peers in the target file.

### `controller_credentials` → `controller_credentials_*` (`ansible.controller.credential`)

| Key | Omit when |
|-----|-----------|
| `description` | `""` |
| `inputs` | `{}` |
| `update_secrets` | `true` (role default when enforce-defaults) — omit unless explicitly needed |

Never commit real secrets from API `inputs` (`$encrypted$` or plaintext).

### `controller_inventory_sources` → `controller_inventory_sources_*` (`ansible.controller.inventory_source`)

| Key | Omit when |
|-----|-----------|
| `overwrite`, `overwrite_vars`, `update_on_launch` | `false` |
| `timeout`, `update_cache_timeout` | `0` |
| `verbosity` | `1` (role enforce default) — omit if matching peers that omit it, or if value is the platform default you do not care about |
| `enabled_var`, `enabled_value`, `host_filter`, `limit`, `scm_branch`, `source_path`, `description` | `""` |
| `source_vars` | `{}` / null / empty |

Prefer matching the **lean** style of nearby domain entries (hashi sources are name-first and shorter; common sources historically included more empty fields — still prefer omitting empties for new entries).

### `controller_workflows` → `controller_workflows_*` (`ansible.controller.workflow_job_template`)

| Key | Omit when |
|-----|-----------|
| `ask_*_on_launch` | `false` |
| `allow_simultaneous` | `false` |
| `survey_enabled` | `false` |
| `extra_vars` | `{}` |
| `labels` | `[]` |
| `survey_spec` | empty / unused |

Keep `workflow_nodes` (required for a useful workflow entry).

### `controller_schedules` → `controller_schedules_*` (`ansible.controller.schedule`)

| Key | Omit when |
|-----|-----------|
| `disabled` | `false` |
| `extra_data` | `{}` / absent |
| `description` | `""` |

### `controller_inventories` / groups / labels / EEs

Omit empty `description`, empty `variables: {}`, and other no-op empties. Keep `labels` on inventories only when non-empty.

### EDA / Hub / Gateway

Use `ansible.eda.*`, `ansible.hub.*`, and `ansible.platform.*` module docs (plus the matching `infra.aap_configuration` role) for omit decisions. Omit falsey enable flags and empty optional blocks when peers omit them (`enabled: false` may still be intentional for rulebook activations in this repo — **keep** `enabled: false` when present in aiops activations). Prefer matching an existing sibling entry in the same file.

## Domain hint keywords (non-exhaustive)

| Cue in name / labels / project | Likely domain |
|--------------------------------|---------------|
| AWS, Azure, GCP, VMware, Cloud | `cloud` |
| Cisco, Palo Alto, Summit Connect, Network | `networking` |
| Linux, RHEL, Satellite, Lockdown | `linux` |
| Windows, Proxmox, AD, SQL | `windows` |
| Terraform, HCP, Vault, Hashi | `hashi` |
| EDA, AIOps, Dynatrace remediation workflows | `aiops` |
| ServiceNow, Selenium (SNOW demos) | `servicenow` |
| SSL/ACME, Kasa, CyberArk, OPA, Lab DNS | `apps` |
| PAH, EE build, AAP backup, Support Analyzer | `aap` |
| Hub registries/remotes/AH users | `hub` |
| Shared org/user/team/EE/label/multi-domain project or credential | `common` |
