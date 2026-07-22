"""Tests for the PawPal AI multi-source retriever."""

import pytest

from pawpal_ai.retriever import MultiSourceRetriever


@pytest.fixture
def retriever() -> MultiSourceRetriever:
    """Create a retriever using the project knowledge base."""
    return MultiSourceRetriever()


def test_loads_all_four_knowledge_sources(retriever):
    assert len(retriever.documents) == 4

    document_ids = {
        document.document_id for document in retriever.documents
    }

    assert document_ids == {
        "general-daily-care",
        "general-medication-safety",
        "general-scheduling-guidelines",
        "pet-max-care-notes",
    }


def test_max_query_ranks_pet_specific_notes_first(retriever):
    results = retriever.retrieve(
        query="Schedule Max's morning walk safely",
        pet_name="Max",
    )

    assert results
    assert results[0].document_id == "pet-max-care-notes"
    assert results[0].category == "pet_specific"


def test_medication_query_retrieves_safety_guidance(retriever):
    results = retriever.retrieve(
        query="medication dosage veterinarian instructions safety",
    )

    document_ids = {result.document_id for result in results}

    assert "general-medication-safety" in document_ids


def test_results_use_distinct_documents(retriever):
    results = retriever.retrieve(
        query="daily care schedule safety instructions",
        top_k=4,
    )

    document_ids = [result.document_id for result in results]

    assert len(document_ids) == len(set(document_ids))


def test_top_k_limits_number_of_results(retriever):
    results = retriever.retrieve(
        query="care schedule safety",
        top_k=2,
    )

    assert len(results) <= 2


def test_unrelated_query_returns_no_evidence(retriever):
    results = retriever.retrieve(
        query="quantum spaceship calculus",
    )

    assert results == []


def test_empty_query_is_rejected(retriever):
    with pytest.raises(
        ValueError,
        match="A retrieval query is required",
    ):
        retriever.retrieve("")


def test_invalid_top_k_is_rejected(retriever):
    with pytest.raises(
        ValueError,
        match="top_k must be at least 1",
    ):
        retriever.retrieve("pet care", top_k=0)


def test_formatted_context_contains_source_details(retriever):
    results = retriever.retrieve(
        query="Max morning walk",
        pet_name="Max",
    )

    context = retriever.format_context(results)

    assert "[Source 1]" in context
    assert "Document ID:" in context
    assert "Relevance score:" in context
    assert "pet-max-care-notes" in context