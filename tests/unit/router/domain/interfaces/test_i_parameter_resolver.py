"""
Unit tests for Parameter Resolution Interfaces.

Tests that interfaces are properly defined as ABCs and cannot be
instantiated directly.

TASK-055-0
"""

import pytest
from abc import ABC

from server.router.domain.interfaces.i_parameter_resolver import (
    IParameterStore,
    IParameterResolver,
)
from server.router.domain.entities.parameter import (
    ParameterSchema,
    StoredMapping,
    ParameterResolutionResult,
)


class TestIParameterStoreInterface:
    """Tests for IParameterStore interface definition."""

    def test_is_abstract_base_class(self):
        """Test that IParameterStore is an ABC."""
        assert issubclass(IParameterStore, ABC)

    def test_cannot_instantiate_directly(self):
        """Test that IParameterStore cannot be instantiated."""
        with pytest.raises(TypeError, match="abstract"):
            IParameterStore()

    def test_has_required_abstract_methods(self):
        """Test that interface defines all required methods."""
        abstract_methods = IParameterStore.__abstractmethods__

        assert "find_mapping" in abstract_methods
        assert "store_mapping" in abstract_methods
        assert "increment_usage" in abstract_methods
        assert "list_mappings" in abstract_methods
        assert "delete_mapping" in abstract_methods

    def test_concrete_implementation_must_implement_all_methods(self):
        """Test that concrete class must implement all abstract methods."""

        # Incomplete implementation - missing some methods
        class IncompleteStore(IParameterStore):
            def find_mapping(self, prompt, parameter_name, workflow_name, similarity_threshold=0.85):
                return None

        with pytest.raises(TypeError, match="abstract"):
            IncompleteStore()

    def test_complete_implementation_can_be_instantiated(self):
        """Test that complete implementation can be instantiated."""

        class CompleteStore(IParameterStore):
            def find_mapping(self, prompt, parameter_name, workflow_name, similarity_threshold=0.85):
                return None

            def store_mapping(self, context, parameter_name, value, workflow_name):
                pass

            def increment_usage(self, mapping):
                pass

            def list_mappings(self, workflow_name=None, parameter_name=None):
                return []

            def delete_mapping(self, context, parameter_name, workflow_name):
                return False

        # Should not raise
        store = CompleteStore()
        assert store is not None


class TestIParameterResolverInterface:
    """Tests for IParameterResolver interface definition."""

    def test_is_abstract_base_class(self):
        """Test that IParameterResolver is an ABC."""
        assert issubclass(IParameterResolver, ABC)

    def test_cannot_instantiate_directly(self):
        """Test that IParameterResolver cannot be instantiated."""
        with pytest.raises(TypeError, match="abstract"):
            IParameterResolver()

    def test_has_required_abstract_methods(self):
        """Test that interface defines all required methods."""
        abstract_methods = IParameterResolver.__abstractmethods__

        assert "resolve" in abstract_methods
        assert "calculate_relevance" in abstract_methods
        assert "extract_context" in abstract_methods

    def test_incomplete_implementation_raises_error(self):
        """Test that incomplete implementation raises TypeError."""

        class IncompleteResolver(IParameterResolver):
            def resolve(self, prompt, workflow_name, parameters, existing_modifiers):
                return ParameterResolutionResult()

        with pytest.raises(TypeError, match="abstract"):
            IncompleteResolver()

    def test_complete_implementation_can_be_instantiated(self):
        """Test that complete implementation can be instantiated."""

        class CompleteResolver(IParameterResolver):
            def resolve(self, prompt, workflow_name, parameters, existing_modifiers):
                return ParameterResolutionResult()

            def calculate_relevance(self, prompt, schema):
                return 0.5

            def extract_context(self, prompt, schema):
                return prompt

        # Should not raise
        resolver = CompleteResolver()
        assert resolver is not None


class TestInterfaceImports:
    """Tests for interface imports from package."""

    def test_imports_from_interfaces_package(self):
        """Test that interfaces can be imported from package."""
        from server.router.domain.interfaces import (
            IParameterStore,
            IParameterResolver,
        )

        assert IParameterStore is not None
        assert IParameterResolver is not None

    def test_imports_from_entities_package(self):
        """Test that entities can be imported from package."""
        from server.router.domain.entities import (
            ParameterSchema,
            StoredMapping,
            UnresolvedParameter,
            ParameterResolutionResult,
        )

        assert ParameterSchema is not None
        assert StoredMapping is not None
        assert UnresolvedParameter is not None
        assert ParameterResolutionResult is not None
