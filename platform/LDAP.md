# LDAP config-as-code

There are two components to configuring an authentication mechanism for AAP 2.5+. You first define the main authenticator configuration (which maps to a plugin) and then create associated authenticator_maps which define what permissions to give a user logging into the system.

## LDAP authenticator

[Config-as-code](./authenticators.yml) for my Authenticators.

```yaml
gateway_authenticators:
  - name: Autodotes LDAP
    type: ansible_base.authentication.authenticator_plugins.ldap
    slug: ansible_base-authentication-authenticator_plugins-ldap__autodotes-ldap
    order: 2
    enabled: true
    create_objects: true
    remove_users: true
    configuration:
      BIND_DN: cn=Directory Manager
      BIND_PASSWORD: "{{ gateway_auth_ldap_bind_password }}"
      CONNECTION_OPTIONS: {}
      GROUP_SEARCH:
        - dc=autodotes,dc=com
        - SCOPE_SUBTREE
        - "(objectClass=groupOfUniqueNames)"
      GROUP_TYPE: GroupOfUniqueNamesType
      GROUP_TYPE_PARAMS:
        name_attr: cn
      SERVER_URI:
        - ldap://ldap.autodotes.com:389
      START_TLS: false
      USER_ATTR_MAP:
        email: mail
        last_name: sn
        first_name: givenName
      USER_SEARCH:
        - dc=autodotes,dc=com
        - SCOPE_SUBTREE
        - "(uid=%(user)s)"
...
```

## LDAP authenticator maps

[Config-as-code](./authenticator_maps.yml) for my Authenticator Maps.

Authenticator Maps are applied in order (ascending) and later maps take precedence over their predecessors. Refer to the documentation [here](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.5/html/access_management_and_authentication/gw-configure-authentication#gw-adjust-mapping-order) for more details.

```yaml
gateway_authenticator_maps:
  # This is one of many maps applied to users authenticated by the Autodotes LDAP authenticator
  - authenticator: Autodotes LDAP
    map_type: allow
    name: Allow Login
    order: 1
    organization: Ldappers
    revoke: true
    triggers:
      groups:
        has_or:
        - cn=networkingansible,ou=networking,dc=autodotes,dc=com
        - cn=platformansible,ou=platform,dc=autodotes,dc=com
        - cn=cloudansible,ou=cloud,dc=autodotes,dc=com
        - cn=linuxansible,ou=linux,dc=autodotes,dc=com
        - cn=windowsansible,ou=windows,dc=autodotes,dc=com
...
```
