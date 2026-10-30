# ORACLE OS — Architecture

**Project:** ORACLE OS  
**Version:** 0.1.0  
**Base Distribution:** Debian  
**Purpose:** Personal Cybersecurity Lab  
**Status:** Initial Architecture

## 1. Overview

ORACLE OS is a Debian-based Linux distribution designed as a personal cybersecurity lab and an environment for learning Linux systems, networking, and security.

The project uses Debian as its foundation while introducing ORACLE-specific configuration, tooling, and package management capabilities over time.

The initial development priority is to build a working, reproducible, and testable security lab before expanding into installation, persistence, visual customization, and advanced system research.

## 2. Design Principles

ORACLE OS follows these principles:

- **Security by default:** Provide reasonable security protections without unnecessarily restricting legitimate experiments.
- **Terminal-first:** Prioritize command-line workflows while allowing an optional graphical environment.
- **Debian-native foundation:** Reuse established Debian tools and mechanisms instead of reinventing core operating system components.
- **Modular security tools:** Provide essential tools by default and additional tools through selectable profiles.
- **Reproducible development:** Make the image-building process repeatable and document test results.
- **Safe experimentation:** Develop and test in virtual machines before testing on physical hardware.
- **Incremental development:** Implement a functional foundation before expanding the system's scope.

## 3. Base System

ORACLE OS uses **Debian + Debian Live** as its foundation.

The initial system will use established Debian components:

- APT for package management.
- systemd for service and system management.
- Standard Linux configuration files and mechanisms.
- Debian Live and `live-build` for constructing the initial live image.

ORACLE-specific components will be added on top of this foundation rather than replacing established system infrastructure.

The initial release will prioritize compatibility with Debian packages and repositories. A dedicated ORACLE package repository is a long-term goal.

## 4. User Interface

ORACLE OS follows a terminal-first approach.

The initial release prioritizes:

- Command-line access.
- Shell-based administration and troubleshooting.
- CLI-based security tool management.
- An ORACLE-specific command-line interface, introduced incrementally.

A graphical environment remains optional. The desktop environment, display manager, and graphical customization are **TBD**.

Visual branding, including boot artwork, login appearance, and custom themes, will be developed after the underlying system becomes stable.

## 5. Security Tool Architecture

ORACLE OS will combine preinstalled core tools with optional tool profiles.

### 5.1 Core Tools

Core tools will be included in the initial image to provide essential system diagnostics, networking utilities, and basic security-lab capabilities.

The exact package list is **TBD**.

### 5.2 Tool Profiles

Additional tools will be organized into profiles based on their purpose.

Potential profile categories include:

- Networking and diagnostics.
- Web security testing.
- Digital forensics.

These categories are initial examples, not a finalized package specification.

### 5.3 Profile Management

The architecture supports two profile installation stages:

1. **Build-time:** Select profiles to include when building an ORACLE OS image.
2. **Runtime:** Install additional profiles after the operating system has booted.

The initial profile manager will be CLI-only.

Profile definitions should be reusable between build-time and runtime workflows to avoid maintaining separate package lists for the same profile.

The implementation, dependency handling, and final profile catalog are **TBD**.

## 6. Default Security Model

ORACLE OS adopts a **safe but flexible** security model.

The initial configuration should follow these principles:

- Use an unprivileged account for normal activities.
- Require administrative privileges for system-level changes.
- Minimize unnecessary services and network exposure.
- Configure firewall behavior according to the intended use case.
- Avoid enabling potentially risky services or tools without a clear reason.
- Keep security-related configuration understandable and auditable.

Security tools are intended for authorized testing, controlled experiments, and environments the user owns or has permission to assess.

Specific firewall rules, hardening measures, and service defaults are **TBD**.

## 7. Configuration and ORACLE Tooling

ORACLE OS will use a hybrid configuration architecture.

Debian remains responsible for fundamental operating system functions. ORACLE-specific components will provide a consistent interface for managing ORACLE configuration and features.

Planned components include:

- ORACLE identity and version configuration.
- ORACLE-specific configuration files.
- A CLI command named `oracle`.
- Tool profile definitions and installation workflows.
- Build automation and validation scripts.

The exact command syntax, directory structure, and internal interfaces will be determined during implementation.

## 8. Build System

ORACLE OS will use a staged hybrid build system.

### Initial stage

Use Debian `live-build` to construct the first images. Maintain the build configuration, package selections, and customization scripts in the project repository.

### Build environment

Builds run inside a **rootful Podman container based on Debian 13 (trixie)**, not on the host system.

Reason for a container: the host is an Arch-based Omarchy system, where `live-build` is not packaged in the official repositories (and is absent from the AUR). Running the build in a Debian container keeps the host untouched and matches the Debian environment the image is built from.

Reason for rootful (`sudo podman`): `lb build` mounts `/proc`, `/sys`, and `/dev/pts` inside the image chroot, and `debootstrap` runs `chroot(2)`. These require `CAP_SYS_ADMIN` and `CAP_SYS_CHROOT` in the namespace that owns the mounts. Rootless Podman cannot satisfy this. Documented facts:

- `live-build(7)` lists dedicated helpers `lb chroot_proc`, `lb chroot_sysfs`, and `lb chroot_devpts`, i.e. mounting kernel filesystems is part of the build.
- `debootstrap(8)` uses `chroot(2)`, which requires `CAP_SYS_CHROOT`.
- Podman's own documentation states that rootless `--privileged` grants `CAP_SYS_ADMIN` only to UID 0 inside the container, and that user-namespace UID mapping blocks these mounts.

The builder uses Podman's **host network** (`--network=host`) for image build and
container runs. On the development host, the rootful bridge failed DNS and direct
TCP egress; the same Debian 13 image succeeded with host networking. The build
script now requires a VM, so this mode shares the VM's network namespace and still
needs outbound access through the VM's NAT. It does not share the physical host's
network namespace. Repairing the bridge path remains a separate task.

Consequence, stated plainly: **the build container runs rootful with `--privileged`, which disables Podman's capability limits, device restrictions, read-only kernel mounts, and seccomp/AppArmor/SELinux confinement.** It also uses the VM's host network. The container can access VM devices and VM-local services, but not the physical host's devices unless they are passed through. This is why the build VM must not have host disks attached or a shared folder pointing at the source checkout.

`sudo` is required for two things only: launching Podman rootful, and removing the previous `build/` directory, which ends up root-owned.

### Blast radius of the build container

Since `--privileged` removes container isolation, what the container *can* reach is the only meaningful boundary. As of this writing:

- **Explicit bind mounts:** the project repository is mounted at `/work`, and `build/` at `/work/build`. The script does not explicitly bind-mount `/`, `/home`, `/etc`, `/var`, or device paths. `--privileged` still exposes host devices.
- **Network namespace:** host networking is used, so the container shares the VM's network namespace and can reach VM-local services. It does not receive a separate network namespace.
- **Mount propagation:** the default (`private`) is used. Mounts created inside the container do not propagate to the host.
- **Write targets inside the project:** `scripts/build.sh` writes exclusively under `build/`. `image/` is only ever read (`cp` reads from it, writes into `build/`). This was verified by inspecting every write operation in the script; `image/` can therefore be mounted read-only.
- **SELinux:** the host has no SELinux and no AppArmor, so the `:Z` relabel suffix is a no-op here.

**What this does NOT mean:** mounting the source read-only does not make the container safe. Inside a privileged container `CAP_SYS_ADMIN` can remount bind mounts. The builder can modify the VM and reach VM-local services; run it only inside a disposable VM with no physical host disks or source-folder shares attached.

Whether a *less* privileged configuration is possible has **not** been verified. Candidate options and their trade-offs are recorded in section 14 rather than assumed.

### Build workspace

`live-build` writes its working directories (`config/`, `binary/`, `chroot/`, `cache/`) into the directory where it is invoked. Running it at the repository root would collide with the project's own `config/` directory.

The repository therefore separates sources from build output:

- `image/` holds the version-controlled build sources (package lists, hooks, `auto/` configuration, includes).
- `build/` is a throwaway, git-ignored workspace where `live-build` actually runs.
- `scripts/build.sh` stages `image/` into `build/` before invoking `lb build`.

`build/` and all generated images are excluded from Git by `.gitignore`.

### Later stage

Introduce an ORACLE CLI wrapper to simplify common build operations, profile selection, and validation.

The wrapper will use the existing build infrastructure rather than immediately replacing it with a custom build framework.

Build scripts should be version-controlled, repeatable, and designed to make failures diagnosable.

## 9. Testing and Development Safety

**QEMU/virtual-machine testing is mandatory before testing an image on physical USB media.**

The development workflow is:

1. Prepare and validate the build configuration.
2. Build the image.
3. Boot the image in QEMU.
4. Test the required functionality and inspect failures.
5. Fix problems and repeat the tests.
6. Consider physical hardware testing only after the image passes the required checks.

Physical USB media must not be written without explicit permission.

Development must not modify the host's partitions, EFI configuration, bootloader, Windows installation, or primary Omarchy system without separate explicit authorization.

Network security experiments should use an isolated local lab whenever possible.

## 10. Update and Package Distribution Strategy

Initially, ORACLE OS will use Debian packages and repositories through APT.

The long-term plan is to establish a dedicated ORACLE package repository for ORACLE-maintained packages and tools.

This repository is a future capability, not a requirement for the first bootable image.

Before operating a public or shared repository, the project must define package signing, key management, repository metadata, release procedures, and security update responsibilities.

The repository implementation and infrastructure are **TBD**.

## 11. Installation and Persistence

The long-term product vision supports:

- Booting ORACLE OS as a live USB system.
- Trying the live environment before installation.
- Installing the system to persistent storage through a graphical installer.
- Full persistence for supported changes across reboots, including personal files, configuration, and installed packages.

The specific installer technology and persistence implementation are **TBD**.

**Neither the graphical installer nor full persistence is required for v0.1.** These features will be developed after the initial security-lab foundation is working.

Persistence is not a substitute for backups.

## 12. Version 0.1 Scope

The primary goal of v0.1 is to deliver an initial, usable personal security lab.

### Required goals

- [ ] Build a Debian Live image using `live-build`.
- [ ] Boot the image successfully in QEMU.
- [ ] Include ORACLE's initial technical identity and configuration.
- [ ] Provide essential preinstalled core tools.
- [ ] Implement several functional security tool profiles.
- [ ] Support profile selection during image builds.
- [ ] Support installing additional profiles through the CLI after boot.
- [ ] Document and validate the repeatable build process.
- [ ] Test basic networking in an isolated local lab.
- [ ] Document test results and known limitations.

### Excluded from v0.1

- Graphical installer.
- Full persistence.
- GUI-based profile management.
- Complete visual branding.
- Dedicated ORACLE package repository infrastructure.
- Custom kernel development.

These exclusions do not cancel the project's long-term goals.

## 13. Long-Term Direction

After v0.1 establishes a stable foundation, development may proceed toward:

1. Graphical installation and full persistence.
2. Improved CLI tooling and profile management.
3. Dedicated ORACLE package distribution.
4. Optional graphical environment and visual identity.
5. More comprehensive security-lab capabilities.
6. Advanced operating system research, including kernel-related experiments.

The detailed roadmap and priorities will be maintained separately in `docs/ROADMAP.md`.

## 14. Open Implementation Decisions

The following details remain intentionally unresolved until implementation requires them:

- Core package list.
- Tool profile names, packages, and dependencies.
- Desktop environment and display manager.
- Detailed default firewall and hardening configuration.
- ORACLE CLI command structure.
- Graphical installer technology.
- Full-persistence implementation.
- Package repository infrastructure.
- Detailed release and acceptance criteria.

These items should be resolved incrementally and documented when decisions are made.

### Decided

- **Debian release:** Debian **13 (trixie)** is the target base for v0.1. Debian 13 became the current stable release on 9 August 2025; version 13.7 was published on 12 September 2026. Debian 12 (bookworm) is now *oldstable* and is not used. The release is pinned in `config/oracle.conf` as `DEBIAN_RELEASE="13"` / `DEBIAN_CODENAME="trixie"`.
- **Build environment:** **rootful** Podman container running Debian 13, launched via `sudo podman`, using `--privileged` and `--userns=host` (see section 8).

### Container privilege — evaluated, not yet reduced

The current build runs `--privileged`. That is known to be a blunt instrument; the question is whether anything narrower works. Nothing below has been tested. They are ranked by how much they would reduce exposure, and each is a candidate for verification once Podman is available.

| Option | What it would change | Trade-off / why unverified |
|---|---|---|
| **Status quo:** `--privileged --userns=host`, rootful | Baseline | Works against the documented requirements, but disables all container confinement. |
| `--cap-add SYS_ADMIN --cap-add SYS_CHROOT --cap-drop ALL` (rootful, no `--privileged`) | Keeps the two capabilities the build plausibly needs, drops the rest | Whether `lb build` also needs `CAP_MKNOD` (device nodes in the chroot) or `CAP_DAC_OVERRIDE` is unknown. Community reports of building live images in containers consistently end up at `--privileged`. Would need a real build to confirm. |
| Rootless Podman with `--privileged` | No `sudo` needed | Documented as insufficient: rootless `--privileged` does not grant `CAP_SYS_ADMIN` to non-UID-0, and UID mapping blocks the kernel-filesystem mounts. Already tried conceptually and rejected; would need re-verification only if the mount strategy changes. |
| Rootless + `debootstrap --variant=fakechroot` | Avoids real `chroot`/mounts via `fakechroot` | `fakechroot` emulates `chroot` by `LD_PRELOAD`. It does not cover `mount` at all, which `lb build` needs for `/proc`, `/sys`, `/dev/pts`. Also changes the build toolchain in ways upstream does not support for live-build. |
| Pre-mounted host loop device passed into an unprivileged container | Bind-mount an already-mounted ISO/loop into the container | Requires the host to perform `losetup` + `mount` — i.e. the host gets *more* involvement, not less. Shifts privilege instead of removing it. |

**Recommendation:** run the privileged build inside a disposable Debian VM with no host disks attached. Once a baseline build works there, try the `--cap-add` variant inside that VM and compare. Do not treat a read-only project mount as protection from a compromised privileged builder.

## 15. Architecture Summary

ORACLE OS is a Debian-based, terminal-first personal cybersecurity lab with preinstalled core tools, modular security profiles, and ORACLE-specific tooling.

The first release prioritizes a reproducible build, successful QEMU boot, functional tool profiles, and isolated local-network testing.

Installation, full persistence, a dedicated package repository, visual customization, and advanced kernel research remain part of the longer-term direction.

**The immediate priority is a working, testable v0.1—not a complete distribution on day one.**
