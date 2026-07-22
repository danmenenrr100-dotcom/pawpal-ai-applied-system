"""Local multi-source retrieval for PawPal AI."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_KNOWLEDGE_BASE = (
    Path(__file__).resolve().parent.parent / "knowledge_base"
)

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "for", "from",
    "how", "i", "in", "is", "it", "my", "of", "on", "or",
    "should", "the", "to", "what", "when", "with",
}


@dataclass(frozen=True)
class KnowledgeDocument:
    """A document loaded from the PawPal AI knowledge base."""

    document_id: str
    title: str
    category: str
    source_path: str
    content: str


@dataclass(frozen=True)
class RetrievedEvidence:
    """A relevant section returned by the retriever."""

    document_id: str
    title: str
    category: str
    source_path: str
    section: str
    content: str
    score: float

    @property
    def citation(self) -> str:
        return f"{self.title} ({self.document_id})"


class MultiSourceRetriever:
    """Retrieve relevant evidence from general and pet-specific files."""

    def __init__(
        self,
        knowledge_base_path: str | Path | None = None,
    ) -> None:
        self.knowledge_base_path = Path(
            knowledge_base_path or DEFAULT_KNOWLEDGE_BASE
        )

        if not self.knowledge_base_path.exists():
            raise FileNotFoundError(
                "Knowledge base not found: "
                f"{self.knowledge_base_path}"
            )

        self.documents = self._load_documents()

    def _load_documents(self) -> list[KnowledgeDocument]:
        documents: list[KnowledgeDocument] = []

        for path in sorted(self.knowledge_base_path.rglob("*.md")):
            content = path.read_text(encoding="utf-8").strip()

            if not content:
                continue

            relative_path = path.relative_to(self.knowledge_base_path)
            category = relative_path.parts[0]
            title = self._extract_title(content, path)
            document_id = self._extract_document_id(content, path)

            documents.append(
                KnowledgeDocument(
                    document_id=document_id,
                    title=title,
                    category=category,
                    source_path=relative_path.as_posix(),
                    content=content,
                )
            )

        return documents

    @staticmethod
    def _extract_title(content: str, path: Path) -> str:
        match = re.search(r"(?m)^#\s+(.+)$", content)

        if match:
            return match.group(1).strip()

        return path.stem.replace("_", " ").title()

    @staticmethod
    def _extract_document_id(content: str, path: Path) -> str:
        match = re.search(
            r"(?im)^Document ID:\s*(.+?)\s*$",
            content,
        )

        if match:
            return match.group(1).strip()

        return path.stem.replace("_", "-")

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        return {
            token
            for token in tokens
            if token not in STOP_WORDS and len(token) > 1
        }

    @staticmethod
    def _split_sections(
        document: KnowledgeDocument,
    ) -> list[tuple[str, str]]:
        matches = list(
            re.finditer(r"(?m)^##\s+(.+?)\s*$", document.content)
        )

        if not matches:
            return [("Document", document.content)]

        sections: list[tuple[str, str]] = []

        for index, match in enumerate(matches):
            start = match.start()
            end = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(document.content)
            )

            heading = match.group(1).strip()
            section_text = document.content[start:end].strip()
            sections.append((heading, section_text))

        return sections

    def retrieve(
        self,
        query: str,
        pet_name: str | None = None,
        top_k: int = 3,
    ) -> list[RetrievedEvidence]:
        """Return the most relevant evidence from different sources."""

        if not query or not query.strip():
            raise ValueError("A retrieval query is required.")

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        best_result_by_document: dict[str, RetrievedEvidence] = {}

        for document in self.documents:
            for heading, section_text in self._split_sections(document):
                searchable_text = " ".join(
                    [
                        document.title,
                        document.category,
                        document.source_path,
                        heading,
                        section_text,
                    ]
                )

                section_tokens = self._tokenize(searchable_text)
                overlapping_tokens = query_tokens & section_tokens

                if not overlapping_tokens:
                    continue

                score = len(overlapping_tokens) / len(query_tokens)

                heading_tokens = self._tokenize(heading)
                heading_overlap = query_tokens & heading_tokens
                score += len(heading_overlap) * 0.15

                if pet_name:
                    normalized_pet_name = pet_name.strip().lower()

                    if (
                        normalized_pet_name
                        and normalized_pet_name
                        in searchable_text.lower()
                    ):
                        score += 0.35

                result = RetrievedEvidence(
                    document_id=document.document_id,
                    title=document.title,
                    category=document.category,
                    source_path=document.source_path,
                    section=heading,
                    content=section_text,
                    score=round(score, 3),
                )

                current_best = best_result_by_document.get(
                    document.document_id
                )

                if current_best is None or result.score > current_best.score:
                    best_result_by_document[document.document_id] = result

        ranked_results = sorted(
            best_result_by_document.values(),
            key=lambda result: (-result.score, result.source_path),
        )

        return ranked_results[:top_k]

    @staticmethod
    def format_context(
        evidence: list[RetrievedEvidence],
    ) -> str:
        """Format retrieved evidence for an AI prompt or explanation."""

        if not evidence:
            return "No relevant knowledge-base evidence was found."

        sections: list[str] = []

        for index, item in enumerate(evidence, start=1):
            sections.append(
                "\n".join(
                    [
                        f"[Source {index}]",
                        f"Title: {item.title}",
                        f"Document ID: {item.document_id}",
                        f"Category: {item.category}",
                        f"File: {item.source_path}",
                        f"Relevance score: {item.score}",
                        item.content,
                    ]
                )
            )

        return "\n\n".join(sections)

    def list_sources(self) -> list[str]:
        """Return citations for every loaded source."""

        return [
            f"{document.title} ({document.document_id})"
            for document in self.documents
        ]


if __name__ == "__main__":
    retriever = MultiSourceRetriever()

    results = retriever.retrieve(
        query="Schedule Max's morning walk safely",
        pet_name="Max",
    )

    print(f"Loaded sources: {len(retriever.documents)}")
    print(f"Retrieved sources: {len(results)}")
    print()
    print(retriever.format_context(results))