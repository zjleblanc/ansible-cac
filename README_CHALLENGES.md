# Challenges

Last updated 11/26/2024

## General

| Obstacle | Description |
| --- | --- |
| Resolving FQDN - containerized AIO topology | When containerized AAP is installed via the AIO topology, execution environments will fail to resolve the FQDN of gateway/controller/eda if the underlying host has an entry in `/etc/hosts` when connecting to the API. |

## Organizations

The Organization resource has moved from Controller to the new Gateway component. The previously used data model for configuration-as-code no longer works. To workaround the changes, one must take a few steps **in order**:

1. Replace `ansible.controller.organization` with `ansible.platform.organization` and provide a subset of the fields {name, description} as parameters (otherwise you will get errors).
2. Run your ansible platform configuration-as-code job_template/playbook/play.
3. Modify use of the `ansible.controller.organization` module using the previous fields minus description (otherwise you will get errors).
4. Run your ansible controller configuration-as-code job_template/playbook/play.
5. Observe the Organization exists under the Access Management tab and you can see appropriate links to Controller resources like Galaxy Credentials, Execution Environments, etc.

## EDA

The ansible.eda collection does not support oauth, so you will have to provide one of the following:

- `controller_username, controller_password` ansible variables
- `CONTROLLER_USERNAME, CONTROLLER_PASSWORD` environment variables