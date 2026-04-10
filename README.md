# Story & Stars Slow Travel Planning API

**Module:** XJCO3011 — Web Services and Web Data (University of Leeds)  
**Coursework 1:** Individual data-driven web API with database integration.

## Project overview

This is a **RESTful JSON API** built with **FastAPI**, **SQLAlchemy**, and **SQLite**. It models **multi-stop slow-travel journeys**: each journey has ordered stops (transport mode, distance), optional links to **literary / film locations**, **dark-sky stargazing sites**, and **UK public transport access nodes (NaPTAN)**. The service exposes **full CRUD** on journeys (Create, Read, Update, Delete) plus **read-only reference** endpoints and **analytics** (carbon footprint estimate, narrative coherence, stargazing suitability).

**Open data:** Datasets are drawn from UK-oriented public sources (e.g. **data.gov.uk**, NaPTAN/NPTG, Natural England). See the repository **`data/DATASETS.md`** for sources, licences, and file-level notes. Your **technical report** must cite each dataset, licence, and date of access.

**Why this stack (summary — expand in report):**

| Choice | Rationale (short) |
|--------|-------------------|
| **Python 3.11+** | Strong ecosystem for APIs, CSV/ETL, and teaching alignment with the module. |
| **FastAPI** | Automatic **OpenAPI 3** / **Swagger UI** (`/docs`), async-capable, typed request/response models. |
| **SQLite** | File-based SQL database, zero separate server, easy submission and local demo; satisfies SQL requirement. |
| **SQLAlchemy 2** | ORM + migrations alignment; explicit schema in code. |
| **Alembic** | Versioned schema for the on-disk database; reproducible upgrades. |

---

## Prerequisites

- **Python 3.11+** (recommended)
- **pip** and **virtual environment** support
- A modern browser (for **Swagger UI** and optional PDF export)

---

## Setup and run (local)

From the **`code`** directory (this folder):

### Windows (PowerShell)

```powershell
cd code
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### macOS / Linux

```bash
cd code
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- **Interactive API docs (Swagger UI):** <http://127.0.0.1:8000/docs>  
  - **`persistAuthorization`** is enabled: after **Authorize**, your API key survives a page refresh.  
- **ReDoc:** <http://127.0.0.1:8000/redoc>  
- **OpenAPI JSON:** <http://127.0.0.1:8000/openapi.json>

**Database file:** by default **`./slowtravel.db`** in the `code` directory. Override with environment variable **`SQLITE_PATH`**. Tests use **`SQLITE_PATH=:memory:`** (see `tests/conftest.py`).

Copy **`.env.example`** to **`.env`** and adjust values if needed.

---

## Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `SQLITE_PATH` | SQLite database file path, or `:memory:` for tests | `./slowtravel.db` |
| `API_KEY` | API key for **POST / PATCH / DELETE** on journeys; empty string disables checks (local debug only) | `dev-api-key` |

---

## Authentication

- **Write operations:** `POST /journeys`, `PATCH /journeys/{id}`, `DELETE /journeys/{id}` require header **`X-API-Key`** matching **`API_KEY`**.
- **Read operations:** all **GET** endpoints (including `/journeys` and `/reference/*`) are **public** (no key).
- In **`/docs`**, use **Authorize** and enter the same value as `API_KEY`.
- The OpenAPI document declares an **`apiKey`** security scheme for tooling and documentation.

---

## API documentation PDF (coursework deliverable)

**Submitted API documentation (PDF):** [`API documentation.pdf`]([API%20documentation.pdf](https://github.com/Searoar/Web-/blob/main/%E6%9C%80%E7%BB%88%E7%89%88%E6%9C%AC/code/API%20documentation.pdf))

The file is stored in this **`code/`** directory next to `README.md`. On **GitHub**, use the link above (or browse to **`API documentation.pdf`** in the repository). If **Minerva** requires a different URL or attachment, upload the same PDF there and keep this README line pointing to the copy graders will open (e.g. update the link to your Minerva asset or **GitHub Release** file URL).

---

## Pagination (list GET endpoints)

List endpoints use **`skip`** and **`limit`** (see `app/pagination.py`):

| Parameter | Meaning | Default / bounds |
|-----------|---------|-------------------|
| `skip` | Offset (non-negative) | Default **0** |
| `limit` | Page size | Default **50**, min **1**, max **500** (`MAX_PAGE_SIZE`); invalid values → **422** |

---

## HTTP status codes and error shape

| Situation | HTTP | `error.code` |
|-----------|------|----------------|
| Journey id in URL does not exist | **404** | `not_found` |
| Invalid `literary_location_id` / `dark_sky_site_id` / `naptan_access_node_id` in body | **422** | `invalid_reference` |
| Validation error (types, empty title, pagination bounds, etc.) | **422** | `validation_error` |
| Missing or wrong API key on write | **401** | `unauthorized` |

Successful responses use the Pydantic models defined per route. Errors use a common envelope: `{"error": { ... }}` (validation errors may include an `errors` list).

---

## Example: create a journey (curl)

Replace `dev-api-key` if you changed `API_KEY`.

```bash
curl -s -X POST "http://127.0.0.1:8000/journeys" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{"title":"Weekend slow trip","stops":[{"sequence_order":0,"stop_type":"transit","transport_mode":"train","distance_km":120.5}]}'
```

On **Windows PowerShell**, use your own quoting or:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/journeys" `
  -Headers @{ "X-API-Key" = "dev-api-key" } `
  -ContentType "application/json" `
  -Body '{"title":"Weekend slow trip","stops":[{"sequence_order":0,"stop_type":"transit","transport_mode":"train","distance_km":120.5}]}'
```

**Expected success:** HTTP **201** and a JSON body with `id`, `title`, `stops`, etc. **Expected failure examples:** **401** without key; **422** for invalid foreign keys or empty title.

---

## Main endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness; includes **`database`** (`connected` if `SELECT 1` succeeds) |
| GET | `/reference/literary-locations` | Literary / film / heritage-style POIs (filters: `region`, `work_title`) |
| GET | `/reference/dark-sky-sites` | Dark-sky sites (filter: `max_tier`) |
| GET | `/reference/naptan-access-nodes` | NaPTAN nodes (requires ETL; filters: `q`, `stop_type`) |
| GET | `/reference/nptg-localities` | NPTG localities (filter: `q`) |
| POST | `/journeys` | Create journey + stops |
| GET | `/journeys` | List journeys |
| GET | `/journeys/{id}` | Journey detail (expanded associations) |
| PATCH | `/journeys/{id}` | Update journey (may replace stops) |
| DELETE | `/journeys/{id}` | Delete journey |
| GET | `/journeys/{id}/summary` | Counts summary |
| GET | `/journeys/{id}/analytics` | Carbon / narrative / stargazing analytics |

---

## Importing CSV reference data (`data/`)

CSV files under the repository **`data/`** folder enrich **`literary_locations`** and **`dark_sky_sites`**. See **`data/DATASETS.md`** for provenance and licences.

From the **`code`** directory:

```bash
python -m scripts.import_local_data
```

Custom root:

```bash
python -m scripts.import_local_data --data-root "../data"
```

Imported files include **`film_literary/*`**, **`dark_skies/*`** (sample + expanded + optional **Natural England** park centroids), and **`heritage/*`**. Duplicates are skipped by **`title` + `latitude`** / **`name` + `latitude`**.

If imports show **0 new** rows, data may already be present (seed + prior import). To re-import from scratch, **delete `slowtravel.db`** (with the server stopped), then run the import script and start the app again.

### NaPTAN / NPTG ETL

Bulk load from UK transport CSVs (see `scripts/etl_naptan_nptg.py`). Default sample paths live under `data/downloads/transport/`. Full national **`Stops.csv`** may be large — do not commit it to Git.

```bash
python -m scripts.etl_naptan_nptg
python -m scripts.etl_naptan_nptg --naptan-csv "PATH/TO/Stops.csv" --nptg-csv "PATH/TO/Localities.csv"
```

Rows with empty WGS84 lat/lon but valid **British National Grid** easting/northing are converted with **pyproj**.

### National Parks (England) GeoJSON → CSV

If you manually download **Natural England** `National_Parks_England.geojson` (EPSG:27700):

```bash
python -m scripts.national_parks_geojson_to_csv --geojson "PATH/TO/National_Parks_England.geojson"
```

This writes **`data/dark_skies/national_parks_england_ogl_centroids.csv`** (included in the import script’s dark-sky file list).

---

## Database migrations (Alembic)

- Revision scripts: **`alembic/versions/`**.
- **On-disk SQLite:** on startup the app runs **`alembic upgrade head`**. You can also run:

```bash
alembic upgrade head
```

- **pytest with `SQLITE_PATH=:memory:`:** uses **`Base.metadata.create_all`** only (no Alembic run), for fast isolated tests. Keep ORM models and Alembic revisions in sync.

If you see errors about existing tables from an old `create_all`-only database, back up and **remove `slowtravel.db`**, then restart so migrations apply cleanly.

---

## Testing

```bash
pip install -r requirements.txt
pytest
```

- **`tests/test_api.py`** — CRUD, auth, validation, core behaviour.  
- **`tests/test_transport.py`** — reference transport listings.  
- **`tests/test_polish.py`** — pagination bounds, NaPTAN foreign keys, OpenAPI **apiKey** scheme, `/health` database field.  

Do not change **`API_KEY`** in `tests/conftest.py` without updating tests.

---

## Technical notes (for your report)

- **Analytics constants** (e.g. emission factors) in `app/services/analytics.py` are **simplified**; document assumptions and limitations in the **technical report**.
- **GenAI:** If you used generative AI, the brief requires a **declaration** and sample logs in supplementary material — see the module brief **Section 2**.

---

## Repository layout (high level)

```
code/
  app/                 # FastAPI app, routers, models, schemas, services
  alembic/             # Migration scripts
  scripts/             # import_local_data, etl_naptan_nptg, national_parks_geojson_to_csv
  tests/               # pytest
  requirements.txt
  README.md            # This file
../data/               # CSV sources and DATASETS.md (sibling of code/)
```

---

## Licence and data

Application code is submitted for academic assessment. **Third-party datasets** retain their respective licences (e.g. **Open Government Licence** for many UK government datasets). Cite sources in your **technical report** and in module materials as required.
