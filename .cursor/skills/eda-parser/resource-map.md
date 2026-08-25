# Resource map: EDA API → config file / variable / omit defaults

All EDA component resources live under `config/aiops/` in this repo (no `common` EDA precedent yet). Variable suffix is `_aiops`.

## Type → file → variable prefix → dispatch tag

| API resource (path) | `ansible.eda` module | File | Variable prefix | Dispatch tag |
|---|---|---|---|---|
| Project (`/projects/`) | `project` | `eda_projects.yml` | `eda_projects` | `project` |
| Credential (`/eda-credentials/`) | `credential` | `eda_credentials.yml` | `eda_credentials` | `credential` |
| Credential Type (`/credential-types/`) | `credential_type` | `eda_credential_types.yml` | `eda_credential_types` | `credential_type` |
| Credential Input Source (`/credential-input-sources/`) | `credential_input_source` | `eda_credential_input_sources.yml` | `eda_credential_input_sources` | `credential_input_sources` |
| Decision Environment (`/decision-environments/`) | `decision_environment` | `eda_decision_environments.yml` | `eda_decision_environments` | `decision_environment` |
| Event Stream (`/event-streams/`) | `event_stream` | `eda_event_streams.yml` | `eda_event_streams` | `event_stream` |
| Rulebook Activation (`/activations/`) | `rulebook_activation` | `eda_rulebook_activations.yml` | `eda_rulebook_activations` | `rulebook_activation` |

Dispatch tags confirmed from `infra.aap_configuration.dispatch`'s `eda_configuration_dispatcher_roles` (`roles/dispatch/defaults/main.yml`). Rulebooks themselves are **not** a standalone CaC resource — they are files inside the referenced project's git repo, referenced by filename only.

If the target file does not exist yet under `config/aiops/`: create it with the correct one-liner comment (see AGENTS.md pattern: `# ansible-playbook pb_aap_config.yml -e "domains=aiops" -e "skip_common=true" --tags <tag>`), add the suffixed list variable, and add a row to [config/aiops/README.md](../../../config/aiops/README.md)'s file table.

## Ref-object / `_id` unwrap cheat sheet

The EDA API has two shapes for the same relationship — create/update payloads use `<field>_id` integers, read/list responses embed a ref object (`{id, name, ...}`). Both resolve to the same CaC field: a bare name string (or list of name strings).

| API shape (either) | CaC field | Notes |
|---|---|---|
| `organization: {name: Autodotes}` / `organization_id: 3` | `organization: Autodotes` | |
| `project: {name: "EDA Demos", ...}` (`ProjectRef`) | `project: EDA Demos` | Activation-only |
| `rulebook: {name: "datadog_event_stream.yml"}` (`RulebookRef`) / `rulebook_id` | `rulebook: datadog_event_stream.yml` | Filename inside the project, not a DB object with its own CaC entry |
| `decision_environment: {name: "Default Decision Environment"}` (`DecisionEnvironmentRef`) / `decision_environment_id` | `decision_environment: Default Decision Environment` | Built-in DE needs no CaC entry; custom DEs do |
| `credential_type: {name: "Token Event Stream"}` (`CredentialTypeRef`) / `credential_type_id` | `credential_type: Token Event Stream` | On EDA credentials |
| `eda_credential: {name: X}` (`EdaCredentialRef`) / `eda_credential_id` | Event stream → `credential_name: X`; DE/Project → `credential: X` | Field name differs by parent module — see module argspecs below |
| `eda_credentials: [{name: A}, {name: B}]` / `eda_credentials: [1, 2]` | `eda_credentials: [A, B]` | Rulebook activation only — flat list of names |
| `event_streams: [EventStreamOut, ...]` + `source_mappings` (JSON string) | `event_streams: [{event_stream: A, source_name: S}, ...]` | Decode `source_mappings`, resolve stream IDs → names; pair with the source name (or `source_index` if the rulebook doesn't name its source) |
| `source_credential: 12` / `target_credential: 34` (ints) | `source_credential: X`, `target_credential: Y` | Credential input source — resolve both to EDA credential names |
| `is_enabled: false` (activation) | `enabled: false` | Field renamed by the module |
| `extra_var: "{...yaml string...}"` (activation, singular) | `extra_vars: {...}` (dict, plural) | Parse the YAML/JSON string into a mapping |
| `image_url` | `image_url` | Decision environment — kept as-is (required) |
| `signature_validation_credential` / `signature_validation_credential_id` | *(no direct CaC field yet — flag as follow-up if present)* | Not exposed by `ansible.eda.project` module as of this writing |

## `ansible.eda` module defaults (omit when payload matches)

Sourced from each module's `DOCUMENTATION` argument spec (`plugins/modules/<module>.py`).

### `eda_projects_*` (`ansible.eda.project`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description`, `scm_branch`, `proxy` | `""` / absent |
| `update_revision_on_launch` | `false` |
| `scm_update_cache_timeout` | `0` |
| `sync` | `false` (and generally omit — this is an imperative trigger, not desired-state) |
| `wait` | `true` (module default) |

Keep `name`, `url`, `organization`, and any non-default `credential` / `scm_branch`.

### `eda_credentials_*` (`ansible.eda.credential`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description` | `""` |

Never commit real secret values in `inputs` — use `{{ eda_credential_* }}` vault vars, matching the existing `eda_credentials_aiops` entries.

### `eda_credential_types_*` (`ansible.eda.credential_type`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description` | `""` |
| `inputs` | `{}` (but typically required — a credential type without inputs is unusual; keep if meaningful) |
| `injectors` | `{}` / absent |

Drop API-only `namespace` and `kind` (managed-type metadata, not creatable via the module) unless the user is defining a genuinely custom kind.

### `eda_credential_input_sources_*` (`ansible.eda.credential_input_source`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description` | `""` |
| `metadata` | `{}` only if the target credential type truly needs no lookup metadata (rare — usually required for HashiCorp Vault-style lookups) |

`target_credential`, `input_field_name`, `source_credential`, `organization` are effectively required — always keep.

### `eda_decision_environments_*` (`ansible.eda.decision_environment`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `description` | `""` |
| `pull_policy` | `always` (module default) |
| `credential` | absent (only set when the image needs registry auth) |

Keep `name`, `image_url`, `organization`.

### `eda_event_streams_*` (`ansible.eda.event_stream`)

| Key | Omit when |
|---|---|
| `state` | `present` |
| `forward_events` | `false` |
| `headers` | `""` (empty = include all headers) |
| `event_stream_type` | absent (deprecated field, ignored by the API; never emit) |
| `uuid` | absent (auto-generated unless the user needs a stable custom URL) |

Keep `name`, `organization`, `credential_name` (this repo's convention — matches existing `eda_event_streams_aiops` entries which use `credential_name`, the module's alias for `credential`).

### `eda_rulebook_activations_*` (`ansible.eda.rulebook_activation`)

| Key | Omit when |
|---|---|
| `state` | `present` (this repo uses `enabled`/`disabled` via the `enabled` key instead — see note below) |
| `restart_policy` | `on-failure` |
| `log_level` | `error` |
| `restart_on_project_update` | `false` |
| `enable_persistence` | `false` |
| `skip_audit_events` | `false` |
| `k8s_service_name` | absent |
| `description`, `extra_vars` | `""` / `{}` / absent |
| `rule_engine_credential_id` | absent (optional — only set when a non-default rule engine credential is required) |

**Do not omit `enabled` reflexively.** Every existing `eda_rulebook_activations_aiops` entry sets `enabled: false` explicitly (demo activations ship disabled) — match that convention for new entries in the same file rather than dropping it because `true` is the module default. Only omit `enabled` when the payload's value truly is the intended default AND no sibling entries in the target file set it explicitly.

Keep `name`, `organization`, `project`, `rulebook`, `decision_environment`, `event_streams`, `eda_credentials` — these are the identity/relationship fields.

## Enums reference

| Enum | Values | Default |
|---|---|---|
| `RestartPolicyEnum` | `always`, `on-failure`, `never` | `on-failure` (module) |
| `LogLevelEnum` | `debug`, `info`, `error` | `error` (module) |
| `PullPolicyEnum` | `always`, `missing`, `never` | `always` (module) |
| `ScmTypeEnum` | `git` | n/a (read-only, EDA projects are always git) |

## API-only noise (always drop, any EDA resource type)

`id`, `url` (except `project.url`, the required git repo URL), `created_at`, `modified_at`, `created_by`, `modified_by`, `edited_at`, `edited_by`, `managed`, `git_hash`, `import_state`, `import_error`, `status`, `status_message`, `restart_count`, `current_job_id`, `rules_count`, `rules_fired_count`, `ruleset_stats`, `restarted_at`, `owner`, `test_content`, `test_content_type`, `test_error_message`, `test_headers`, `events_received`, `last_event_received_at`, `log_tracking_id`, `awx_token_id`, `scm_type`, `references`, `namespace`, `kind` (credential type managed metadata), `proxy` (unless explicitly configured), `verify_ssl` (project/DE — keep only if the user explicitly disabled cert verification; default is `true`).

## Relationship graph

```text
Rulebook Activation
  → Project              (eda_projects_aiops)
  → Rulebook              (filename inside the Project's repo — no separate CaC object)
  → Decision Environment  (eda_decision_environments_aiops, or built-in "Default Decision Environment")
  → EDA Credentials       (eda_credentials_aiops, list of names)
  → Event Streams          (eda_event_streams_aiops, list of {event_stream, source_name})

Event Stream       → EDA Credential (credential_name)
Decision Environment → EDA Credential (optional; registry auth for image_url)
Project             → EDA Credential (optional; SCM auth for private repos)
EDA Credential      → Credential Type (credential_type name)
Credential Input Source → source_credential + target_credential (both EDA credential names)
```

Before finalizing a conversion, confirm every referenced name exists (or will be added) in `config/aiops/`. Flag missing dependencies as follow-ups rather than inventing them.
