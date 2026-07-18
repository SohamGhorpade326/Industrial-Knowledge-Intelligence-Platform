from backend.app.services.rag_service import rag_service
from backend.app.services.groq_service import groq_service
from backend.app.core.constants import EMERGENCY_KEYWORDS
from backend.app.core.logging_config import logger

EMERGENCY_SYSTEM_PROMPT = """You are an Emergency Response AI Agent for an industrial manufacturing plant. You handle life-threatening and safety-critical situations.

When an emergency is detected, you MUST provide:

1. **IMMEDIATE ACTIONS** - What to do RIGHT NOW (first 60 seconds)
2. **EMERGENCY SOP** - Step-by-step emergency standard operating procedure
3. **SHUTDOWN SEQUENCE** - How to safely shut down affected equipment
4. **PPE REQUIRED** - Personal Protective Equipment needed
5. **EVACUATION** - Evacuation procedures if needed
6. **EMERGENCY CONTACTS** - Who to call immediately

Format your response clearly with sections. Use BOLD for critical actions.
Prioritize human safety above equipment safety.
Never suggest actions that could put people at risk.
If in doubt, recommend evacuation first."""

EMERGENCY_CONTACTS = [
    {"name": "Plant Safety Officer", "phone": "+91-9876543210", "role": "Safety Officer"},
    {"name": "Fire Department", "phone": "101", "role": "Fire Emergency"},
    {"name": "Ambulance", "phone": "108", "role": "Medical Emergency"},
    {"name": "Plant Manager", "phone": "+91-9876543211", "role": "Plant Manager"},
    {"name": "Electrical Safety", "phone": "+91-9876543212", "role": "Electrical Emergency"},
    {"name": "Chemical Safety", "phone": "+91-9876543213", "role": "Chemical Emergency"},
]


class EmergencyAgent:
    def detect_emergency(self, question: str) -> bool:
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in EMERGENCY_KEYWORDS)

    def query(self, question: str) -> dict:
        try:
            is_emergency = self.detect_emergency(question)

            rag_result = rag_service.query(question)

            if is_emergency:
                emergency_context = rag_result.get("context_used", "")
                answer = groq_service.generate_with_context(
                    system_prompt=EMERGENCY_SYSTEM_PROMPT,
                    context=emergency_context if emergency_context else "No specific emergency documents found. Provide general industrial emergency response.",
                    question=question,
                )

                shutdown_steps = self._extract_shutdown_steps(answer)
                ppe_required = self._extract_ppe(question)

                return {
                    "is_emergency": True,
                    "answer": answer,
                    "emergency_sop": answer,
                    "shutdown_steps": shutdown_steps,
                    "ppe_required": ppe_required,
                    "emergency_contacts": EMERGENCY_CONTACTS,
                    "sources": rag_result.get("sources", []),
                    "severity": "critical",
                    "confidence": max(rag_result.get("confidence", 50.0), 50.0),
                }
            else:
                return {
                    "is_emergency": False,
                    "answer": rag_result.get("answer", "No emergency detected. If you are experiencing an emergency, please describe the situation clearly."),
                    "emergency_sop": "",
                    "shutdown_steps": [],
                    "ppe_required": [],
                    "emergency_contacts": EMERGENCY_CONTACTS,
                    "sources": rag_result.get("sources", []),
                    "severity": "low",
                    "confidence": rag_result.get("confidence", 0.0),
                }
        except Exception as e:
            logger.error(f"Emergency agent error: {e}")
            return {
                "is_emergency": True,
                "answer": "SYSTEM ERROR during emergency query. Follow standard emergency procedures. Contact Plant Safety Officer immediately.",
                "emergency_sop": "Follow posted emergency procedures. Evacuate if in doubt.",
                "shutdown_steps": ["Press emergency stop button", "Evacuate the area", "Call emergency services"],
                "ppe_required": ["Safety helmet", "Safety goggles", "Safety shoes", "High-visibility vest"],
                "emergency_contacts": EMERGENCY_CONTACTS,
                "sources": [],
                "severity": "critical",
                "confidence": 0.0,
            }

    def _extract_shutdown_steps(self, answer: str) -> list:
        steps = [
            "Activate emergency stop (E-Stop) on the affected equipment",
            "Isolate power supply to the affected area",
            "Alert all personnel in the vicinity",
            "Follow equipment-specific shutdown procedure",
            "Secure the area and prevent unauthorized access",
            "Document the incident details",
        ]
        return steps

    def _extract_ppe(self, question: str) -> list:
        question_lower = question.lower()
        ppe = ["Safety helmet", "Safety goggles", "Safety shoes"]

        if any(kw in question_lower for kw in ["fire", "explosion", "heat", "overheating"]):
            ppe.extend(["Fire-resistant clothing", "Heat-resistant gloves", "Fire extinguisher"])
        if any(kw in question_lower for kw in ["gas", "chemical", "toxic", "leak"]):
            ppe.extend(["Gas mask / Respirator", "Chemical-resistant gloves", "Chemical suit"])
        if any(kw in question_lower for kw in ["electrical", "shock", "voltage"]):
            ppe.extend(["Insulated gloves", "Rubber-soled boots", "Insulated tools"])

        return list(set(ppe))


emergency_agent = EmergencyAgent()
