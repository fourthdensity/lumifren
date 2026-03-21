---
name: parallel-research
version: "1.0.0"
description: "Execute complex research tasks by spawning multiple subagents simultaneously, then synthesize converging insights for higher quality results. Ideal for emerging tech, market analysis, and multi-domain investigations."
---

# Parallel Research Skill

Execute complex research by spawning multiple subagents in parallel, then synthesize their findings for deeper insights and cross-validation.

## When to Use

- **Complex research questions** requiring multiple perspectives
- **Emerging tech analysis** where information is scattered
- **Market opportunity assessment** needing market + technical + legal angles
- **Intersection analysis** exploring how two domains converge
- **Fact-checking** through independent verification

## When NOT to Use

- Simple factual lookups (single web search sufficient)
- Time-critical tasks (parallel adds coordination overhead)
- Sequential dependencies (each step needs previous output)

## ⚠️ IMPORTANT: User Authorization Required

**Before spawning subagents, ALWAYS ask user for confirmation:**

> "I'll use the parallel-research skill to investigate [TOPIC] by spawning [N] subagents simultaneously. This will take ~4-6 minutes. Proceed?"

**Why:** Subagent spawning consumes API resources and requires user awareness of parallel execution.

## The Pattern

### 1. Define Scope
Create a clear research brief with:
- Specific questions to answer
- Areas to investigate (market, technical, legal, etc.)
- Deliverable format
- Success criteria

### 2. Spawn Subagents

Spawn 2-3 subagents with **identical or complementary prompts**:

```
sessions_spawn:
  task: "Research [TOPIC] focusing on [ANGLE]. 
         
         Key questions:
         1. [Question 1]
         2. [Question 2]
         
         Provide specific data, cite sources, avoid hype."
  label: "Research-[ANGLE]"
  thinking: "high"
```

**Example angles for emerging tech:**
- Subagent 1: Market sizing & competition
- Subagent 2: Technical feasibility & architecture  
- Subagent 3: Legal/regulatory landscape

### 3. Parallel Execution

- All subagents run simultaneously (4-5 min each)
- No coordination needed during execution
- Save results to workspace files

### 4. Synthesize Findings

Review all outputs for:
- **Convergence**: What do multiple agents agree on? (High confidence)
- **Divergence**: Where do they disagree? (Needs deeper investigation)
- **Gaps**: What did no one cover? (Missing angles)
- **Opportunities**: What emerges from the intersection?

### 5. Deliver Synthesis

Present executive summary with:
- Key findings (prioritized by confidence)
- Actionable insights
- Recommended next steps
- Links to full reports

## Benefits

| Benefit | Description |
|---------|-------------|
| **Multiple Perspectives** | Reduces blind spots from single viewpoint |
| **Cross-Validation** | Converging findings = higher confidence |
| **Speed** | Parallel execution faster than sequential deep dives |
| **Built-in Fact-Checking** | Independent verification catches errors |
| **Intersection Discovery** | Novel insights emerge from synthesis |

## Real Example: Voice NFTs × AI Payments

**Prompt (all 3 subagents):**
```
Research [DOMAIN] deeply. Focus on:
1. Market size and growth drivers
2. Existing players (what's working/failing)
3. Technical architecture
4. Legal/regulatory considerations
5. Real use cases (not hype)
6. Opportunities for builders

Provide specific data, cite sources. Save full report to workspace.
```

**Results:**
- All 3 converged: "Voice NFTs barely exist as category" (blue ocean confirmed)
- Market estimates aligned: $2-5B TAM by 2030
- Technical assessment + Market analysis = Convergence opportunity: Voice auth for AI payments

**Outcome:** 10x better insight than single-agent research.

## Prompt Templates

### Template A: Identical Prompts (for cross-validation)
```
Research [TOPIC] comprehensively. Cover:
- What is it? (clear definition)
- Market opportunity (size, growth, timing)
- Technical feasibility (what's possible now vs future)
- Existing solutions (who's building, what's working/failing)
- Challenges and risks
- Opportunities for [user context]

Be thorough. Use web_search, web_fetch. Cite sources.
Save full report to: research/[topic]-[timestamp].md
```

### Template B: Complementary Angles
**Subagent 1 (Market):**
```
Research [TOPIC] from MARKET perspective:
- TAM/SAM/SOM analysis
- Competition mapping
- Growth drivers and timing
- Investment/funding landscape
- Go-to-market strategies
```

**Subagent 2 (Technical):**
```
Research [TOPIC] from TECHNICAL perspective:
- Current state of the art
- Architecture patterns
- Implementation complexity
- Performance benchmarks
- Integration challenges
```

**Subagent 3 (Legal/Regulatory):**
```
Research [TOPIC] from LEGAL perspective:
- Regulatory status by jurisdiction
- Compliance requirements
- Liability frameworks
- Intellectual property considerations
- Emerging legislation
```

## Tool Usage

**Recommended tools for research subagents:**
- `web_search` - Current information, market data
- `web_fetch` - Deep dive into specific sources
- `read` - Analyze existing workspace files
- `write` - Save findings to structured reports

**NOT recommended:**
- `sessions_spawn` (avoid recursion)
- `browser` (unless specific site analysis needed)
- External API calls (adds latency)

## Output Format

Subagents should save structured reports:

```markdown
# [Topic] Research Report

## Executive Summary
2-3 sentences on key findings

## 1. [Section]
Detailed findings with data and citations

## 2. [Section]
...

## Sources
- [Title](URL) - Key insight
- [Title](URL) - Key insight

## Confidence Assessment
- High confidence: [findings with multiple sources]
- Medium confidence: [findings with limited sources]
- Speculative: [emerging trends, projections]
```

## Synthesis Template

After reviewing all subagent outputs:

```markdown
## Research Synthesis: [Topic]

### 🎯 Key Findings
What converged across all agents (highest confidence)

### 📊 Market Opportunity
Size, timing, positioning

### 🔧 Technical Reality
What's possible today vs 2-3 years

### 💡 Opportunities
Specific, actionable paths forward

### ⚠️ Challenges
Known blockers and risks

### 📄 Full Reports
- [Report 1](path)
- [Report 2](path)
- [Report 3](path)
```

## Performance Notes

- **Runtime**: 4-6 minutes total (parallel)
- **Cost**: ~40-80k tokens per subagent (3x single agent)
- **Quality**: Significantly higher due to cross-validation
- **Best for**: Complex, ambiguous, or emerging topics

## Variations

### Quick Validation (2 subagents)
For time-sensitive research:
- Spawn 2 agents with identical prompts
- Focus on convergence only
- Skip detailed synthesis

### Deep Investigation (3+ subagents)
For critical decisions:
- 3+ agents with complementary angles
- Include contradictory viewpoints intentionally
- Extended synthesis with decision matrix

### Intersection Analysis
For exploring domain convergence:
- Agent 1: Domain A deep dive
- Agent 2: Domain B deep dive  
- Agent 3: Explicit intersection analysis

## Common Pitfalls

❌ **Vague prompts** → Agents wander, low-quality output  
✅ **Specific questions** → Focused, actionable findings

❌ **Too many agents** → Diminishing returns, coordination overhead  
✅ **2-3 agents optimal** → Good coverage, manageable synthesis

❌ **Ignoring divergence** → Miss important nuances  
✅ **Highlight disagreements** → Indicates uncertainty or opportunity

## Integration with Self-Improvement

After using this skill:
1. Log workflow effectiveness to `.learnings/LEARNINGS.md`
2. Note which angles produced most value
3. Refine templates based on results
4. Promote proven patterns to `AGENTS.md`

## Example Session

```
User: "Research Voice NFTs and AI Agent Payments"

Action:
1. Spawn subagent: "Research Voice NFTs" → 4 min
2. Spawn subagent: "Research AI Agent Payments" → 4 min  
3. Spawn subagent: "Research voice authorization" → 4 min
4. All complete simultaneously
5. Synthesize convergence findings
6. Identify intersection opportunity

Result: Voice NFT signatures for AI payment authorization
```

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-17  
**Tested On**: Voice NFTs, AI Agent Payments, Voice Authorization research
