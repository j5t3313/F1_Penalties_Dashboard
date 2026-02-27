# F1 Penalties Dashboard — Feature Integration Guide

## Files Delivered

| File | Rename To | Destination |
|------|-----------|-------------|
| OutstandingPenalties.xlsx | (keep name) | `data/` |
| outstanding.py | (keep name) | `data/` |
| outstanding_callbacks.py | outstanding.py | `callbacks/` |
| panels_data.py | panels.py | `data/` |
| panels_callbacks.py | panels.py | `callbacks/` |

---

## Feature 1: Outstanding Penalties

### Step 1 — Place Files

1. Copy `OutstandingPenalties.xlsx` into `data/` alongside `F1Penalties.xlsx`
2. Copy `outstanding.py` into `data/`
3. Copy `outstanding_callbacks.py` into `callbacks/` and rename it to `outstanding.py`

### Step 2 — Edit `layouts/current_season.py`

Add the import at the top of the file with the other imports:

```python
from callbacks.outstanding import create_outstanding_section
```

Add `create_outstanding_section(),` as the last element inside the `dbc.Container` in `create_layout()`.

Before:

```python
        dbc.Row([
            dbc.Col([
                html.H5("Race-by-Race Log", className="mt-2 mb-3"),
                html.Div(id="cs-race-log"),
            ], xs=12, className="mb-4"),
        ]),
    ], fluid=True, className="py-3")
```

After:

```python
        dbc.Row([
            dbc.Col([
                html.H5("Race-by-Race Log", className="mt-2 mb-3"),
                html.Div(id="cs-race-log"),
            ], xs=12, className="mb-4"),
        ]),

        create_outstanding_section(),

    ], fluid=True, className="py-3")
```

### Step 3 — Register Callbacks

In your main app file (where you call `register_current_season_callbacks(app)`), add:

```python
from callbacks.outstanding import register_outstanding_callbacks
register_outstanding_callbacks(app)
```

### Step 4 — Verify

1. Run the app
2. Navigate to the Current Season page
3. You should see an "Outstanding Penalties" section below the Race-by-Race Log
4. The Bottas seed data should appear in the table

### Data Maintenance

To add or update outstanding penalties, edit `data/OutstandingPenalties.xlsx` directly. The columns are:

| Column | Required | Notes |
|--------|----------|-------|
| Driver | Yes | Use post-normalization names (e.g., "Valtteri Bottas") |
| Issued_Team | Yes | Team at time of infraction |
| Issuing_Race | Yes | Match existing race name conventions |
| Issuing_Year | Yes | Integer |
| Issuing_Round | Yes | Integer, for sorting |
| Session | Yes | R, Q, SQ, etc. |
| Allegation | Yes | Matches canonical allegation categories |
| Penalty_Type | Yes | Grid Penalty, Pit Lane Start, etc. |
| Grid_Positions | No | Numeric for grid drops, leave blank for pit lane starts |
| Notes | No | Free text |
| Status | Yes | Outstanding, Served, or Void |
| Serving_Race | No | Populated when served |
| Serving_Year | No | Populated when served |
| Serving_Round | No | Populated when served |
| Serving_Team | No | Populated when served (useful for team changes) |
| Resolution_Notes | No | Why voided, or context on serving |
| Last_Updated | Yes | ISO date string (e.g., 2024-12-08) |

When a penalty is served, update `Status` to `Served` and fill in the `Serving_*` columns. When a penalty is voided, update `Status` to `Void` and add context in `Resolution_Notes`.

Note: The data loader uses `lru_cache`. If you update the Excel file while the app is running, you will need to restart the app or call `invalidate_cache()` from `data.outstanding` to pick up changes.

---

## Feature 2: Stewarding Panels

### Step 1 — Place Files

1. Copy `panels_data.py` into `data/` and rename it to `panels.py`
2. Copy `panels_callbacks.py` into `callbacks/` and rename it to `panels.py`

### Step 2 — Edit `layouts/stewards.py`

Add the import at the top of the file with the other imports:

```python
from callbacks.panels import create_panel_lookup_section
```

Add `create_panel_lookup_section(stewards),` as the last element inside the `dbc.Container` in `create_layout(stewards)`.

Before:

```python
        html.Div(id="steward-content"),
    ], fluid=True, className="py-3")
```

After:

```python
        html.Div(id="steward-content"),

        create_panel_lookup_section(stewards),

    ], fluid=True, className="py-3")
```

### Step 3 — Register Callbacks

In your main app file (where you call `register_callbacks(app)`), add:

```python
from callbacks.panels import register_panel_callbacks
register_panel_callbacks(app)
```

### Step 4 — Verify

1. Run the app
2. Navigate to the Stewards page
3. Scroll below the existing steward detail section
4. You should see a "Panel Lookup" section with a multi-select dropdown
5. Select 2 or more stewards to see their shared history

### How It Works

The panel lookup uses your existing `Stewards_List` data. When you select stewards:

- It finds all penalty records where at least 2 of the selected stewards served together (partial matching)
- Stat cards show aggregate numbers for all matched records
- The co-occurrence chart shows how often each pair of selected stewards has served together
- The comparison chart shows each steward's individual avg PP per incident alongside the combined panel average
- Allegation and outcome charts show the distribution for matched records
- The pairwise table gives per-pair breakdowns (races together, penalties, avg PP)
- The penalty history table shows all matched penalty records

Global filters from the filter sidebar apply to panel results as well.

---

## Final Checklist

- [ ] `data/OutstandingPenalties.xlsx` is in place
- [ ] `data/outstanding.py` is in place
- [ ] `callbacks/outstanding.py` is in place
- [ ] `data/panels.py` is in place
- [ ] `callbacks/panels.py` is in place
- [ ] Import and layout edit in `layouts/current_season.py`
- [ ] Import and layout edit in `layouts/stewards.py`
- [ ] Both `register_outstanding_callbacks(app)` and `register_panel_callbacks(app)` called in main app file
- [ ] App runs without errors
- [ ] Outstanding Penalties section visible on Current Season page
- [ ] Panel Lookup section visible on Stewards page
