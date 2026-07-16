# Configuration domains

AAP Configuration as Code is split into **domain** folders under `config/`. Shared definitions live in [`common/`](./common/README.md). Every other domain depends only on itself plus `common` (no cross-domain definitions).

Apply with [`pb_aap_config.yml`](../pb_aap_config.yml) from the repository root. Wildcard variable suffixes (e.g. `controller_templates_cloud`) are merged by `infra.aap_configuration.dispatch` when `dispatch_include_wildcard_vars: true`.

## Domains

| Domain | Tag | Description |
|--------|-----|-------------|
| [common](./common/README.md) | `always` (skip with `--skip-tags common`) | Platform fundamentals and multi-domain shared resources |
| [cloud](./cloud/README.md) | `cloud` | AWS, Azure, GCP, VMware |
| [networking](./networking/README.md) | `networking` | Cisco, Palo Alto, Summit Connect |
| [linux](./linux/README.md) | `linux` | Linux/RHEL management and patching |
| [windows](./windows/README.md) | `windows` | Windows, AD, Proxmox |
| [hashi](./hashi/README.md) | `hashi` | HashiCorp Terraform/HCP and Vault |
| [aiops](./aiops/README.md) | `aiops` | AIOps + Event-Driven Ansible |
| [servicenow](./servicenow/README.md) | `servicenow` | ServiceNow ITSM and Selenium demos |
| [apps](./apps/README.md) | `apps` | SSL/ACME, Kasa, CyberArk, policy demos |
| [aap](./aap/README.md) | `aap` | AAP self-management and EE builds |
| [hub](./hub/README.md) | `hub` | Private Automation Hub |

## Quick examples

Add `--ask-vault-pass` or `--vault-password-file <path>` when vaulted secrets in `vars/` are required for the resources you are applying.

```bash
# common only
ansible-playbook pb_aap_config.yml

# common + one domain
ansible-playbook pb_aap_config.yml --tags networking

# common + domain, single resource type
ansible-playbook pb_aap_config.yml --tags networking,job_templates

# everything
ansible-playbook pb_aap_config.yml \
  --tags cloud,networking,linux,windows,hashi,aiops,servicenow,apps,aap,hub
```

Each domain README lists the files in that folder and the exact tag combinations to scope to a single file. Each YAML var file also has a matching one-liner comment at the top.
