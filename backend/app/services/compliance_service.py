from backend.app.services.rag_service import rag_service
from backend.app.services.groq_service import groq_service
from backend.app.core.logging_config import logger

COMPLIANCE_SYSTEM_PROMPT = """You are a Compliance and Safety Assistant for an industrial manufacturing plant. You help safety officers, engineers, and managers find and understand compliance requirements, safety procedures, and regulatory guidelines.

For every response, provide:
1. Relevant safety procedures and SOPs
2. Compliance requirements and standards
3. Regulatory guidelines that apply
4. Safety checklists when appropriate
5. PPE requirements if relevant
6. Any warnings or cautions

Always reference source documents with citations. Prioritize safety above all else."""


class ComplianceService:
    def query_compliance(self, question: str) -> dict:
        rag_result = rag_service.query(
            question,
            filter_metadata=None,
        )

        system_prompt = COMPLIANCE_SYSTEM_PROMPT

        if rag_result.get("sources"):
            answer = rag_result["answer"]
        else:
            answer = groq_service.generate_response(
                system_prompt=system_prompt,
                user_message=f"""A user has asked the following compliance/safety question, but no specific documents were found in the knowledge base:

Question: {question}

Provide general industrial safety guidance based on common standards (ISO, OSHA) while noting that specific plant documents should be consulted for definitive answers.""",
            )

        return {
            "answer": answer,
            "confidence": rag_result.get("confidence", 0.0),
            "sources": rag_result.get("sources", []),
            "suggested_questions": rag_result.get("suggested_questions", []),
        }

    def generate_checklist(self, topic: str) -> dict:
        prompt = f"""Generate a detailed compliance checklist for the following topic in an industrial manufacturing plant:

Topic: {topic}

Format the checklist with:
- Clear numbered items
- Specific checkpoints
- Required documentation
- Responsible personnel roles
- Frequency (daily/weekly/monthly/quarterly)
- Compliance standard reference where applicable"""

        checklist = groq_service.generate_response(
            system_prompt=COMPLIANCE_SYSTEM_PROMPT,
            user_message=prompt,
        )

        return {
            "topic": topic,
            "checklist": checklist,
            "generated": True,
        }


compliance_service = ComplianceService()
