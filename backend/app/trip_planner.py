"""
Trip-planning logic, ported from the frontend planTrip() family of helpers,
but reading from the database instead of hardcoded STOPS/ROUTES constants.

Improvements over the original port:
- Respects stop order on each route (no reverse-direction suggestions).
- Scores and sorts options by (minutes, fare, transfer count).
- Picks a better transfer stop and applies a fixed transfer-time penalty.
"""
import math
from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload

from app.models import Route, RouteStop, Stop

# Extra minutes added when a transfer is required (walking + waiting).
TRANSFER_PENALTY_MINS = 10


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
    """Ordered list of stop keys along the route (by position)."""
    return [rs.stop.key for rs in sorted(route.stops, key=lambda rs: rs.position)]


def _index_of(keys: list[str], key: str) -> int | None:
    try:
        return keys.index(key)
    except ValueError:
        return None


def find_direct_routes(db: Session, from_key: str, to_key: str) -> list[Route]:
    """Routes that contain both stops with from appearing before to."""
    routes = _routes_with_stops(db)
    result = []
    for r in routes:
        keys = _stop_keys(r)
        i_from = _index_of(keys, from_key)
        i_to = _index_of(keys, to_key)
        if i_from is not None and i_to is not None and i_from < i_to:
            result.append(r)
    return result


def find_transfer_routes(db: Session, from_key: str, to_key: str) -> list[dict]:
    """One-transfer options that respect stop order on both legs.

    For each candidate pair of routes we pick the *best* shared transfer
    stop: the one that minimises the number of stops the passenger would
    travel (progress on leg1 after boarding + remaining on leg2).
    """
    routes = _routes_with_stops(db)
    from_routes = [r for r in routes if from_key in _stop_keys(r)]
    to_routes = [r for r in routes if to_key in _stop_keys(r)]

    options = []
    for r1 in from_routes:
        for r2 in to_routes:
            if r1.route_no == r2.route_no:
                continue

            r1_keys = _stop_keys(r1)
            r2_keys = _stop_keys(r2)
            i_from = _index_of(r1_keys, from_key)
            i_to = _index_of(r2_keys, to_key)
            if i_from is None or i_to is None:
                continue

            # Candidate transfer stops: after origin on r1, before destination on r2
            candidates = []
            for s in r1_keys:
                if s in (from_key, to_key):
                    continue
                i1 = _index_of(r1_keys, s)
                i2 = _index_of(r2_keys, s)
                if i1 is None or i2 is None:
                    continue
                if i1 > i_from and i2 < i_to:
                    cost = (i1 - i_from) + (i_to - i2)
                    candidates.append((cost, s))

            if not candidates:
                continue

            candidates.sort(key=lambda x: (x[0], x[1]))
            best_transfer = candidates[0][1]
            options.append(
                {
                    "leg1": r1,
                    "leg2": r2,
                    "transfer_at": best_transfer,
                    "cost": candidates[0][0],
                }
            )

    options.sort(key=lambda o: (o["cost"], o["leg1"].route_no, o["leg2"].route_no))
    return options


def _traffic_str(route: Route) -> str:
    t = route.traffic
    return t.value if hasattr(t, "value") else str(t)


def plan_trip(db: Session, from_key: str, to_key: str) -> list[TripOption]:
    if not from_key or not to_key or from_key == to_key:
        return []

    from_stop = db.query(Stop).filter(Stop.key == from_key).first()
    to_stop = db.query(Stop).filter(Stop.key == to_key).first()
    km = distance_km(from_stop, to_stop) if from_stop and to_stop else None

    options: list[TripOption] = []

    # --- Direct routes ---
    direct = find_direct_routes(db, from_key, to_key)
    for r in direct:
        options.append(
            TripOption(
                id=f"d-{r.route_no}",
                route=r.route_no,
                via=r.via,
                fare=r.fare,
                mins=r.minutes,
                km=km,
                traffic=_traffic_str(r),
                recommended=False,
                transfer=False,
            )
        )

    # --- One-transfer routes ---
    transfers = find_transfer_routes(db, from_key, to_key)[:5]
    for t in transfers:
        leg1, leg2, transfer_at_key = t["leg1"], t["leg2"], t["transfer_at"]
        transfer_stop = db.query(Stop).filter(Stop.key == transfer_at_key).first()
        if not transfer_stop:
            continue

        traffic1 = _traffic_str(leg1)
        traffic2 = _traffic_str(leg2)
        if "Heavy" in (traffic1, traffic2):
            combined_traffic = "Heavy"
        elif "Moderate" in (traffic1, traffic2):
            combined_traffic = "Moderate"
        else:
            combined_traffic = "Low"

        options.append(
            TripOption(
                id=f"t-{leg1.route_no}-{leg2.route_no}",
                route=f"{leg1.route_no} → {leg2.route_no}",
                via=f"Transfer at {transfer_stop.name}",
                fare=leg1.fare + leg2.fare,
                mins=leg1.minutes + leg2.minutes + TRANSFER_PENALTY_MINS,
                km=km,
                traffic=combined_traffic,
                recommended=False,
                transfer=True,
                transfer_at=transfer_stop.name,
            )
        )

    if not options:
        return []

    # Sort: minutes → fare → prefer non-transfer
    options.sort(key=lambda o: (o.mins, o.fare, o.transfer))

    options = options[:5]
    options[0].recommended = True
    return options
