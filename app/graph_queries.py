from typing import Dict, Any, List
from app.database import db_manager

# MOCK/FALLBACK GRAPH DATA FOR DEMO & TESTING WHEN UNCONNECTED
MOCK_NODES = [
    {"id": "SUP-101", "label": "Supplier", "name": "Taiwan Semi Mfg Co (TSMC)", "type": "Supplier", "tier": 1, "country": "Taiwan", "riskScore": 78, "status": "Active"},
    {"id": "SUP-102", "label": "Supplier", "name": "ASML Lithography NV", "type": "Supplier", "tier": 2, "country": "Netherlands", "riskScore": 45, "status": "Active"},
    {"id": "SUP-103", "label": "Supplier", "name": "SK Hynix Memory Corp", "type": "Supplier", "tier": 1, "country": "South Korea", "riskScore": 62, "status": "Active"},
    {"id": "SUP-104", "label": "Supplier", "name": "Kyocera Precision Components", "type": "Supplier", "tier": 2, "country": "Japan", "riskScore": 30, "status": "Active"},
    {"id": "SUP-105", "label": "Supplier", "name": "Shenzhen Circuit Tech", "type": "Supplier", "tier": 3, "country": "China", "riskScore": 85, "status": "Warning"},
    
    {"id": "FAC-201", "label": "Facility", "name": "Fab 18 Tainan Science Park", "type": "Facility", "city": "Tainan", "country": "Taiwan", "facilityType": "Semiconductor Fab"},
    {"id": "FAC-202", "label": "Facility", "name": "Veldhoven EUV Assembly Hub", "type": "Facility", "city": "Veldhoven", "country": "Netherlands", "facilityType": "High-Precision Tooling"},
    {"id": "FAC-203", "label": "Facility", "name": "Icheon DRAM Plant 3", "type": "Facility", "city": "Icheon", "country": "South Korea", "facilityType": "Memory Fab"},

    {"id": "CMP-301", "label": "Component", "name": "N3 3nm System Processor Die", "sku": "IC-N3-991", "category": "Semiconductors", "criticality": "CRITICAL", "leadTimeDays": 120},
    {"id": "CMP-302", "label": "Component", "name": "EUV Optics Lens Array", "sku": "OPT-EUV-004", "category": "Optics", "criticality": "CRITICAL", "leadTimeDays": 210},
    {"id": "CMP-303", "label": "Component", "name": "LPDDR5X 16GB Memory Module", "sku": "MEM-D5-16G", "category": "Memory", "criticality": "HIGH", "leadTimeDays": 45},
    {"id": "CMP-304", "label": "Component", "name": "Ultra-Dense Substrate Board", "sku": "PCB-UD-882", "category": "Printed Circuit Boards", "criticality": "HIGH", "leadTimeDays": 60},
    {"id": "CMP-305", "label": "Component", "name": "Titanium Thermal Heat Sink", "sku": "THM-TI-101", "category": "Cooling", "criticality": "MEDIUM", "leadTimeDays": 14},
    {"id": "CMP-306", "label": "Component", "name": "Alternative 4nm Processor Die (Samsung)", "sku": "IC-N4-ALT", "category": "Semiconductors", "criticality": "HIGH", "leadTimeDays": 90},

    {"id": "PRD-401", "label": "Product", "name": "QuantumX AI Server Blade Pro", "sku": "PRD-QX-9000", "category": "Enterprise Data Center", "retailPrice": 24500.0, "marginPct": 42.0},
    {"id": "PRD-402", "label": "Product", "name": "EdgeVision Autonomous AI Drone", "sku": "PRD-EV-DRONE", "category": "Robotics & Defense", "retailPrice": 12800.0, "marginPct": 38.5},
    {"id": "PRD-403", "label": "Product", "name": "HyperCompute Mobile Workstation", "sku": "PRD-HC-WS15", "category": "Consumer Electronics", "retailPrice": 3499.0, "marginPct": 28.0},

    {"id": "DIS-501", "label": "Disruption", "name": "Typhoon Gaemi Port Closure", "type": "Geopolitical / Severe Weather", "severity": "CRITICAL", "impactedRegion": "Tainan, Taiwan", "description": "Port of Kaohsiung cargo operations suspended indefinitely."}
]

MOCK_EDGES = [
    {"from": "SUP-101", "to": "FAC-201", "label": "OPERATES", "relation": "OPERATES"},
    {"from": "SUP-102", "to": "FAC-202", "label": "OPERATES", "relation": "OPERATES"},
    {"from": "SUP-103", "to": "FAC-203", "label": "OPERATES", "relation": "OPERATES"},

    {"from": "FAC-201", "to": "CMP-301", "label": "MANUFACTURES", "relation": "MANUFACTURES"},
    {"from": "FAC-202", "to": "CMP-302", "label": "MANUFACTURES", "relation": "MANUFACTURES"},
    {"from": "FAC-203", "to": "CMP-303", "label": "MANUFACTURES", "relation": "MANUFACTURES"},

    {"from": "SUP-101", "to": "CMP-301", "label": "SUPPLIES", "relation": "SUPPLIES", "unitCost": 450.0, "leadTimeDays": 120},
    {"from": "SUP-102", "to": "CMP-302", "label": "SUPPLIES", "relation": "SUPPLIES", "unitCost": 8200.0, "leadTimeDays": 210},
    {"from": "SUP-103", "to": "CMP-303", "label": "SUPPLIES", "relation": "SUPPLIES", "unitCost": 65.0, "leadTimeDays": 45},
    {"from": "SUP-104", "to": "CMP-304", "label": "SUPPLIES", "relation": "SUPPLIES", "unitCost": 28.0, "leadTimeDays": 60},
    {"from": "SUP-105", "to": "CMP-304", "label": "SUPPLIES", "relation": "SUPPLIES", "unitCost": 22.0, "leadTimeDays": 75},

    {"from": "CMP-302", "to": "CMP-301", "label": "REQUIRES", "relation": "REQUIRES", "quantity": 1},
    {"from": "CMP-304", "to": "CMP-301", "label": "REQUIRES", "relation": "REQUIRES", "quantity": 2},

    {"from": "CMP-301", "to": "PRD-401", "label": "PART_OF", "relation": "PART_OF", "quantity": 4},
    {"from": "CMP-303", "to": "PRD-401", "label": "PART_OF", "relation": "PART_OF", "quantity": 16},
    {"from": "CMP-301", "to": "PRD-402", "label": "PART_OF", "relation": "PART_OF", "quantity": 1},
    {"from": "CMP-305", "to": "PRD-402", "label": "PART_OF", "relation": "PART_OF", "quantity": 2},
    {"from": "CMP-303", "to": "PRD-403", "label": "PART_OF", "relation": "PART_OF", "quantity": 2},

    {"from": "CMP-301", "to": "CMP-306", "label": "ALTERNATIVE_TO", "relation": "ALTERNATIVE_TO", "switchLeadTimeDays": 30, "costDeltaPct": 12.5},

    {"from": "DIS-501", "to": "FAC-201", "label": "AFFECTS", "relation": "AFFECTS"},
    {"from": "DIS-501", "to": "SUP-101", "label": "AFFECTS", "relation": "AFFECTS"}
]


class GraphQueryRepository:

    @staticmethod
    def get_full_graph() -> Dict[str, Any]:
        """
        Retrieves the complete graph topology.
        Parameterized Cypher:
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        cypher = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        if db_manager.is_connected:
            try:
                records = db_manager.execute_query(cypher)
                nodes_dict = {}
                edges = []
                for rec in records:
                    n = rec.get("n")
                    if n and "id" in n:
                        nodes_dict[n["id"]] = n
                    m = rec.get("m")
                    if m and "id" in m:
                        nodes_dict[m["id"]] = m
                    r = rec.get("r")
                    if r and n and m:
                        edges.append({
                            "from": n["id"],
                            "to": m["id"],
                            "label": r.type if hasattr(r, 'type') else "RELATION",
                            "relation": r.type if hasattr(r, 'type') else "RELATION"
                        })
                return {
                    "nodes": list(nodes_dict.values()),
                    "edges": edges,
                    "cypher": cypher.strip(),
                    "source": "CognoDB Cloud"
                }
            except Exception as err:
                pass

        # Fallback to rich dataset
        return {
            "nodes": MOCK_NODES,
            "edges": MOCK_EDGES,
            "cypher": cypher.strip(),
            "source": "Fallback Demo Dataset (CognoDB credentials pending)"
        }

    @staticmethod
    def get_multi_hop_blast_radius(supplier_id: str) -> Dict[str, Any]:
        """
        Executes multi-hop traversal (1 to 5 hops) from a Supplier down to end Products.
        Parameterized Cypher:
        MATCH (s:Supplier {id: $supplier_id})
        MATCH path = (s)-[:OPERATES|SUPPLIES|MANUFACTURES|REQUIRES|PART_OF*1..5]->(p:Product)
        RETURN s, p, path, length(path) as hops
        """
        cypher = """
        MATCH (s:Supplier {id: $supplier_id})
        MATCH path = (s)-[:OPERATES|SUPPLIES|MANUFACTURES|REQUIRES|PART_OF*1..5]->(p:Product)
        RETURN s.name as supplierName, p.name as productName, p.retailPrice as revenueExposed, length(path) as hops
        """
        params = {"supplier_id": supplier_id}

        if db_manager.is_connected:
            try:
                results = db_manager.execute_query(cypher, params)
                return {
                    "supplier_id": supplier_id,
                    "results": results,
                    "cypher": cypher.strip(),
                    "params": params,
                    "source": "CognoDB Cloud"
                }
            except Exception as err:
                pass

        # Fallback multi-hop computation logic
        impacted_products = []
        if supplier_id == "SUP-101":
            impacted_products = [
                {"supplierName": "Taiwan Semi Mfg Co (TSMC)", "productName": "QuantumX AI Server Blade Pro", "revenueExposed": 24500.0, "hops": 3},
                {"supplierName": "Taiwan Semi Mfg Co (TSMC)", "productName": "EdgeVision Autonomous AI Drone", "revenueExposed": 12800.0, "hops": 3}
            ]
        elif supplier_id == "SUP-102":
            impacted_products = [
                {"supplierName": "ASML Lithography NV", "productName": "QuantumX AI Server Blade Pro", "revenueExposed": 24500.0, "hops": 4},
                {"supplierName": "ASML Lithography NV", "productName": "EdgeVision Autonomous AI Drone", "revenueExposed": 12800.0, "hops": 4}
            ]
        elif supplier_id == "SUP-103":
            impacted_products = [
                {"supplierName": "SK Hynix Memory Corp", "productName": "QuantumX AI Server Blade Pro", "revenueExposed": 24500.0, "hops": 3},
                {"supplierName": "SK Hynix Memory Corp", "productName": "HyperCompute Mobile Workstation", "revenueExposed": 3499.0, "hops": 3}
            ]
        else:
            impacted_products = [
                {"supplierName": "Generic Supplier", "productName": "QuantumX AI Server Blade Pro", "revenueExposed": 24500.0, "hops": 2}
            ]

        return {
            "supplier_id": supplier_id,
            "results": impacted_products,
            "cypher": cypher.strip(),
            "params": params,
            "source": "Demo Graph Traversal Engine"
        }

    @staticmethod
    def get_single_points_of_failure() -> Dict[str, Any]:
        """
        Queries the graph to find Critical components supplied by only 1 supplier across N tiers.
        Parameterized Cypher:
        MATCH (c:Component)
        OPTIONAL MATCH (s:Supplier)-[:SUPPLIES]->(c)
        WITH c, count(s) AS supplierCount, collect(s.name) AS suppliers
        WHERE supplierCount = 1 AND c.criticality IN ['CRITICAL', 'HIGH']
        OPTIONAL MATCH (c)-[:PART_OF|REQUIRES*1..3]->(p:Product)
        RETURN c.name AS component, c.sku AS sku, c.criticality AS criticality, suppliers, collect(DISTINCT p.name) AS affectedProducts
        """
        cypher = """
        MATCH (c:Component)
        OPTIONAL MATCH (s:Supplier)-[:SUPPLIES]->(c)
        WITH c, count(s) AS supplierCount, collect(s.name) AS suppliers
        WHERE supplierCount = 1 AND c.criticality IN ['CRITICAL', 'HIGH']
        OPTIONAL MATCH (c)-[:PART_OF|REQUIRES*1..3]->(p:Product)
        RETURN c.name AS component, c.sku AS sku, c.criticality AS criticality, suppliers, collect(DISTINCT p.name) AS affectedProducts
        """

        if db_manager.is_connected:
            try:
                results = db_manager.execute_query(cypher)
                return {
                    "spofs": results,
                    "cypher": cypher.strip(),
                    "source": "CognoDB Cloud"
                }
            except Exception as err:
                pass

        # Fallback SPOFs
        spofs = [
            {
                "component": "N3 3nm System Processor Die",
                "sku": "IC-N3-991",
                "criticality": "CRITICAL",
                "suppliers": ["Taiwan Semi Mfg Co (TSMC)"],
                "supplierCount": 1,
                "affectedProducts": ["QuantumX AI Server Blade Pro", "EdgeVision Autonomous AI Drone"]
            },
            {
                "component": "EUV Optics Lens Array",
                "sku": "OPT-EUV-004",
                "criticality": "CRITICAL",
                "suppliers": ["ASML Lithography NV"],
                "supplierCount": 1,
                "affectedProducts": ["QuantumX AI Server Blade Pro", "EdgeVision Autonomous AI Drone"]
            },
            {
                "component": "LPDDR5X 16GB Memory Module",
                "sku": "MEM-D5-16G",
                "criticality": "HIGH",
                "suppliers": ["SK Hynix Memory Corp"],
                "supplierCount": 1,
                "affectedProducts": ["QuantumX AI Server Blade Pro", "HyperCompute Mobile Workstation"]
            }
        ]

        return {
            "spofs": spofs,
            "cypher": cypher.strip(),
            "source": "Demo Graph Analysis Engine"
        }

    @staticmethod
    def get_alternative_pathways(component_id: str) -> Dict[str, Any]:
        """
        Finds mitigation pathways using alternative components & suppliers.
        Parameterized Cypher:
        MATCH (c:Component {id: $component_id})-[r:ALTERNATIVE_TO]-(alt:Component)
        MATCH (s:Supplier)-[:SUPPLIES]->(alt)
        RETURN c.name AS primaryComponent, alt.name AS alternativeComponent, s.name AS supplier, r.switchLeadTimeDays AS leadTime, r.costDeltaPct AS costDelta
        """
        cypher = """
        MATCH (c:Component {id: $component_id})-[r:ALTERNATIVE_TO]-(alt:Component)
        MATCH (s:Supplier)-[:SUPPLIES]->(alt)
        RETURN c.name AS primaryComponent, alt.name AS alternativeComponent, s.name AS supplier, r.switchLeadTimeDays AS leadTime, r.costDeltaPct AS costDelta
        """
        params = {"component_id": component_id}

        if db_manager.is_connected:
            try:
                results = db_manager.execute_query(cypher, params)
                return {
                    "component_id": component_id,
                    "alternatives": results,
                    "cypher": cypher.strip(),
                    "params": params,
                    "source": "CognoDB Cloud"
                }
            except Exception as err:
                pass

        return {
            "component_id": component_id,
            "alternatives": [
                {
                    "primaryComponent": "N3 3nm System Processor Die",
                    "alternativeComponent": "Alternative 4nm Processor Die (Samsung)",
                    "supplier": "Samsung Electronics Foundry",
                    "leadTime": 30,
                    "costDelta": 12.5
                }
            ],
            "cypher": cypher.strip(),
            "params": params,
            "source": "Demo Graph Mitigation Engine"
        }
