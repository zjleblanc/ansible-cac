---
name: playbook-to-cac
description: Read Ansible playbook(s) from a remote GitHub or GitLab repository and generate ansible-cac config entries for them — primarily controller job templates, plus project/credential/inventory/EE dependency stubs when they don't already exist in config/. Applies this repo's domain placement, key ordering, and label rules, and scans config/ for name/scm_url collisions with existing resources before writing anything new, asking the user how to resolve any conflict. Use when the user gives a remote repo URL and asks to onboard, template, or generate job templates/CaC config from playbook(s) that live outside this repo.
disable-model-invocation: true
---

# playbook-to-cac — remote playbook(s) → ansible-cac job templates

Turn playbook(s) living in an external GitHub/GitLab repo into `controller_templates_<domain>` entries (and any missing project/credential/inventory/EE stubs) for this repo, following the same conventions as [cac-parser](../cac-parser/SKILL.md) — but starting from playbook source instead of an API payload.

## Required reading

1. [AGENTS.md](../../../AGENTS.md) — domains, wildcard suffixes, placement rules, domain labels.
2. [cac-parser/key_ordering.md](../cac-parser/key_ordering.md) — canonical key order for Job Templates and Projects.
3. [cac-parser/resource-map.md](../cac-parser/resource-map.md) — omit-able defaults for `controller_templates_*` and `controller_projects_*`.

Do not invent secrets. Any credential a playbook needs that doesn't already exist in `config/` becomes a **stub with a vault placeholder**, never a real value.

## Workflow

Copy this checklist and track it:

```
- [ ] 1. Gather inputs (repo, playbook path(s), domain, project name)
- [ ] 2. Fetch remote repo tree + playbook content
- [ ] 3. Analyze each playbook
- [ ] 4. Resolve dependencies (project / credentials / inventory / EE)
- [ ] 5. Scan for collisions with existing resources
- [ ] 6. Generate job template entries (key order + omit defaults + domain label)
- [ ] 7. Scaffold missing dependency stubs
- [ ] 8. Emit placement + YAML (write only if asked)
```

### 1. Gather inputs

Need, from the user or inference:

- **Repo URL** — GitHub (`github.com/owner/repo`) or GitLab (`gitlab.com/owner/repo`), HTTPS or SSH form.
- **Branch/ref** — default to the repo's default branch if unstated.
- **Playbook path(s)** — a specific file, a glob (e.g. `playbooks/aws/*.yml`), or "all playbooks" (search the whole tree for plausible playbook files — see step 3).
- **Domain** — `common`, `cloud`, `networking`, `linux`, `windows`, `hashi`, `aiops`, `itsm`, `apps`, `aap`, `hub`, `business`.
- **Project name** — the AAP `project` this job template will reference.

Resolving domain and project when not stated:

1. Check whether a `controller_projects_*` entry across `config/*/projects.yml` already has an `scm_url` matching this repo (case-insensitive, ignore `.git` suffix / protocol). If found, reuse its `name` and the domain of the file it lives in.
2. Otherwise derive a candidate project name from the repo name (`ansible-cloud-mgmt` → `Cloud Mgmt`; strip `ansible-`/`-mgmt` conventions loosely, Title Case the rest) and a candidate domain from repo/playbook naming cues — see the domain hint table in [resource-map.md](../cac-parser/resource-map.md#domain-hint-keywords-non-exhaustive).
3. If domain is still ambiguous (no strong naming cue, could plausibly fit 2+ domains, or repo mixes content for multiple domains), **stop and ask the user** which domain to target — do not guess silently. State your best guess with rationale as the default option.

### 2. Fetch remote repo tree + playbook content

**GitHub** (prefer `gh` CLI — respects existing auth, works for private repos the user has access to):

```bash
# List tree (recursive) at a ref
gh api repos/{owner}/{repo}/git/trees/{branch}?recursive=1 --jq '.tree[] | select(.type=="blob") | .path'

# Read one file's content (base64-decoded)
gh api repos/{owner}/{repo}/contents/{path}?ref={branch} --jq '.content' | base64 -d
```

Fall back to raw URLs for public repos when `gh` is unavailable or unauthenticated:

```
https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

**GitLab** (prefer `glab` CLI if installed; otherwise `curl` with `GITLAB_TOKEN` against the v4 API):

```bash
# glab
glab api "projects/{owner}%2F{repo}/repository/tree?ref={branch}&recursive=true"
glab api "projects/{owner}%2F{repo}/repository/files/{url_encoded_path}/raw?ref={branch}"

# curl fallback
curl -sH "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  "https://gitlab.com/api/v4/projects/{owner}%2F{repo}/repository/tree?ref=${branch}&recursive=true"
```

Fall back to raw URLs for public GitLab repos:

```
https://gitlab.com/{owner}/{repo}/-/raw/{branch}/{path}
```

If both authenticated and public access fail (private repo, no access), stop and ask the user for a token or to grant access — do not guess repo contents.

When the user asked for "all playbooks" rather than a specific path, filter the tree for `.yml`/`.yaml` files that look like playbooks: a top-level list whose items have `hosts:` (distinguish from `vars/`, `group_vars/`, `host_vars/`, `defaults/`, `meta/`, molecule/test fixtures, and CI config — skip those).

### 3. Analyze each playbook

For every target playbook, extract:

| Signal | Use |
|--------|-----|
| Play `name` | Seed for the job template's descriptive name |
| `hosts` | Inventory hint — `localhost`/`all` vs. a named group |
| `become` | Hints at `Machine` credential need |
| `collections` / module FQCNs used (`amazon.aws.*`, `azure.azcollection.*`, `google.cloud.*`, `vmware.*`, `cisco.*`, `paloaltonetworks.*`, `servicenow.itsm.*`, `community.hashi_vault.*`, `ansible.windows.*`) | Domain confirmation + credential/EE hints (see table below) |
| `vars_files` | Note as a follow-up (playbook expects vars this JT won't supply unless `ask_variables_on_launch`) |
| `vars_prompt` | Convert each entry to a `survey_spec` question (see step 6) |
| Top-level `vars:` that look like required user input (placeholder-y values, empty strings, `CHANGE_ME`) | Candidate `extra_vars` + `ask_variables_on_launch: true` |

Module-family → credential/EE hint table:

| Modules / collection prefix | Credential hint | EE hint |
|---|---|---|
| `amazon.aws.*`, `community.aws.*` | an existing `AWS *` credential in `config/common\|cloud/credentials.yml` | `ee-cloud` or `ee-default` |
| `azure.azcollection.*` | an existing `Azure *` credential | `ee-cloud` |
| `google.cloud.*` | an existing `GCP *` credential | `ee-cloud` |
| `community.vmware.*`, `vmware.vmware_rest.*` | an existing `VMWare *` credential | `ee-cloud` or `ee-default` |
| `cisco.*`, `ansible.netcommon.*` | network device credential | `ee-networking` |
| `ansible.windows.*`, `community.windows.*` | a `Windows *` / AD credential | `ee-windows` |
| `servicenow.itsm.*` | `West ServiceNow (...)` / OpenFlake credential | `ee-default` |
| `community.hashi_vault.*` | Vault credential | `ee-default` or domain-specific |
| plain `ansible.builtin.*` + `become: true` over SSH | `Machine` / `AAP (...)` SSH credential | `ee-default` |

Cross-check hint candidates against what's actually defined in `config/common/credentials.yml`, `config/common/execution_environments.yml`, and the target domain's own files before assuming a name — prefer an **exact existing name** over inventing one.

### 4. Resolve dependencies

For the **project**:

- Search `config/*/projects.yml` for an entry whose `scm_url` matches the repo (normalize: strip `.git`, ignore `http(s)://` vs `git@` form, ignore trailing slash).
- If found: reuse that `name`; job templates reference it via `project:` as-is, no new project entry needed.
- If not found: this is a new project — scaffold it (step 7).

For **credentials / inventory / execution_environment**: search existing `config/common/*.yml` and `config/<domain>/*.yml` for a name matching the hints from step 3. Prefer reusing an existing resource by exact name. Only scaffold a new credential stub when nothing plausible exists (step 7) — never scaffold a new inventory or EE automatically; flag those as follow-ups instead, since they usually require real infrastructure decisions the agent can't make.

### 5. Scan for collisions with existing resources

Before generating any new YAML, check every candidate name (job template, new project stub, new credential stub) against what's already in `config/` — a same-named resource must never be silently duplicated, shadowed, or applied under the wrong domain.

```bash
# Job template name — search every domain, not just the target one
rg -n "name: <Candidate JT Name>$" config/*/job_templates.yml

# Project name, and scm_url under a possibly different name
rg -n "name: <Candidate Project Name>$" config/*/projects.yml
rg -n "<repo-slug>" config/*/projects.yml

# Credential name
rg -n "name: <Candidate Credential Name>$" config/common/credentials.yml config/*/credentials.yml
```

| Collision | How it shows up | Ask the user |
|---|---|---|
| JT name already exists in the **target** domain | exact `name:` match in `config/<domain>/job_templates.yml` | Update that entry in place, or pick a different name — show the existing entry's current fields next to the proposed new ones |
| JT name already exists in **another** domain | exact `name:` match in a different domain's `job_templates.yml` | Confirm an intentional cross-domain duplicate name, rename the new entry, or re-target the new entry to that domain instead |
| Project name matches but `scm_url` differs | name match in `config/*/projects.yml`, different repo | Rename the new project stub (different project) vs. correct the stored `scm_url` on the existing one — never silently pick |
| Repo `scm_url` already backs a **differently-named** project | `scm_url` match under another `name:` | Reuse that existing name — do not create a second project pointing at the same repo |
| Credential name matches but `credential_type` / evident purpose differs | name match, mismatched type or clearly different service | Rename the new credential stub, or confirm the existing credential is genuinely reusable for this playbook |
| Resolved domain conflicts with the domain of an existing same-name/same-repo resource | any of the above landing in a domain other than the one requested | Confirm which domain is canonical — per [AGENTS.md](../../../AGENTS.md#placement-rules-no-cross-dependencies), the same resource must not live in two domains |

Resolution rules:

- Surface every collision **before** emitting final output for that resource — show the existing entry (name + file, and line range if trivial to locate) next to the proposed new one, then ask using a structured question (options: reuse/update existing, rename the new one, re-target the domain).
- Never auto-resolve by appending a disambiguating suffix (` (2)`, `-new`, …) or silently overwriting — the user decides.
- A collision on one resource (e.g. a credential) doesn't block progress on independent, non-colliding resources in the same batch — keep generating those and call out the blocked one in the output's Follow-ups.
- If there's no way to ask synchronously (e.g. an unattended batch run), stop and list every unresolved collision instead of guessing.

### 6. Generate job template entries

One `- name: ...` entry per playbook, in [key_ordering.md](../cac-parser/key_ordering.md) Job Templates order:

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
  ask_variables_on_launch:
  extra_vars:
  survey_enabled:
  survey_spec:
```

Rules:

- **Name**: `<Prefix> // <Descriptive Name>` matching the target domain's existing naming convention (look at sibling entries in the target `job_templates.yml` — e.g. `AWS //`, `EDA //`, `Terraform //`). Ask the user to confirm/override if no convention is obvious and the play `name:` is not already suitable.
- **`playbook`**: the path relative to the project's SCM root (the path you fetched the file at), not an absolute or repo-qualified path.
- **`labels`**: exactly one domain label from [labels.yml](../../../config/common/labels.yml) (see [AGENTS.md](../../../AGENTS.md#domain-labels-required)) — omit entirely for `common`.
- **`vars_prompt`** entries become `survey_spec.spec[]` items (`question_name`, `variable`, `type` mapped from `private`/`default`, `required` from `vars_prompt.private`/absence of default) with `survey_enabled: true`.
- Omit defaults per [resource-map.md](../cac-parser/resource-map.md#controller_job_templates--controller_templates_-ansiblecontrollerjob_template): no `job_type: run`, `job_slice_count: 1`, false `ask_*`, empty `limit`/`job_tags`/`description`.
- `extra_vars` must be a YAML dict, never a string (see [extra-vars-dict rule](../../../.cursor/rules/extra-vars-dict.mdc)).
- If credentials/inventory/EE could not be confidently resolved in step 4, leave a `# TODO:` comment inline rather than guessing a name that doesn't exist.
- If step 5 found an unresolved collision for this entry's name, do not emit a final entry for it — surface the collision and wait for the user's resolution instead.

### 7. Scaffold missing dependency stubs

**New project** (only when step 4 found no match, and step 5 found no unresolved name/`scm_url` collision) — append to `controller_projects_<domain>` in `config/<domain>/projects.yml` (or `config/common/projects.yml` if this repo will clearly back job templates in 2+ domains):

```yaml
- name: <Derived Name>
  organization: Autodotes
  scm_type: git
  scm_url: <normalized clone URL>
  scm_branch: <default branch>
  scm_clean: "no"
  scm_delete_on_update: "no"
  scm_update_on_launch: "no"
```

If the file doesn't exist yet in that domain, create it with the correct one-liner (see [AGENTS.md](../../../AGENTS.md#var-file-one-liners-required)) and update that domain's README file table.

**New credential** (only when no existing credential fits) — append a placeholder entry to `controller_credentials_<domain>` noting the needed `credential_type` and a new vault var name (`controller_credential_<descriptive>`), documented as a follow-up for `vars/*_secrets.redacted.yml` — never a real secret value.

Do **not** auto-scaffold inventories or execution environments; surface them as follow-ups (step 8) since they require real target-system decisions.

### 8. Emit result

Default: **do not write files** unless the user asks to add/append. Output, per playbook processed:

1. **Placement** — domain, file path(s), variable name(s), apply one-liner(s) matching [AGENTS.md](../../../AGENTS.md#var-file-one-liners-required) style.
2. **Rationale** — domain/project match or derivation reasoning.
3. **Collisions** — any conflicts found in step 5, how the user resolved them, or that a resolution is still pending (and which resource is blocked as a result).
4. **YAML entries** — job template entry (and any new project/credential stub), each ready to paste under its target variable.
5. **Follow-ups** — anything scaffolded that needs a real value (vault var, inventory, EE), any `# TODO:` left in a JT, and the domain label added to `labels.yml` if it was missing.

If the user asks to apply: append entries to the correct list(s) in the vars file(s); preserve file one-liners and `---`; update the domain README file table only when adding a **new** YAML file (per [AGENTS.md](../../../AGENTS.md#adding-a-new-resource-checklist)).

## Output template

```markdown
## Placement
- Domain: `<domain>`
- Files: `config/<domain>/job_templates.yml`[, `config/<domain>/projects.yml`]
- Variables: `controller_templates_<domain>`[, `controller_projects_<domain>`]
- Apply: `ansible-playbook pb_aap_config.yml -e "domains=<domain>" -e "skip_common=true" --tags job_templates[,projects]`

## Rationale
<domain/project match or derivation reasoning>

## Collisions
<omit this section entirely when step 5 found none>
- `<resource>`: existing `<name>` in `<file>` — asked user; resolution: <reuse / update existing / renamed to X / re-targeted to domain Y / still pending>

## Entries
\`\`\`yaml
- name: ...
  ...
\`\`\`

## Follow-ups
- ...
```

## Examples

See [examples.md](examples.md) for a GitHub single-playbook walkthrough, a GitLab multi-playbook walkthrough, and a collision-resolution walkthrough.

## Additional resources

- [cac-parser/SKILL.md](../cac-parser/SKILL.md) — the conversion conventions this skill reuses (key order, omit defaults, domain labels, output template)
- [cac-parser/key_ordering.md](../cac-parser/key_ordering.md) — Job Templates / Projects / Credentials key order
- [cac-parser/resource-map.md](../cac-parser/resource-map.md) — omit-able defaults, domain hint keywords
- [AGENTS.md](../../../AGENTS.md) — placement rules, domain labels, var-file one-liners
- [.cursor/rules/extra-vars-dict.mdc](../../../.cursor/rules/extra-vars-dict.mdc) — `extra_vars` must be a dict
- [.cursor/rules/aap-read-only.mdc](../../../.cursor/rules/aap-read-only.mdc) — this skill only ever edits `config/` files; it never applies changes to AAP
