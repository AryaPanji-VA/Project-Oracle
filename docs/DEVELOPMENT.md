# ORACLE OS — Development and Testing Workflow

This document describes the repository workflow and the checks available before any image build. Keep `docs/SPECIFICATION.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` aligned when project decisions change.

## Source of truth

- `config/oracle.conf`: distribution identity.
- `config/profiles.conf`: optional profile selection.
- `image/auto/config`: `live-build` configuration.
- `image/config/`: package lists and image customizations.
- `image/Containerfile`: Debian builder environment.
- `scripts/`: build and maintenance commands.
- `tests/`: automated repository checks.
- `docs/`: specification, architecture, workflow, roadmap, and current status.
- `build/`: disposable generated workspace; never store hand-maintained files here.

If documentation and executable configuration disagree, inspect the configuration and script, then update the documentation in the same change. Do not silently change project scope to match stale documentation.

## Change workflow

1. Start from the intended Git branch and inspect `git status`; preserve existing edits.
2. Make a focused change to source/configuration and its documentation. Keep generated build output out of commits.
3. Run the checks below and review the complete diff, including `git diff --check`.
4. Commit only the reviewed changes with a message describing the change. Push only when the repository owner chooses to do so.

## Local checks

From the repository root:

```bash
./scripts/build.sh --check
./tests/run_all.sh
git diff --check
```

`--check` validates basic build prerequisites; it does not build an image and does not prove that Podman networking or `live-build` works end to end. The test suite includes static checks and mocked build-flow checks. A passing suite does not replace a real build or QEMU boot test.

For shell syntax checks, run `bash -n` on Bash scripts and `sh -n` on scripts declared for POSIX `sh` (including `image/auto/config` and `scripts/gen-profile-list.sh`). Keep each script's interpreter consistent with its syntax.

## Isolated image build

The build uses rootful Podman with `--privileged` and `--network=host`. The script refuses the build path unless it detects a VM. Run it only in a disposable Debian 13 VM with NAT connectivity, no physical host disks attached, and no shared folder that exposes the original checkout. The builder can access VM devices and VM-local services.

Copy or clone the exact reviewed Git state into the VM; include any intended local commit and verify its revision before building. Then install Podman and sudo in the VM and run:

```bash
./scripts/build.sh --check
./scripts/build.sh
```

A normal build deletes and recreates the repository's `build/` workspace. Keep no manual data there. The generated ISO is an artifact, not a source file. Do not perform the build on the physical development host.

## Boot and hardware validation

Boot testing is separate from build and is intended for QEMU. Use the project's QEMU test path only after an ISO exists and the owner has chosen to test it. Do not write an image to USB or install it to physical storage as part of routine development; those actions need a separately reviewed target and recovery plan.

## What is not verified by repository tests

Automated tests do not establish that package repositories are reachable, the privileged build succeeds, the ISO is bootable, security controls are effective, or the system is safe for installation. Record evidence and limitations in `docs/STATUS.md` after each real environment check.
