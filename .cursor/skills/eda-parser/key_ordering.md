# Canonical Key Ordering — EDA (Event-Driven Ansible)

Every list entry under an `eda_*` config variable must follow the canonical key order defined below for its resource type.

## Guiding principles

1. **Identity first** — `name`, `organization`, `description`.
2. **Classification / type** — `credential_type`.
3. **Core references** — `project`, `rulebook`, `decision_environment`, `credential`.
4. **Behavioral config** — booleans, level flags, `restart_policy`.
5. **Complex / nested structures last** — `inputs`, `injectors`, `event_streams`, `eda_credentials`, `extra_vars`.

Keys that are absent from an entry are simply omitted; the remaining keys keep the relative order shown here.

---

### Projects (`eda_projects_*`)

```yaml
- name:
  description:
  url:
  organization:
```

### Credentials (`eda_credentials_*`)

```yaml
- name:
  organization:
  description:
  credential_type:
  inputs:
```

### Credential Types (`eda_credential_types_*`)

```yaml
- name:
  description:
  inputs:
  injectors:
```

### Credential Input Sources (`eda_credential_input_sources_*`)

```yaml
- target_credential:
  source_credential:
  input_field_name:
  organization:
  description:
  metadata:
```

### Decision Environments (`eda_decision_environments_*`)

```yaml
- name:
  organization:
  description:
  image_url:
  credential:
  pull_policy:
```

### Event Streams (`eda_event_streams_*`)

```yaml
- name:
  organization:
  description:
  credential_name:
  forward_events:
```

### Rulebook Activations (`eda_rulebook_activations_*`)

```yaml
- name:
  description:
  organization:
  project:
  rulebook:
  decision_environment:
  event_streams:
  eda_credentials:
  extra_vars:
  enabled:
  log_level:
  restart_policy:
```
