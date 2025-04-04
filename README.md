# ansible-cac

Configuration as Code for Ansible Automation Platform

## secrets

Sensitive values used to populate credentials and other configuration details are supplied from vaulted files.
```
vars
├── controller_secrets.yml
├── eda_secrets.yml
└── platform_secrets.yml

1 directory, 3 files
```

Each file is encrypted with ansible-vault and you will see references to them in each `pb_{component}_cac.yml` playbook. Since I run these playbooks locally for now, I opted not to include these in the public repository. If you were looking for them and don't see them, that's why 🙂