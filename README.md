# Authentik Home Assistant Add-on

A Home Assistant add-on for [Authentik](https://goauthentik.io/), a self-hosted identity provider supporting OAuth2/OIDC, SAML, LDAP, and more.

## Features

- Authentik server and background worker
- Bundled PostgreSQL 17; no external database or Valkey required
- Persistent add-on data in `/data`
- Web UI and OIDC endpoints on port `9000` (not Home Assistant ingress)
- Installation, configuration, logs, backups, and updates through Home Assistant Supervisor
- Automatic upstream Authentik release tracking with reviewable update PRs

## Status

The add-on is under runtime validation. Docker builds passing CI do not yet establish successful first boot, identity-provider operation, or tested backup/restore.

- Supported architecture: `amd64`
- Upstream Authentik version: `2026.8.5`
- Automatic boot remains disabled pending runtime validation

## Installation

1. Add `https://github.com/Akm0d/ha-authentic-addon` to the Home Assistant add-on repositories.
2. Install **Authentik** from the add-on store.
3. Configure and start the add-on from Home Assistant.
4. Access the web UI through port `9000`. An **Open Web UI** button is being added as part of the next packaging revision.
5. Before configuring SSO clients, set up a stable HTTPS URL for Authentik that does not depend on an existing Home Assistant session.

See [configuration and recovery documentation](authentik/DOCS.md).

## Releases

The repository checks for new stable Authentik releases every six hours and proposes updates as pull requests. Container images are rebuilt for upstream changes; newer Debian packages are resolved at build time, not installed into running containers.

New Authentik versions are **not automatically deployed**. Database compatibility, major release sequencing, backup and restore, and login/OIDC behavior must be validated before deployment.

## License

Add-on packaging is distributed under the [Apache License 2.0](LICENSE). Authentik itself is a separate project with its own licensing.
