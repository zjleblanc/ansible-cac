# EDA API reference — export endpoints

Derived from the Event-Driven Ansible API OpenAPI spec (v1.3.5), base path `/api/eda/v1`. This is
read-only reference material for **exporting** objects before conversion — see [SKILL.md](SKILL.md)
for the conversion workflow.

## Base URL and authentication

The EDA API sits behind the AAP Gateway. Assume these environment variables are already set in the
shell:

| Var | Meaning |
|---|---|
| `AAP_HOSTNAME` | Gateway hostname (no scheme), e.g. `aap.example.com` |
| `AAP_USERNAME` | Platform username (reference only — not needed once `AAP_TOKEN` is set) |
| `AAP_TOKEN` | Bearer token for the Gateway/EDA API |

Every request:

```bash
curl -sk "https://${AAP_HOSTNAME}/api/eda/v1/<path>/" \
  -H "Authorization: Bearer ${AAP_TOKEN}"
```

Never echo `AAP_TOKEN` into output, commit it, or write it into `config/`. It's a live credential for
whatever platform the user is exporting from — treat it the same as any other secret.

## Pagination

All list endpoints return the same envelope:

```json
{"count": 123, "next": "...", "previous": null, "page_size": 50, "page": 1, "results": [...]}
```

Pass `?page_size=100` (or higher) to reduce round-trips, and follow `next` until it is `null`. For a
single known object prefer **retrieve by ID** over paging through list results.

## List vs retrieve — which to use

List and retrieve responses diverge for **projects**, **decision environments**, and **rulebook
activations**: list items carry `_id` integers (`organization_id`, `decision_environment_id`,
`project_id`, `rulebook_id`, `awx_token_id`, `rule_engine_credential_id`), while retrieve-by-ID
responses embed full ref objects (`organization: {id, name}`, `project: {id, name, url, ...}`,
`decision_environment: {id, name, image_url, ...}`).

**Always prefer retrieve-by-ID when exporting for CaC conversion** — it gives you name strings
directly instead of requiring a second lookup to resolve an ID to a name. Use list endpoints only to
discover which IDs exist (e.g. `?name=` filter to find an ID, or bulk reconciliation across every
object of a type).

EDA credentials and credential types have **no separate list/retrieve schema** — both return the same
shape either way (`EdaCredential`, `CredentialType`).

## Recommended export order

Export in dependency order so every ref name is already known by the time you need it:

1. **Credential types** (`/credential-types/`) — usually managed/built-in, rarely need export
2. **EDA credentials** (`/eda-credentials/`) + **credential input sources** (`/credential-input-sources/`)
3. **Projects** (`/projects/`)
4. **Decision environments** (`/decision-environments/`)
5. **Event streams** (`/event-streams/`)
6. **Rulebooks** (`/rulebooks/`, `/rulebooks/{id}/sources/`) — for source names referenced by activations
7. **Rulebook activations** (`/activations/`) — depends on all of the above

## Endpoint catalog

### Projects

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /projects/` | `projects_list` | `PaginatedProjectList` → `Project` (IDs) | `name`, `url`, `page`, `page_size` |
| `GET /projects/{id}/` | `projects_retrieve` | `ProjectRead` (embedded refs) | — |

### EDA Credentials

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /eda-credentials/` | `eda_credentials_list` | `PaginatedEdaCredentialList` → `EdaCredential` | `name`, `credential_type_id`, `credential_type__kind`, `credential_type__kind__in`, `credential_type__namespace__in`, `credential_type__namespace__not_in`, `page`, `page_size` |
| `GET /eda-credentials/{id}/` | `eda_credentials_retrieve` | `EdaCredential` | `refs=true` to see what references this credential |
| `GET /eda-credentials/{id}/input_sources/` | `eda_credentials_input_sources_list` | `PaginatedCredentialInputSourceList` | same filters as list + path `id` |

`inputs` on `EdaCredential` is always `readOnly` and secret fields always come back `$encrypted$` —
see [SKILL.md](SKILL.md) "Secrets standards".

### Credential Types

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /credential-types/` | `credential_types_list` | `PaginatedCredentialTypeList` → `CredentialType` | `name`, `namespace`, `page`, `page_size` |
| `GET /credential-types/{id}/` | `credential_types_retrieve` | `CredentialType` | — |

### Credential Input Sources

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /credential-input-sources/` | `credential_input_sources_list` | `PaginatedCredentialInputSourceList` → `CredentialInputSource` | `source_credential`, `target_credential`, `page`, `page_size` |
| `GET /credential-input-sources/{id}/` | `credential_input_sources_retrieve` | `CredentialInputSource` | `refs=true` |

### Decision Environments

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /decision-environments/` | `decision_environments_list` | `PaginatedDecisionEnvironmentList` → `DecisionEnvironment` (IDs) | `name`, `page`, `page_size` |
| `GET /decision-environments/{id}/` | `decision_environments_retrieve` | `DecisionEnvironmentRead` (embedded refs) | — |

### Event Streams

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /event-streams/` | `event_streams_list` | `PaginatedEventStreamOutList` → `EventStreamOut` | `name`, `test_mode`, `page`, `page_size` |
| `GET /event-streams/{id}/` | `event_streams_retrieve` | `EventStreamOut` | — |
| `GET /event-streams/{id}/activations/` | `event_streams_activations_list` | `PaginatedActivationListList` | `decision_environment_id`, `name`, `project_id`, `status`, `page`, `page_size` |

Note: `EventStreamOut.organization` is a **string** (not an `OrganizationRef` object) — unlike every
other resource type.

### Rulebook Activations

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /activations/` | `activations_list` | `PaginatedActivationListList` → `ActivationList` (IDs) | `name`, `status`, `decision_environment_id`, `project_id`, `page`, `page_size` |
| `GET /activations/{id}/` | `activations_retrieve` | `ActivationRead` (embedded refs) | — |
| `GET /activations/{id}/instances/` | `activations_instances_list` | `PaginatedActivationInstanceList` | `name`, `status`, `page`, `page_size` |

`ActivationRead.source_mappings` is a **JSON string**, not a structured object — decode it to resolve
event stream IDs → names when converting `event_streams`. `ActivationRead.eda_credentials` is a list
of full `EdaCredential` objects.

### Rulebooks (not a standalone CaC resource — needed for names/sources only)

| Endpoint | operationId | Response schema | Useful filters |
|---|---|---|---|
| `GET /rulebooks/` | `rulebooks_list` | `PaginatedRulebookList` → `Rulebook` | `name`, `project_id`, `page`, `page_size` |
| `GET /rulebooks/{id}/` | `rulebooks_retrieve` | `Rulebook` | — |
| `GET /rulebooks/{id}/sources/` | `rulebooks_sources_list` | `PaginatedSourceList` → `Source` | `name`, `project_id`, `page`, `page_size` |

Use `/rulebooks/{id}/sources/` to get the declared source `name` for an activation's
`event_streams[].source_name` — more reliable than guessing from `source_mappings` alone.

## Response schema quirks worth knowing

- **List vs retrieve schemas are named differently per resource** — there is no consistent `*Out` /
  `*Read` suffix convention. See the table above for the exact schema name per endpoint.
- `EdaCredential` and `CredentialType` have a single shape for both list and retrieve (no separate
  `*Read`/`*Out` variant).
- Shared enums: `StatusEnum`, `RestartPolicyEnum` (`always` / `on-failure` / `never`), `LogLevelEnum`
  (`debug` / `info` / `error`), `ScmTypeEnum` (`git`, read-only), `ImportStateEnum`, `PullPolicyEnum`
  (`always` / `missing` / `never`).
- `created_by` / `modified_by` / `edited_by` are inline `{id, username, first_name, last_name}`
  objects, not named refs — drop them, they're API noise (see SKILL.md step 5).

## Example: exporting a single rulebook activation end to end

```bash
# 1. Find the activation ID by name
curl -sk "https://${AAP_HOSTNAME}/api/eda/v1/activations/?name=DataDog%20Event%20Stream%20Activation" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool

# 2. Retrieve full detail (embedded refs) by ID
curl -sk "https://${AAP_HOSTNAME}/api/eda/v1/activations/42/" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool

# 3. If event_streams source names are unclear, list the rulebook's declared sources
curl -sk "https://${AAP_HOSTNAME}/api/eda/v1/rulebooks/7/sources/" \
  -H "Authorization: Bearer ${AAP_TOKEN}" | python3 -m json.tool
```

Paste the output of step 2 (and step 3 if needed) into the chat to run the conversion workflow in
[SKILL.md](SKILL.md).
