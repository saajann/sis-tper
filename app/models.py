from app import db
from datetime import datetime

class StopRequest(db.Model):
    __tablename__ = 'stop_requests'

    id = db.Column(db.Integer, primary_key=True)
    line_code = db.Column(db.String(20), nullable=False, index=True)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending | approved | rejected
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'line_code': self.line_code,
            'lat': self.lat,
            'lon': self.lon,
            'note': self.note,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
