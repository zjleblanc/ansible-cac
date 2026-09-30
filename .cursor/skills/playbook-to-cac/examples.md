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
