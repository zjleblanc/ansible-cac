# Export Controller Assets

Use this flow when a **source** Automation Controller (or compatible API) already holds the configuration you want, and you need **configuration as code** under `controller/` to apply to a **destination** with `pb_controller_cac.yml`.

Export-related paths and playbooks (not shown in [Repository structure](#repository-structure) above):

```text
.
├── filter_plugins/
├── staging/                    (created by pb_controller_export.yml)
├── configs/                    (optional; used by pb_process_assets.yml)
├── pb_controller_export.yml
└── pb_process_assets.yml
```

- **`filter_plugins/`** — Custom Jinja filters (`core.py`); Ansible loads them when you run the export or process playbooks from the repository root.
- **`staging/`** — Populated by `pb_controller_export.yml` with `controller_assets.staging.yml` and parsed per-resource `*.staging.yml` files.
- **`configs/`** — Optional location for `old_controller_assets_raw.yml` input and `old_controller_assets.yml` output when using `pb_process_assets.yml`.
- **`pb_controller_export.yml`** — Calls the source controller API and writes staging YAML (details below).
- **`pb_process_assets.yml`** — Normalizes a single-file raw export via the `process_assets` filter (details in step 3).

## Export from the source (`pb_controller_export.yml`)

From the repository root, set API connectivity to the source instance:

- `OLD_CONTROLLER_HOST` — hostname of the controller you are exporting from
- `OLD_CONTROLLER_OAUTH_TOKEN` — OAuth token for that instance

```bash
export OLD_CONTROLLER_HOST=controller.example.com
export OLD_CONTROLLER_OAUTH_TOKEN='<your oauth token>'
ansible-playbook pb_controller_export.yml
```

The playbook uses `ansible.controller.export` with `all: true`, then writes the full API payload to `staging/controller_assets.staging.yml`. Subsequent tasks read that structure and emit **per-resource** staging files under `staging/` (for example `controller_credentials.staging.yml`, `controller_inventories.staging.yml`, `controller_projects.staging.yml`, `controller_job_templates.staging.yml`, `controller_workflow_job_templates.staging.yml`, plus credential types and inventory sources).

**Re-run parsing only** — If `staging/controller_assets.staging.yml` already exists and you want to regenerate the parsed files without calling the API again, run with `-e export=false`.

**Partial runs** — Tasks are tagged (for example `credentials`, `credential_types`, `inventories`, `inventory_sources`, `projects`, `job_templates`, `workflow_job_templates`). Use `--tags` / `--skip-tags` to limit what is rewritten.

## Custom filters (`filter_plugins/core.py`)

The export playbook applies **parse** filters so exported objects match the shape expected for CaC / dispatch-style variables: resolve nested objects to names where appropriate, drop `natural_key` and other API-only fields, expand credential inputs (replacing `$encrypted$` with placeholders), flatten job template and workflow `related` data into fields such as `credentials` and `survey_spec`, and similar cleanup for inventories, inventory sources, and projects.

`process_assets` is a lighter **bulk** normalizer: it removes top-level `schedules` and strips `related.schedules` from inventory sources, job templates, and workflow job templates so the document is easier to treat as static config.

## Optional raw pipeline (`pb_process_assets.yml`)

If you already have a single-file raw export at `configs/old_controller_assets_raw.yml` (same overall shape as an `ansible.controller.export` assets map), run `pb_process_assets.yml`. It loads that file, pipes it through `process_assets`, and writes `configs/old_controller_assets.yml` for hand-editing or downstream use. This path does not replace the per-file staging output from `pb_controller_export.yml`; it is an alternative when your starting artifact is one raw YAML file.

## Promote to CaC and apply on the destination

Copy or merge the staged (or processed) YAML into the canonical files under `controller/` (and adjust names, organizations, or secrets to match the destination). Populate `vars/controller_secrets.yml` for any credential inputs and other vaulted values. Then apply to the **destination** controller:

```bash
ansible-playbook pb_controller_cac.yml --ask-vault-pass
```

The destination is whatever host and credentials your `pb_controller_cac.yml` / collection configuration targets; it does not use `OLD_CONTROLLER_*`.
