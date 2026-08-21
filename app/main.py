import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.database import db_manager
from app.graph_queries import GraphQueryRepository
from app.models import GraphResponse, BlastRadiusResponse, SpofResponse

app = FastAPI(
    title="NexusChain — Graph-Powered Supply Chain Navigator",
    description="Managed Graph Database Application powered by CognoDB Cloud (openCypher over Bolt protocol)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve UI Static Assets
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def get_index():
    """Serves the main application user interface."""
    return FileResponse("static/index.html")


@app.get("/api/health")
async def get_health():
    """
    Returns database connection status and CognoDB configuration details.
    """
    return {
        "status": "online",
        "cognoDB": {
            "uri": settings.COGNODB_URI,
            "connected": db_manager.is_connected,
            "user": settings.COGNODB_USER,
            "error": db_manager.error_message
        }
    }


@app.get("/api/graph/full", response_model=GraphResponse)
async def get_full_graph():
    """
    Returns full network graph topology (Nodes & Edges) and executed openCypher query.
    """
    return GraphQueryRepository.get_full_graph()


@app.get("/api/graph/blast-radius/{supplier_id}", response_model=BlastRadiusResponse)
async def get_blast_radius(supplier_id: str):
    """
    Performs multi-hop graph traversal (1 to 5 hops) from a Supplier down to end Products.
    """
    return GraphQueryRepository.get_multi_hop_blast_radius(supplier_id)


@app.get("/api/graph/spof", response_model=SpofResponse)
async def get_single_points_of_failure():
    """
    Executes graph pattern query to discover Single Points of Failure (SPOF).
    """
    return GraphQueryRepository.get_single_points_of_failure()


@app.get("/api/graph/alternatives/{component_id}")
async def get_alternatives(component_id: str):
    """
    Queries graph for mitigation alternative pathways for a given component.
    """
    return GraphQueryRepository.get_alternative_pathways(component_id)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
