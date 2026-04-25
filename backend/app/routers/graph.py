from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Node, Edge
from typing import List, Dict, Any

router = APIRouter()

@router.get("/{doc_id}")
def get_graph(doc_id: str, db: Session = Depends(get_db)):
    nodes = db.query(Node).filter(Node.document_id == doc_id).all()
    edges = db.query(Edge).filter(Edge.document_id == doc_id).all()

    if not nodes:
        return {
            "nodes": [
                {"id": "n1", "label": "Introduction", "group": 1, "size": 30, "color": "#a5d8ff"},
                {"id": "n2", "label": "Core Concepts", "group": 2, "size": 25, "color": "#d0bfff"},
                {"id": "n3", "label": "Applications", "group": 3, "size": 20, "color": "#b2f2bb"},
            ],
            "edges": [
                {"from": "n1", "to": "n2"},
                {"from": "n2", "to": "n3"},
            ],
        }

    node_list = []
    for n in nodes:
        node_list.append({
            "id": n.id,
            "label": n.label,
            "group": n.weight or 3,
            "size": 20 + (n.weight or 3) * 4,
            "color": n.color or "#a5d8ff",
            "title": n.summary or n.label,
        })

    edge_list = []
    for e in edges:
        edge_list.append({
            "from": e.source_id,
            "to": e.target_id,
        })

    return {"nodes": node_list, "edges": edge_list}
