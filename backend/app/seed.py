"""
Populates the database with the real stop/route/bus network already
built into the frontends, plus a couple of demo accounts so you can
log in immediately.

Run with:  python -m app.seed
Safe to re-run — it skips anything that already exists.
"""
from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Bus, BusStatus, PromoCode, Route, RouteStop, Stop, User, UserRole
from app.seed_data import BUS_DRIVERS, BUSES, PROMO_CODES, ROUTES, STOPS


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ---- Stops ----
        stop_by_key = {}
        for s in STOPS:
            existing = db.query(Stop).filter_by(key=s["key"]).first()
            if existing:
                stop_by_key[s["key"]] = existing
                continue
            stop = Stop(
                key=s["key"],
                name=s["name"],
                x=s["x"],
                y=s["y"],
                aliases=",".join(s["aliases"]),
            )
            db.add(stop)
            db.flush()
            stop_by_key[s["key"]] = stop
        print(f"Stops: {len(stop_by_key)}")

        # ---- Routes + ordered route_stops ----
        route_by_no = {}
        for r in ROUTES:
            existing = db.query(Route).filter_by(route_no=r["route_no"]).first()
            if existing:
                route_by_no[r["route_no"]] = existing
                continue
            route = Route(
                route_no=r["route_no"],
                via=r["via"],
                fare=r["fare"],
                minutes=r["mins"],
                traffic=r["traffic"],
            )
            db.add(route)
            db.flush()
            for position, stop_key in enumerate(r["stops"]):
                db.add(RouteStop(route_id=route.id, stop_id=stop_by_key[stop_key].id, position=position))
            route_by_no[r["route_no"]] = route
        print(f"Routes: {len(route_by_no)}")

        # ---- Demo driver accounts (from operator dashboard's LIVE_BUSES) ----
        driver_by_bus_no = {}
        for bus_no, driver_name in BUS_DRIVERS.items():
            phone = f"260-driver-{bus_no}"
            driver = db.query(User).filter_by(phone=phone).first()
            if not driver:
                driver = User(
                    name=driver_name,
                    phone=phone,
                    hashed_password=hash_password("driver123"),
                    role=UserRole.driver,
                )
                db.add(driver)
                db.flush()
            driver_by_bus_no[bus_no] = driver

        # ---- Buses ----
        bus_count = 0
        for b in BUSES:
            existing = db.query(Bus).filter_by(bus_no=b["bus_no"]).first()
            if existing:
                continue
            route = route_by_no.get(b["bus_no"])  # bus number happens to match route_no here
            driver = driver_by_bus_no.get(b["bus_no"])
            bus = Bus(
                bus_no=b["bus_no"],
                route_id=route.id if route else None,
                driver_id=driver.id if driver else None,
                status=BusStatus(b.get("status", "On Route")),
                seats_total=b["seats_total"],
                seats_available=b["seats_available"],
                fuel_level=100.0,
                color=b["color"],
                current_stop_key=route.stops[0].stop.key if route and route.stops else None,
            )
            db.add(bus)
            bus_count += 1
        print(f"Buses added: {bus_count}")

        # ---- Promo codes ----
        promo_count = 0
        for p in PROMO_CODES:
            if db.query(PromoCode).filter_by(code=p["code"]).first():
                continue
            db.add(PromoCode(code=p["code"], percent=p["percent"], label=p["label"]))
            promo_count += 1
        print(f"Promo codes added: {promo_count}")

        # ---- Demo passenger account so the app is usable immediately ----
        if not db.query(User).filter_by(phone="0977000000").first():
            db.add(
                User(
                    name="Demo Passenger",
                    phone="0977000000",
                    hashed_password=hash_password("password123"),
                    role=UserRole.passenger,
                    wallet_balance=50.0,
                    home_place="Kamwala",
                    work_place="Town Centre",
                )
            )
            print("Demo passenger created: phone=0977000000 password=password123")

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
