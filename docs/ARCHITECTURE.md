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

- Exact Debian release and image configuration.
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

## 15. Architecture Summary

ORACLE OS is a Debian-based, terminal-first personal cybersecurity lab with preinstalled core tools, modular security profiles, and ORACLE-specific tooling.

The first release prioritizes a reproducible build, successful QEMU boot, functional tool profiles, and isolated local-network testing.

Installation, full persistence, a dedicated package repository, visual customization, and advanced kernel research remain part of the longer-term direction.

**The immediate priority is a working, testable v0.1—not a complete distribution on day one.**
