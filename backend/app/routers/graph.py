from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import document, node, edge

router = APIRouter()

@router.get("/{doc_id}")
def get_graph(doc_id: str, db: Session = Depends(get_db)):
    nodes = db.query(node.Node).filter(node.Node.document_id == doc_id).all()
    edges = db.query(edge.Edge).filter(edge.Edge.document_id == doc_id).all()
    
    # If no graph generated yet, return a placeholder
    if not nodes:
        # We'll populate real nodes in Phase 2
        nodes = [
            {"id": "n1", "label": "Introduction", "group": 1, "size": 30, "color": "#a5d8ff"},
            {"id": "n2", "label": "Core Concepts", "group": 2, "size": 25, "color": "#d0bfff"},
            {"id": "n3", "label": "Applications", "group": 3, "size": 20, "color": "#b2f2bb"},
        ]
        edges = [
            {"from": "n1", "to": "n2"},
            {"from": "n2", "to": "n3"},
        ]
    else:
        nodes = [{"id": n.id, "label": n.label, "group": n.weight, "size": 25 + n.weight * 5, "color": n.color or "#a5d8ff"} for n in nodes]
        edges = [{"from": e.source_id, "to": e.target_id} for e in edges]
    
    return {"nodes": nodes, "edges": edges}
