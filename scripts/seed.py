#!/usr/bin/env python3
"""
CognoDB Cloud Database Seeder
Populates live CognoDB graph database instance with a realistic multi-tier supply chain network dataset
using parameterized openCypher queries via the official Neo4j Python Driver.
"""
import sys
import os
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from neo4j import GraphDatabase
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed-script")

# Realistic Dataset
SUPPLIERS = [
    {"id": "SUP-101", "name": "Taiwan Semi Mfg Co (TSMC)", "tier": 1, "country": "Taiwan", "riskScore": 78, "status": "Active"},
    {"id": "SUP-102", "name": "ASML Lithography NV", "tier": 2, "country": "Netherlands", "riskScore": 45, "status": "Active"},
    {"id": "SUP-103", "name": "SK Hynix Memory Corp", "tier": 1, "country": "South Korea", "riskScore": 62, "status": "Active"},
    {"id": "SUP-104", "name": "Kyocera Precision Components", "tier": 2, "country": "Japan", "riskScore": 30, "status": "Active"},
    {"id": "SUP-105", "name": "Shenzhen Circuit Tech", "tier": 3, "country": "China", "riskScore": 85, "status": "Warning"},
    {"id": "SUP-106", "name": "Samsung Electronics Foundry", "tier": 1, "country": "South Korea", "riskScore": 40, "status": "Active"}
]

FACILITIES = [
    {"id": "FAC-201", "name": "Fab 18 Tainan Science Park", "city": "Tainan", "country": "Taiwan", "facilityType": "Semiconductor Fab"},
    {"id": "FAC-202", "name": "Veldhoven EUV Assembly Hub", "city": "Veldhoven", "country": "Netherlands", "facilityType": "High-Precision Tooling"},
    {"id": "FAC-203", "name": "Icheon DRAM Plant 3", "city": "Icheon", "country": "South Korea", "facilityType": "Memory Fab"},
    {"id": "FAC-204", "name": "Pyeongtaek Line 3 Fab", "city": "Pyeongtaek", "country": "South Korea", "facilityType": "Advanced Semiconductor Fab"}
]

COMPONENTS = [
    {"id": "CMP-301", "name": "N3 3nm System Processor Die", "sku": "IC-N3-991", "category": "Semiconductors", "criticality": "CRITICAL", "leadTimeDays": 120},
    {"id": "CMP-302", "name": "EUV Optics Lens Array", "sku": "OPT-EUV-004", "category": "Optics", "criticality": "CRITICAL", "leadTimeDays": 210},
    {"id": "CMP-303", "name": "LPDDR5X 16GB Memory Module", "sku": "MEM-D5-16G", "category": "Memory", "criticality": "HIGH", "leadTimeDays": 45},
    {"id": "CMP-304", "name": "Ultra-Dense Substrate Board", "sku": "PCB-UD-882", "category": "Printed Circuit Boards", "criticality": "HIGH", "leadTimeDays": 60},
    {"id": "CMP-305", "name": "Titanium Thermal Heat Sink", "sku": "THM-TI-101", "category": "Cooling", "criticality": "MEDIUM", "leadTimeDays": 14},
    {"id": "CMP-306", "name": "Alternative 4nm Processor Die (Samsung)", "sku": "IC-N4-ALT", "category": "Semiconductors", "criticality": "HIGH", "leadTimeDays": 90}
]

PRODUCTS = [
    {"id": "PRD-401", "name": "QuantumX AI Server Blade Pro", "sku": "PRD-QX-9000", "category": "Enterprise Data Center", "retailPrice": 24500.0, "marginPct": 42.0},
    {"id": "PRD-402", "name": "EdgeVision Autonomous AI Drone", "sku": "PRD-EV-DRONE", "category": "Robotics & Defense", "retailPrice": 12800.0, "marginPct": 38.5},
    {"id": "PRD-403", "name": "HyperCompute Mobile Workstation", "sku": "PRD-HC-WS15", "category": "Consumer Electronics", "retailPrice": 3499.0, "marginPct": 28.0}
]

DISRUPTIONS = [
    {"id": "DIS-501", "title": "Typhoon Gaemi Port Closure", "type": "Geopolitical / Severe Weather", "severity": "CRITICAL", "impactedRegion": "Tainan, Taiwan", "description": "Port of Kaohsiung cargo operations suspended indefinitely due to super typhoon."}
]

# Parameterized Relationship Lists
RELATIONS_OPERATES = [
    {"supplier_id": "SUP-101", "facility_id": "FAC-201"},
    {"supplier_id": "SUP-102", "facility_id": "FAC-202"},
    {"supplier_id": "SUP-103", "facility_id": "FAC-203"},
    {"supplier_id": "SUP-106", "facility_id": "FAC-204"}
]

RELATIONS_MANUFACTURES = [
    {"facility_id": "FAC-201", "component_id": "CMP-301"},
    {"facility_id": "FAC-202", "component_id": "CMP-302"},
    {"facility_id": "FAC-203", "component_id": "CMP-303"},
    {"facility_id": "FAC-204", "component_id": "CMP-306"}
]

RELATIONS_SUPPLIES = [
    {"supplier_id": "SUP-101", "component_id": "CMP-301", "unitCost": 450.0, "leadTimeDays": 120},
    {"supplier_id": "SUP-102", "component_id": "CMP-302", "unitCost": 8200.0, "leadTimeDays": 210},
    {"supplier_id": "SUP-103", "component_id": "CMP-303", "unitCost": 65.0, "leadTimeDays": 45},
    {"supplier_id": "SUP-104", "component_id": "CMP-304", "unitCost": 28.0, "leadTimeDays": 60},
    {"supplier_id": "SUP-105", "component_id": "CMP-304", "unitCost": 22.0, "leadTimeDays": 75},
    {"supplier_id": "SUP-106", "component_id": "CMP-306", "unitCost": 410.0, "leadTimeDays": 90}
]

RELATIONS_REQUIRES = [
    {"parent_comp_id": "CMP-302", "child_comp_id": "CMP-301", "quantity": 1},
    {"parent_comp_id": "CMP-304", "child_comp_id": "CMP-301", "quantity": 2}
]

RELATIONS_PART_OF = [
    {"component_id": "CMP-301", "product_id": "PRD-401", "quantity": 4},
    {"component_id": "CMP-303", "product_id": "PRD-401", "quantity": 16},
    {"component_id": "CMP-301", "product_id": "PRD-402", "quantity": 1},
    {"component_id": "CMP-305", "product_id": "PRD-402", "quantity": 2},
    {"component_id": "CMP-303", "product_id": "PRD-403", "quantity": 2}
]

RELATIONS_ALTERNATIVE = [
    {"primary_id": "CMP-301", "alt_id": "CMP-306", "switchLeadTimeDays": 30, "costDeltaPct": 12.5}
]

RELATIONS_AFFECTS = [
    {"disruption_id": "DIS-501", "facility_id": "FAC-201"},
    {"disruption_id": "DIS-501", "supplier_id": "SUP-101"}
]


def seed_cognodb():
    uri = settings.COGNODB_URI
    user = settings.COGNODB_USER
    password = settings.COGNODB_PASSWORD

    logger.info(f"Connecting to CognoDB Cloud at {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        logger.info("Successfully connected to CognoDB instance!")
    except Exception as e:
        logger.error(f"Failed to connect to CognoDB Cloud: {e}")
        logger.info("Please verify your COGNODB_URI and COGNODB_PASSWORD in .env")
        sys.exit(1)

    with driver.session() as session:
        logger.info("Purging existing nodes & relationships...")
        session.run("MATCH (n) DETACH DELETE n")

        # 1. Create Nodes via Parameterized Cypher
        logger.info("Seeding Supplier nodes...")
        cypher_supplier = """
        UNWIND $suppliers AS s
        CREATE (:Supplier {
            id: s.id,
            name: s.name,
            tier: s.tier,
            country: s.country,
            riskScore: s.riskScore,
            status: s.status
        })
        """
        session.run(cypher_supplier, {"suppliers": SUPPLIERS})

        logger.info("Seeding Facility nodes...")
        cypher_facility = """
        UNWIND $facilities AS f
        CREATE (:Facility {
            id: f.id,
            name: f.name,
            city: f.city,
            country: f.country,
            facilityType: f.facilityType
        })
        """
        session.run(cypher_facility, {"facilities": FACILITIES})

        logger.info("Seeding Component nodes...")
        cypher_component = """
        UNWIND $components AS c
        CREATE (:Component {
            id: c.id,
            name: c.name,
            sku: c.sku,
            category: c.category,
            criticality: c.criticality,
            leadTimeDays: c.leadTimeDays
        })
        """
        session.run(cypher_component, {"components": COMPONENTS})

        logger.info("Seeding Product nodes...")
        cypher_product = """
        UNWIND $products AS p
        CREATE (:Product {
            id: p.id,
            name: p.name,
            sku: p.sku,
            category: p.category,
            retailPrice: p.retailPrice,
            marginPct: p.marginPct
        })
        """
        session.run(cypher_product, {"products": PRODUCTS})

        logger.info("Seeding Disruption nodes...")
        cypher_disruption = """
        UNWIND $disruptions AS d
        CREATE (:Disruption {
            id: d.id,
            title: d.title,
            type: d.type,
            severity: d.severity,
            impactedRegion: d.impactedRegion,
            description: d.description
        })
        """
        session.run(cypher_disruption, {"disruptions": DISRUPTIONS})

        # 2. Create Parameterized Relationships
        logger.info("Creating OPERATES relationships...")
        cypher_operates = """
        UNWIND $rels AS r
        MATCH (s:Supplier {id: r.supplier_id})
        MATCH (f:Facility {id: r.facility_id})
        CREATE (s)-[:OPERATES]->(f)
        """
        session.run(cypher_operates, {"rels": RELATIONS_OPERATES})

        logger.info("Creating MANUFACTURES relationships...")
        cypher_mfg = """
        UNWIND $rels AS r
        MATCH (f:Facility {id: r.facility_id})
        MATCH (c:Component {id: r.component_id})
        CREATE (f)-[:MANUFACTURES]->(c)
        """
        session.run(cypher_mfg, {"rels": RELATIONS_MANUFACTURES})

        logger.info("Creating SUPPLIES relationships...")
        cypher_supplies = """
        UNWIND $rels AS r
        MATCH (s:Supplier {id: r.supplier_id})
        MATCH (c:Component {id: r.component_id})
        CREATE (s)-[:SUPPLIES {unitCost: r.unitCost, leadTimeDays: r.leadTimeDays}]->(c)
        """
        session.run(cypher_supplies, {"rels": RELATIONS_SUPPLIES})

        logger.info("Creating REQUIRES sub-assembly relationships...")
        cypher_requires = """
        UNWIND $rels AS r
        MATCH (parent:Component {id: r.parent_comp_id})
        MATCH (child:Component {id: r.child_comp_id})
        CREATE (parent)-[:REQUIRES {quantity: r.quantity}]->(child)
        """
        session.run(cypher_requires, {"rels": RELATIONS_REQUIRES})

        logger.info("Creating PART_OF product assembly relationships...")
        cypher_partof = """
        UNWIND $rels AS r
        MATCH (c:Component {id: r.component_id})
        MATCH (p:Product {id: r.product_id})
        CREATE (c)-[:PART_OF {quantity: r.quantity}]->(p)
        """
        session.run(cypher_partof, {"rels": RELATIONS_PART_OF})

        logger.info("Creating ALTERNATIVE_TO relationships...")
        cypher_alt = """
        UNWIND $rels AS r
        MATCH (c1:Component {id: r.primary_id})
        MATCH (c2:Component {id: r.alt_id})
        CREATE (c1)-[:ALTERNATIVE_TO {switchLeadTimeDays: r.switchLeadTimeDays, costDeltaPct: r.costDeltaPct}]->(c2)
        """
        session.run(cypher_alt, {"rels": RELATIONS_ALTERNATIVE})

        logger.info("Creating AFFECTS disruption relationships...")
        cypher_affects_fac = """
        UNWIND $rels AS r
        MATCH (d:Disruption {id: r.disruption_id})
        MATCH (f:Facility {id: r.facility_id})
        CREATE (d)-[:AFFECTS]->(f)
        """
        session.run(cypher_affects_fac, {"rels": RELATIONS_AFFECTS})

        # Verification Query
        result = session.run("""
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->()
        RETURN count(DISTINCT n) AS nodeCount, count(r) AS relCount
        """).single()

        logger.info(f"SEEDING COMPLETE! Database now contains {result['nodeCount']} nodes and {result['relCount']} relationships.")

    driver.close()


if __name__ == "__main__":
    seed_cognodb()
