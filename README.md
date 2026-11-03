# Authentik for Home Assistant

A focused, community-maintained **Authentik** Home Assistant add-on repository, forked from [akentner/homeassistant-addons](https://github.com/akentner/homeassistant-addons).

This fork packages **only Authentik**; unrelated upstream add-ons and multi-add-on automation have been excluded. Upstream Authentik source: https://github.com/goauthentik/authentik.

## Status

**Packaging validation in progress. Not yet deployed or accepted as the household identity provider.**

- Bundled Authentik server/worker, PostgreSQL and Valkey
- Persistent add-on data under `/data`
- UI/API on host-mapped port `9000` (not Home Assistant ingress)
- Currently only `amd64`, matching the inherited build
- Manual boot remains enabled until startup, backup and upgrade tests pass

[Add-on configuration and recovery notes](authentik/DOCS.md) · [Packaging source](authentik/) · [Original repository](https://github.com/akentner/homeassistant-addons)

## Installation (after validation)

Add `https://github.com/Akm0d/ha-authentic-addon` as a custom repository in **Home Assistant → Settings → Add-ons → Add-on Store**, then install Authentik. Verify Hearth architecture is `amd64` first.

Configure a stable HTTPS hostname for the identity provider and preserve native Home Assistant sign-in as a break-glass method. Do not depend on Authentik for restoring its own credentials.

## Release policy

Upstream Authentik versions are checked automatically every six hours. New versions open a reviewable PR and run build validation; an upstream release does not automatically deploy to Hearth. Rebuilds refresh Debian `apt` packages at build time, not in running containers. An independent dependency-refresh policy is still needed for periods without upstream Authentik releases.

Do not merge or auto-install new Authentik versions solely because a newer upstream image exists. Major migrations and PostgreSQL compatibility require explicit verification and a tested off-host backup.

The next work items are release-PR automation, startup/health checks, backup-and-restore testing, and an explicit upgrade gate. Unrelated Windows/LDAP/domain-controller work is out of scope.

## Attribution and license

Fork of akentner's Home Assistant add-on packaging. Retain the original [Apache-2.0 LICENSE](LICENSE). Authentik itself has its own upstream licensing.
