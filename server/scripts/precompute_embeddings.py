"""
Pre-compute tool embeddings for Docker image build.

This script runs during Docker build to pre-populate the LanceDB
vector store with tool embeddings, avoiding ~30s computation on every start.

TASK-047: LanceDB Migration
"""

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main():
    """Pre-compute and store tool embeddings."""
    logger.info("Pre-computing tool embeddings for Docker image...")

    # Import after logging setup
    from server.router.application.classifier.intent_classifier import IntentClassifier
    from server.router.infrastructure.config import RouterConfig
    from server.router.infrastructure.metadata_loader import MetadataLoader

    # Create classifier with default config
    config = RouterConfig()
    classifier = IntentClassifier(config=config)

    # Load tool metadata and compute embeddings
    loader = MetadataLoader()
    metadata = loader.load_all()

    # Convert ToolMetadata objects to dicts for classifier
    metadata_dicts = {name: tool.to_dict() for name, tool in metadata.items()}

    logger.info(f"Found {len(metadata_dicts)} tools to embed")

    # This will compute embeddings and store in LanceDB
    classifier.load_tool_embeddings(metadata_dicts)

    # Verify
    info = classifier.get_model_info()
    logger.info(f"Stored {info.get('num_tools', 0)} tool embeddings in LanceDB")

    # Also pre-compute workflow embeddings
    logger.info("Pre-computing workflow embeddings...")

    from server.router.application.workflows.registry import get_workflow_registry

    registry = get_workflow_registry()
    registry.ensure_custom_loaded()

    workflows = {}
    for name in registry.get_all_workflows():
        workflow = registry.get_workflow(name)
        if workflow:
            workflows[name] = workflow
        else:
            definition = registry.get_definition(name)
            if definition:
                workflows[name] = definition

    if workflows:
        from server.router.application.classifier.workflow_intent_classifier import (
            WorkflowIntentClassifier,
        )

        workflow_classifier = WorkflowIntentClassifier(config=config)
        workflow_classifier.load_workflow_embeddings(workflows)

        wf_info = workflow_classifier.get_info()
        logger.info(
            f"Stored {wf_info.get('num_workflows', 0)} workflow embeddings in LanceDB"
        )
    else:
        logger.info("No workflows found to embed")

    logger.info("Pre-computation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
