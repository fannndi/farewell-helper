---
name: farewell-9router
description: Use when interacting with 9Router model gateway, configuring model combos, checking model health, or troubleshooting model/provider issues.
---

# Farewell 9Router Skill

## Provider Gateway
9Router is the model gateway at `:20128`. All LLM calls route through it.

## Combo Strategies
| Strategy | Behavior |
|----------|----------|
| fallback | Try first model, failover on error — cache-friendly |
| round-robin | Rotate models per request — cache-diverse |

## Model Tiers
| Combo | Use Case |
|-------|----------|
| FREE_Model | Research, planning, quick queries (free tier models) |
| Pro_Plan | Deep analysis, spec drafting, architecture |
| Execution_Paid | Complex implementation, bug fixing, code review |
| Execution_Free | Light step-by-step execution |

## Token Savers
| Feature | Savings | Effect |
|---------|---------|--------|
| RTK | 20-40% input | Compresses tool results |
| Headroom | ~15% input | Context window compression |
| Caveman | ~65% output | Ultra-terse AI responses |
