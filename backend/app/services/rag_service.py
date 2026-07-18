import json
from typing import List, Optional
from backend.app.services.embedding_service import embedding_service
from backend.app.services.groq_service import groq_service
from backend.app.core.constants import TOP_K_RESULTS
from backend.app.core.logging_config import logger

RAG_SYSTEM_PROMPT = """You are an expert Industrial Knowledge Assistant for a manufacturing plant. You help engineers, plant managers, and safety officers find information from industrial documents including SOPs, maintenance manuals, safety guidelines, inspection reports, and calibration certificates.

Rules:
1. Answer ONLY based on the provided context from industrial documents.
2. Always cite the source document name and page number when available.
3. If the context doesn't contain enough information, clearly state that and suggest what documents might be needed.
4. Never make up information or hallucinate facts.
5. Provide practical, actionable answers relevant to industrial operations.
6. For safety-related questions, always err on the side of caution.
7. Use clear, professional language appropriate for engineering professionals.
8. Structure your answers with bullet points and sections when appropriate.
9. Include confidence level in your assessment.

Format your citations as: [Source: document_name, Page: X]"""


class RAGService:
    def query(
        self,
        question: str,
        top_k: int = TOP_K_RESULTS,
        filter_metadata: Optional[dict] = None,
    ) -> dict:
        try:
            search_results = embedding_service.similarity_search(
                query=question,
                top_k=top_k,
                filter_metadata=filter_metadata,
            )

            if not search_results:
                return {
                    "answer": "No relevant documents found in the knowledge base for this query. Please upload relevant documents or rephrase your question.",
                    "confidence": 0.0,
                    "sources": [],
                    "context_used": "",
                }

            context_parts = []
            sources = []
            for i, result in enumerate(search_results):
                metadata = result.get("metadata", {})
                doc_name = metadata.get("filename", "Unknown Document")
                chunk_idx = metadata.get("chunk_index", 0)

                context_parts.append(
                    f"[Document: {doc_name}, Section {chunk_idx + 1}]\n{result['text']}"
                )
                sources.append({
                    "document": doc_name,
                    "page": chunk_idx + 1,
                    "chunk_text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                    "relevance_score": round(result.get("relevance_score", 0.0), 3),
                })

            context = "\n\n".join(context_parts)

            answer = groq_service.generate_with_context(
                system_prompt=RAG_SYSTEM_PROMPT,
                context=context,
                question=question,
            )

            avg_relevance = sum(s["relevance_score"] for s in sources) / len(sources) if sources else 0.0
            confidence = min(avg_relevance * 100, 95.0)

            suggested_questions = self._generate_follow_ups(question, answer)

            return {
                "answer": answer,
                "confidence": round(confidence, 1),
                "sources": sources,
                "context_used": context,
                "suggested_questions": suggested_questions,
            }
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {
                "answer": f"An error occurred while processing your query: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "context_used": "",
            }

    def _generate_follow_ups(self, question: str, answer: str) -> List[str]:
        try:
            prompt = f"""Based on this Q&A exchange in an industrial setting:
Question: {question}
Answer: {answer[:500]}

Generate exactly 3 follow-up questions an engineer might ask next. Return ONLY the questions, one per line, without numbering."""

            response = groq_service.generate_response(
                system_prompt="You generate follow-up questions for industrial knowledge queries. Return only the questions, one per line.",
                user_message=prompt,
                temperature=0.5,
                max_tokens=256,
            )
            questions = [q.strip().lstrip("0123456789.-) ") for q in response.strip().split("\n") if q.strip()]
            return questions[:3]
        except Exception:
            return [
                "What are the maintenance requirements for this equipment?",
                "Are there any safety precautions I should be aware of?",
                "What is the recommended inspection schedule?",
            ]


rag_service = RAGService()
