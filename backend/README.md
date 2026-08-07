# Lusaka Bus AI — Backend (Week 1 + Week 2)

FastAPI + SQLAlchemy backend for the Lusaka minibus app.

- **Week 1**: models, auth, database seeded with the real stop/route/bus
  data from the two existing frontends.
- **Week 2**: trip-planning endpoint (ported from the frontend's
  `planTrip`), trip booking with wallet charge/refund, wallet top-up +
  transaction history, ratings — plus everything needed to deploy to
  Railway.

## What's here

```
backend/
  app/
    config.py          # settings (DATABASE_URL, JWT secret, etc.)
    database.py          # SQLAlchemy engine/session (handles Postgres + SQLite)
    models.py             # User, Stop, Route, RouteStop, Bus, Trip, WalletTransaction, Rating, PromoCode
    schemas.py             # Pydantic request/response models
    auth.py                # bcrypt password hashing + JWT create/verify
    trip_planner.py         # resolve_stop / plan_trip, ported from the frontend
    routers_trips.py         # /trip-planner, /trips (book/start/complete/cancel)
    routers_wallet.py         # /wallet/balance, /wallet/topup, /wallet/transactions
    routers_ratings.py         # /ratings
    seed_data.py                # stops/routes/buses/promos, extracted from the frontend .jsx files
    seed.py                      # populates the DB from seed_data.py
    main.py                       # FastAPI app, wires all routers together
  requirements.txt
  Procfile             # tells Railway how to start the app
  railway.json          # Railway build/deploy config
  .env.example
```

## Run it locally

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # defaults to local SQLite, no setup needed
python -m app.seed            # loads 30 stops, 19 routes, 4 buses, 2 promo codes, 1 demo passenger
uvicorn app.main:app --reload
```

Then open http://localhost:8000/docs for interactive API docs.

**Demo login:** phone `0977000000`, password `password123`

## API overview

| Endpoint | Method | Auth? | What it does |
|---|---|---|---|
| `/auth/register` | POST | no | Create an account |
| `/auth/login` | POST | no | Get a JWT |
| `/auth/me` | GET | yes | Current user's profile |
| `/stops` | GET | no | All stops |
| `/routes` | GET | no | All routes with ordered stops |
| `/buses` | GET | no | Fleet status |
| `/trip-planner?from=X&to=Y` | GET | no | Direct or transfer route options (accepts stop keys or free text like "kulima") |
| `/trips` | POST | yes | Book a trip — charges the fare from the wallet |
| `/trips` | GET | yes | List your trips |
| `/trips/{id}/start` | PATCH | yes | planned → active |
| `/trips/{id}/complete` | PATCH | yes | active → completed |
| `/trips/{id}/cancel` | PATCH | yes | planned → cancelled, refunds fare |
| `/wallet/balance` | GET | yes | Current balance |
| `/wallet/topup` | POST | yes | Add funds |
| `/wallet/transactions` | GET | yes | Transaction history |
| `/ratings` | POST | yes | Rate a completed trip |

In Swagger UI (`/docs`), click **Authorize**, paste in the raw token from
`/auth/login` (no need to type "Bearer"), and every protected endpoint
will work from the page.

## Deploying to Railway

1. Push this `backend/` folder to a GitHub repo (or push the whole
   project — Railway can be pointed at a subfolder).
2. On [railway.app](https://railway.app), create a new project →
   "Deploy from GitHub repo" → pick the repo.
3. Add a **PostgreSQL** plugin to the project (New → Database →
   PostgreSQL). Railway automatically creates a `DATABASE_URL` variable
   and makes it available to your service.
4. On your web service, go to **Variables** and add:
   - `DATABASE_URL` → reference the Postgres plugin's variable (Railway
     lets you do this with a variable reference, e.g. `${{Postgres.DATABASE_URL}}`)
   - `SECRET_KEY` → generate a real one: `openssl rand -hex 32`
   - `ALGORITHM` → `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` → `1440`
5. Railway will detect the `Procfile` / `railway.json` and run
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT` automatically.
6. Once deployed, seed the production database once. Easiest way: open
   a shell on the Railway service (Settings → the "..." menu → shell,
   or `railway run` from the CLI) and run `python -m app.seed`.
7. Test it: `https://<your-app>.up.railway.app/health` should return
   `{"status":"ok"}`, and `/docs` gives you the same Swagger UI as local.

The code doesn't need to change at all between SQLite (local) and
Postgres (Railway) — `database.py` already handles both, including
normalizing Railway's `postgres://` URLs to the `postgresql://` format
SQLAlchemy expects.

## Notes for Week 3

- Point both frontends at the deployed Railway URL instead of their mock
  `STOPS`/`ROUTES`/`NEARBY_BUSES` constants.
- The `/trip-planner` endpoint's response shape matches the frontend's
  `planTrip()` output field-for-field, so wiring it in should be a
  straight swap.

