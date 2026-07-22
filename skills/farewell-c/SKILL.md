---
name: farewell-c
description: Use when writing, reviewing, or debugging C code — kernel or userspace memory safety, concurrency, error handling, and kernel build conventions. Credits: adapted from ECC by affaan-m cpp-standards + Linux kernel coding-style.
---

# C + Kernel Patterns

## Memory Safety

Every `malloc`/`kmalloc` has a visible `free`/`kfree` — same function or paired init/exit. Check returns: no allocation success assumed. `kzalloc` over `kmalloc`+`memset`. `goto` for single-exit cleanup is idiomatic kernel C — labels in reverse alloc order.

## Concurrency

Identify shared data first — only lock what crosses IRQ/tasklet/workqueue/thread boundaries. `spin_lock` for IRQ context, `mutex_lock` for sleepable. Document lock ordering. RCU for read-heavy/write-rare paths.

## Error Handling

Return `-Exxx` codes in kernel: `-ENOMEM`, `-EINVAL`, `-ENODEV`. Never `-1`. `IS_ERR()`/`PTR_ERR()` for pointer-or-error returns. `WARN_ON()` for "should never happen" — leaves system running. `BUG_ON()` only for unrecoverable corruption.

## Kernel Style

Tabs (8-char) for indentation, not spaces. 80 columns. `if (err) return err;` — no braces for single-statement. Functions: `subsystem_verb_object()`. No `typedef` for kernel structs.

## Build & Device Tree

Kbuild: `obj-y` for always-built, `obj-$(CONFIG_FEATURE)` for conditional. Kconfig documents depends. Device tree: `compatible` strings snake_case. Always add `of_match_table` alongside platform driver. Test boot with `fastboot boot Image.gz-dtb` for quick iteration.
