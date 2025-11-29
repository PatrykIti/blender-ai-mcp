# Router Architecture & Code Template
# (for blender-ai-mcp)

This file contains:
- router directory structure,
- code skeleton,
- base classes,
- implementation template.

Note: everything is offline and does not require LLM.


============================================================
# 1. DIRECTORY STRUCTURE
============================================================

router/
├── __init__.py
├── router.py
├── metadata_loader.py
├── classifier.py
├── embeddings.py
├── planner.py
├── utils.py
├── tools_metadata.json
└── models/
    └── (optionally) embedding_model/


============================================================
# 2. FILE: tools_metadata.json (template)
============================================================

[
  {
    "name": "mesh_extrude",
    "category": "mesh",
    "keywords": ["extrude", "pull", "extend", "face", "depth"],
    "description": "Extrudes selected mesh elements.",
    "sample_prompts": [
      "extrude face",
      "pull the face outward",
      "extrude the face geometry"
    ]
  },
  {
    "name": "modeling_add_cube",
    "category": "modeling",
    "keywords": ["cube", "box", "primitive", "create cube"],
    "description": "Adds a cube primitive.",
    "sample_prompts": [
      "add cube",
      "create a cube",
      "create a box"
    ]
  }
]


============================================================
# 3. FILE: metadata_loader.py
============================================================

import json
from pathlib import Path

class ToolMetadata:
    def __init__(self, data):
        self.name = data["name"]
        self.category = data["category"]
        self.keywords = data.get("keywords", [])
        self.description = data.get("description", "")
        self.sample_prompts = data.get("sample_prompts", [])

class MetadataLoader:
    def __init__(self, path="tools_metadata.json"):
        self.path = Path(path)
        self.tools = []

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.tools = [ToolMetadata(item) for item in data]
        return self.tools

    def find_tool_by_name(self, name):
        for t in self.tools:
            if t.name == name:
                return t
        return None


============================================================
# 4. FILE: classifier.py (TF-IDF + SVM / LR)
============================================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

class IntentClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.labels = []

    def train(self, metadata):
        """
        metadata = list of ToolMetadata
        """
        corpus = []
        labels = []

        for tool in metadata:
            for prompt in tool.sample_prompts:
                corpus.append(prompt)
                labels.append(tool.name)

        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(corpus)

        self.model = LogisticRegression(max_iter=200)
        self.model.fit(X, labels)

        self.labels = labels

    def predict(self, text):
        if not self.model:
            raise RuntimeError("Classifier not trained.")
        vec = self.vectorizer.transform([text])
        return self.model.predict(vec)[0]


============================================================
# 5. FILE: embeddings.py (optional, offline)
============================================================

import numpy as np

class EmbeddingStore:
    def __init__(self):
        self.model = None  # load sentence-transformers model here
        self.index = []    # list of (tool_name, embedding_vector)

    def load_model(self):
        # lazy load
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def build_index(self, metadata):
        self.load_model()
        for tool in metadata:
            # combine sample_prompts into one description
            text = tool.description + " " + " ".join(tool.sample_prompts)
            emb = self.model.encode(text)
            self.index.append((tool.name, emb))

    def most_similar(self, text, top_k=1):
        if not self.model:
            self.load_model()

        query = self.model.encode(text)
        best = None
        best_score = -1

        for name, emb in self.index:
            score = np.dot(query, emb) / (np.linalg.norm(query)*np.linalg.norm(emb))
            if score > best_score:
                best_score = score
                best = name

        return best, best_score


============================================================
# 6. FILE: planner.py (workflow engine)
============================================================

class Planner:
    """
    Maps intent → sequence of tools.
    """

    def __init__(self):
        self.workflows = {
            "create_phone": [
                "modeling_add_cube",
                "transform_scale",
                "mesh_bevel",
                "mesh_inset",
                "mesh_extrude",
                "material_assign"
            ]
        }

    def get_workflow(self, intent):
        return self.workflows.get(intent, None)


============================================================
# 7. FILE: utils.py
============================================================

import re

def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    return text


============================================================
# 8. FILE: router.py (MAIN ROUTER)
============================================================

from metadata_loader import MetadataLoader
from classifier import IntentClassifier
from embeddings import EmbeddingStore
from planner import Planner
from utils import clean_text

class Router:
    def __init__(self):
        self.metadata_loader = MetadataLoader()
        self.tools = self.metadata_loader.load()

        self.classifier = IntentClassifier()
        self.classifier.train(self.tools)

        self.embeddings = EmbeddingStore()
        self.embeddings.build_index(self.tools)

        self.planner = Planner()

    def route(self, prompt: str):
        text = clean_text(prompt)

        # 1) classifier (primary matching)
        try:
            intent_or_tool = self.classifier.predict(text)
        except:
            intent_or_tool = None

        # 2) if classifier weak → fallback to embeddings
        emb_tool, score = self.embeddings.most_similar(text)
        if score > 0.40:  # threshold to adjust
            final_tool = emb_tool
        else:
            final_tool = intent_or_tool or emb_tool

        # 3) check if it's a workflow
        workflow = self.planner.get_workflow(final_tool)
        if workflow:
            return workflow

        # 4) normal tool
        return [final_tool]


============================================================
# 9. USAGE EXAMPLE (in MCP server)
============================================================

router = Router()

prompt = "create a phone with rounded edges"
tools_to_run = router.route(prompt)

print("Tools to execute:", tools_to_run)


============================================================
# END
============================================================
