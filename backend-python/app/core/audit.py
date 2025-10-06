import hashlib
from sqlalchemy.orm import Session
from ..models.overpass_audit import OverpassAudit
def sha1(s: str) -> str:
    import hashlib
    return hashlib.sha1(s.encode('utf-8')).hexdigest()
def log_overpass_audit(db: Session, user_id: str, query: str, bbox: str, status: str = "success"):
    if db is None: return
    rec = OverpassAudit(user_id=user_id, query_hash=sha1(query), bbox=bbox, status=status)
    db.add(rec); db.commit()
