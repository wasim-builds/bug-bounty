# Bug Bounty Program Updates — August 2026

## Major Platform Changes

### GitHub (July 27, 2026)
**Status: RESTRUCTURED**
- Public payouts: $250 Low / $2,000 Medium / $5,000 High / $10,000 Critical
- VIP invite-only: $1,000 / $7,500 / $20,000 / $30,000+
- HackerOne signal requirement: max 4 initial submissions for new researchers
- AI-generated reports explicitly targeted; require human validation
- Reports before July 27 grandfathered under old rates

### HackerOne Internet Bug Bounty (August 2026)
**Status: PAUSED / REWARDS SLASHED**
- Program paused citing "maximize value"
- Critical bugs: $9,250 → $2,257 (75% drop)
- Medium severity: $1,843 → $297
- Attributed to AI-generated report flood
- Open-source ecosystem affected

## AI / Model Safety Programs

| Program | Status | Payout | Platform | Notes |
|---------|--------|--------|----------|-------|
| OpenAI Safety Bug Bounty | Active | Up to $100K | Bugcrowd | Prompt injection, agentic manipulation, MCP abuse |
| OpenAI Bio Bounty | Active | Up to $50K | Private | Universal jailbreaks against GPT-5.5/5.6 biosafety |
| Anthropic Model Safety | Active | Up to $35K | HackerOne | Universal jailbreaks, Constitutional Classifier bypass |
| Anthropic Product Security | Active | Up to $15K | HackerOne | Claude Code sandbox escape, unauthorized tool execution |
| IBM Granite AI Guardrails | Invite-only | Up to $100K | HackerOne | Jailbreaks against Granite Guardian |
| Google AI VRP | Active | Up to $31.3K | bughunters.google.com | EXCLUDES prompt injection/jailbreaks; focus on data exfiltration |
| Microsoft Copilot / AI | Active | Up to $30K | MSRC | Copilot indirect injection, privilege escalation, MCP servers |
| Meta GenAI | Active | Up to $130K | Meta Bug Bounty | Prompt injection, invisible formatting, agentic tool abuse |
| Mozilla 0din | Active | $500-$15K | 0din.ai | Open submissions, prompt injection, jailbreaks, training data leakage |
| xAI / Grok | Active | Tiers | HackerOne/email | Prompt injection, data access, auth flaws |
| Gray Swan Arena | Active | Competitions | grayswan.ai | Prize pools $40K-$300K+, wave-based challenges |

## Web / Traditional Programs

| Program | Status | Payout | Platform | Recent Changes |
|---------|--------|--------|----------|----------------|
| Microsoft Hyper-V | Active | Up to $250K | MSRC | Updated April 2026 |
| Microsoft Identity | Active | Up to $100K | MSRC | Steady |
| Microsoft Zero Day Quest | Event | Up to $250K | MSRC | Flash challenges Feb-Mar 2026 |
| Agoda | Public | Up to $6K | HackerOne | Launched June 2026, 100% triage |
| Zendesk | Public | Up to $50K | Bugcrowd | Launched May 2026, scope updated May 31 |
| GitHub | Restructured | $250-$10K public | HackerOne | July 2026 changes |
| Shopify | Active | Up to $10K | HackerOne | Steady |
| Slack | Active | Up to $5K | HackerOne | Steady |
| Google VRP | Active | Up to $31.3K | bughunters.google.com | Steady |
| Apple Security Bounty | Active | Up to $2M | Apple | Raised Oct 2025, PCC added |
| HPE Networking | Public | Tiers | Bugcrowd | New |
| CMS (Medicare/Medicaid) | Public | Tiers | Bugcrowd | New 2026 |

## Crypto / Web3 Programs

| Program | Payout | Platform | Status |
|---------|--------|----------|--------|
| Polymarket | Up to $5M | Cantina | Active |
| Usual | Up to $16M | Sherlock | Active |
| Loopscale | Up to $250K | Direct | Active |
| Exactly Protocol | Up to $500K | Sherlock | Active |
| Cronos | Up to $250K | Immunefi/Cantina | Active |
| Aave V4 | Proposed $500K | TBD | Proposed |

## Key Trends for August 2026

1. **AI safety dominates** — Every major lab runs a dedicated program; payouts $500-$100K
2. **Prompt injection only pays when chained** — standalone jailbreaks increasingly out of scope
3. **GitHub tightened access** — signal requirement + lower public payouts; VIP is the real money
4. **HackerOne IBB slashed** — open-source bounties down 75%; pause indefinite
5. **Human validation required everywhere** — AI-assisted research accepted but must be human-verified
6. **Indirect prompt injection = highest AI payout** — when chained to data exfiltration/SSRF
7. **Web3 bounties massive but niche** — require blockchain/Solidity expertise
8. **Apple at $2M** — top of the market for hardware/software exploits

## Recommended Targets for Beginners

| Priority | Program | Why | Expected Payout |
|----------|---------|-----|-----------------|
| 1 | Agoda | Public, simple scope, fast triage | $500-$3,000 |
| 2 | Zendesk | Public, up to $50K, fresh program | $500-$5,000 |
| 3 | Meta GenAI | $130K max, AI-specific | $500-$5,000 |
| 4 | Mozilla 0din | Open submissions, AI-focused | $500-$15,000 |
| 5 | Microsoft Copilot | Up to $30K, enterprise AI | $500-$5,000 |

## Action Items

1. **This week**: Target Agoda or Zendesk for first real report
2. **Build AI skills**: Practice prompt injection, indirect injection, tool abuse
3. **Build HackerOne signal**: Submit valid reports to any public program
4. **Aim for GitHub VIP**: Need 1 critical or 2 high findings to qualify
5. **Avoid**: Google AI VRP for prompt injection (explicitly excluded)
