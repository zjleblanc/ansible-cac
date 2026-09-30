# Examples

## Example 1 — GitHub, single playbook, new project

**User input:** "Template a job template from `https://github.com/acme-corp/ansible-aws-patching`, playbook `playbooks/patch_instances.yml`. This is cloud domain."

**Fetched playbook (`playbooks/patch_instances.yml`):**

```yaml
---
- name: Patch AWS EC2 instances
  hosts: all
  become: true
  collections:
    - amazon.aws
  vars_prompt:
    - name: reboot_after_patch
      prompt: Reboot instances after patching?
      default: "true"
      private: false
  tasks:
    - name: Apply OS updates
      ansible.builtin.package:
        name: "*"
        state: latest
    - name: Reboot if requested
      ansible.builtin.reboot:
      when: reboot_after_patch | bool
```

**Analysis:**

- `hosts: all` + `amazon.aws` collection → AWS-flavored, domain `cloud` confirmed by user.
- `become: true` + `ansible.builtin.package`/`reboot` → needs a `Machine`/SSH credential, not a cloud API credential (no `amazon.aws.*` modules actually used despite the collection declaration).
- `vars_prompt` → one survey question (`reboot_after_patch`, boolean-ish text default `"true"`).
- Repo `ansible-aws-patching` has no matching `scm_url` in any `config/*/projects.yml` → new project needed.
- Inventory: `hosts: all` with no group hint → check `config/cloud/inventories.yml` / `config/common/inventories.yml`; found `Cloud Inventory` already used by sibling cloud job templates — reuse it.
- Credential: `AWS (ec2-user)` already exists in `config/common/credentials.yml` and is used by sibling AWS job templates for SSH — reuse it.

**Output:**

```markdown
## Placement
- Domain: `cloud`
- Files: `config/cloud/job_templates.yml`, `config/cloud/projects.yml`
- Variables: `controller_templates_cloud`, `controller_projects_cloud`
- Apply: `ansible-playbook pb_aap_config.yml -e "domains=cloud" -e "skip_common=true" --tags job_templates,projects`

## Rationale
No existing `config/*/projects.yml` entry has `scm_url` matching `ansible-aws-patching`, so a new project stub is needed. Job template placed in `cloud` per your instruction and confirmed by the `amazon.aws` collection + AWS-only usage. Reused `Cloud Inventory` and `AWS (ec2-user)` since sibling cloud job templates already reference them for SSH-based tasks.

## Entries
\`\`\`yaml
# config/cloud/projects.yml — controller_projects_cloud
- name: AWS Patching
  organization: Autodotes
  scm_type: git
  scm_url: https://github.com/acme-corp/ansible-aws-patching.git
  scm_branch: main
  scm_clean: "no"
  scm_delete_on_update: "no"
  scm_update_on_launch: "no"
\`\`\`

\`\`\`yaml
# config/cloud/job_templates.yml — controller_templates_cloud
- name: AWS // Patch Instances
  labels:
    - Cloud
  project: AWS Patching
  playbook: playbooks/patch_instances.yml
  inventory: Cloud Inventory
  execution_environment: ee-cloud
  credentials:
    - AWS (ec2-user)
  ask_variables_on_launch: true
  survey_enabled: true
  survey_spec:
    name: ""
    description: ""
    spec:
      - question_name: Reboot instances after patching?
        type: text
        default: "true"
        variable: reboot_after_patch
        required: true
\`\`\`

## Follow-ups
- Confirm `AWS Patching` is the desired project display name (derived from repo name).
- Verify the default branch is `main` (assumed — confirm against the repo if it differs).
- No new credential/vault var needed — reused existing `AWS (ec2-user)`.
```

---

## Example 2 — GitLab, multiple playbooks, existing project

**User input:** "Pull all playbooks under `playbooks/network/` from `gitlab.com/acme-corp/ansible-network-ops` (branch `main`) and add job templates — networking domain, project already exists as `Network Mgmt`."

**Fetched tree** (via `glab api "projects/acme-corp%2Fansible-network-ops/repository/tree?ref=main&recursive=true"`), filtered to `playbooks/network/*.yml`:

- `playbooks/network/backup_configs.yml` — `hosts: cisco_ios`, `cisco.ios.ios_command`, no prompts.
- `playbooks/network/push_acl.yml` — `hosts: cisco_ios`, `cisco.ios.ios_config`, `vars_prompt` for `acl_name`.

**Analysis:**

- Both plays use `cisco.ios.*` → domain `networking` confirmed, EE hint `ee-networking`.
- Project `Network Mgmt` given by user — skip step 4/6 project scaffolding, just verify it exists in `config/networking/projects.yml` (it does).
- `hosts: cisco_ios` → matches an existing inventory group `Network Devices` in `config/networking/inventories.yml`; reuse it.
- No existing Cisco credential found under `config/common/credentials.yml` or `config/networking/credentials.yml` with a name that clearly matches — flag as a follow-up rather than inventing one.

**Output (abridged):**

```markdown
## Placement
- Domain: `networking`
- File: `config/networking/job_templates.yml`
- Variable: `controller_templates_networking`
- Apply: `ansible-playbook pb_aap_config.yml -e "domains=networking" -e "skip_common=true" --tags job_templates`

## Rationale
Both playbooks target `cisco.ios.*` devices; domain and project were already specified by the user and verified to exist.

## Entries
\`\`\`yaml
- name: Cisco // Backup Configs
  labels:
    - Network
  project: Network Mgmt
  playbook: playbooks/network/backup_configs.yml
  inventory: Network Devices
  execution_environment: ee-networking
  credentials:
    - # TODO: no matching Cisco credential found in config/ — add or confirm name
- name: Cisco // Push ACL
  labels:
    - Network
  project: Network Mgmt
  playbook: playbooks/network/push_acl.yml
  inventory: Network Devices
  execution_environment: ee-networking
  credentials:
    - # TODO: no matching Cisco credential found in config/ — add or confirm name
  ask_variables_on_launch: true
  survey_enabled: true
  survey_spec:
    name: ""
    description: ""
    spec:
      - question_name: acl_name
        type: text
        variable: acl_name
        required: true
\`\`\`

## Follow-ups
- Resolve the Cisco device credential: none found by name under `config/common/credentials.yml` or `config/networking/credentials.yml`. Provide an existing name or approve a new stub (credential_type + vault var) before applying.
- Both entries use the single `Network` domain label already defined in `config/common/labels.yml` — no label changes needed.
```

---

## Example 3 — GitHub, name and project collisions detected

**User input:** "Template `playbooks/resize_disk.yml` from `https://github.com/acme-corp/ansible-aws-ops` into the `cloud` domain."

**Fetched playbook (`playbooks/resize_disk.yml`):**

```yaml
---
- name: Resize Disk
  hosts: all
  collections:
    - amazon.aws
  tasks:
    - name: Grow the root EBS volume
      amazon.aws.ec2_vol:
        state: present
        resize: true
```

**Step 4 — resolve dependencies:** derived project name `AWS Ops` (from `ansible-aws-ops`); derived JT name `AWS // Resize Disk` (matching sibling `AWS //` naming in `config/aiops/job_templates.yml` / `config/cloud/job_templates.yml`).

**Step 5 — scan for collisions:**

```bash
$ rg -n "name: AWS // Resize Disk$" config/*/job_templates.yml
config/aiops/job_templates.yml:246:  - name: AO // Resize Disk
# (no exact match on "AWS // Resize Disk" itself, but a near-duplicate exists)

$ rg -n "name: AWS Ops$" config/*/projects.yml
# no match

$ rg -n "ansible-aws-ops" config/*/projects.yml
# no match — this is a genuinely new project
```

A closer look shows `config/aiops/job_templates.yml` already has `AO // Resize Disk` pointed at `playbooks/aws/resize_disk.yml` in the `Cloud Mgmt` project — functionally the same operation, different repo/project, different domain, similar-but-not-identical name.

**Agent asks the user (structured question, not a guess):**

> Found an existing job template that looks like the same operation: `AO // Resize Disk` in `config/aiops/job_templates.yml` (project `Cloud Mgmt`, playbook `playbooks/aws/resize_disk.yml`). Your new source is a different repo (`ansible-aws-ops`) and domain (`cloud`). How do you want to resolve this?
> 1. **Keep both** — proceed with a new `AWS // Resize Disk` entry in `cloud`, treating these as intentionally separate job templates (recommended if `ansible-aws-ops` is meant to replace/supersede the `aiops` one over time).
> 2. **Consolidate** — don't create a new entry; instead point the existing `AO // Resize Disk` at the new repo/playbook (tell me if `Cloud Mgmt` project's `scm_url` should change, or if a new project stub should replace it).
> 3. **Rename** — create the new entry under a different name so there's no ambiguity with the existing one.

**User selects option 1 (keep both).** No project-name collision exists (`AWS Ops` is new), so the project stub proceeds normally.

**Output:**

```markdown
## Placement
- Domain: `cloud`
- Files: `config/cloud/job_templates.yml`, `config/cloud/projects.yml`
- Variables: `controller_templates_cloud`, `controller_projects_cloud`
- Apply: `ansible-playbook pb_aap_config.yml -e "domains=cloud" -e "skip_common=true" --tags job_templates,projects`

## Rationale
No `scm_url` match for `ansible-aws-ops` in any domain, so a new project stub is required. `AWS // Resize Disk` is a distinct name from the existing `AO // Resize Disk` (different repo/project/domain) — user confirmed both should coexist.

## Collisions
- Job template: existing `AO // Resize Disk` in `config/aiops/job_templates.yml` (similar operation, different repo) — asked user; resolution: keep both as separate entries.

## Entries
\`\`\`yaml
# config/cloud/projects.yml — controller_projects_cloud
- name: AWS Ops
  organization: Autodotes
  scm_type: git
  scm_url: https://github.com/acme-corp/ansible-aws-ops.git
  scm_branch: main
  scm_clean: "no"
  scm_delete_on_update: "no"
  scm_update_on_launch: "no"
\`\`\`

\`\`\`yaml
# config/cloud/job_templates.yml — controller_templates_cloud
- name: AWS // Resize Disk
  labels:
    - Cloud
  project: AWS Ops
  playbook: playbooks/resize_disk.yml
  inventory: Cloud Inventory
  execution_environment: ee-cloud
  credentials:
    - # TODO: no matching AWS credential confirmed for this project — verify AWS Sandbox Credential applies
\`\`\`

## Follow-ups
- Confirm the AWS credential to attach (defaulted to a `# TODO:` rather than assuming `AWS Sandbox Credential` fits this new repo's account).
- No further collisions outstanding — both `AO // Resize Disk` and `AWS // Resize Disk` will coexist per user decision.
```
