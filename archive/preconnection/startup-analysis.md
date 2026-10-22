# Historical blocked startup notes — superseded by live reports

## Status: BLOCKED

Current HOME handler, boot receivers, boot duration, logs, wake locks, ignition
integration and standby configuration are unknown.

## Passive inventory after connection

- Resolve the current HOME handler and enumerate HOME/LAUNCHER activities using
  commands supported by the detected Android release; retain raw package dumps
  where newer package-query commands are unavailable.
- Read uptime, boot-completed properties, boot timing where available, and
  bounded existing log buffers. Do not clear logcat or trigger a new boot.
- Inspect BOOT_COMPLETED and LOCKED_BOOT_COMPLETED receivers, persistent
  applications, running/bound services and vendor init definitions if readable.
- Inspect power/idle diagnostics, relevant settings and vendor properties for
  ACC shutdown, sleep and wake behavior. Do not change settings or CANbus data.
- Map native MCU/audio services as well as APK dependencies. A package-only
  analysis cannot establish the complete startup chain.

## Later measurement proposal

After approval, compare at least three cold starts and three ACC resumes under
consistent conditions. Record time to interactive HOME, available audio/radio,
Bluetooth readiness and any camera/vehicle-control regression. MCU resume and
Android cold boot are different events and must not be pooled. No timed boot or
ACC tests have been performed.

## Minimal native launcher — design deferred, not implemented

Select build compatibility only after reading the actual SDK level and ABI.
Prefer a single native Activity with simple platform views and a small local
configuration store, without WebView, a persistent background service, polling,
animations or third-party SDKs. Avoid permissions not required by its features.

Provide explicit shortcuts to verified installed activities, including the
original radio UI and factory launcher. Keep the factory launcher installed and
enabled; verify a host-side HOME recovery path before considering default-HOME
selection. The radio shortcut is not proof of direct tuning/control support.

API-specific package visibility, manifest requirements and HOME-selection APIs
must be checked against the detected release before producing implementation
code. No APK installation or default-HOME change is authorised by this plan.
