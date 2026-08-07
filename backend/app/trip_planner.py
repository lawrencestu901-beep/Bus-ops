"""
Trip-planning logic, ported directly from planTrip() / findDirectRoutes() /
findTransferRoutes() / resolveStop() in lusaka-bus-ai-app.jsx, but reading
from the database instead of the hardcoded STOPS/ROUTES constants.
"""
import math
from dataclasses import dataclass, field

from sqlalchemy.orm import Session, joinedload

from app.models import Route, RouteStop, Stop


@dataclass
class TripOption:
    id: str
    route: str  # "125" for direct, "125 → 130" for transfer
    via: str
    fare: float
    mins: int
    km: float | None
    traffic: str
    recommended: bool
    transfer: bool
    transfer_at: str | None = None


def resolve_stop(db: Session, text: str) -> Stop | None:
    """Find a stop by key, exact name, alias, or loose substring match —
    mirrors resolveStop() so free-text input like 'kulima' still works."""
    t = text.strip().lower()

    stop = db.query(Stop).filter(Stop.key == t).first()
    if stop:
        return stop

    all_stops = db.query(Stop).all()
    for s in all_stops:
        aliases = (s.aliases or "").split(",")
        if s.name.lower() == t or t in aliases:
            return s

    # loose contains-match fallback, same as the frontend's fallback loop
    for s in all_stops:
        aliases = [a for a in (s.aliases or "").split(",") if a]
        if aliases and (t in aliases[0] or any(a in t for a in aliases)):
            return s
    return None


def distance_km(a: Stop, b: Stop) -> float | None:
    if not a or not b:
        return None
    return round(math.hypot(a.x - b.x, a.y - b.y) / 4.2, 1)  # same mock scale as the frontend


def _routes_with_stops(db: Session) -> list[Route]:
    return (
        db.query(Route)
        .options(joinedload(Route.stops).joinedload(RouteStop.stop))
        .all()
    )


def _stop_keys(route: Route) -> list[str]:
    return [rs.stop.key for rs in sorted(route.stops, key=lambda rs: rs.position)]


def find_direct_routes(db: Session, from_key: str, to_key: str) -> list[Route]:
    routes = _routes_with_stops(db)
    return [r for r in routes if from_key in _stop_keys(r) and to_key in _stop_keys(r)]


def find_transfer_routes(db: Session, from_key: str, to_key: str):
    routes = _routes_with_stops(db)
    from_routes = [r for r in routes if from_key in _stop_keys(r)]
    to_routes = [r for r in routes if to_key in _stop_keys(r)]

    options = []
    for r1 in from_routes:
        for r2 in to_routes:
            if r1.route_no == r2.route_no:
                continue
            r1_stops, r2_stops = _stop_keys(r1), _stop_keys(r2)
            shared = [s for s in r1_stops if s not in (from_key, to_key) and s in r2_stops]
            if shared:
                options.append({"leg1": r1, "leg2": r2, "transfer_at": shared[0]})
    return options


def plan_trip(db: Session, from_key: str, to_key: str) -> list[TripOption]:
    if not from_key or not to_key or from_key == to_key:
        return []

    from_stop = db.query(Stop).filter(Stop.key == from_key).first()
    to_stop = db.query(Stop).filter(Stop.key == to_key).first()
    km = distance_km(from_stop, to_stop) if from_stop and to_stop else None

    direct = find_direct_routes(db, from_key, to_key)
    if direct:
        return [
            TripOption(
                id=f"d-{r.route_no}",
                route=r.route_no,
                via=r.via,
                fare=r.fare,
                mins=r.minutes,
                km=km,
                traffic=r.traffic.value if hasattr(r.traffic, "value") else r.traffic,
                recommended=(i == 0),
                transfer=False,
            )
            for i, r in enumerate(direct)
        ]

    transfers = find_transfer_routes(db, from_key, to_key)[:3]
    options = []
    for i, t in enumerate(transfers):
        leg1, leg2, transfer_at_key = t["leg1"], t["leg2"], t["transfer_at"]
        transfer_stop = db.query(Stop).filter(Stop.key == transfer_at_key).first()
        traffic1 = leg1.traffic.value if hasattr(leg1.traffic, "value") else leg1.traffic
        traffic2 = leg2.traffic.value if hasattr(leg2.traffic, "value") else leg2.traffic
        combined_traffic = "Heavy" if "Heavy" in (traffic1, traffic2) else "Moderate"
        options.append(
            TripOption(
                id=f"t-{leg1.route_no}-{leg2.route_no}",
                route=f"{leg1.route_no} → {leg2.route_no}",
                via=f"Transfer at {transfer_stop.name}",
                fare=leg1.fare + leg2.fare,
                mins=leg1.minutes + leg2.minutes,
                km=km,
                traffic=combined_traffic,
                recommended=(i == 0),
                transfer=True,
                transfer_at=transfer_stop.name,
            )
        )
    return options
