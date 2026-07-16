# Canonical Key Ordering for Config Variables

Every list entry under a `config/` variable must follow the canonical key order defined below for its resource type.

## Guiding principles

1. **Identity first** — `name` (or `username`), `organization`, `description`.
2. **Classification / type** — `credential_type`, `kind`, `type`, `labels`.
3. **Core references** — `project`, `playbook`, `inventory`, `execution_environment`, `credentials`.
4. **Behavioral config** — booleans, limits, verbosity, launch-prompt flags (`ask_*`).
5. **Complex / nested structures last** — `extra_vars`, `survey_spec`, `workflow_nodes`, `inputs`, `injectors`, `configuration`, `notification_templates_*`.

Keys that are absent from an entry are simply omitted; the remaining keys keep the relative order shown here. Keys not listed in a type's canonical order are placed at the end in their original order (safety net for future additions).

---

## Controller

### Job Templates (`controller_templates_*`)

```yaml
- name:
  organization:
  description:
  labels:
  project:
  playbook:
  inventory:
  execution_environment:
  credentials:
  job_type:
  job_slice_count:
  verbosity:
  forks:
  limit:
  job_tags:
  skip_tags:
  use_fact_cache:
  host_config_key:
  allow_simultaneous:
  ask_variables_on_launch:
  ask_inventory_on_launch:
  ask_limit_on_launch:
  ask_verbosity_on_launch:
  ask_skip_tags_on_launch:
  ask_tags_on_launch:
  ask_labels_on_launch:
  ask_execution_environment_on_launch:
  ask_credential_on_launch:
  extra_vars:
  survey_enabled:
  survey_spec:
  notification_templates_success:
  notification_templates_error:
```

### Workflow Job Templates (`controller_workflows_*`)

```yaml
- name:
  organization:
  description:
  labels:
  inventory:
  allow_simultaneous:
  webhook_service:
  ask_variables_on_launch:
  ask_inventory_on_launch:
  ask_limit_on_launch:
  ask_labels_on_launch:
  limit:
  extra_vars:
  survey_enabled:
  survey_spec:
  workflow_nodes:
```

### Projects (`controller_projects_*`)

```yaml
- name:
  organization:
  description:
  scm_type:
  scm_url:
  scm_branch:
  scm_clean:
  scm_delete_on_update:
  scm_update_on_launch:
  credential:
  default_environment:
```

### Credentials (`controller_credentials_*`)

```yaml
- name:
  organization:
  description:
  credential_type:
  inputs:
```

### Credential Input Sources (`controller_credential_input_sources_*`)

```yaml
- source_credential:
  target_credential:
  input_field_name:
  description:
  metadata:
```

### Credential Types (`controller_credential_types_*`)

```yaml
- name:
  organization:
  description:
  kind:
  inputs:
  injectors:
```

### Inventories (`controller_inventories_*`)

```yaml
- name:
  organization:
  description:
  labels:
  variables:
```

### Inventory Sources (`controller_inventory_sources_*`)

```yaml
- name:
  organization:
  description:
  inventory:
  source:
  source_project:
  source_path:
  source_vars:
  credential:
  execution_environment:
  overwrite:
  overwrite_vars:
  update_on_launch:
  update_cache_timeout:
  enabled_var:
  enabled_value:
  host_filter:
  limit:
  scm_branch:
  timeout:
  verbosity:
```

### Groups (`controller_groups_*`)

```yaml
- name:
  inventory:
  description:
  preserve_existing_hosts:
  preserve_existing_children:
  variables:
  hosts:
```

### Schedules (`controller_schedules_*`)

```yaml
- name:
  description:
  unified_job_template:
  rrule:
  disabled:
  extra_data:
```

### Execution Environments (`controller_execution_environments_*`)

```yaml
- name:
  description:
  image:
```

### Labels (`controller_labels_*`)

```yaml
- name:
  organization:
```

### Notification Templates (`controller_notifications_*`)

```yaml
- name:
  description:
  organization:
  notification_type:
  notification_configuration:
```

---

## Platform / Gateway

### Organizations (`aap_organizations_*`)

```yaml
- name:
  description:
  max_hosts:
  default_environment:
  galaxy_credentials:
```

### Users (`aap_user_accounts_*`)

```yaml
- username:
  password:
  email:
  first_name:
  last_name:
  organizations:
  is_superuser:
  update_secrets:
```

### Teams (`aap_teams_*`)

```yaml
- name:
  description:
  organization:
```

### Authenticators (`gateway_authenticators_*`)

```yaml
- name:
  type:
  slug:
  order:
  enabled:
  create_objects:
  remove_users:
  configuration:
```

### Authenticator Maps (`gateway_authenticator_maps_*`)

```yaml
- name:
  authenticator:
  map_type:
  order:
  organization:
  revoke:
  role:
  team:
  triggers:
```

---

## EDA (Event-Driven Ansible)

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

---

## Private Automation Hub

### EE Registries (`hub_ee_registries_*`)

```yaml
- name:
  url:
  username:
  password:
```

### EE Repositories (`hub_ee_repositories_*`)

```yaml
- name:
  description:
  registry:
  upstream_name:
  readme:
```

### Collection Remotes (`hub_collection_remotes_*`)

```yaml
- name:
  url:
  requirements:
```

### Groups (`ah_groups_*`)

```yaml
- name:
  state:
```

### Roles (`ah_roles_*`)

```yaml
- name:
  description:
  perms:
```

### Users (`ah_users_*`)

```yaml
- username:
  password:
  email:
  first_name:
  last_name:
  groups:
  append:
  is_superuser:
```
