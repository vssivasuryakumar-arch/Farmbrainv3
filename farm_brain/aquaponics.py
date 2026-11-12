"""Magppliv Aquaponics Phase 1: manual records, user-configured alerts and reports.

This module never labels manual readings as sensor readings. Thresholds are blank
by default and must be configured by a qualified person for each farm/system.
"""
from datetime import date
from decimal import Decimal, InvalidOperation
from math import isfinite
import csv
import io
import json

from flask import Blueprint, abort, flash, make_response, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .extensions import db
from .models import (
    AquaponicsAlert, AquaponicsCrop, AquaponicsExperiment, AquaponicsFarm,
    AquaponicsFinanceEntry, AquaponicsFishLog, AquaponicsMembership,
    AquaponicsSystem, AquaponicsTank, AquaponicsWaterReading, utcnow,
)


aqua_bp = Blueprint("aquaponics", __name__, url_prefix="/aquaponics")
EDIT_ROLES = {"owner", "r_and_d_manager", "aquaculture_specialist", "horticulture_specialist", "operator", "research_collaborator", "partner_farm_manager"}
ROLE_OPTIONS = {
    "r_and_d_manager", "aquaculture_specialist", "horticulture_specialist",
    "operator", "research_collaborator", "partner_farm_manager", "investor_readonly",
}


def farm_membership(farm_id: int):
    farm = db.get_or_404(AquaponicsFarm, farm_id)
    membership = AquaponicsMembership.query.filter_by(
        farm_id=farm.id, user_id=current_user.id
    ).first()
    if not membership:
        abort(404)
    return farm, membership


def require_editor(membership):
    if membership.role not in EDIT_ROLES:
        abort(403)


def optional_float(value, label, min_value=None, max_value=None):
    value = (value or "").strip()
    if not value:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Enter a valid {label}.")
    if not isfinite(number) or (min_value is not None and number < min_value) or (max_value is not None and number > max_value):
        raise ValueError(f"Check the allowed range for {label}.")
    return number


def _create_threshold_alert(farm, reading, system):
    """Create alerts only when farm-specific thresholds have been configured."""
    checks = [
        ("pH", reading.ph, system.ph_min, system.ph_max, "Review the sensor calibration and the farm's approved water-quality SOP. Do not dose chemicals based on this alert alone."),
        ("Water temperature °C", reading.temperature_c, system.temperature_min_c, system.temperature_max_c, "Verify the reading with a calibrated thermometer and inspect the system's temperature-control plan."),
        ("Dissolved oxygen mg/L", reading.dissolved_oxygen_mg_l, system.dissolved_oxygen_min_mg_l, None, "Check aeration, circulation, sensor calibration and the farm's emergency response plan. Seek aquaculture specialist advice."),
        ("Ammonia mg/L", reading.ammonia_mg_l, None, system.ammonia_max_mg_l, "Confirm the test method and units, review feeding and biofilter records, and consult a qualified aquaculture specialist before changing the system."),
        ("Nitrite mg/L", reading.nitrite_mg_l, None, system.nitrite_max_mg_l, "Repeat the test with a verified method and consult the farm's aquaculture specialist before treatment or dosing."),
    ]
    for metric, value, lower, upper, action in checks:
        if value is None:
            continue
        outside = (lower is not None and value < lower) or (upper is not None and value > upper)
        if not outside:
            continue
        threshold = f"configured min={lower if lower is not None else 'not set'}; max={upper if upper is not None else 'not set'}"
        db.session.add(AquaponicsAlert(
            farm_id=farm.id, reading_id=reading.id, metric=metric,
            severity="warning", measured_value=value, threshold_text=threshold,
            message=f"{metric} is outside this farm's configured threshold.",
            recommended_action=action, status="open",
        ))


@aqua_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:160]
        mode = request.form.get("mode", "").strip()
        country = request.form.get("country", "").strip().upper()
        location = request.form.get("location", "").strip()[:200]
        partner_name = request.form.get("partner_name", "").strip()[:160]
        notes = request.form.get("notes", "").strip()[:2000]
        expected = {"india_rnd": ("IN", "INR"), "uae_pilot": ("AE", "AED")}
        if not name or mode not in expected or country != expected[mode][0]:
            flash("Choose India R&D with India, or UAE commercial pilot with UAE.", "error")
            return redirect(url_for("aquaponics.index"))
        farm = AquaponicsFarm(
            name=name, owner_id=current_user.id, country=country, mode=mode,
            currency=expected[mode][1], location=location,
            partner_name=partner_name, notes=notes, status="planning",
        )
        db.session.add(farm)
        db.session.flush()
        db.session.add(AquaponicsMembership(farm_id=farm.id, user_id=current_user.id, role="owner"))
        db.session.add(AquaponicsSystem(farm_id=farm.id, name="Primary system"))
        db.session.commit()
        flash("Aquaponics workspace created. Record readings manually until a real sensor integration is configured.", "success")
        return redirect(url_for("aquaponics.dashboard", farm_id=farm.id))
    farm_ids = [row.farm_id for row in AquaponicsMembership.query.filter_by(user_id=current_user.id).all()]
    farms = AquaponicsFarm.query.filter(AquaponicsFarm.id.in_(farm_ids)).order_by(AquaponicsFarm.created_at.desc()).all() if farm_ids else []
    return render_template("aquaponics/index.html", farms=farms)


@aqua_bp.get("/farm/<int:farm_id>")
@login_required
def dashboard(farm_id):
    farm, membership = farm_membership(farm_id)
    systems = AquaponicsSystem.query.filter_by(farm_id=farm.id).all()
    tanks = AquaponicsTank.query.join(AquaponicsSystem).filter(AquaponicsSystem.farm_id == farm.id).all()
    latest_reading = AquaponicsWaterReading.query.filter_by(farm_id=farm.id).order_by(AquaponicsWaterReading.recorded_at.desc()).first()
    open_alerts = AquaponicsAlert.query.filter_by(farm_id=farm.id, status="open").order_by(AquaponicsAlert.created_at.desc()).limit(10).all()
    crops = AquaponicsCrop.query.filter_by(farm_id=farm.id).order_by(AquaponicsCrop.created_at.desc()).limit(10).all()
    experiments = AquaponicsExperiment.query.filter_by(farm_id=farm.id).order_by(AquaponicsExperiment.created_at.desc()).limit(5).all()
    fish_biomass = round(sum(t.estimated_biomass_kg or 0 for t in tanks), 3)
    expense = db.session.query(db.func.coalesce(db.func.sum(AquaponicsFinanceEntry.amount), 0)).filter_by(farm_id=farm.id, entry_type="expense").scalar()
    revenue = db.session.query(db.func.coalesce(db.func.sum(AquaponicsFinanceEntry.amount), 0)).filter_by(farm_id=farm.id, entry_type="revenue").scalar()
    return render_template(
        "aquaponics/dashboard.html", farm=farm, membership=membership,
        systems=systems, tanks=tanks, latest_reading=latest_reading,
        open_alerts=open_alerts, crops=crops, experiments=experiments,
        fish_biomass=fish_biomass, expense=expense, revenue=revenue,
    )


@aqua_bp.route("/farm/<int:farm_id>/system", methods=["GET", "POST"])
@login_required
def system_config(farm_id):
    farm, membership = farm_membership(farm_id)
    if request.method == "POST":
        require_editor(membership)
        name = request.form.get("name", "Primary system").strip()[:160]
        system = AquaponicsSystem.query.filter_by(farm_id=farm.id).first()
        if not system:
            system = AquaponicsSystem(farm_id=farm.id, name=name)
            db.session.add(system)
        system.name = name or "Primary system"
        raw_layout = request.form.get("configuration_json", "{}").strip() or "{}"
        try:
            layout = json.loads(raw_layout)
            if not isinstance(layout, dict):
                raise ValueError
            system.configuration_json = json.dumps(layout, ensure_ascii=False)
        except (TypeError, ValueError, json.JSONDecodeError):
            flash("System layout must be a valid JSON object.", "error")
            return redirect(url_for("aquaponics.system_config", farm_id=farm.id))
        try:
            system.ph_min = optional_float(request.form.get("ph_min"), "minimum pH", 0, 14)
            system.ph_max = optional_float(request.form.get("ph_max"), "maximum pH", 0, 14)
            system.temperature_min_c = optional_float(request.form.get("temperature_min_c"), "minimum temperature", -5, 60)
            system.temperature_max_c = optional_float(request.form.get("temperature_max_c"), "maximum temperature", -5, 60)
            system.dissolved_oxygen_min_mg_l = optional_float(request.form.get("dissolved_oxygen_min_mg_l"), "minimum dissolved oxygen", 0, 100)
            system.ammonia_max_mg_l = optional_float(request.form.get("ammonia_max_mg_l"), "maximum ammonia", 0, 1000)
            system.nitrite_max_mg_l = optional_float(request.form.get("nitrite_max_mg_l"), "maximum nitrite", 0, 1000)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("aquaponics.system_config", farm_id=farm.id))
        if system.ph_min is not None and system.ph_max is not None and system.ph_min > system.ph_max:
            flash("Minimum pH cannot be greater than maximum pH.", "error")
            return redirect(url_for("aquaponics.system_config", farm_id=farm.id))
        if system.temperature_min_c is not None and system.temperature_max_c is not None and system.temperature_min_c > system.temperature_max_c:
            flash("Minimum temperature cannot be greater than maximum temperature.", "error")
            return redirect(url_for("aquaponics.system_config", farm_id=farm.id))
        db.session.commit()
        flash("System configuration saved. Thresholds are farm-defined, not universal safety advice.", "success")
        return redirect(url_for("aquaponics.dashboard", farm_id=farm.id))
    system = AquaponicsSystem.query.filter_by(farm_id=farm.id).first()
    return render_template("aquaponics/system.html", farm=farm, membership=membership, system=system)


@aqua_bp.route("/farm/<int:farm_id>/water", methods=["GET", "POST"])
@login_required
def water_quality(farm_id):
    farm, membership = farm_membership(farm_id)
    systems = AquaponicsSystem.query.filter_by(farm_id=farm.id).all()
    if request.method == "POST":
        require_editor(membership)
        system_id = request.form.get("system_id", type=int)
        system = AquaponicsSystem.query.filter_by(id=system_id, farm_id=farm.id).first()
        if not system:
            abort(400)
        try:
            reading = AquaponicsWaterReading(
                farm_id=farm.id, system_id=system.id, recorded_by=current_user.id,
                source="manual",
                temperature_c=optional_float(request.form.get("temperature_c"), "temperature", -5, 60),
                ph=optional_float(request.form.get("ph"), "pH", 0, 14),
                dissolved_oxygen_mg_l=optional_float(request.form.get("dissolved_oxygen_mg_l"), "dissolved oxygen", 0, 100),
                ammonia_mg_l=optional_float(request.form.get("ammonia_mg_l"), "ammonia", 0, 1000),
                nitrite_mg_l=optional_float(request.form.get("nitrite_mg_l"), "nitrite", 0, 1000),
                nitrate_mg_l=optional_float(request.form.get("nitrate_mg_l"), "nitrate", 0, 10000),
                ec_ms_cm=optional_float(request.form.get("ec_ms_cm"), "EC", 0, 100),
                water_level_percent=optional_float(request.form.get("water_level_percent"), "water level", 0, 100),
                flow_l_min=optional_float(request.form.get("flow_l_min"), "flow", 0, 100000),
                alkalinity_mg_l=optional_float(request.form.get("alkalinity_mg_l"), "alkalinity", 0, 10000),
                notes=request.form.get("notes", "").strip()[:1200],
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("aquaponics.water_quality", farm_id=farm.id))
        db.session.add(reading)
        db.session.flush()
        _create_threshold_alert(farm, reading, system)
        db.session.commit()
        flash("Manual water-quality reading saved. It is not a live sensor measurement.", "success")
        return redirect(url_for("aquaponics.water_quality", farm_id=farm.id))
    readings = AquaponicsWaterReading.query.filter_by(farm_id=farm.id).order_by(AquaponicsWaterReading.recorded_at.desc()).limit(100).all()
    return render_template("aquaponics/water.html", farm=farm, membership=membership, systems=systems, readings=readings)


@aqua_bp.route("/farm/<int:farm_id>/fish", methods=["GET", "POST"])
@login_required
def fish_management(farm_id):
    farm, membership = farm_membership(farm_id)
    tanks = AquaponicsTank.query.join(AquaponicsSystem).filter(AquaponicsSystem.farm_id == farm.id).order_by(AquaponicsTank.name.asc()).all()
    if request.method == "POST":
        require_editor(membership)
        action = request.form.get("action", "log")
        if action == "create_tank":
            system = AquaponicsSystem.query.filter_by(id=request.form.get("system_id", type=int), farm_id=farm.id).first()
            name = request.form.get("name", "").strip()[:100]
            species = request.form.get("species", "").strip()[:100]
            try:
                count = int(request.form.get("stocked_count", "0"))
                weight = optional_float(request.form.get("average_weight_g"), "average fish weight", 0, 100000)
                volume = optional_float(request.form.get("volume_litres"), "tank volume", 0, 100000000)
                if count < 0 or count > 10000000 or not system or not name:
                    raise ValueError("Check the tank name, fish count and system.")
            except ValueError as exc:
                flash(str(exc), "error")
                return redirect(url_for("aquaponics.fish_management", farm_id=farm.id))
            db.session.add(AquaponicsTank(system_id=system.id, name=name, species=species,
                                          stocked_count=count, current_count=count,
                                          average_weight_g=weight, volume_litres=volume))
            db.session.commit()
            flash("Fish tank created.", "success")
            return redirect(url_for("aquaponics.fish_management", farm_id=farm.id))
        tank = AquaponicsTank.query.join(AquaponicsSystem).filter(
            AquaponicsTank.id == request.form.get("tank_id", type=int),
            AquaponicsSystem.farm_id == farm.id,
        ).first()
        if not tank:
            abort(400)
        log_type = request.form.get("log_type", "")
        if log_type not in {"feed", "mortality", "sample", "harvest"}:
            abort(400)
        try:
            quantity = optional_float(request.form.get("quantity_kg"), "quantity", 0, 100000)
            count = int(request.form.get("fish_count", "0") or 0)
            weight = optional_float(request.form.get("average_weight_g"), "average weight", 0, 100000)
            if count < 0 or count > 10000000:
                raise ValueError("Check the fish count.")
            if log_type in {"mortality", "harvest"} and count > tank.current_count:
                raise ValueError("The recorded fish count cannot exceed the current population.")
            if log_type == "feed" and (quantity is None or quantity <= 0):
                raise ValueError("Enter feed quantity in kilograms.")
            if log_type == "sample" and (weight is None or weight <= 0):
                raise ValueError("Enter the sampled average fish weight in grams.")
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("aquaponics.fish_management", farm_id=farm.id))
        log = AquaponicsFishLog(farm_id=farm.id, tank_id=tank.id, user_id=current_user.id,
                                log_type=log_type, quantity_kg=quantity, fish_count=count,
                                average_weight_g=weight, notes=request.form.get("notes", "").strip()[:1200])
        if log_type in {"mortality", "harvest"}:
            tank.current_count -= count
        elif log_type == "sample":
            tank.average_weight_g = weight
        db.session.add(log)
        db.session.commit()
        flash("Fish activity recorded.", "success")
        return redirect(url_for("aquaponics.fish_management", farm_id=farm.id))
    logs = AquaponicsFishLog.query.filter_by(farm_id=farm.id).order_by(AquaponicsFishLog.logged_at.desc()).limit(100).all()
    biomass = round(sum(t.estimated_biomass_kg or 0 for t in tanks), 3)
    return render_template("aquaponics/fish.html", farm=farm, membership=membership, systems=AquaponicsSystem.query.filter_by(farm_id=farm.id).all(), tanks=tanks, logs=logs, biomass=biomass)


@aqua_bp.route("/farm/<int:farm_id>/crops", methods=["GET", "POST"])
@login_required
def crop_management(farm_id):
    farm, membership = farm_membership(farm_id)
    systems = AquaponicsSystem.query.filter_by(farm_id=farm.id).all()
    if request.method == "POST":
        require_editor(membership)
        system = AquaponicsSystem.query.filter_by(id=request.form.get("system_id", type=int), farm_id=farm.id).first()
        crop = request.form.get("crop", "").strip()[:100]
        method = request.form.get("growing_method", "DWC").strip()
        if not system or not crop or method not in {"DWC", "NFT", "media bed", "ebb and flow", "other"}:
            flash("Check crop, growing method and system.", "error")
            return redirect(url_for("aquaponics.crop_management", farm_id=farm.id))
        try:
            count = int(request.form.get("plant_count", "0"))
            planted = date.fromisoformat(request.form["planted_on"]) if request.form.get("planted_on") else None
            expected = date.fromisoformat(request.form["expected_harvest"]) if request.form.get("expected_harvest") else None
            if count < 0 or count > 10000000 or (planted and expected and expected < planted):
                raise ValueError
        except (TypeError, ValueError):
            flash("Check plant count and harvest dates.", "error")
            return redirect(url_for("aquaponics.crop_management", farm_id=farm.id))
        db.session.add(AquaponicsCrop(
            farm_id=farm.id, system_id=system.id, crop=crop,
            variety=request.form.get("variety", "").strip()[:100],
            growing_method=method, plant_count=count, planted_on=planted,
            expected_harvest=expected, notes=request.form.get("notes", "").strip()[:1200],
        ))
        db.session.commit()
        flash("Aquaponics crop cycle saved.", "success")
        return redirect(url_for("aquaponics.crop_management", farm_id=farm.id))
    crops = AquaponicsCrop.query.filter_by(farm_id=farm.id).order_by(AquaponicsCrop.created_at.desc()).all()
    return render_template("aquaponics/crops.html", farm=farm, membership=membership, systems=systems, crops=crops)


@aqua_bp.post("/farm/<int:farm_id>/crops/<int:crop_id>/harvest")
@login_required
def record_crop_harvest(farm_id, crop_id):
    farm, membership = farm_membership(farm_id)
    require_editor(membership)
    crop = AquaponicsCrop.query.filter_by(id=crop_id, farm_id=farm.id).first_or_404()
    try:
        amount = optional_float(request.form.get("actual_harvest_kg"), "actual harvest kg", 0, 10000000)
        if amount is None:
            raise ValueError("Enter the harvested weight in kilograms.")
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("aquaponics.crop_management", farm_id=farm.id))
    crop.actual_harvest_kg = amount
    crop.status = "harvested"
    db.session.commit()
    flash("Harvest record saved.", "success")
    return redirect(url_for("aquaponics.crop_management", farm_id=farm.id))


@aqua_bp.route("/farm/<int:farm_id>/research", methods=["GET", "POST"])
@login_required
def research(farm_id):
    farm, membership = farm_membership(farm_id)
    if request.method == "POST":
        require_editor(membership)
        title = request.form.get("title", "").strip()[:180]
        objective = request.form.get("objective", "").strip()[:2000]
        if not title or not objective:
            flash("Enter an experiment title and research objective.", "error")
            return redirect(url_for("aquaponics.research", farm_id=farm.id))
        db.session.add(AquaponicsExperiment(
            farm_id=farm.id, created_by=current_user.id, title=title, objective=objective,
            hypothesis=request.form.get("hypothesis", "").strip()[:1500],
            test_group=request.form.get("test_group", "").strip()[:500],
            control_group=request.form.get("control_group", "").strip()[:500],
            observations=request.form.get("observations", "").strip(),
        ))
        db.session.commit()
        flash("R&D experiment has been registered.", "success")
        return redirect(url_for("aquaponics.research", farm_id=farm.id))
    experiments = AquaponicsExperiment.query.filter_by(farm_id=farm.id).order_by(AquaponicsExperiment.created_at.desc()).all()
    return render_template("aquaponics/research.html", farm=farm, membership=membership, experiments=experiments)


@aqua_bp.route("/farm/<int:farm_id>/finance", methods=["GET", "POST"])
@login_required
def finance(farm_id):
    farm, membership = farm_membership(farm_id)
    if request.method == "POST":
        require_editor(membership)
        entry_type = request.form.get("entry_type", "")
        category = request.form.get("category", "").strip()[:80]
        description = request.form.get("description", "").strip()[:1200]
        try:
            amount = Decimal(request.form.get("amount", ""))
            entry_date = date.fromisoformat(request.form.get("entry_date", date.today().isoformat()))
            if entry_type not in {"expense", "revenue"} or not amount.is_finite() or amount <= 0 or not category:
                raise ValueError
        except (InvalidOperation, TypeError, ValueError):
            flash("Check transaction type, category, date and positive amount.", "error")
            return redirect(url_for("aquaponics.finance", farm_id=farm.id))
        db.session.add(AquaponicsFinanceEntry(
            farm_id=farm.id, user_id=current_user.id, entry_type=entry_type,
            category=category, amount=amount, currency=farm.currency,
            description=description, entry_date=entry_date,
        ))
        db.session.commit()
        flash(f"{entry_type.title()} entry saved in {farm.currency}.", "success")
        return redirect(url_for("aquaponics.finance", farm_id=farm.id))
    entries = AquaponicsFinanceEntry.query.filter_by(farm_id=farm.id).order_by(AquaponicsFinanceEntry.entry_date.desc(), AquaponicsFinanceEntry.id.desc()).limit(300).all()
    total_expense = db.session.query(db.func.coalesce(db.func.sum(AquaponicsFinanceEntry.amount), 0)).filter_by(farm_id=farm.id, entry_type="expense").scalar()
    total_revenue = db.session.query(db.func.coalesce(db.func.sum(AquaponicsFinanceEntry.amount), 0)).filter_by(farm_id=farm.id, entry_type="revenue").scalar()
    return render_template("aquaponics/finance.html", farm=farm, membership=membership, entries=entries, total_expense=total_expense, total_revenue=total_revenue)


@aqua_bp.route("/farm/<int:farm_id>/members", methods=["GET", "POST"])
@login_required
def members(farm_id):
    from .models import Notification, User
    farm, membership = farm_membership(farm_id)
    if membership.role != "owner":
        abort(403)
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "").strip()
        invited = User.query.filter_by(email=email).first()
        if not invited or role not in ROLE_OPTIONS:
            flash("Enter the email of an existing FARM BRAIN account and choose a valid role.", "error")
            return redirect(url_for("aquaponics.members", farm_id=farm.id))
        existing = AquaponicsMembership.query.filter_by(farm_id=farm.id, user_id=invited.id).first()
        if existing:
            existing.role = role
            flash("Workspace role updated.", "success")
        else:
            db.session.add(AquaponicsMembership(farm_id=farm.id, user_id=invited.id, role=role))
            db.session.add(Notification(
                user_id=invited.id,
                message=f"You have been added to {farm.name} as {role.replace('_', ' ')}.",
                url=url_for("aquaponics.dashboard", farm_id=farm.id),
            ))
            flash("Member added to the aquaponics workspace.", "success")
        db.session.commit()
        return redirect(url_for("aquaponics.members", farm_id=farm.id))
    members = AquaponicsMembership.query.filter_by(farm_id=farm.id).order_by(AquaponicsMembership.created_at.asc()).all()
    return render_template("aquaponics/members.html", farm=farm, membership=membership, members=members, role_options=sorted(ROLE_OPTIONS))


@aqua_bp.post("/farm/<int:farm_id>/members/<int:member_id>/remove")
@login_required
def remove_member(farm_id, member_id):
    farm, membership = farm_membership(farm_id)
    if membership.role != "owner":
        abort(403)
    target = AquaponicsMembership.query.filter_by(id=member_id, farm_id=farm.id).first_or_404()
    if target.role == "owner":
        abort(400)
    db.session.delete(target)
    db.session.commit()
    flash("Workspace access removed.", "success")
    return redirect(url_for("aquaponics.members", farm_id=farm.id))


@aqua_bp.get("/farm/<int:farm_id>/alerts")
@login_required
def alerts(farm_id):
    farm, membership = farm_membership(farm_id)
    items = AquaponicsAlert.query.filter_by(farm_id=farm.id).order_by(AquaponicsAlert.created_at.desc()).limit(200).all()
    return render_template("aquaponics/alerts.html", farm=farm, membership=membership, alerts=items)


@aqua_bp.post("/alert/<int:alert_id>/resolve")
@login_required
def resolve_alert(alert_id):
    alert = db.get_or_404(AquaponicsAlert, alert_id)
    farm, membership = farm_membership(alert.farm_id)
    require_editor(membership)
    alert.status = "resolved"
    alert.resolved_at = utcnow()
    db.session.commit()
    flash("Alert marked resolved. This records your action; it does not verify the physical system has recovered.", "success")
    return redirect(url_for("aquaponics.alerts", farm_id=farm.id))


@aqua_bp.get("/farm/<int:farm_id>/finance.csv")
@login_required
def finance_csv(farm_id):
    farm, membership = farm_membership(farm_id)
    entries = AquaponicsFinanceEntry.query.filter_by(farm_id=farm.id).order_by(AquaponicsFinanceEntry.entry_date.asc()).all()
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["date", "type", "category", "amount", "currency", "description"])
    for item in entries:
        writer.writerow([item.entry_date.isoformat(), item.entry_type, item.category, item.amount, item.currency, item.description])
    response = make_response(stream.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=magppliv-farm-{farm.id}-finance.csv"
    return response


@aqua_bp.get("/farm/<int:farm_id>/report.csv")
@login_required
def report_csv(farm_id):
    farm, membership = farm_membership(farm_id)
    rows = AquaponicsWaterReading.query.filter_by(farm_id=farm.id).order_by(AquaponicsWaterReading.recorded_at.asc()).all()
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["recorded_at_utc", "source", "temperature_c", "ph", "dissolved_oxygen_mg_l", "ammonia_mg_l", "nitrite_mg_l", "nitrate_mg_l", "ec_ms_cm", "water_level_percent", "flow_l_min", "alkalinity_mg_l", "notes"])
    for row in rows:
        writer.writerow([row.recorded_at.isoformat(), row.source, row.temperature_c, row.ph,
                         row.dissolved_oxygen_mg_l, row.ammonia_mg_l, row.nitrite_mg_l,
                         row.nitrate_mg_l, row.ec_ms_cm, row.water_level_percent,
                         row.flow_l_min, row.alkalinity_mg_l, row.notes])
    response = make_response(stream.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=magppliv-farm-{farm.id}-water-readings.csv"
    return response
