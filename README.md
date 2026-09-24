# ArchAgent — Architecture Decision Agent

ArchAgent is an AI agent that helps software engineers and architects research, evaluate, and document software architecture decisions.

Unlike a traditional chatbot or fixed RAG pipeline, ArchAgent can decide which tools it needs, perform multiple research steps, recover when a tool fails, maintain conversational context, and require human approval before performing write actions.

## Problem

Software architecture decisions often require engineers to:

* Search internal architecture documentation
* Research current external technologies and vendor guidance
* Compare multiple architecture approaches
* Evaluate tradeoffs and risks
* Document the final decision in an Architecture Decision Record (ADR)

This process is often manual and requires switching between multiple sources.

ArchAgent brings these steps into an agent-driven workflow.

## Solution

A user describes an architecture problem or system requirement.

ArchAgent determines what information it needs and can autonomously use internal architecture knowledge, external web research, or both.

It then analyzes the evidence and produces a grounded architecture recommendation including requirements, options, tradeoffs, risks, and sources.

When the user decides to save the architecture decision, ArchAgent generates an ADR. Because saving an ADR is a write operation, execution requires explicit human approval.

## How It Works

```text
User Requirement
       |
       v
   ArchAgent
       |
       v
     Reason
       |
       v
 Decide which tools are needed
    /             \
   v               v
Internal         Web Search
Knowledge
   \               /
    \             /
       v
     Reason
       |
       v
Compare Architecture Options
       |
       v
Architecture Recommendation
       |
       v
User requests ADR
       |
       v
    save_adr
       |
       v
 Human Approval
       |
       v
   ADR Saved
```

The sequence is not a fixed pipeline. ArchAgent decides which tools to use based on the user's request and the information available.

## Agent Tools

### 1. Architecture Knowledge

`architecture_knowledge`

Searches an internal architecture knowledge base stored in Pinecone.

The tool:

1. Converts the architecture query into an embedding using OpenAI `text-embedding-3-small`
2. Searches Pinecone for semantically relevant documentation
3. Returns the top matching architecture knowledge chunks to the agent

This is a read-only tool and can execute autonomously.

### 2. Web Search

`web_search`

Uses Mastra's web search capability when current, external, vendor-specific, or additional information is required.

ArchAgent can decide to use web search after consulting internal documentation or use it directly when the request requires current external information.

This is also a read-only operation.

### 3. Save ADR

`save_adr`

Creates an Architecture Decision Record as a Markdown file under the `adrs/` directory.

Because this modifies the system, the tool is configured with:

```typescript
requireApproval: true
```

Mastra suspends execution until the user explicitly approves or declines the operation.

## Human-in-the-Loop

ArchAgent distinguishes between read and write operations.

```text
Internal Knowledge Search → Autonomous
Web Search                → Autonomous
Save ADR                  → Human Approval Required
```

The approval requirement is enforced by the tool configuration rather than relying only on instructions to the language model.

If the user declines the operation, the ADR is not written.

## Failure Handling

ArchAgent is designed to recover when a research source is unavailable.

For example:

```text
Architecture Knowledge
        |
        X
   Tool Failure
        |
        v
 Agent observes failure
        |
        v
    Web Search
        |
        v
Architecture Recommendation
```

During testing, the internal architecture knowledge tool was intentionally made to throw an error.

ArchAgent detected the failure, continued reasoning, selected web search as an alternative research source, and completed the architecture recommendation rather than terminating the workflow.

## Memory

ArchAgent uses Mastra memory to preserve conversational context.

This allows follow-up requests such as:

```text
"This looks good. Save this architecture decision as an ADR."
```

The agent can understand which previously discussed architecture decision the user is referring to without requiring the complete decision to be provided again.

## Tech Stack

* TypeScript
* Mastra
* OpenAI
* Pinecone
* OpenAI Embeddings
* Mastra Web Search
* Zod
* Node.js

## Architecture Knowledge Base

ArchAgent builds on the architecture knowledge base created for the earlier ArchRAG project.

Architecture documentation is:

```text
Documentation
     |
     v
Text Chunking
     |
     v
OpenAI Embeddings
     |
     v
Pinecone
```

At query time, the `architecture_knowledge` tool performs semantic retrieval and returns relevant evidence to ArchAgent.

## From ArchRAG to ArchAgent

ArchAgent evolved from a traditional RAG application built in Week 2.

### Week 2 — ArchRAG

ArchRAG used a fixed application-controlled pipeline:

```text
Question
   |
   v
Embedding
   |
   v
Pinecone Search
   |
   v
Retrieved Context
   |
   v
LLM
   |
   v
Answer
```

The application determined the sequence.

### Week 3 — ArchAgent

ArchAgent changes the control model:

```text
Goal
 |
 v
Agent Reasons
 |
 v
Chooses Tool
 |
 v
Observes Result
 |
 v
Reasons Again
 |
 v
May Choose Another Tool
 |
 v
Recommendation
 |
 v
Human-approved Action
```

The important difference is that the agent determines its next step based on the goal and observations rather than following a predefined retrieval pipeline.

## Example

Example architecture question:

```text
We are considering Apache Kafka versus AWS EventBridge for an
event-driven order processing platform. Compare them using our
internal architecture guidance and current external information.
```

During testing, ArchAgent:

1. Queried the internal architecture knowledge base.
2. Evaluated the retrieved information.
3. Performed external web research.
4. Performed additional web research when needed.
5. Compared Kafka and AWS EventBridge.
6. Produced an architecture recommendation.

The user then requested:

```text
Save this architecture decision as an ADR titled
"Kafka vs AWS EventBridge for Order Processing".
```

ArchAgent generated the ADR and attempted to invoke `save_adr`.

Mastra suspended the write operation and presented the user with **Approve** and **Decline** controls.

After approval, the ADR was written to:

```text
adrs/kafka-vs-aws-eventbridge-for-order-processing.md
```

## Setup

Clone the repository and install dependencies:

```bash
npm install
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

The `.env` file should not be committed to source control.

The project expects a Pinecone index named:

```text
archrag
```

containing architecture documentation embeddings compatible with:

```text
openai/text-embedding-3-small
```

Start the development environment:

```bash
npm run dev
```

Open Mastra Studio and select **ArchAgent**.

## Key Learnings

Building ArchAgent demonstrated several differences between a RAG application and an agentic system.

**RAG retrieves; an agent decides.**

In ArchRAG, the application controlled when retrieval happened. In ArchAgent, retrieval became one capability available to the agent.

**Tools should perform focused actions.**

The architecture knowledge tool retrieves evidence. I
