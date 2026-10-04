"""Assemble evals/golden/v1.jsonl from the hand-authored source files and the seed data.

Database rows are *computed* from mongo/seed/*.json so the gold values cannot drift from the
fixtures. Web, routing and knowledge-base rows are authored in evals/golden/sources/*.jsonl.

    uv run python evals/golden/build.py            # write v1.jsonl
    uv run python evals/golden/build.py --check    # exit 1 if v1.jsonl is stale

Row schema (every row): id, specialist, question, mode, expected_answer, expected_sources,
expected_route, difficulty, tags, grader. Optional: expected_values, governance, notes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SEED_DIR = PROJECT_ROOT / "mongo" / "seed"
SOURCES = HERE / "sources"
OUTPUT = HERE / "v1.jsonl"

SOURCE_ORDER = ["kb", "web", "routing"]  # db rows are generated first


def load_seed() -> tuple[list[dict], list[dict], list[dict]]:
    def read(name: str) -> list[dict]:
        return json.loads((SEED_DIR / f"{name}.json").read_text(encoding="utf-8"))

    return read("drugs"), read("inventory"), read("sales_records")


def _date(doc: dict, key: str) -> str:
    return doc[key]["$date"][:10]


def _fmt(n: float) -> str:
    return f"{n:,.0f}" if float(n).is_integer() else f"{n:,.2f}"


def db_row(id_: str, question: str, answer: str, targets: list, sources: list[str], difficulty: str,
           tags: list[str], method: str = "numeric", values: dict | None = None, notes: str | None = None) -> dict:
    row = {
        "id": id_,
        "specialist": "db",
        "question": question,
        "mode": "auto",
        "expected_answer": answer,
        "expected_sources": [f"mongodb:{c}" for c in sources],
        "expected_route": ["database"],
        "difficulty": difficulty,
        "tags": tags,
        "grader": {"method": method, "targets": targets},
    }
    if values:
        row["expected_values"] = values
    if notes:
        row["notes"] = notes
    return row


def build_db_rows() -> list[dict]:  # noqa: C901 - one long, explicit list of questions
    drugs, inventory, sales = load_seed()
    by_id = {d["drug_id"]: d for d in drugs}
    name = {i: d["generic_name"] for i, d in by_id.items()}

    inv_by_drug = Counter()
    for i in inventory:
        inv_by_drug[name[i["drug_id"]]] += i["quantity_on_hand"]
    rev_by_drug, units_by_drug = Counter(), Counter()
    for s in sales:
        rev_by_drug[name[s["drug_id"]]] += s["total_amount"]
        units_by_drug[name[s["drug_id"]]] += s["quantity_sold"]
    rev_by_region = Counter()
    for s in sales:
        rev_by_region[s["region"]] += s["total_amount"]
    rev_by_area, inv_by_area = Counter(), Counter()
    for s in sales:
        rev_by_area[by_id[s["drug_id"]]["therapeutic_area"]] += s["total_amount"]
    for i in inventory:
        inv_by_area[by_id[i["drug_id"]]["therapeutic_area"]] += i["quantity_on_hand"]
    building = Counter()
    for i in inventory:
        building[i["warehouse_location"].split(" - ")[0]] += i["quantity_on_hand"]
    city = Counter()
    for i in inventory:
        city[i["warehouse_location"].split(" ")[0]] += i["quantity_on_hand"]

    rows: list[dict] = []
    total_drugs = len(drugs)
    capsules = sum(1 for d in drugs if d["dosage_form"] == "Capsule")
    rows.append(db_row("db-01", "How many drugs are in our product catalogue?",
                       f"{total_drugs} drugs.", [total_drugs], ["drugs"], "easy", ["count"],
                       values={"count": total_drugs}))
    rows.append(db_row("db-02", "How many of our drugs are supplied as capsules?",
                       f"{capsules} capsule products.", [capsules], ["drugs"], "easy", ["count", "filter"],
                       values={"count": capsules}))
    rows.append(db_row("db-03", "How many inventory batch records do we hold in total?",
                       f"{len(inventory)} inventory records.", [len(inventory)], ["inventory"], "easy", ["count"],
                       values={"count": len(inventory)}))
    rows.append(db_row("db-04", "How many sales records were booked in calendar year 2025?",
                       f"{len(sales)} sales records.", [len(sales)], ["sales_records"], "easy", ["count", "date"],
                       values={"count": len(sales)}))

    amox = inv_by_drug["Amoxicillin Capsules"]
    rows.append(db_row("db-05", "What is the total quantity on hand across all inventory batches of Amoxicillin Capsules?",
                       f"{_fmt(amox)} units across three batches.", [amox], ["inventory", "drugs"], "medium",
                       ["aggregate", "lookup"], values={"quantity_on_hand": amox}))
    top_inv, top_inv_qty = inv_by_drug.most_common(1)[0]
    rows.append(db_row("db-06", "Which drug do we hold the most stock of, and how many units is that?",
                       f"{top_inv}, {_fmt(top_inv_qty)} units.", [top_inv, top_inv_qty], ["inventory", "drugs"], "medium",
                       ["aggregate", "lookup", "ranking"], method="contains_all",
                       values={"drug": top_inv, "quantity_on_hand": top_inv_qty}))
    total_inv = sum(inv_by_drug.values())
    rows.append(db_row("db-07", "What is the total quantity on hand across our entire inventory?",
                       f"{_fmt(total_inv)} units.", [total_inv], ["inventory"], "easy", ["aggregate"],
                       values={"quantity_on_hand": total_inv}))
    total_rev = sum(rev_by_drug.values())
    rows.append(db_row("db-08", "What was our total sales revenue in 2025?",
                       f"{_fmt(total_rev)} (sum of total_amount).", [total_rev], ["sales_records"], "easy",
                       ["aggregate", "date"], values={"total_amount": total_rev}))
    top_rev, top_rev_amt = rev_by_drug.most_common(1)[0]
    rows.append(db_row("db-09", "Which drug generated the highest total sales revenue, and how much?",
                       f"{top_rev}, {_fmt(top_rev_amt)}.", [top_rev, top_rev_amt], ["sales_records", "drugs"], "medium",
                       ["aggregate", "lookup", "ranking"], method="contains_all",
                       values={"drug": top_rev, "total_amount": top_rev_amt}))
    top3 = rev_by_region.most_common(3)
    rows.append(db_row("db-10", "Which three regions generated the most sales revenue, and how much each?",
                       "; ".join(f"{r} {_fmt(a)}" for r, a in top3) + ".",
                       [x for r, a in top3 for x in (r, a)], ["sales_records"], "medium", ["aggregate", "ranking"],
                       method="contains_all", values={r: a for r, a in top3}))
    east = [s for s in sales if s["region"] == "East China"]
    rows.append(db_row("db-11", "How many sales records are from the East China region?",
                       f"{len(east)} records.", [len(east)], ["sales_records"], "easy", ["count", "filter"],
                       values={"count": len(east)}))
    big = max(sales, key=lambda s: s["total_amount"])
    rows.append(db_row("db-12", "What was our single largest sale by total amount: which drug, which customer, and for how much?",
                       f"{name[big['drug_id']]} to {big['customer_name']} for {_fmt(big['total_amount'])} on {_date(big, 'sale_date')}.",
                       [name[big["drug_id"]], big["customer_name"], big["total_amount"]], ["sales_records", "drugs"], "medium",
                       ["ranking", "lookup"], method="contains_all",
                       values={"drug": name[big["drug_id"]], "customer_name": big["customer_name"],
                               "total_amount": big["total_amount"], "sale_date": _date(big, "sale_date")}))
    osel_units, osel_rev = units_by_drug["Oseltamivir Phosphate Capsules"], rev_by_drug["Oseltamivir Phosphate Capsules"]
    rows.append(db_row("db-13", "How many units of Oseltamivir Phosphate Capsules did we sell in total, and for what total revenue?",
                       f"{_fmt(osel_units)} units, {_fmt(osel_rev)} revenue.", [osel_units, osel_rev],
                       ["sales_records", "drugs"], "medium", ["aggregate", "lookup"],
                       values={"quantity_sold": osel_units, "total_amount": osel_rev}))
    expiring = [i for i in inventory if _date(i, "expiry_date") < "2027-07-01"]
    exp_batches = sorted({i["batch_number"] for i in expiring})
    rows.append(db_row("db-14", "Which inventory batches expire before 1 July 2027, and how many inventory records is that?",
                       f"{len(expiring)} records, batches {' and '.join(exp_batches)}.", exp_batches + [len(expiring)],
                       ["inventory"], "medium", ["filter", "date"], method="contains_all",
                       values={"count": len(expiring), "batch_numbers": exp_batches}))
    jan_units = sum(i["quantity_on_hand"] for i in inventory if _date(i, "expiry_date") == "2027-01-01")
    rows.append(db_row("db-15", "How many units of stock expire on 1 January 2027?",
                       f"{_fmt(jan_units)} units (batch MY-250101-A).", [jan_units], ["inventory"], "medium",
                       ["aggregate", "date"], values={"quantity_on_hand": jan_units}))
    top_b, top_b_qty = building.most_common(1)[0]
    rows.append(db_row("db-16", "Which warehouse building holds the most stock in total (ignore the zone), and how many units?",
                       f"{top_b}, {_fmt(top_b_qty)} units.", [top_b, top_b_qty], ["inventory"], "hard",
                       ["aggregate", "string-parsing", "ranking"], method="contains_all",
                       values={"warehouse": top_b, "quantity_on_hand": top_b_qty},
                       notes="warehouse_location is 'Building - Zone'; the agent must group by the prefix."))
    rows.append(db_row("db-17", "Compare our total stock held in Tianjin with the total held in Beijing.",
                       f"Tianjin {_fmt(city['Tianjin'])} units; Beijing {_fmt(city['Beijing'])} units.",
                       [city["Tianjin"], city["Beijing"]], ["inventory"], "hard", ["aggregate", "string-parsing"],
                       values={"Tianjin": city["Tianjin"], "Beijing": city["Beijing"]}))
    cold = sorted({name[i["drug_id"]] for i in inventory if "Cold" in i["warehouse_location"] or "Cool" in i["warehouse_location"]})
    rows.append(db_row("db-18", "Which drugs do we keep in cold or cool storage locations?",
                       " and ".join(cold) + ".", cold, ["inventory", "drugs"], "medium", ["filter", "lookup", "regex"],
                       method="contains_all", values={"drugs": cold}))
    area_counts = Counter(d["therapeutic_area"] for d in drugs)
    two = sorted(a for a, n in area_counts.items() if n == 2)
    rows.append(db_row("db-19", "Which therapeutic areas have more than one product in our catalogue?",
                       " and ".join(two) + f" ({len(area_counts)} areas in total).", two, ["drugs"], "medium",
                       ["aggregate", "filter"], method="contains_all", values={"areas": two, "distinct_areas": len(area_counts)}))
    top_area, top_area_rev = rev_by_area.most_common(1)[0]
    rows.append(db_row("db-20", "Which therapeutic area generated the most sales revenue, and how much?",
                       f"{top_area}, {_fmt(top_area_rev)}.", [top_area, top_area_rev], ["sales_records", "drugs"], "hard",
                       ["aggregate", "lookup", "ranking"], method="contains_all",
                       values={"therapeutic_area": top_area, "total_amount": top_area_rev}))
    amox_prices = [s["unit_price"] for s in sales if name[s["drug_id"]] == "Amoxicillin Capsules"]
    amox_avg = round(sum(amox_prices) / len(amox_prices), 2)
    rows.append(db_row("db-21", "What is the simple average unit price across our Amoxicillin Capsules sales records?",
                       f"{amox_avg} (mean of {len(amox_prices)} records).", [amox_avg], ["sales_records", "drugs"], "medium",
                       ["aggregate", "lookup"], values={"avg_unit_price": amox_avg}))
    hi = max(sales, key=lambda s: s["unit_price"])
    rows.append(db_row("db-22", "Which drug has the highest unit price in our sales records, and what is that price?",
                       f"{name[hi['drug_id']]}, {_fmt(hi['unit_price'])} per unit.", [name[hi["drug_id"]], hi["unit_price"]],
                       ["sales_records", "drugs"], "easy", ["ranking", "lookup"], method="contains_all",
                       values={"drug": name[hi["drug_id"]], "unit_price": hi["unit_price"]}))
    q4 = [s for s in sales if _date(s, "sale_date") >= "2025-10-01"]
    q4_rev = sum(s["total_amount"] for s in q4)
    rows.append(db_row("db-23", "How many sales did we make in Q4 2025 (October to December), and what was their total revenue?",
                       f"{len(q4)} sales totalling {_fmt(q4_rev)}.", [len(q4), q4_rev], ["sales_records"], "medium",
                       ["aggregate", "date"], values={"count": len(q4), "total_amount": q4_rev}))
    h1 = sum(s["total_amount"] for s in sales if _date(s, "sale_date") < "2025-07-01")
    h2 = total_rev - h1
    rows.append(db_row("db-24", "Compare our sales revenue in the first half of 2025 with the second half.",
                       f"H1 {_fmt(h1)}; H2 {_fmt(h2)}.", [h1, h2], ["sales_records"], "hard", ["aggregate", "date"],
                       values={"H1": h1, "H2": h2}))
    osel_sales = [s for s in sales if name[s["drug_id"]] == "Oseltamivir Phosphate Capsules"]
    top_cust = max(osel_sales, key=lambda s: s["quantity_sold"])
    rows.append(db_row("db-25", "Which customer bought the most units of Oseltamivir Phosphate Capsules from us, and how many?",
                       f"{top_cust['customer_name']}, {_fmt(top_cust['quantity_sold'])} units.",
                       [top_cust["customer_name"], top_cust["quantity_sold"]], ["sales_records", "drugs"], "medium",
                       ["ranking", "lookup"], method="contains_all",
                       values={"customer_name": top_cust["customer_name"], "quantity_sold": top_cust["quantity_sold"]}))
    n_cust = len({s["customer_name"] for s in sales})
    n_reps = len({s["sales_rep"] for s in sales})
    rows.append(db_row("db-26", "How many distinct customers and how many distinct sales departments appear in our sales records?",
                       f"{n_cust} customers and {n_reps} sales departments.", [n_cust, n_reps], ["sales_records"], "medium",
                       ["aggregate", "distinct"], values={"customers": n_cust, "sales_reps": n_reps}))
    large = [s for s in sales if s["total_amount"] >= 100_000]
    rows.append(db_row("db-27", "How many sales had a total amount of at least 100,000, and which customers were they?",
                       f"{len(large)} sales: " + "; ".join(s["customer_name"] for s in large) + ".",
                       [len(large)] + [s["customer_name"] for s in large], ["sales_records"], "medium", ["filter"],
                       method="contains_all", values={"count": len(large), "customers": [s["customer_name"] for s in large]}))
    sell_through = {n: units_by_drug[n] / inv_by_drug[n] for n in inv_by_drug}
    st_name = max(sell_through, key=sell_through.get)
    st_pct = round(sell_through[st_name] * 100, 1)
    rows.append(db_row("db-28", "Which drug has the highest ratio of units sold to units currently on hand, and what is that ratio as a percentage?",
                       f"{st_name}, {st_pct}% ({_fmt(units_by_drug[st_name])} sold vs {_fmt(inv_by_drug[st_name])} on hand).",
                       [st_name, st_pct], ["sales_records", "inventory", "drugs"], "hard",
                       ["aggregate", "lookup", "ratio", "multi-collection"], method="contains_all",
                       values={"drug": st_name, "sell_through_pct": st_pct}))
    non_h = sorted(d["generic_name"] for d in drugs if not d["approval_number"].startswith("H"))
    rows.append(db_row("db-29", "Which of our drugs have an approval number that does not start with the letter H?",
                       " and ".join(non_h) + ".", non_h, ["drugs"], "medium", ["filter", "regex"],
                       method="contains_all", values={"drugs": non_h}))
    met = by_id[3]
    rows.append(db_row("db-30", "For Metformin Hydrochloride Tablets, give the brand name, pack specification, total units on hand, and total sales revenue.",
                       f"{met['brand_name']}; {met['specifications']}; {_fmt(inv_by_drug[met['generic_name']])} on hand; "
                       f"{_fmt(rev_by_drug[met['generic_name']])} revenue.",
                       [met["brand_name"], met["specifications"], inv_by_drug[met["generic_name"]], rev_by_drug[met["generic_name"]]],
                       ["drugs", "inventory", "sales_records"], "hard", ["lookup", "aggregate", "multi-collection"],
                       method="contains_all",
                       values={"brand_name": met["brand_name"], "specifications": met["specifications"],
                               "quantity_on_hand": inv_by_drug[met["generic_name"]], "total_amount": rev_by_drug[met["generic_name"]]}))
    rows.append(db_row("db-31", "How many units of Vitamin C Tablets do we have in stock?",
                       "None: Vitamin C Tablets are not in the catalogue, so there is no inventory for them.",
                       ["not"], ["drugs", "inventory"], "medium", ["negative", "hallucination-check"], method="contains_any",
                       values={"quantity_on_hand": 0},
                       notes="Grader: answer must state the product does not exist / no records; any positive quantity is a failure."))
    rows[-1]["grader"]["targets"] = ["not in", "no record", "does not exist", "not found", "no inventory", "not carry",
                                     "not listed", "no such", "no vitamin c", "0 matching", "zero matching"]
    return rows


def load_source(name: str) -> list[dict]:
    path = SOURCES / f"{name}.jsonl"
    if not path.exists():
        return []
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def build() -> list[dict]:
    rows = build_db_rows()
    for name in SOURCE_ORDER:
        rows.extend(load_source(name))
    ids = [r["id"] for r in rows]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    if dupes:
        raise SystemExit(f"duplicate ids: {dupes}")
    return rows


def dumps(rows: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="verify v1.jsonl is up to date instead of writing it")
    args = parser.parse_args()
    text = dumps(build())
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != text:
            print(f"{OUTPUT.relative_to(PROJECT_ROOT)} is stale; run `uv run python evals/golden/build.py`", file=sys.stderr)
            return 1
        print("golden set is up to date")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    counts = Counter(r["specialist"] for r in build())
    print(f"wrote {OUTPUT.relative_to(PROJECT_ROOT)}: {sum(counts.values())} rows {dict(counts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
