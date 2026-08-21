---
name: cac-schedules
description: Retrieve AAP Controller schedules directly via the REST API (the aap-job-mgmt MCP server has no schedules endpoint) and hand them off to cac-parser for conversion into ansible-cac domain YAML. Use when the user asks to list/pull/export schedules from the platform, or asks to add/sync a Controller schedule into config/ and no payload was pasted.
disable-model-invocation: true
---

# cac-schedules — retrieve AAP schedules via API → cac-parser

The `aap-job-mgmt` MCP server (and its siblings) do not expose a schedules tool. This skill retrieves schedule objects directly from the Controller REST API, then normalizes schedule-specific fields before handing off to [cac-parser](../cac-parser/SKILL.md) for the actual CaC conversion (domain placement, key ordering, omit-able defaults).

## Required reading

1. [cac-parser/SKILL.md](../cac-parser/SKILL.md) — conversion workflow this skill feeds into.
2. [cac-parser/resource-map.md](../cac-parser/resource-map.md) — schedule omit-defaults table, nested-unwrap cheat sheet.
3. [cac-parser/key_ordering.md](../cac-parser/key_ordering.md) — Schedules key order: `name`, `description`, `unified_job_template`, `rrule`, `disabled`, `extra_data`.

## Authentication

Reuse the same environment variables the AAP MCP servers use (defined in `mcp.json`):

- `$AAP_HOST` — Controller hostname (no scheme/port).
- `$AAP_TOKEN` — Bearer token used for `Authorization: Bearer $AAP_TOKEN`.

Call the standard Controller HTTPS API port, **not** `$AAP_MCP_PORT` (that port is MCP-only):

```bash
curl -sk -H "Authorization: Bearer ${AAP_TOKEN}" \
  "https://${AAP_HOST}/api/controller/v2/schedules/"
```

If `$AAP_HOST` or `$AAP_TOKEN` is unset or the request returns `401`/`403`, stop and ask the user to export them (or provide a token) rather than guessing credentials or reading vault secrets.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Confirm AAP_HOST / AAP_TOKEN are set
- [ ] 2. List or search schedules
- [ ] 3. Retrieve the target schedule(s) by id
- [ ] 4. Normalize schedule-specific fields
- [ ] 5. Hand off to cac-parser (steps 2-7)
```

### 1. Confirm credentials

```bash
[ -n "$AAP_HOST" ] && [ -n "$AAP_TOKEN" ] && echo ok
```

If missing, ask the user to export them before continuing.

### 2. List or search schedules

```bash
# All schedules
curl -sk -H "Authorization: Bearer ${AAP_TOKEN}" \
  "https://${AAP_HOST}/api/controller/v2/schedules/?page_size=200"

# Search by name
curl -sk -H "Authorization: Bearer ${AAP_TOKEN}" \
  "https://${AAP_HOST}/api/controller/v2/schedules/?name__icontains=Nightly"

# Schedules for a specific job/workflow template (unified_job_template id)
curl -sk -H "Authorization: Bearer ${AAP_TOKEN}" \
  "https://${AAP_HOST}/api/controller/v2/job_templates/230/schedules/"
```

Paginate with `?page=N` if `next` is non-null in the response.

### 3. Retrieve the target schedule

```bash
curl -sk -H "Authorization: Bearer ${AAP_TOKEN}" \
  "https://${AAP_HOST}/api/controller/v2/schedules/59/"
```

If the user asked for "all schedules" or a bulk export, loop step 3 (or use the list payload directly — list results include the same fields as retrieve).

### 4. Normalize schedule-specific fields

Apply these rules before passing the object to cac-parser (cac-parser step 3 covers generic normalization; these are schedule-specific additions):

| API field | CaC handling |
|-----------|--------------|
| `unified_job_template` (numeric id) | Resolve to name via `summary_fields.unified_job_template.name` |
| `enabled: true` | Omit (role default) |
| `enabled: false` | Becomes `disabled: true` |
| `rrule` | Keep verbatim (already iCal format); quote in YAML if it contains `:` at the start of a flow scalar context |
| `extra_data: {}` / `null` | Omit |
| `extra_data: {...}` (non-empty) | Keep as nested dict |
| `description: ""` | Omit |
| `dtstart`, `dtend`, `next_run`, `timezone`, `until` | Drop — derived from `rrule`, not role input fields |
| `id`, `type`, `url`, `related`, `summary_fields`, `created`, `modified` | Drop — API-only |
| `inventory`, `scm_branch`, `job_type`, `job_tags`, `skip_tags`, `limit`, `diff_mode`, `verbosity`, `execution_environment`, `forks`, `job_slice_count`, `timeout`, `credentials` | Launch-time prompt overrides — keep only if non-null/non-empty, and only meaningful if the target template has the matching `ask_*_on_launch` enabled |

### 5. Hand off to cac-parser

Pass the normalized object to the [cac-parser](../cac-parser/SKILL.md) workflow starting at step 2 (step 1 — identify resource type — is already known: `schedule`):

- Domain placement: same domain as the `unified_job_template` it targets (per `AGENTS.md` — schedules are not global). If the template lives in `common`, place the schedule in `common` too.
- File: `config/<domain>/schedules.yml`, variable `controller_schedules_<domain>`.
- Apply canonical key order: `name`, `description`, `unified_job_template`, `rrule`, `disabled`, `extra_data`.

## Example

**Retrieved payload** (`GET /api/controller/v2/schedules/59/`):

```json
{
  "name": "BPA // Account Task Updater // Nightly",
  "description": "This schedule is used to process RHSC report email and update account dashbord.",
  "unified_job_template": 230,
  "rrule": "DTSTART;TZID=America/Chicago:20260813T100000 RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR;BYHOUR=23;BYMINUTE=45",
  "enabled": true,
  "extra_data": {},
  "inventory": null,
  "summary_fields": {
    "unified_job_template": { "id": 230, "name": "BPA // Account Task Updater", "unified_job_type": "job" }
  }
}
```

**After normalization → cac-parser output:**

```yaml
- name: BPA // Account Task Updater // Nightly
  description: This schedule is used to process RHSC report email and update account dashbord.
  unified_job_template: BPA // Account Task Updater
  rrule: "DTSTART;TZID=America/Chicago:20260813T100000 RRULE:FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU,WE,TH,FR;BYHOUR=23;BYMINUTE=45"
```

`enabled: true`, empty `extra_data`, empty `description` (n/a here since it's non-empty), and null `inventory` are all omitted per defaults. Domain is whichever domain owns `BPA // Account Task Updater` (look it up in `config/*/job_templates.yml`); place under `common` if that template lives there.

## Additional resources

- [cac-parser/SKILL.md](../cac-parser/SKILL.md) — full conversion workflow, domain placement rules, output template
- [cac-parser/resource-map.md](../cac-parser/resource-map.md) — schedule omit-defaults table (`controller_schedules` section)
- [cac-parser/key_ordering.md](../cac-parser/key_ordering.md) — Schedules key order
- [AGENTS.md](../../../AGENTS.md) — "Schedules are not global" placement rule
