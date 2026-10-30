# ORACLE OS — Project Specification

**Version:** 0.1.0  
**Status:** Initial specification  
**Source of truth:** This repository; project identity is recorded in `config/oracle.conf`.

## Purpose

ORACLE OS is an experimental Debian-based Linux distribution for learning Linux system construction and operating a personal cybersecurity lab. The first milestone is a small, reproducible Debian Live image that can be evaluated in an isolated virtual machine. ORACLE OS uses the Debian Linux kernel; developing a separate kernel is a long-term research objective, not part of the first release.

## Intended users and use

- The project owner, for learning Linux, networking, and system administration.
- Authorized, controlled cybersecurity exercises in an isolated lab.
- Development and initial boot validation in virtual machines.

Security tools must be used only on systems the operator owns or is authorized to assess.

## Version 0.1 scope

- Debian 13 (trixie) as the base distribution.
- Debian Live and `live-build` for image construction.
- A minimal terminal-first system with Debian's existing kernel, systemd, and package management.
- ORACLE identity and package selection maintained in repository configuration.
- Optional tool package lists kept separate from the core package list.
- Rootful Podman builder based on Debian 13, launched from a disposable VM for actual builds.
- QEMU as the planned first environment for boot evaluation.

The implemented package set and build flags are defined by `config/`, `image/config/`, `image/auto/config`, and `image/Containerfile`; those files take precedence over illustrative prose here.

## Out of scope for the first milestone

- A custom Linux kernel, graphical desktop, ORACLE package repository, or complete runtime profile manager.
- Installation on the owner's physical machine or modification of its partitions, bootloader, EFI, Windows, or unrelated runtimes.
- Treating an unbuilt or untested image as secure or release-ready.
- Running privileged image builds on the physical development host.

## Identity and platform

`config/oracle.conf` is the canonical project identity:

| Field | Value |
|---|---|
| Name / ID | ORACLE OS / `oracle` |
| Version | `0.1.0` |
| Base / release | Debian / 13 (`trixie`) |
| Purpose | `cybersecurity-lab` |

The initial live image targets AMD64 as configured in `image/auto/config`. Image configuration and package lists are kept under `image/`, separate from the root-level project `config/` and generated `build/` workspace.

## Safety and security requirements

1. Keep source, configuration, tests, and documentation in version control; generated output belongs in ignored `build/`.
2. Run the privileged Podman build only in a disposable VM with outbound connectivity through NAT.
3. Do not attach physical host disks or share the original source checkout with that VM. The build uses `--privileged` and host networking within the VM; this grants the builder access to VM devices and VM-local services.
4. Review the build script before running it: a normal build clears the generated `build/` workspace.
5. Validate changes with static checks and the repository test suite before building.
6. Boot validation is a separate QEMU step. Physical USB/live testing or installation requires a separately reviewed plan.

## Acceptance criteria for the first bootable-image milestone

- The image build completes from documented, version-controlled sources in the isolated VM.
- The resulting ISO is present and its basic metadata and integrity are checked.
- The image reaches the intended live environment in QEMU without a critical failure.
- Build and QEMU results, limitations, and reproduction steps are recorded.

These are future acceptance criteria. As of this specification, no ISO has been built or booted.

## Decisions still open

Graphical environment, exact core security-tool set, firewall defaults, persistence, installation workflow, release and signing process, and long-term kernel research design remain undecided. Resolve them in the roadmap when their phase begins.
