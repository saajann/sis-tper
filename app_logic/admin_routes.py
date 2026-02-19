import os
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app_logic import db
from app_logic.models import StopRequest, ApprovedStop
from app_logic.utils.optimizer import optimize_route, get_existing_stops, get_full_route, cluster_requests

admin = Blueprint('admin', __name__)

def _data_dir():
    # app/admin_routes.py → app/ → sis-tper/ → data/
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def _admin_required():
    return session.get('is_admin', False)

# ── Auth ──────────────────────────────────────────────────────────────────────

@admin.route('/')
def index():
    if not _admin_required():
        return redirect(url_for('admin.login'))
    return redirect(url_for('admin.dashboard'))

@admin.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == current_app.config['ADMIN_PASSWORD']:
            session['is_admin'] = True
            return redirect(url_for('admin.dashboard'))
        flash('Password errata')
    return render_template('admin_login.html')

@admin.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin.login'))

# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin.route('/dashboard')
def dashboard():
    if not _admin_required():
        return redirect(url_for('admin.login'))

    pending  = StopRequest.query.filter_by(status='pending').order_by(StopRequest.line_code, StopRequest.created_at).all()
    approved = StopRequest.query.filter_by(status='approved').order_by(StopRequest.created_at.desc()).limit(20).all()
    rejected = StopRequest.query.filter_by(status='rejected').order_by(StopRequest.created_at.desc()).limit(20).all()

    # Cluster pending requests per line
    line_clusters = defaultdict(list)
    for r in pending:
        line_clusters[r.line_code].append(r)

    clustered = {}
    for line, reqs in line_clusters.items():
        clustered[line] = cluster_requests(reqs)

    line_stats = {line: len(reqs) for line, reqs in line_clusters.items()}

    return render_template('admin_dashboard.html',
                           pending=pending,
                           approved=approved,
                           rejected=rejected,
                           line_stats=line_stats,
                           clustered=clustered)

# ── Preview (before / after) ──────────────────────────────────────────────────

@admin.route('/preview/<int:req_id>')
def preview(req_id):
    if not _admin_required():
        return jsonify({'ok': False}), 403

    req = StopRequest.query.get_or_404(req_id)
    data_dir = _data_dir()

    # Approved stops already in DB for this line
    existing_approved = ApprovedStop.query.filter_by(line_code=req.line_code).all()

    before = get_full_route(req.line_code, data_dir, existing_approved)
    after, insert_idx = optimize_route(req.line_code, req.lat, req.lon, data_dir, existing_approved)

    return jsonify({
        'ok': True,
        'new_point': {'lat': req.lat, 'lon': req.lon},
        'before': before,
        'after': after,
        'line_code': req.line_code,
        'insert_idx': insert_idx,
    })

# ── Approve ───────────────────────────────────────────────────────────────────

@admin.route('/approve/<int:req_id>', methods=['POST'])
def approve(req_id):
    if not _admin_required():
        return jsonify({'ok': False}), 403

    req = StopRequest.query.get_or_404(req_id)
    data_dir = _data_dir()

    existing_approved = ApprovedStop.query.filter_by(line_code=req.line_code).all()
    after, insert_idx = optimize_route(req.line_code, req.lat, req.lon, data_dir, existing_approved)

    # Persist the approved stop
    approved_stop = ApprovedStop(
        line_code=req.line_code,
        lat=req.lat,
        lon=req.lon,
        insert_after=insert_idx,
        request_id=req.id,
    )
    req.status = 'approved'
    db.session.add(approved_stop)
    db.session.commit()

    return jsonify({'ok': True, 'optimized_route': after, 'line_code': req.line_code})

# ── Reject ────────────────────────────────────────────────────────────────────

@admin.route('/reject/<int:req_id>', methods=['POST'])
def reject(req_id):
    if not _admin_required():
        return jsonify({'ok': False}), 403
    req = StopRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    db.session.commit()
    return jsonify({'ok': True})

# ── Approve cluster (bulk) ────────────────────────────────────────────────────

@admin.route('/approve-cluster', methods=['POST'])
def approve_cluster():
    """Approve a cluster of requests, using their centroid as the new stop."""
    if not _admin_required():
        return jsonify({'ok': False}), 403

    data = request.get_json()
    ids = data.get('ids', [])
    lat = data.get('lat')
    lon = data.get('lon')
    line_code = data.get('line_code')

    if not ids or lat is None or lon is None or not line_code:
        return jsonify({'ok': False, 'error': 'Dati mancanti'}), 400

    data_dir = _data_dir()
    existing_approved = ApprovedStop.query.filter_by(line_code=line_code).all()
    after, insert_idx = optimize_route(line_code, lat, lon, data_dir, existing_approved)

    approved_stop = ApprovedStop(
        line_code=line_code,
        lat=lat,
        lon=lon,
        insert_after=insert_idx,
    )
    db.session.add(approved_stop)

    # Mark all requests in cluster as approved
    StopRequest.query.filter(StopRequest.id.in_(ids)).update(
        {'status': 'approved'}, synchronize_session=False
    )
    db.session.commit()

    return jsonify({'ok': True, 'optimized_route': after, 'line_code': line_code})
