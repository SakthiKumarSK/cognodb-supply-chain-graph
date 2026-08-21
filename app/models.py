from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class NodeModel(BaseModel):
    id: str
    label: str
    name: str
    type: str
    tier: Optional[int] = None
    country: Optional[str] = None
    riskScore: Optional[int] = None
    status: Optional[str] = None
    city: Optional[str] = None
    facilityType: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    criticality: Optional[str] = None
    leadTimeDays: Optional[int] = None
    retailPrice: Optional[float] = None
    marginPct: Optional[float] = None
    severity: Optional[str] = None
    impactedRegion: Optional[str] = None

class EdgeModel(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    label: str
    relation: Optional[str] = None
    unitCost: Optional[float] = None
    leadTimeDays: Optional[int] = None
    quantity: Optional[int] = None
    switchLeadTimeDays: Optional[int] = None
    costDeltaPct: Optional[float] = None

    class Config:
        populate_by_name = True

class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    cypher: str
    source: str

class BlastRadiusResponse(BaseModel):
    supplier_id: str
    results: List[Dict[str, Any]]
    cypher: str
    params: Dict[str, Any]
    source: str

class SpofResponse(BaseModel):
    spofs: List[Dict[str, Any]]
    cypher: str
    source: str
