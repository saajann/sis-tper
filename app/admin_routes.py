import os
import json
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app import db
from app.models import StopRequest
from app.utils.optimizer import optimize_route, get_existing_stops
import geopandas as gpd

admin = Blueprint('admin', __name__)

def _data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def _admin_required():
    return session.get('is_admin', False)

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

@admin.route('/dashboard')
def dashboard():
    if not _admin_required():
        return redirect(url_for('admin.login'))

    pending  = StopRequest.query.filter_by(status='pending').order_by(StopRequest.line_code, StopRequest.created_at).all()
    approved = StopRequest.query.filter_by(status='approved').order_by(StopRequest.created_at.desc()).limit(20).all()
    rejected = StopRequest.query.filter_by(status='rejected').order_by(StopRequest.created_at.desc()).limit(20).all()

    line_stats = defaultdict(int)
    for r in pending:
        line_stats[r.line_code] += 1

    return render_template('admin_dashboard.html',
                           pending=pending,
                           approved=approved,
                           rejected=rejected,
                           line_stats=dict(line_stats))

# ── Preview endpoint ──────────────────────────────────────────────────────────
@admin.route('/preview/<int:req_id>')
def preview(req_id):
    """Return before/after stop sequences as JSON for the mini-map."""
    if not _admin_required():
        return jsonify({'ok': False}), 403

    req = StopRequest.query.get_or_404(req_id)
    data_dir = _data_dir()

    before = get_existing_stops(req.line_code, data_dir)
    after  = optimize_route(req.line_code, req.lat, req.lon, data_dir)

    return jsonify({
        'ok': True,
        'new_point': {'lat': req.lat, 'lon': req.lon},
        'before': before,
        'after': after,
        'line_code': req.line_code,
    })

# ── Approve / Reject ──────────────────────────────────────────────────────────
@admin.route('/approve/<int:req_id>', methods=['POST'])
def approve(req_id):
    if not _admin_required():
        return jsonify({'ok': False}), 403
    req = StopRequest.query.get_or_404(req_id)
    req.status = 'approved'
    db.session.commit()

    data_dir = _data_dir()
    after = optimize_route(req.line_code, req.lat, req.lon, data_dir)
    return jsonify({'ok': True, 'optimized_route': after})

@admin.route('/reject/<int:req_id>', methods=['POST'])
def reject(req_id):
    if not _admin_required():
        return jsonify({'ok': False}), 403
    req = StopRequest.query.get_or_404(req_id)
    req.status = 'rejected'
    db.session.commit()
    return jsonify({'ok': True})
