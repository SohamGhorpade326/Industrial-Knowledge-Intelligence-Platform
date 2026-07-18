from typing import List, Optional
from backend.app.core.config import get_settings
from backend.app.core.logging_config import logger

settings = get_settings()

_driver = None
_available = False


def _init_neo4j():
    global _driver, _available
    try:
        from neo4j import GraphDatabase
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
        )
        _driver.verify_connectivity()
        _available = True
        logger.info("Neo4j connection established")
    except Exception as e:
        _available = False
        logger.warning(f"Neo4j not available: {e}. Knowledge graph features will use fallback data.")


class GraphService:
    def __init__(self):
        if _driver is None:
            _init_neo4j()

    @property
    def is_available(self) -> bool:
        return _available

    def _run_query(self, query: str, parameters: dict = None) -> list:
        if not _available:
            return []
        try:
            with _driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query failed: {e}")
            return []

    def add_machine_node(self, machine_data: dict) -> bool:
        query = """
        MERGE (m:Machine {name: $name})
        SET m.type = $type,
            m.manufacturer = $manufacturer,
            m.location = $location,
            m.department = $department,
            m.status = $status,
            m.health_score = $health_score
        RETURN m
        """
        result = self._run_query(query, {
            "name": machine_data.get("name", ""),
            "type": machine_data.get("machine_type", ""),
            "manufacturer": machine_data.get("manufacturer", ""),
            "location": machine_data.get("location", ""),
            "department": machine_data.get("department", ""),
            "status": machine_data.get("status", "operational"),
            "health_score": machine_data.get("health_score", 85.0),
        })
        return len(result) > 0

    def add_document_node(self, doc_data: dict) -> bool:
        query = """
        MERGE (d:Document {id: $id})
        SET d.filename = $filename,
            d.title = $title,
            d.category = $category,
            d.type = $type
        RETURN d
        """
        result = self._run_query(query, {
            "id": doc_data.get("id", 0),
            "filename": doc_data.get("filename", ""),
            "title": doc_data.get("title", ""),
            "category": doc_data.get("category", ""),
            "type": doc_data.get("file_type", ""),
        })
        return len(result) > 0

    def link_document_to_machine(self, doc_id: int, machine_name: str) -> bool:
        query = """
        MATCH (d:Document {id: $doc_id})
        MATCH (m:Machine {name: $machine_name})
        MERGE (m)-[:HAS_DOCUMENT]->(d)
        RETURN m, d
        """
        result = self._run_query(query, {"doc_id": doc_id, "machine_name": machine_name})
        return len(result) > 0

    def add_failure_node(self, failure_data: dict) -> bool:
        query = """
        MERGE (f:Failure {id: $id})
        SET f.issue = $issue,
            f.severity = $severity,
            f.date = $date
        WITH f
        MATCH (m:Machine {name: $machine_name})
        MERGE (m)-[:FAILED_WITH]->(f)
        RETURN f
        """
        return len(self._run_query(query, failure_data)) > 0

    def add_engineer_node(self, engineer_name: str) -> bool:
        query = """
        MERGE (e:Engineer {name: $name})
        RETURN e
        """
        return len(self._run_query(query, {"name": engineer_name})) > 0

    def link_engineer_to_maintenance(self, engineer_name: str, machine_name: str, action: str) -> bool:
        query = """
        MATCH (e:Engineer {name: $engineer_name})
        MATCH (m:Machine {name: $machine_name})
        MERGE (e)-[:PERFORMED {action: $action}]->(m)
        RETURN e, m
        """
        return len(self._run_query(query, {
            "engineer_name": engineer_name,
            "machine_name": machine_name,
            "action": action,
        })) > 0

    def add_sop_node(self, sop_data: dict) -> bool:
        query = """
        MERGE (s:SOP {title: $title})
        SET s.document_id = $document_id,
            s.category = $category
        RETURN s
        """
        return len(self._run_query(query, sop_data)) > 0

    def add_vendor_node(self, vendor_name: str) -> bool:
        query = """
        MERGE (v:Vendor {name: $name})
        RETURN v
        """
        return len(self._run_query(query, {"name": vendor_name})) > 0

    def add_spare_part_node(self, part_data: dict) -> bool:
        query = """
        MERGE (sp:SparePart {name: $name})
        SET sp.part_number = $part_number
        WITH sp
        MATCH (m:Machine {name: $machine_name})
        MERGE (m)-[:HAS_SPARE]->(sp)
        RETURN sp
        """
        return len(self._run_query(query, part_data)) > 0

    def get_full_graph(self) -> dict:
        if not _available:
            return self._get_fallback_graph()

        nodes_query = """
        MATCH (n)
        RETURN id(n) AS id, labels(n) AS labels, properties(n) AS props
        LIMIT 200
        """
        edges_query = """
        MATCH (a)-[r]->(b)
        RETURN id(a) AS source, id(b) AS target, type(r) AS relationship, properties(r) AS props
        LIMIT 500
        """

        raw_nodes = self._run_query(nodes_query)
        raw_edges = self._run_query(edges_query)

        nodes = []
        for n in raw_nodes:
            node_label = n["labels"][0] if n["labels"] else "Unknown"
            props = n.get("props", {})
            display_name = props.get("name", props.get("title", props.get("filename", f"Node {n['id']}")))
            nodes.append({
                "id": str(n["id"]),
                "label": display_name,
                "type": node_label,
                "properties": props,
            })

        edges = []
        for e in raw_edges:
            edges.append({
                "source": str(e["source"]),
                "target": str(e["target"]),
                "relationship": e["relationship"],
                "properties": e.get("props", {}),
            })

        if not nodes:
            return self._get_fallback_graph()

        return {"nodes": nodes, "edges": edges}

    def get_machine_subgraph(self, machine_name: str) -> dict:
        if not _available:
            return self._get_fallback_graph()

        query = """
        MATCH (m:Machine {name: $name})-[r]-(connected)
        RETURN m, r, connected
        """
        results = self._run_query(query, {"name": machine_name})

        nodes = []
        edges = []
        seen_nodes = set()

        for record in results:
            for key, value in record.items():
                if hasattr(value, "labels"):
                    node_id = str(value.id)
                    if node_id not in seen_nodes:
                        seen_nodes.add(node_id)
                        nodes.append({
                            "id": node_id,
                            "label": dict(value).get("name", dict(value).get("title", node_id)),
                            "type": list(value.labels)[0] if value.labels else "Unknown",
                            "properties": dict(value),
                        })

        if not nodes:
            return self._get_fallback_graph()

        return {"nodes": nodes, "edges": edges}

    def update_graph_from_document(self, doc_data: dict, metadata: dict) -> None:
        self.add_document_node(doc_data)

        machine_name = doc_data.get("machine_name", "")
        if machine_name:
            self.link_document_to_machine(doc_data["id"], machine_name)

        if metadata.get("has_sop_content"):
            self.add_sop_node({
                "title": doc_data.get("title", doc_data.get("filename", "")),
                "document_id": doc_data.get("id", 0),
                "category": doc_data.get("category", ""),
            })

        for machine in metadata.get("machines_mentioned", []):
            self.add_machine_node({"name": machine})
            self.link_document_to_machine(doc_data["id"], machine)

    def _get_fallback_graph(self) -> dict:
        nodes = [
            {"id": "m1", "label": "CNC Machine", "type": "Machine", "properties": {"status": "operational", "location": "Production Floor A"}},
            {"id": "m2", "label": "Hydraulic Press", "type": "Machine", "properties": {"status": "operational", "location": "Production Floor A"}},
            {"id": "m3", "label": "Conveyor Belt", "type": "Machine", "properties": {"status": "maintenance", "location": "Assembly Line B"}},
            {"id": "m4", "label": "Industrial Robot", "type": "Machine", "properties": {"status": "operational", "location": "Assembly Line A"}},
            {"id": "m5", "label": "Boiler", "type": "Machine", "properties": {"status": "operational", "location": "Utility Room"}},
            {"id": "m6", "label": "Compressor", "type": "Machine", "properties": {"status": "operational", "location": "Utility Room"}},
            {"id": "d1", "label": "CNC Operation SOP", "type": "Document", "properties": {"category": "sop"}},
            {"id": "d2", "label": "Safety Manual", "type": "Document", "properties": {"category": "safety_manual"}},
            {"id": "d3", "label": "Maintenance Guide", "type": "Document", "properties": {"category": "maintenance_manual"}},
            {"id": "e1", "label": "Rajesh Kumar", "type": "Engineer", "properties": {"role": "maintenance_engineer"}},
            {"id": "e2", "label": "Priya Sharma", "type": "Engineer", "properties": {"role": "safety_officer"}},
            {"id": "f1", "label": "Bearing Failure", "type": "Failure", "properties": {"severity": "high"}},
            {"id": "f2", "label": "Overheating", "type": "Failure", "properties": {"severity": "critical"}},
            {"id": "v1", "label": "Siemens", "type": "Vendor", "properties": {}},
            {"id": "v2", "label": "ABB", "type": "Vendor", "properties": {}},
            {"id": "sp1", "label": "Ball Bearing SKF-6205", "type": "SparePart", "properties": {"part_number": "SKF-6205"}},
            {"id": "sp2", "label": "Hydraulic Seal Kit", "type": "SparePart", "properties": {"part_number": "HS-400"}},
        ]
        edges = [
            {"source": "m1", "target": "d1", "relationship": "HAS_DOCUMENT", "properties": {}},
            {"source": "m1", "target": "d3", "relationship": "HAS_DOCUMENT", "properties": {}},
            {"source": "m1", "target": "f1", "relationship": "FAILED_WITH", "properties": {}},
            {"source": "m2", "target": "f2", "relationship": "FAILED_WITH", "properties": {}},
            {"source": "m2", "target": "d2", "relationship": "HAS_DOCUMENT", "properties": {}},
            {"source": "f1", "target": "sp1", "relationship": "RESOLVED_BY", "properties": {}},
            {"source": "e1", "target": "m1", "relationship": "MAINTAINED_BY", "properties": {}},
            {"source": "e1", "target": "m3", "relationship": "MAINTAINED_BY", "properties": {}},
            {"source": "e2", "target": "d2", "relationship": "REFERENCES", "properties": {}},
            {"source": "m1", "target": "sp1", "relationship": "HAS_SPARE", "properties": {}},
            {"source": "m2", "target": "sp2", "relationship": "HAS_SPARE", "properties": {}},
            {"source": "m1", "target": "v1", "relationship": "MAINTAINED_BY", "properties": {}},
            {"source": "m4", "target": "v2", "relationship": "MAINTAINED_BY", "properties": {}},
        ]
        return {"nodes": nodes, "edges": edges}


graph_service = GraphService()
