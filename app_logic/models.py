from app_logic import db
from datetime import datetime


class StopRequest(db.Model):
    __tablename__ = 'stop_requests'

    id         = db.Column(db.Integer, primary_key=True)
    line_code  = db.Column(db.String(20), nullable=False, index=True)
    lat        = db.Column(db.Float, nullable=False)
    lon        = db.Column(db.Float, nullable=False)
    note           = db.Column(db.String(300), nullable=True)
    preferred_days = db.Column(db.String(100), nullable=True) # e.g. "lun,mar,mer"
    preferred_time = db.Column(db.String(20), nullable=True)  # e.g. "14:30"
    status         = db.Column(db.String(20), nullable=False, default='pending')  # pending | approved | rejected
    created_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'line_code': self.line_code,
            'lat': self.lat,
            'lon': self.lon,
            'note': self.note,
            'preferred_days': self.preferred_days,
            'preferred_time': self.preferred_time,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }


class ApprovedStop(db.Model):
    """
    Persists approved stops so the citizen map reflects them dynamically.
    These are layered on top of the original shapefile data.
    """
    __tablename__ = 'approved_stops'

    id           = db.Column(db.Integer, primary_key=True)
    line_code    = db.Column(db.String(20), nullable=False, index=True)
    lat          = db.Column(db.Float, nullable=False)
    lon          = db.Column(db.Float, nullable=False)
    insert_after = db.Column(db.Integer, nullable=True)   # index in the original sequence
    approved_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    request_id   = db.Column(db.Integer, db.ForeignKey('stop_requests.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'line_code': self.line_code,
            'lat': self.lat,
            'lon': self.lon,
            'insert_after': self.insert_after,
            'approved_at': self.approved_at.isoformat(),
        }
