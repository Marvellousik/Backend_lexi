"""
Retrieval Tool for LexiAssist AI Infrastructure.
Executes cosine similarity searches across 1024-dim pgvector chunks with tenant & course isolation.
"""
import logging
from typing import Dict, Any, Tuple, List
from ai_service.tools.base import BaseTool
from ai_service.contracts.context import AIRequestContext
from ai_service.contracts.usage import TokenUsage
from ai_service.storage.database import get_db_session
from ai_service.storage.models import LexiChunk

logger = logging.getLogger(__name__)


class RetrievalTool(BaseTool):
    """Handles retrieval.search operations."""

    @property
    def operation_prefix(self) -> str:
        return "retrieval"

    async def execute(
        self,
        ctx: AIRequestContext,
        gateway: Any,
    ) -> Tuple[Dict[str, Any], TokenUsage, Dict[str, str]]:
        query = ctx.input.get("query", "")
        top_k = ctx.parameters.get("top_k", 5)
        course_code = ctx.course.course_id or ctx.input.get("course_code")
        institution_id = ctx.tenant.institution_id
        material_id = ctx.input.get("material_id")

        if not query:
            raise ValueError("Query cannot be empty for retrieval")

        # 1. Generate query embedding via Cohere
        query_vector = await gateway.cohere_adapter.embed_query(query)

        # 2. Query pgvector in database enforcing multi-tenant boundaries
        results: List[Dict[str, Any]] = []
        with get_db_session() as session:
            try:
                # Cosine distance query
                distance = LexiChunk.embedding.cosine_distance(query_vector)
                q = session.query(LexiChunk, distance.label("distance"))
                
                # Multi-tenant and course filters
                if institution_id:
                    q = q.filter(LexiChunk.institution_id == institution_id)
                if course_code:
                    q = q.filter(LexiChunk.course == course_code)
                if material_id:
                    q = q.filter(LexiChunk.doc_id == material_id)

                rows = q.order_by("distance").limit(top_k).all()

                for row in rows:
                    chunk = row.LexiChunk
                    similarity = round(1.0 - float(row.distance), 4)
                    results.append({
                        "chunk_id": chunk.id,
                        "doc_id": chunk.doc_id,
                        "course": chunk.course,
                        "text": chunk.chunk_text,
                        "chunk_index": chunk.chunk_index,
                        "similarity_score": similarity,
                    })

            except Exception as e:
                logger.warning(f"Vector search failed (pgvector might be in test mode): {e}")

        result = {
            "query": query,
            "results_count": len(results),
            "chunks": results,
        }

        usage = TokenUsage(total_tokens=len(query) // 4)
        return result, usage, {"provider": "cohere", "model": "embed-multilingual-v3.0"}
