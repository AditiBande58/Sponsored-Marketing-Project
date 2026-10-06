# Campus Cart

A shopping study about whether a **Sponsored** label changes what people click and buy.

Each person shops 10 aisles (snacks, dorm gear, tech, and so on). Every aisle has nine products and a play-money budget. The mid-priced item is always in the first slot, top-left on a wide screen. On five aisles that item is labeled Sponsored. On five it is not. Odd-numbered participants see the label on aisles 1, 3, 5, 7, and 9. Even-numbered participants see the opposite order, so the label is not always first.

The React shop records each click and purchase. Flask stores one row per aisle in MongoDB.

## Run it

MongoDB has to be listening on port 27017. From the project folder:

```powershell
docker compose up -d
```

If you already have MongoDB, skip Docker and start that instead. Copy `.env.example` to `.env` only if you need a different database or researcher key. The app defaults to `mongodb://localhost:27017` and the researcher key `campus-cart`.

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Frontend, in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). The store is the participant view. Results are at [http://127.0.0.1:5173/researcher](http://127.0.0.1:5173/researcher).

Check the design rules without MongoDB:

```powershell
pip install pytest
pytest test_study.py
```

## What gets saved

Each finished aisle is one observation:

| Column | Meaning |
| --- | --- |
| `participant_id` | Anonymous shopper id. Cluster on this. |
| `sponsored_label` | 1 if the top-left item said Sponsored, else 0 |
| `price` | Price of that top-left item |
| `clicked_target` | 1 if they opened it |
| `purchased_target` | 1 if it was in the cart at checkout |
| `spend` | Basket total |
| `target_spend` | Price of the top-left item if they bought it, else 0 |
| `round_num` | Aisle number, 1–10 |
| `cognitive_state` | Focus rating from 1 to 7, collected once at the start |
| `sequence` | A or B, the counterbalanced label order |

The researcher page compares click share, purchase share, and average spend with and without the label. Its interval resamples **participants**, not rows. The CSV is shaped for:

```text
purchased_target ~ sponsored_label + price + round_num + cognitive_state
```

Use standard errors clustered by `participant_id`.

Change `RESEARCHER_KEY` before anyone outside the team can reach the server.
