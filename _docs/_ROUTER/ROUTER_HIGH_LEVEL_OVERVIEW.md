# Router / Intent-Matching / Embedding-based Layer for blender-ai-mcp

## Goal

- Have a layer that, based on a text prompt, selects the appropriate tool or sequence of tools.
- Work offline, without the need for an external LLM.
- Be scalable — easily add new tools.
- (Optionally) Learn from prompt experience.
- Offer stable and deterministic routing.

------------------------------------------------------------

## System Structure / Components

User prompt (string)
        │
        ▼
[ Router / Intent-Matcher ]
        │  (intent / embedding / rule)
        ▼
[ Tool Resolver / Planner ]
        │ — mapping intent → tool / sequence
        ▼
[ MCP Server ] (tool invocation)
        │
        ▼
[ Blender (bpy) ] — operation execution
        │
        ▼
[ Result / Feedback ]
        └─ optionally: user feedback → to logs / training data

Components:
- Metadata for all tools
- Intent-Matcher / Classifier
- Fallback logic (fuzzy/regex)
- Planner / Sequencer
- Feedback / Learning module
- Optional vector store + embeddings

------------------------------------------------------------

## Metadata (tools definition)

File: tools_metadata.json

Example:

[
  {
    "name": "mesh_extrude",
    "category": "mesh",
    "keywords": ["extrude", "pull", "push", "face", "extend", "depth"],
    "description": "Extrudes selected mesh elements along normals.",
    "sample_prompts": [
      "extrude face by 0.2",
      "extend the face downward",
      "pull the top face outwards"
    ]
  },
  {
    "name": "modeling_add_cube",
    "category": "modeling",
    "keywords": ["add cube", "create cube", "new box", "primitive cube"],
    "description": "Creates a new cube mesh primitive.",
    "sample_prompts": [
      "create a 2x2x2 cube",
      "add a cube",
      "now add box"
    ]
  }
]

------------------------------------------------------------

## Router / Intent-Matcher Implementation Options

--------------------------------
### 1) Rules + classifier (TF-IDF, SVM, LogisticRegression)

Libraries:
- scikit-learn
- regex
- rapidfuzz

Flow:
- prompt → normalization
- tf-idf → vector
- classifier → label (e.g., "extrude_mesh")
- mapping label → tool

Pros: fast, offline, deterministic
Cons: sensitive to keywords

--------------------------------
### 2) Embedding + vector lookup (FAISS)

Libraries:
- sentence-transformers
- faiss

Flow:
- prompt → embedding
- embedding → comparison to sample_prompts/tool embeddings
- closest tool, if distance < threshold

Pros: generalizes semantics better
Cons: depends on embedding quality

------------------------------------------------------------

## Embedding Models (small, high quality)

1) all-MiniLM-L6-v2
- lightweight, 22M parameters
- 384D embedding
- very fast on CPU

2) intfloat/e5-base-v2
- ~110M parameters
- 768D embedding
- better quality, better semantic matching

3) BAAI/bge-base-en-v1.5
- very good for retrieval
- ~110M parameters

Recommendation:
- Start: all-MiniLM-L6-v2 (lightest)
- Later: e5-base-v2 or bge-base-en-v1.5

------------------------------------------------------------

## Planner / Sequencer (workflow)

You can define workflows in YAML:

intents:
  create_phone:
    - modeling_add_cube
    - transform_scale
    - mesh_bevel
    - mesh_inset
    - mesh_extrude
    - material_assign

Example: prompt "make a phone" → intent "create_phone" → above sequence of tools.

------------------------------------------------------------

## Learning / Feedback

Mechanism:
- After each invocation, save: prompt, tool used, result, optionally user feedback.
- Store data in JSON file or SQLite.
- Every X executed prompts: retrain classifier or rebuild embedding index.

Possible training types:
- Adding new prompt→tool examples
- Hard negatives (incorrect matching cases)
- User correction (if user corrects tool)

------------------------------------------------------------

## Step-by-Step Implementation

1. Prepare tools_metadata.json with full description of 80 tools.
2. Implement Intent-Matcher:
   - Simple version: TF-IDF + SVM (easiest)
   - Advanced: embedding + FAISS
3. Implement Tool Resolver / Planner.
4. Create route(prompt) → list(tool_calls) function.
5. Add logging and feedback-learning mechanism.
6. Create tests for router (unit + integration).
7. (Optionally) Add fallback chain:
   - regex → fuzzy → classifier → embeddings

------------------------------------------------------------

## Router Architecture (text diagram)

prompt
  ↓
preprocess text → normalize, tokenize
  ↓
intent-matcher (classifier + embeddings + fuzzy)
  ↓
intent
  ↓
tool resolver (metadata + mapping)
  ↓
workflow (list of tools)
  ↓
MCP server
  ↓
Blender API
  ↓
result

------------------------------------------------------------

## Recommended Plan

PHASE 1 – create 80 tools
PHASE 2 – prepare tools_metadata.json
PHASE 3 – add Intent-Matcher (TF-IDF → easy and stable)
PHASE 4 – add embeddings (optional, for better quality)
PHASE 5 – add Planner / Sequencer
PHASE 6 – add feedback-learning
PHASE 7 – fine-tune thresholds, tests and fallback logic

------------------------------------------------------------

## Summary

Router, Intent-Matcher and Embedding Engine will allow:
- handling full prompt → tool 100% offline,
- minimizing hallucinations,
- increasing reliability,
- bringing higher quality MCP tool usage for Blender,
- introducing "AI-like behavior" without using LLM models.
