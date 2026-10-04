# Calibration review sheet: v1_baseline

## Grading criteria

Grade each answer on three metrics and record the grades in `human_grades.jsonl` (same directory, one line
per row id): `groundedness` and `completeness` as `true`/`false`, `report_quality` as an integer 1–5, and
`notes`. These are the metrics the LLM judge grades (`prompt/prompts.yaml`, `evals.judge`); the criteria
below restate its rubrics. Grade the three metrics independently: a wrong answer can still be grounded,
and a padded answer can still be complete.

### What each row shows

- **Question**: what the user asked.
- **Gold answer**: the minimum a correct answer must convey. Use it for completeness only.
- **Route**: expected versus actual delegation. Context only; not graded here.
- **Evidence**: every tool output recorded during the run (database results, web search summaries with
  their source lists, knowledge-base answers and passages), exactly as the judge receives it. Tool
  arguments such as query filters or aggregation pipelines are not recorded, only outputs. If the block
  ends with `[evidence truncated]`, the judge saw the same cut: grade against what is shown.
- **Answer**: the text being graded.

### groundedness (true / false)

Is every material factual claim in the answer supported by the evidence block? Use only the evidence,
not your own knowledge of the data or the gold answer.

- **Supported**: the evidence states it, or it follows arithmetically from the evidence (sums, ratios,
  percentages, counts of listed items). Check the arithmetic; a miscalculated figure is unsupported.
- **Unsupported**: it contradicts the evidence, or it asserts a specific fact (number, date, name, dosage,
  quotation, citation) that appears in no evidence. A data-quality assurance ("no null quantities",
  "no expired batches", "no orphan ids") is unsupported unless the outputs shown establish it; an empty
  result from an unrecorded query does not.
- **Inferred from complete results**: a claim that necessarily follows from outputs covering every record
  (an unfiltered count, or groups that add up to the collection total) is supported, even when no query
  testing it directly is shown. Example: if all 20 sales fall within a 2025 date range, none has a null
  `sale_date`. If the outputs do not show that every record is covered, the claim is unsupported.
- **Labelled inferences**: a claim the answer itself marks as an inference, assumption or estimate
  ("inferred from", "assuming", "likely") is neutral, provided the answer does not state it elsewhere as
  fact. The same claim stated flatly is graded normally.
- **Web sources**: a claim attributed to a web source is supported only when the search summary states
  it. A title or URL in a source list shows that the page exists, not what it says.
- **Neutral (ignore)**: general background a reader would accept without a source (definitions,
  well-known drug classes) unless the answer attributes it to a source; process narration (which tools or
  collections were consulted and the query or pipeline used, whether files were attached, what the
  assistant could not do); and
  statements of what a figure includes or excludes by construction ("gross stock, not net of
  reservations"), which describe the method rather than the data.
- An answer that honestly says information was unavailable is grounded.
- **Material** means any specific fact a reader could rely on, including side tables, comparisons and
  caveats, not only the headline answer. `true` only when no material claim is unsupported; one is
  enough for `false`.

### completeness (true / false)

Does the answer convey every fact in the gold answer?

- `true`: every gold fact is present and not contradicted elsewhere in the answer. Equivalent forms count
  (25,000 = 25000; "third generation" = "3rd-generation"; a more precise value that falls within the gold
  one, such as 27 October 1999 for "October 1999"). Extra content does not matter here.
- `false`: a gold fact is missing, wrong, contradicted, or hedged into uselessness.
- If the gold answer says no record exists or that the request should be declined, an answer that
  invents data is `false`.
- Ignore the evidence here: a gold fact stated without supporting evidence still counts as present (that
  is a groundedness failure, not a completeness one).

### report_quality (1–5)

Rate the answer as a research deliverable:

- **5**: answers the question first; structure fits the content (a table for tabular data, prose for a
  single fact); states provenance (which database, document or web source); no padding; no invented
  detail; in the user's language.
- **4**: answers directly with minor issues: slightly long, one vague provenance statement, or a small
  formatting problem.
- **3**: answers the question but is hard to use: buried answer, padded sections, unclear provenance, or
  unnecessary caveats.
- **2**: partial or confusing: important parts missing, contradictory statements, or mostly process
  narration ("I queried...") instead of results.
- **1**: does not answer, is wrong throughout, or is unreadable.

When two levels fit, choose the one whose description matches the most serious problem.

### notes

For every `false` and every rating below 5, name the specific claim (groundedness), the missing or wrong
gold fact (completeness), or the main problem (report_quality). Leave a metric `null` if you cannot
decide; rows with `null` grades are skipped as pending.

## 1. db-02 (db, easy)

**Question:** How many of our drugs are supplied as capsules?

**Gold answer:** 4 capsule products.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[3] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[4] tool count_documents returned:
{"count": 10}

[5] tool aggregate_documents returned:
{"documents": [{"_id": "Capsule", "count": 4}, {"_id": "Tablet", "count": 4}, {"_id": "Powder", "count": 1}, {"_id": "Injection", "count": 1}], "count": 4, "appliedLimits": []}

[6] tool find_documents returned:
{"documents": [{"drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "specifications": "0.25g*24 capsules", "dosage_form": "Capsule", "therapeutic_area": "Antibiotic"}, {"drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule", "therapeutic_area": "Analgesic/Antipyretic"}, {"drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "specifications": "75mg*10 capsules", "dosage_form": "Capsule", "therapeutic_area": "Antiviral"}, {"drug_id": 10, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "specifications": "0.35g*24 capsules", "dosage_form": "Capsule", "therapeutic_area": "TCM / Cold & Flu"}], "queryResultsCount": 4, "appliedLimits": []}
```

</details>

**Answer:**

## Answer: **4 of our 10 drugs** are supplied as capsules.

I queried our internal drug records (MongoDB `drugs` collection). The collection records the supply form in the **`dosage_form`** field, and the capsule entries are all recorded with the single value **`"Capsule"`** (no sub-variants such as "hard/soft capsule").

### Breakdown by dosage form

| Dosage form | Count |
|---|---|
| Capsule | **4** |
| Tablet | 4 |
| Powder | 1 |
| Injection | 1 |
| **Total** | **10** |

### The 4 capsule drugs

| drug_id | Generic name | Brand | Specification | Therapeutic area |
|---|---|---|---|---|
| 1 | Amoxicillin Capsules | Amoxin | 0.25g × 24 capsules | Antibiotic |
| 2 | Ibuprofen Sustained-Release Capsules | Fenbid | 0.3g × 20 capsules | Analgesic / Antipyretic |
| 5 | Oseltamivir Phosphate Capsules | Tamiflu | 75mg × 10 capsules | Antiviral |
| 10 | Lianhua Qingwen Capsules | Lianhua Qingwen | 0.35g × 24 capsules | TCM / Cold & Flu |

**Source:** Internal database — `drugs` collection, field `dosage_form` (value `"Capsule"`). No external or document sources were needed for this question, and no reference files were present in the working directory.

---

## 2. db-04 (db, easy)

**Question:** How many sales records were booked in calendar year 2025?

**Gold answer:** 20 sales records.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[3] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[4] tool count_documents returned:
{"count": 20}

[5] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c46980304"}, "sale_id": 1, "drug_id": 1, "sale_date": {"$date": "2025-02-15T00:00:00.000Z"}, "quantity_sold": 200, "unit_price": 25, "total_amount": 5000, "customer_name": "Beijing Chaoyang Hospital", "region": "North China", "sales_rep": "Beijing Chaoyang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980305"}, "sale_id": 2, "drug_id": 1, "sale_date": {"$date": "2025-08-10T00:00:00.000Z"}, "quantity_sold": 500, "unit_price": 24.5, "total_amount": 12250, "customer_name": "Tianjin Pharmacy", "region": "North China", "sales_rep": "Tianjin Nankai Sales Branch"}, {"_id": {"$oid": "6aabf438cb80345c46980306"}, "sale_id": 3, "drug_id": 2, "sale_date": {"$date": "2025-01-20T00:00:00.000Z"}, "quantity_sold": 1000, "unit_price": 15, "total_amount": 15000, "customer_name": "Neptunus Pharmacy Chain", "region": "East China", "sales_rep": "Hangzhou Binjiang Sales Dept."}], "queryResultsCount": 20, "appliedLimits": []}

[6] tool aggregate_documents returned:
{"documents": [{"_id": 2025, "count": 20, "min_date": {"$date": "2025-01-10T00:00:00.000Z"}, "max_date": {"$date": "2025-12-20T00:00:00.000Z"}}], "count": 1, "appliedLimits": []}

[7] tool aggregate_documents returned:
{"documents": [{"_id": null, "total": 20, "earliest": {"$date": "2025-01-10T00:00:00.000Z"}, "latest": {"$date": "2025-12-20T00:00:00.000Z"}}], "count": 1, "appliedLimits": []}

[8] tool count_documents returned:
{"count": 0}

[9] tool count_documents returned:
{"count": 20}

[10] tool count_documents returned:
{"count": 0}
```

</details>

**Answer:**

## Sales records booked in calendar year 2025

**Answer: 20 sales records** were booked in calendar year 2025.

### How this was determined (internal database)
| Item | Detail |
|---|---|
| Source | Internal database, `sales_records` collection |
| Date field | `sale_date` (BSON `Date`, stored as UTC midnight, e.g. `2025-02-15T00:00:00.000Z`) |
| Filter used | `sale_date` ≥ `2025-01-01T00:00:00Z` and ≤ `2025-12-31T23:59:59.999Z` |
| Method | Full `count_documents` over the collection (exact count, not sampled) |
| **Result** | **20** |

### Coverage check (year-by-year breakdown)
| Year | Records | Earliest `sale_date` | Latest `sale_date` |
|------|--------:|----------------------|--------------------|
| 2025 | 20 | 2025-01-10 | 2025-12-20 |

### Caveats
- **Small dataset:** the collection contains only 20 records, and **all of them fall within 2025** — so the year-by-year table has just one row and cannot cross-validate against other years.
- **Data integrity:** no records have a missing, null, or non-date `sale_date`.
- **Timezone:** since the range (Jan 10 – Dec 20) is far from any year boundary, the count is unaffected by timezone interpretation.
- "Booked" was interpreted as the record's `sale_date`; the schema has no separate order/booking-date field, so this is the only booking-date field available.

### Notes
- No reference/upload files were present in the working directory, so nothing external was consulted.
- This is an internal-record figure only; no public/web or RAGFlow sources were needed for this question.

If you'd like, I can break the 20 records down further (e.g., by product/drug or by month).

---

## 3. db-06 (db, medium)

**Question:** Which drug do we hold the most stock of, and how many units is that?

**Gold answer:** Lianhua Qingwen Capsules, 160,000 units.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[3] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[4] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e6"}, "inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e7"}, "inventory_id": 2, "drug_id": 1, "batch_number": "MY-250615-B", "quantity_on_hand": 8000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e8"}, "inventory_id": 3, "drug_id": 1, "batch_number": "MY-251120-C", "quantity_on_hand": 12000, "warehouse_location": "Tianjin Warehouse 1 - Zone A", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e9"}, "inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ea"}, "inventory_id": 5, "drug_id": 2, "batch_number": "MY-250615-B", "quantity_on_hand": 15000, "warehouse_location": "Beijing Warehouse 1 - Zone C", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}], "queryResultsCount": 30, "appliedLimits": []}

[5] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[6] tool count_documents returned:
{"count": 30}

[7] tool aggregate_documents returned:
{"documents": [{"_id": 10, "total_units": 160000, "batches": 3, "warehouses": ["Beijing Warehouse 2 - Epidemic Prevention Zone", "Tianjin Warehouse 2 - Epidemic Prevention Zone", "Tianjin Warehouse 1 - Epidemic Prevention Zone"], "min_qty": 10000, "max_expiry": {"$date": "2027-11-19T00:00:00.000Z"}, "drug": {"_id": {"$oid": "6aabf437cb80345c469802e5"}, "drug_id": 10, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "approval_number": "Z20040063", "specifications": "0.35g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "TCM / Cold & Flu", "description": "Clears heat-toxin and disperses lung heat. Used to treat influenza with heat-toxin attacking the lung, presenting as fever or high fever, chills, muscle aches, nasal congestion and runny nose, cough, headache, dry and sore throat."}}, {"_id": 2, "total_units": 47000, "batches": 3, "warehouses": ["Tianjin Warehouse 2 - Cold Storage", "Tianjin Warehouse 1 - Zone A", "Beijing Warehouse 1 - Zone C"], "min_qty": 2000, "max_expiry": {"$date": "2027-11-19T00:00:00.000Z"}, "drug": {"_id": {"$oid": "6aabf437cb80345c469802dd"}, "drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "approval_number": "H10900089", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Analgesic/Antipyretic", "description": "Used to relieve mild to moderate pain such as headache, joint pain, migraine, toothache, muscle pain, neuralgia, and dysmenorrhea. Also used for fever caused by the common cold or influenza."}}, {"_id": 5, "total_units": 25500, "batches": 3, "warehouses": ["Tianjin Warehouse 1 - Emergency Drug Zone", "Beijing Warehouse 1 - Emergency Drug Zone", "Beijing Warehouse 2 - Emergency Drug Zone"], "min_qty": 500, "max_expiry": {"$date": "2027-11-19T00:00:00.000Z"}, "drug": {"_id": {"$oid": "6aabf437cb80345c469802e0"}, "drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "approval_number": "H20090123", "specifications": "75mg*10 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antiviral", "description": "For the treatment of influenza A and B in adults and children aged 1 year and older."}}, {"_id": 1, "total_units": 25000, "batches": 3, "warehouses": ["Tianjin Warehouse 1 - Zone A", "Beijing Warehouse 1 - Zone A", "Beijing Warehouse 2 - Zone B"], "min_qty": 5000, "max_expiry": {"$date": "2027-11-19T00:00:00.000Z"}, "drug": {"_id": {"$oid": "6aabf437cb80345c469802dc"}, "drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "approval_number": "H20051234", "specifications": "0.25g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "Used to treat upper respiratory tract infections, urogenital infections, and others caused by susceptible bacteria."}}, {"_id": 7, "total_units": 24000, "batches": 3, "warehouses": ["Beijing Warehouse 2 - General Drug Zone", "Tianjin Warehouse 2 - General Drug Zone", "Beijing Warehouse 1 - General Drug Zone"], "min_qty": 4000, "max_expiry": {"$date": "2027-11-19T00:00:00.000Z"}, "drug": {"_id": {"$oid": "6aabf437cb80345c469802e2"}, "drug_id": 7, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "approval_number": "H20000456", "specifications": "3g*10 sachets", "dosage_form": "Powder", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Digestive System", "description": "For acute and chronic diarrhea in adults and children."}}], "count": 5, "appliedLimits": []}

[8] tool find_documents returned:
{"documents": [{"inventory_id": 28, "batch_number": "MY-250101-A", "quantity_on_hand": 10000, "warehouse_location": "Tianjin Warehouse 2 - Epidemic Prevention Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"inventory_id": 29, "batch_number": "MY-250615-B", "quantity_on_hand": 50000, "warehouse_location": "Beijing Warehouse 2 - Epidemic Prevention Zone", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"inventory_id": 30, "batch_number": "MY-251120-C", "quantity_on_hand": 100000, "warehouse_location": "Tianjin Warehouse 1 - Epidemic Prevention Zone", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}], "queryResultsCount": 3, "appliedLimits": []}

[9] tool aggregate_documents returned:
{"documents": [], "count": 0, "appliedLimits": []}

[10] tool aggregate_documents returned:
{"documents": [{"_id": null, "total": 336000, "n": 30, "distinct_drugs": [3, 5, 2, 9, 8, 4, 10, 7, 6, 1]}], "count": 1, "appliedLimits": []}
```

</details>

**Answer:**

## Answer

We hold the most stock of **Lianhua Qingwen Capsules (Lianhua Qingwen)** — **160,000 units** on hand.

| Field | Value |
|---|---|
| Generic name | Lianhua Qingwen Capsules |
| Brand | Lianhua Qingwen |
| Drug ID | 10 |
| Approval number | Z20040063 |
| Specification | 0.35 g × 24 capsules |
| Dosage form | Capsule |
| Therapeutic area | TCM / Cold & Flu |
| **Total units on hand** | **160,000** |

*Source: internal `inventory` collection, grouped by `drug_id` and summed on `quantity_on_hand`, joined to the `drugs` collection for names (internal database — no public or RAG sources were used).*

### How it compares (top 5 by units on hand)

| Rank | Drug | Form / Spec | Total units |
|---|---|---|---|
| 1 | Lianhua Qingwen Capsules | Capsule, 0.35 g × 24 | **160,000** |
| 2 | Ibuprofen Sustained-Release Capsules (Fenbid) | Capsule, 0.3 g × 20 | 47,000 |
| 3 | Oseltamivir Phosphate Capsules (Tamiflu) | Capsule, 75 mg × 10 | 25,500 |
| 4 | Amoxicillin Capsules (Amoxin) | Capsule, 0.25 g × 24 | 25,000 |
| 5 | Montmorillonite Powder (Smecta) | Powder, 3 g × 10 sachets | 24,000 |

The leader holds roughly **3.4×** the runner-up's stock.

### Supporting detail for the leader
The 160,000 units come from **3 batches**, all stored in epidemic-prevention zones across two cities:

| Batch | Quantity | Location | Expiry |
|---|---|---|---|
| MY-250101-A | 10,000 | Tianjin Warehouse 2 – Epidemic Prevention Zone | 2027-01-01 |
| MY-250615-B | 50,000 | Beijing Warehouse 2 – Epidemic Prevention Zone | 2027-06-14 |
| MY-251120-C | 100,000 | Tianjin Warehouse 1 – Epidemic Prevention Zone | 2027-11-19 |

### Notes and caveats
- No anomalies found: no batches with zero/negative or null quantities, and none expired — the total is not skewed by void or expired stock.
- The figure is **gross on-hand stock**, not net of reservations or pending sales.
- It's a **company-wide** total spread across 3 warehouses (2 in Tianjin, 1 in Beijing), not a single-location figure.
- The inventory collection contains 30 batches across 10 drugs (336,000 units overall); each drug holds 3 batches.

No attachments were present in the working directory, so this answer rests solely on internal database records. Let me know if you'd like this as a downloadable Markdown or PDF report, or a breakdown by warehouse.

---

## 4. db-10 (db, medium)

**Question:** Which three regions generated the most sales revenue, and how much each?

**Gold answer:** Nationwide 1,000,000; Northeast China 500,000; North China 417,250.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[3] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[4] tool count_documents returned:
{"count": 20}

[5] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c46980317"}, "sale_id": 20, "drug_id": 10, "sale_date": {"$date": "2025-12-20T00:00:00.000Z"}, "quantity_sold": 50000, "unit_price": 20, "total_amount": 1000000, "customer_name": "National Pharmacy Chain Central Warehouse", "region": "Nationwide", "sales_rep": "Corporate Key Accounts Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980307"}, "sale_id": 4, "drug_id": 2, "sale_date": {"$date": "2025-12-05T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 15, "total_amount": 75000, "customer_name": "Shanghai Huashan Hospital", "region": "East China", "sales_rep": "Shanghai Jing'an Sales HQ"}, {"_id": {"$oid": "6aabf438cb80345c46980313"}, "sale_id": 16, "drug_id": 8, "sale_date": {"$date": "2025-11-11T00:00:00.000Z"}, "quantity_sold": 500, "unit_price": 30, "total_amount": 15000, "customer_name": "First Hospital of Lanzhou University", "region": "Northwest China", "sales_rep": "Lanzhou Chengguan Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030d"}, "sale_id": 10, "drug_id": 5, "sale_date": {"$date": "2025-11-01T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 100, "total_amount": 500000, "customer_name": "Heilongjiang Provincial Hospital", "region": "Northeast China", "sales_rep": "Harbin Xiangfang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030b"}, "sale_id": 8, "drug_id": 4, "sale_date": {"$date": "2025-10-18T00:00:00.000Z"}, "quantity_sold": 150, "unit_price": 45, "total_amount": 6750, "customer_name": "Chongqing Pharmacy", "region": "Southwest China", "sales_rep": "Chongqing Yuzhong Sales Dept."}], "queryResultsCount": 20, "appliedLimits": []}

[6] tool aggregate_documents returned:
{"documents": [{"_id": "Nationwide", "revenue": 1000000, "check_qty_price": 1000000, "records": 1}, {"_id": "Northeast China", "revenue": 500000, "check_qty_price": 500000, "records": 1}, {"_id": "North China", "revenue": 417250, "check_qty_price": 417250, "records": 4}, {"_id": "East China", "revenue": 166000, "check_qty_price": 166000, "records": 6}, {"_id": "South China", "revenue": 24500, "check_qty_price": 24500, "records": 2}, {"_id": "Northwest China", "revenue": 21000, "check_qty_price": 21000, "records": 2}, {"_id": "Central China", "revenue": 13200, "check_qty_price": 13200, "records": 2}, {"_id": "Southwest China", "revenue": 11250, "check_qty_price": 11250, "records": 2}], "count": 8, "appliedLimits": []}

[7] tool aggregate_documents returned:
{"documents": [{"by_region": [{"_id": "Nationwide", "revenue": 1000000, "records": 1}, {"_id": "Northeast China", "revenue": 500000, "records": 1}, {"_id": "North China", "revenue": 417250, "records": 4}, {"_id": "East China", "revenue": 166000, "records": 6}, {"_id": "South China", "revenue": 24500, "records": 2}, {"_id": "Northwest China", "revenue": 21000, "records": 2}, {"_id": "Central China", "revenue": 13200, "records": 2}, {"_id": "Southwest China", "revenue": 11250, "records": 2}], "overall": [{"_id": null, "total_revenue": 2153200, "min_date": {"$date": "2025-01-10T00:00:00.000Z"}, "max_date": {"$date": "2025-12-20T00:00:00.000Z"}, "records": 20}]}], "count": 1, "appliedLimits": []}
```

</details>

**Answer:**

## Top 3 Regions by Sales Revenue

**Source: internal sales database** (`sales_records` collection, 20 records, covering 2025-01-10 → 2025-12-20). Revenue taken from the dedicated `total_amount` field, grouped by `region` and summed.

| Rank | Region | Sales Revenue | Records |
|---:|---|---:|---:|
| 1 | Nationwide | 1,000,000 | 1 |
| 2 | Northeast China | 500,000 | 1 |
| 3 | North China | 417,250 | 4 |

Total revenue across all eight regions: **2,153,200**.

### ⚠️ One important caveat

**"Nationwide" is not a geographic region.** It is stored in the same `region` field, but its single record is a corporate/central-warehouse sale ("National Pharmacy Chain Central Warehouse", rep "Corporate Key Accounts Dept."). If you want the top three *geographic* regions, the ranking shifts:

| Rank | Geographic Region | Sales Revenue |
|---:|---|---:|
| 1 | Northeast China | 500,000 |
| 2 | North China | 417,250 |
| 3 | East China | 166,000 |

### Notes on the figures
- **Currency unit is not specified** in the database schema — no currency field or symbol exists. The values are reported exactly as stored. (Customers are Chinese hospitals, which *suggests* CNY, but this is not confirmed by the data.)
- All values are whole numbers; no rounding was applied.
- Validation: `quantity_sold × unit_price` was summed per region and matched `total_amount` exactly, confirming it is the correct revenue measure.

### Missing / unavailable information
- **No reference files were found** in the working directory or `uploads/`, so there was nothing to cross-check against. If you attached a file, it did not reach my workspace — please re-upload it and I'll incorporate it.
- No public web search or internal knowledge-base lookup was needed for this question, as it is entirely answerable from internal sales records. If you'd like, I can also pull the supporting detail (customer, product, sales rep) behind any of these region totals, or break revenue down by month or product.

---

## 5. db-11 (db, easy)

**Question:** How many sales records are from the East China region?

**Gold answer:** 6 records.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[3] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[4] tool count_documents returned:
{"count": 20}

[5] tool aggregate_documents returned:
{"documents": [{"_id": "East China", "count": 6}, {"_id": "North China", "count": 4}, {"_id": "Southwest China", "count": 2}, {"_id": "Central China", "count": 2}, {"_id": "Northwest China", "count": 2}, {"_id": "South China", "count": 2}, {"_id": "Northeast China", "count": 1}, {"_id": "Nationwide", "count": 1}], "count": 8, "appliedLimits": []}

[6] tool count_documents returned:
{"count": 6}
```

</details>

**Answer:**

## Answer: 6 sales records

Based on a direct query of the company's internal **`sales_records`** collection (MongoDB), **6 of the 20 sales records** are from the **East China** region.

### How it was determined

| Detail | Value |
|---|---|
| Source | Internal database — `sales_records` collection |
| Field used | `region` (stored directly on each record; no join needed) |
| Matched value | `"East China"` |
| **East China records** | **6** |
| Total records in collection | 20 |

### Region breakdown (full context)

| Region | Records |
|---|---|
| East China | **6** |
| North China | 4 |
| Southwest China | 2 |
| Central China | 2 |
| Northwest China | 2 |
| South China | 2 |
| Northeast China | 1 |
| Nationwide | 1 |

### Caveats
- Region values are stored in **English** (`"East China"`), not Chinese. A filter on `"华东地区"` would return 0 results.
- The `"Nationwide"` category is a separate value and was **not** counted as East China — only the exact value `"East China"` was included.
- The dataset is small (20 records total), so this count reflects the entire collection.

*No reference/attachment files were present in the working directory, and no public web or knowledge-base sources were needed for this internal count.*

---

## 6. db-14 (db, medium)

**Question:** Which inventory batches expire before 1 July 2027, and how many inventory records is that?

**Gold answer:** 20 records, batches MY-250101-A and MY-250615-B.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[3] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[4] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[5] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e6"}, "inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e7"}, "inventory_id": 2, "drug_id": 1, "batch_number": "MY-250615-B", "quantity_on_hand": 8000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e8"}, "inventory_id": 3, "drug_id": 1, "batch_number": "MY-251120-C", "quantity_on_hand": 12000, "warehouse_location": "Tianjin Warehouse 1 - Zone A", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e9"}, "inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ea"}, "inventory_id": 5, "drug_id": 2, "batch_number": "MY-250615-B", "quantity_on_hand": 15000, "warehouse_location": "Beijing Warehouse 1 - Zone C", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}], "queryResultsCount": 30, "appliedLimits": []}

[6] tool count_documents returned:
{"count": 30}

[7] tool count_documents returned:
{"count": 0}

[8] tool count_documents returned:
{"count": 20}

[9] tool aggregate_documents returned:
{"documents": [{"inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "specifications": "0.25g*24 capsules"}, {"inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "specifications": "0.3g*20 capsules"}, {"inventory_id": 7, "drug_id": 3, "batch_number": "MY-250101-A", "quantity_on_hand": 3000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "specifications": "0.5g*48 tablets"}, {"inventory_id": 10, "drug_id": 4, "batch_number": "MY-250101-A", "quantity_on_hand": 1000, "warehouse_location": "Tianjin Warehouse 1 - High-Value Zone", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "specifications": "20mg*7 tablets"}, {"inventory_id": 13, "drug_id": 5, "batch_number": "MY-250101-A", "quantity_on_hand": 500, "warehouse_location": "Beijing Warehouse 1 - Emergency Drug Zone", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "specifications": "75mg*10 capsules"}, {"inventory_id": 16, "drug_id": 6, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cool Storage", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "specifications": "1.0g/vial"}, {"inventory_id": 19, "drug_id": 7, "batch_number": "MY-250101-A", "quantity_on_hand": 4000, "warehouse_location": "Beijing Warehouse 1 - General Drug Zone", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "specifications": "3g*10 sachets"}, {"inventory_id": 22, "drug_id": 8, "batch_number": "MY-250101-A", "quantity_on_hand": 1500, "warehouse_location": "Tianjin Warehouse 1 - Chronic Disease Zone", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat", "specifications": "30mg*30 tablets"}, {"inventory_id": 25, "drug_id": 9, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Beijing Warehouse 2 - Ambient Zone", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin", "specifications": "100mg*30 tablets"}, {"inventory_id": 28, "drug_id": 10, "batch_number": "MY-250101-A", "quantity_on_hand": 10000, "warehouse_location": "Tianjin Warehouse 2 - Epidemic Prevention Zone", "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "specifications": "0.35g*24 capsules"}, {"inventory_id": 2, "drug_id": 1, "batch_number": "MY-250615-B", "quantity_on_hand": 8000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "specifications": "0.25g*24 capsules"}, {"inventory_id": 5, "drug_id": 2, "batch_number": "MY-250615-B", "quantity_on_hand": 15000, "warehouse_location": "Beijing Warehouse 1 - Zone C", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "specifications": "0.3g*20 capsules"}, {"inventory_id": 8, "drug_id": 3, "batch_number": "MY-250615-B", "quantity_on_hand": 4500, "warehouse_location": "Tianjin Warehouse 2 - Zone B", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "specifications": "0.5g*48 tablets"}, {"inventory_id": 11, "drug_id": 4, "batch_number": "MY-250615-B", "quantity_on_hand": 2500, "warehouse_location": "Beijing Warehouse 2 - High-Value Zone", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "specifications": "20mg*7 tablets"}, {"inventory_id": 14, "drug_id": 5, "batch_number": "MY-250615-B", "quantity_on_hand": 5000, "warehouse_location": "Tianjin Warehouse 1 - Emergency Drug Zone", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "specifications": "75mg*10 capsules"}, {"inventory_id": 17, "drug_id": 6, "batch_number": "MY-250615-B", "quantity_on_hand": 3500, "warehouse_location": "Beijing Warehouse 2 - Cool Storage", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "specifications": "1.0g/vial"}, {"inventory_id": 20, "drug_id": 7, "batch_number": "MY-250615-B", "quantity_on_hand": 8000, "warehouse_location": "Tianjin Warehouse 2 - General Drug Zone", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "specifications": "3g*10 sachets"}, {"inventory_id": 23, "drug_id": 8, "batch_number": "MY-250615-B", "quantity_on_hand": 3000, "warehouse_location": "Beijing Warehouse 1 - Chronic Disease Zone", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat", "specifications": "30mg*30 tablets"}, {"inventory_id": 26, "drug_id": 9, "batch_number": "MY-250615-B", "quantity_on_hand": 4500, "warehouse_location": "Tianjin Warehouse 1 - Ambient Zone", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin", "specifications": "100mg*30 tablets"}, {"inventory_id": 29, "drug_id": 10, "batch_number": "MY-250615-B", "quantity_on_hand": 50000, "warehouse_location": "Beijing Warehouse 2 - Epidemic Prevention Zone", "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "specifications": "0.35g*24 capsules"}], "count": 20, "appliedLimits": []}
```

</details>

**Answer:**

## Answer

**20 inventory records** expire before **1 July 2027**, spanning **2 batch/lot numbers** and **10 distinct drugs**. (This is out of 30 total inventory records in the system.)

*Source: internal MongoDB business database (`inventory` collection, joined to `drugs` for names). No uploaded reference files were present in the working directory.*

### Matching batches

| Batch / Lot | Expiry date | Records | Total qty on hand | Warehouse locations involved |
|---|---|---|---|---|
| `MY-250101-A` | 2027-01-01 | 10 | 31,000 units | Beijing Warehouse 1 (Zones A, Emergency, General) & 2 (Zones B, Ambient); Tianjin Warehouse 1 (High-Value, Chronic Disease) & 2 (Cold/Cool Storage, Epidemic Prevention) |
| `MY-250615-B` | 2027-06-14 | 10 | 104,000 units | Beijing Warehouse 1 (Zones C, Chronic Disease) & 2 (Zones B, High-Value, Cool Storage, Epidemic Prevention); Tianjin Warehouse 1 (Emergency, Ambient) & 2 (Zones B, General, Epidemic Prevention) |

### Full list of the 20 records

| # | Batch | Drug ID | Drug (generic / brand) | Specification | Expiry | Qty on hand | Location |
|---|---|---|---|---|---|---|---|
| 1 | MY-250101-A | 1 | Amoxicillin Capsules / Amoxin | 0.25g×24 caps | 2027-01-01 | 5,000 | Beijing WH1 – Zone A |
| 2 | MY-250101-A | 2 | Ibuprofen SR Capsules / Fenbid | 0.3g×20 caps | 2027-01-01 | 2,000 | Tianjin WH2 – Cold Storage |
| 3 | MY-250101-A | 3 | Metformin HCl Tablets / Glucophage | 0.5g×48 tabs | 2027-01-01 | 3,000 | Beijing WH2 – Zone B |
| 4 | MY-250101-A | 4 | Atorvastatin Calcium Tablets / Lipitor | 20mg×7 tabs | 2027-01-01 | 1,000 | Tianjin WH1 – High-Value |
| 5 | MY-250101-A | 5 | Oseltamivir Phosphate Capsules / Tamiflu | 75mg×10 caps | 2027-01-01 | 500 | Beijing WH1 – Emergency |
| 6 | MY-250101-A | 6 | Ceftriaxone Sodium for Injection / Rocephin | 1.0g/vial | 2027-01-01 | 2,000 | Tianjin WH2 – Cool Storage |
| 7 | MY-250101-A | 7 | Montmorillonite Powder / Smecta | 3g×10 sachets | 2027-01-01 | 4,000 | Beijing WH1 – General |
| 8 | MY-250101-A | 8 | Nifedipine CR Tablets / Adalat | 30mg×30 tabs | 2027-01-01 | 1,500 | Tianjin WH1 – Chronic Disease |
| 9 | MY-250101-A | 9 | Aspirin Enteric-Coated Tablets / Bayaspirin | 100mg×30 tabs | 2027-01-01 | 2,000 | Beijing WH2 – Ambient |
| 10 | MY-250101-A | 10 | Lianhua Qingwen Capsules | 0.35g×24 caps | 2027-01-01 | 10,000 | Tianjin WH2 – Epidemic Prevention |
| 11 | MY-250615-B | 1 | Amoxicillin Capsules / Amoxin | 0.25g×24 caps | 2027-06-14 | 8,000 | Beijing WH2 – Zone B |
| 12 | MY-250615-B | 2 | Ibuprofen SR Capsules / Fenbid | 0.3g×20 caps | 2027-06-14 | 15,000 | Beijing WH1 – Zone C |
| 13 | MY-250615-B | 3 | Metformin HCl Tablets / Glucophage | 0.5g×48 tabs | 2027-06-14 | 4,500 | Tianjin WH2 – Zone B |
| 14 | MY-250615-B | 4 | Atorvastatin Calcium Tablets / Lipitor | 20mg×7 tabs | 2027-06-14 | 2,500 | Beijing WH2 – High-Value |
| 15 | MY-250615-B | 5 | Oseltamivir Phosphate Capsules / Tamiflu | 75mg×10 caps | 2027-06-14 | 5,000 | Tianjin WH1 – Emergency |
| 16 | MY-250615-B | 6 | Ceftriaxone Sodium for Injection / Rocephin | 1.0g/vial | 2027-06-14 | 3,500 | Beijing WH2 – Cool Storage |
| 17 | MY-250615-B | 7 | Montmorillonite Powder / Smecta | 3g×10 sachets | 2027-06-14 | 8,000 | Tianjin WH2 – General |
| 18 | MY-250615-B | 8 | Nifedipine CR Tablets / Adalat | 30mg×30 tabs | 2027-06-14 | 3,000 | Beijing WH1 – Chronic Disease |
| 19 | MY-250615-B | 9 | Aspirin Enteric-Coated Tablets / Bayaspirin | 100mg×30 tabs | 2027-06-14 | 4,500 | Tianjin WH1 – Ambient |
| 20 | MY-250615-B | 10 | Lianhua Qingwen Capsules | 0.35g×24 caps | 2027-06-14 | 50,000 | Beijing WH2 – Epidemic Prevention |

### Notes & caveats
- **Filter used:** `expiry_date < 2027-07-01T00:00:00Z` (strict). Batches expiring exactly on 2027-07-01 would be excluded; none exist. The next expiry after these two is 2027-11-19 (batch `MY-251120-C`), correctly excluded.
- **Field name:** the schema uses `expiry_date` (UTC midnight timestamps); batch identifier is `batch_number`; there is no SKU field (drugs are keyed by `drug_id`). No null expiry dates were found.
- **Quantity units:** `quantity_on_hand` is a raw count with no unit column — the unit depends on the dosage form (capsules/tablets/vials/sachets), so the combined 135,000 figure mixes units and is best read per batch.
- **Observation:** only two distinct expiry dates appear below the cutoff, each shared across all 10 drug batches, which looks like generated/test batch data rather than real inventory — noted for your awareness, not adjusted.

Would you like this as a downloadable Markdown/PDF report, or a narrower breakdown (e.g., only batches expiring in the next 6 months, or grouped by warehouse)?

---

## 7. db-15 (db, medium)

**Question:** How many units of stock expire on 1 January 2027?

**Gold answer:** 31,000 units (batch MY-250101-A).

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[3] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[4] tool count_documents returned:
{"count": 10}

[5] tool count_documents returned:
{"count": 30}

[6] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802ec"}, "inventory_id": 7, "drug_id": 3, "batch_number": "MY-250101-A", "quantity_on_hand": 3000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e9"}, "inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f2"}, "inventory_id": 13, "drug_id": 5, "batch_number": "MY-250101-A", "quantity_on_hand": 500, "warehouse_location": "Beijing Warehouse 1 - Emergency Drug Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ef"}, "inventory_id": 10, "drug_id": 4, "batch_number": "MY-250101-A", "quantity_on_hand": 1000, "warehouse_location": "Tianjin Warehouse 1 - High-Value Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e6"}, "inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}], "queryResultsCount": 30, "appliedLimits": []}

[7] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e6"}, "inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e9"}, "inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ec"}, "inventory_id": 7, "drug_id": 3, "batch_number": "MY-250101-A", "quantity_on_hand": 3000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ef"}, "inventory_id": 10, "drug_id": 4, "batch_number": "MY-250101-A", "quantity_on_hand": 1000, "warehouse_location": "Tianjin Warehouse 1 - High-Value Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f2"}, "inventory_id": 13, "drug_id": 5, "batch_number": "MY-250101-A", "quantity_on_hand": 500, "warehouse_location": "Beijing Warehouse 1 - Emergency Drug Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f5"}, "inventory_id": 16, "drug_id": 6, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cool Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f8"}, "inventory_id": 19, "drug_id": 7, "batch_number": "MY-250101-A", "quantity_on_hand": 4000, "warehouse_location": "Beijing Warehouse 1 - General Drug Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802fb"}, "inventory_id": 22, "drug_id": 8, "batch_number": "MY-250101-A", "quantity_on_hand": 1500, "warehouse_location": "Tianjin Warehouse 1 - Chronic Disease Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802fe"}, "inventory_id": 25, "drug_id": 9, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Beijing Warehouse 2 - Ambient Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c46980301"}, "inventory_id": 28, "drug_id": 10, "batch_number": "MY-250101-A", "quantity_on_hand": 10000, "warehouse_location": "Tianjin Warehouse 2 - Epidemic Prevention Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}], "queryResultsCount": 10, "appliedLimits": []}

[8] tool aggregate_documents returned:
{"documents": [{"inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin"}, {"inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid"}, {"inventory_id": 7, "drug_id": 3, "batch_number": "MY-250101-A", "quantity_on_hand": 3000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage"}, {"inventory_id": 10, "drug_id": 4, "batch_number": "MY-250101-A", "quantity_on_hand": 1000, "warehouse_location": "Tianjin Warehouse 1 - High-Value Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor"}, {"inventory_id": 13, "drug_id": 5, "batch_number": "MY-250101-A", "quantity_on_hand": 500, "warehouse_location": "Beijing Warehouse 1 - Emergency Drug Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu"}, {"inventory_id": 16, "drug_id": 6, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cool Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin"}, {"inventory_id": 19, "drug_id": 7, "batch_number": "MY-250101-A", "quantity_on_hand": 4000, "warehouse_location": "Beijing Warehouse 1 - General Drug Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta"}, {"inventory_id": 22, "drug_id": 8, "batch_number": "MY-250101-A", "quantity_on_hand": 1500, "warehouse_location": "Tianjin Warehouse 1 - Chronic Disease Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat"}, {"inventory_id": 25, "drug_id": 9, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Beijing Warehouse 2 - Ambient Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin"}, {"inventory_id": 28, "drug_id": 10, "batch_number": "MY-250101-A", "quantity_on_hand": 10000, "warehouse_location": "Tianjin Warehouse 2 - Epidemic Prevention Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen"}], "count": 10, "appliedLimits": []}

[9] tool aggregate_documents returned:
{"documents": [{"_id": {"$date": "2027-01-01T00:00:00.000Z"}, "batch_count": 10, "units": 31000}, {"_id": {"$date": "2027-06-14T00:00:00.000Z"}, "batch_count": 10, "units": 104000}, {"_id": {"$date": "2027-11-19T00:00:00.000Z"}, "batch_count": 10, "units": 201000}], "count": 3, "appliedLimits": []}

[10] tool aggregate_documents returned:
{"documents": [{"_id": null, "total_batches": 30, "min_expiry": {"$date": "2027-01-01T00:00:00.000Z"}, "max_expiry": {"$date": "2027-11-19T00:00:00.000Z"}, "total_units_all": 336000}], "count": 1, "appliedLimits": []}

[11] tool aggregate_documents returned:
{"documents": [{"_id": null, "matched_batches": 10, "total_units": 31000}], "count": 1, "appliedLimits": []}
```

</details>

**Answer:**

**31,000 units** of stock expire on 1 January 2027, across 10 inventory batches.

## Answer

| Metric | Value |
|---|---|
| Batches expiring 2027-01-01 | 10 |
| **Total units expiring 2027-01-01** | **31,000** |
| Source | Internal `inventory` collection (MongoDB) |
| Expiry field | `expiry_date` (BSON Date, stored as `2027-01-01T00:00:00Z`) |

### Batch detail

All 10 batches share the batch number `MY-250101-A` (production date 2025-01-01):

| Drug (generic) | Brand | Units | Expiry | Location |
|---|---|---:|---|---|
| Amoxicillin Capsules | Amoxin | 5,000 | 2027-01-01 | Beijing Warehouse 1 – Zone A |
| Ibuprofen Sustained-Release Capsules | Fenbid | 2,000 | 2027-01-01 | Tianjin Warehouse 2 – Cold Storage |
| Metformin Hydrochloride Tablets | Glucophage | 3,000 | 2027-01-01 | Beijing Warehouse 2 – Zone B |
| Atorvastatin Calcium Tablets | Lipitor | 1,000 | 2027-01-01 | Tianjin Warehouse 1 – High-Value Zone |
| Oseltamivir Phosphate Capsules | Tamiflu | 500 | 2027-01-01 | Beijing Warehouse 1 – Emergency Drug Zone |
| Ceftriaxone Sodium for Injection | Rocephin | 2,000 | 2027-01-01 | Tianjin Warehouse 2 – Cool Storage |
| Montmorillonite Powder | Smecta | 4,000 | 2027-01-01 | Beijing Warehouse 1 – General Drug Zone |
| Nifedipine Controlled-Release Tablets | Adalat | 1,500 | 2027-01-01 | Tianjin Warehouse 1 – Chronic Disease Zone |
| Aspirin Enteric-Coated Tablets | Bayaspirin | 2,000 | 2027-01-01 | Beijing Warehouse 2 – Ambient Zone |
| Lianhua Qingwen Capsules | Lianhua Qingwen | 10,000 | 2027-01-01 | Tianjin Warehouse 2 – Epidemic Prevention Zone |
| **Total** | | **31,000** | | |

### Verification notes
- Queried as an exact-date match on a true date field (`expiry_date`), and a widened window (2026-12-20 → 2027-01-31) returned the same 10 documents — so no boundary-day ambiguity and no batches expiring in late December 2026.
- The collection holds 30 batches in total; the only distinct expiry dates are 2027-01-01 (10 batches / 31,000 units), 2027-06-14 (10 batches / 104,000 units), and 2027-11-19 (10 batches / 201,000 units). The query is therefore complete and not truncated.

Scope note: this figure covers the internal inventory records only. No public web sources or RAGFlow documents were needed for this question, and no reference files were present in the working directory. Let me know if you'd like this written up as a downloadable Markdown/PDF report.

---

## 8. db-22 (db, easy)

**Question:** Which drug has the highest unit price in our sales records, and what is that price?

**Gold answer:** Oseltamivir Phosphate Capsules, 100 per unit.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[3] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[4] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[5] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c46980304"}, "sale_id": 1, "drug_id": 1, "sale_date": {"$date": "2025-02-15T00:00:00.000Z"}, "quantity_sold": 200, "unit_price": 25, "total_amount": 5000, "customer_name": "Beijing Chaoyang Hospital", "region": "North China", "sales_rep": "Beijing Chaoyang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980305"}, "sale_id": 2, "drug_id": 1, "sale_date": {"$date": "2025-08-10T00:00:00.000Z"}, "quantity_sold": 500, "unit_price": 24.5, "total_amount": 12250, "customer_name": "Tianjin Pharmacy", "region": "North China", "sales_rep": "Tianjin Nankai Sales Branch"}, {"_id": {"$oid": "6aabf438cb80345c46980306"}, "sale_id": 3, "drug_id": 2, "sale_date": {"$date": "2025-01-20T00:00:00.000Z"}, "quantity_sold": 1000, "unit_price": 15, "total_amount": 15000, "customer_name": "Neptunus Pharmacy Chain", "region": "East China", "sales_rep": "Hangzhou Binjiang Sales Dept."}], "queryResultsCount": 20, "appliedLimits": []}

[6] tool count_documents returned:
{"count": 20}

[7] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c4698030d"}, "sale_id": 10, "drug_id": 5, "sale_date": {"$date": "2025-11-01T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 100, "total_amount": 500000, "customer_name": "Heilongjiang Provincial Hospital", "region": "Northeast China", "sales_rep": "Harbin Xiangfang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030c"}, "sale_id": 9, "drug_id": 5, "sale_date": {"$date": "2025-01-15T00:00:00.000Z"}, "quantity_sold": 2000, "unit_price": 100, "total_amount": 200000, "customer_name": "Peking Union Medical College Hospital", "region": "North China", "sales_rep": "Beijing Dongdan Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030b"}, "sale_id": 8, "drug_id": 4, "sale_date": {"$date": "2025-10-18T00:00:00.000Z"}, "quantity_sold": 150, "unit_price": 45, "total_amount": 6750, "customer_name": "Chongqing Pharmacy", "region": "Southwest China", "sales_rep": "Chongqing Yuzhong Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030a"}, "sale_id": 7, "drug_id": 4, "sale_date": {"$date": "2025-04-05T00:00:00.000Z"}, "quantity_sold": 100, "unit_price": 45, "total_amount": 4500, "customer_name": "Chengdu West China Hospital", "region": "Southwest China", "sales_rep": "Chengdu Wuhou Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980309"}, "sale_id": 6, "drug_id": 3, "sale_date": {"$date": "2025-09-22T00:00:00.000Z"}, "quantity_sold": 400, "unit_price": 35, "total_amount": 14000, "customer_name": "Shenzhen People's Hospital", "region": "South China", "sales_rep": "Shenzhen Luohu Sales Branch"}], "queryResultsCount": 20, "appliedLimits": []}

[8] tool aggregate_documents returned:
{"documents": [{"_id": null, "max_unit_price": 100, "min_unit_price": 10, "avg_unit_price": 30.975}], "count": 1, "appliedLimits": []}

[9] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c4698030c"}, "sale_id": 9, "drug_id": 5, "sale_date": {"$date": "2025-01-15T00:00:00.000Z"}, "quantity_sold": 2000, "unit_price": 100, "total_amount": 200000, "customer_name": "Peking Union Medical College Hospital", "region": "North China", "sales_rep": "Beijing Dongdan Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030d"}, "sale_id": 10, "drug_id": 5, "sale_date": {"$date": "2025-11-01T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 100, "total_amount": 500000, "customer_name": "Heilongjiang Provincial Hospital", "region": "Northeast China", "sales_rep": "Harbin Xiangfang Sales Dept."}], "queryResultsCount": 2, "appliedLimits": []}

[10] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e0"}, "drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "approval_number": "H20090123", "specifications": "75mg*10 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antiviral", "description": "For the treatment of influenza A and B in adults and children aged 1 year and older."}], "queryResultsCount": 1, "appliedLimits": []}

[11] tool aggregate_documents returned:
{"documents": [{"_id": 1, "prices": [24.5, 25], "count": 2, "max_price": 25, "min_price": 24.5}, {"_id": 2, "prices": [15], "count": 2, "max_price": 15, "min_price": 15}, {"_id": 3, "prices": [35], "count": 2, "max_price": 35, "min_price": 35}, {"_id": 4, "prices": [45], "count": 2, "max_price": 45, "min_price": 45}, {"_id": 5, "prices": [100], "count": 2, "max_price": 100, "min_price": 100}, {"_id": 6, "prices": [12], "count": 2, "max_price": 12, "min_price": 12}, {"_id": 7, "prices": [18], "count": 2, "max_price": 18, "min_price": 18}, {"_id": 8, "prices": [30], "count": 2, "max_price": 30, "min_price": 30}, {"_id": 9, "prices": [10], "count": 2, "max_price": 10, "min_price": 10}, {"_id": 10, "prices": [20], "count": 2, "max_price": 20, "min_price": 20}], "count": 10, "appliedLimits": []}

[12] tool aggregate_documents returned:
{"documents": [{"sale_id": 10, "drug_id": 5, "sale_date": {"$date": "2025-11-01T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 100, "total_amount": 500000, "customer_name": "Heilongjiang Provincial Hospital", "region": "Northeast China", "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "dosage_form": "Capsule", "specifications": "75mg*10 capsules"}, {"sale_id": 9, "drug_id": 5, "sale_date": {"$date": "2025-01-15T00:00:00.000Z"}, "quantity_sold": 2000, "unit_price": 100, "total_amount": 200000, "customer_name": "Peking Union Medical College Hospital", "region": "North China", "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "dosage_form": "Capsule", "specifications": "75mg*10 capsules"}, {"sale_id": 8, "drug_id": 4, "sale_date": {"$date": "2025-10-18T00:00:00.000Z"}, "quantity_sold": 150, "unit_price": 45, "total_amount": 6750, "customer_name": "Chongqing Pharmacy", "region": "Southwest China", "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "dosage_form": "Tablet", "specifications": "20mg*7 tablets"}, {"sale_id": 7, "drug_id": 4, "sale_date": {"$date": "2025-04-05T00:00:00.000Z"}, "quantity_sold": 100, "unit_price": 45, "total_amount": 4500, "customer_name": "Chengdu West China Hospital", "region": "Southwest China", "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "dosage_form": "Tablet", "specifications": "20mg*7 tablets"}, {"sale_id": 6, "drug_id": 3, "sale_date": {"$date": "2025-09-22T00:00:00.000Z"}, "quantity_sold": 400, "unit_price": 35, "total_amount": 14000, "customer_name": "Shenzhen People's Hospital", "region": "South China", "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "dosage_form": "Tablet", "specifications": "0.5g*48 tablets"}], "count": 5, "appliedLimits": []}
```

</details>

**Answer:**

## Answer

The drug with the **highest unit price** in our sales records is **Oseltamivir Phosphate Capsules (brand: Tamiflu)**, at a **unit price of 100** per unit.

*(Source: internal MongoDB business database — `sales_records` collection, field `unit_price`, enriched via `drugs` on `drug_id`.)*

### The top-priced sale(s)

| Rank | Sale ID | Drug ID | Drug (generic / brand) | Unit Price | Qty Sold | Total Amount | Sale Date | Region |
|---|---|---|---|---|---|---|---|---|
| 1 (tie) | 10 | 5 | Oseltamivir Phosphate Capsules / **Tamiflu** | **100** | 5,000 | 500,000 | 2025-11-01 | Northeast China |
| 1 (tie) | 9 | 5 | Oseltamivir Phosphate Capsules / **Tamiflu** | **100** | 2,000 | 200,000 | 2025-01-15 | North China |

Both records are the same drug at the same price — an exact tie, so there is a single answer for "highest-priced drug."

### Runner-ups (for context)

| Rank | Drug (generic / brand) | Unit Price |
|---|---|---|
| 3 (tie) | Atorvastatin Calcium Tablets / Lipitor | 45 |
| 5 | Metformin Hydrochloride Tablets / Glucophage | 35 |

### Notes and caveats

- **Field used:** the unit price field is exactly `unit_price`; there is no `price` or `sale_price` field. It was verified two ways — a descending sort with a limit, and an independent aggregation (`max = 100`, `min = 10`, `average ≈ 30.98`).
- **Dataset size:** `sales_records` contains **20** records.
- **Drug-specific vs. transaction-specific:** grouping by drug shows each drug uses one constant price, **except drug ID 1**, which shows a slight variation (24.5 and 25). So the "highest unit price" here is effectively drug-level (all records sharing a price), not a one-off transaction price.
- **Outlier check:** the value 100 is internally consistent (`5,000 × 100 = 500,000`; `2,000 × 100 = 200,000`), so nothing is mathematically wrong. However, it is a notable high point — about **2.2×** the runner-up (45) and roughly **9.5×** the mean price (~30.98). Worth a routine business sanity-check, but not flagged as erroneous.

No public web sources or knowledge-base documents were needed for this question — it is answered entirely from our internal sales records.

---

## 9. db-23 (db, medium)

**Question:** How many sales did we make in Q4 2025 (October to December), and what was their total revenue?

**Gold answer:** 5 sales totalling 1,596,750.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[3] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[4] tool count_documents returned:
{"count": 20}

[5] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c46980316"}, "sale_id": 19, "drug_id": 10, "sale_date": {"$date": "2025-01-10T00:00:00.000Z"}, "quantity_sold": 10000, "unit_price": 20, "total_amount": 200000, "customer_name": "Shijiazhuang Yiling Pharmaceutical", "region": "North China", "sales_rep": "Shijiazhuang Hi-Tech Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030c"}, "sale_id": 9, "drug_id": 5, "sale_date": {"$date": "2025-01-15T00:00:00.000Z"}, "quantity_sold": 2000, "unit_price": 100, "total_amount": 200000, "customer_name": "Peking Union Medical College Hospital", "region": "North China", "sales_rep": "Beijing Dongdan Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980306"}, "sale_id": 3, "drug_id": 2, "sale_date": {"$date": "2025-01-20T00:00:00.000Z"}, "quantity_sold": 1000, "unit_price": 15, "total_amount": 15000, "customer_name": "Neptunus Pharmacy Chain", "region": "East China", "sales_rep": "Hangzhou Binjiang Sales Dept."}], "queryResultsCount": 20, "appliedLimits": []}

[6] tool count_documents returned:
{"count": 5}

[7] tool aggregate_documents returned:
{"documents": [{"_id": null, "count": 5, "revenue_total_amount": 1596750, "revenue_qty_x_price": 1596750, "null_total_amount": 0}], "count": 1, "appliedLimits": []}

[8] tool count_documents returned:
{"count": 0}

[9] tool find_documents returned:
{"documents": [{"sale_id": 8, "drug_id": 4, "sale_date": {"$date": "2025-10-18T00:00:00.000Z"}, "quantity_sold": 150, "unit_price": 45, "total_amount": 6750, "region": "Southwest China"}, {"sale_id": 10, "drug_id": 5, "sale_date": {"$date": "2025-11-01T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 100, "total_amount": 500000, "region": "Northeast China"}, {"sale_id": 16, "drug_id": 8, "sale_date": {"$date": "2025-11-11T00:00:00.000Z"}, "quantity_sold": 500, "unit_price": 30, "total_amount": 15000, "region": "Northwest China"}, {"sale_id": 4, "drug_id": 2, "sale_date": {"$date": "2025-12-05T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 15, "total_amount": 75000, "region": "East China"}, {"sale_id": 20, "drug_id": 10, "sale_date": {"$date": "2025-12-20T00:00:00.000Z"}, "quantity_sold": 50000, "unit_price": 20, "total_amount": 1000000, "region": "Nationwide"}], "queryResultsCount": 5, "appliedLimits": []}

[10] tool aggregate_documents returned:
{"documents": [{"_id": "2025-01", "count": 3, "revenue": 415000}, {"_id": "2025-02", "count": 2, "revenue": 11000}, {"_id": "2025-03", "count": 2, "revenue": 20500}, {"_id": "2025-04", "count": 1, "revenue": 4500}, {"_id": "2025-05", "count": 1, "revenue": 6000}, {"_id": "2025-06", "count": 1, "revenue": 18000}, {"_id": "2025-07", "count": 1, "revenue": 7200}, {"_id": "2025-08", "count": 2, "revenue": 48250}, {"_id": "2025-09", "count": 2, "revenue": 26000}, {"_id": "2025-10", "count": 1, "revenue": 6750}, {"_id": "2025-11", "count": 2, "revenue": 515000}, {"_id": "2025-12", "count": 2, "revenue": 1075000}], "count": 12, "appliedLimits": []}

[11] tool aggregate_documents returned:
{"documents": [{"_id": "2025-10", "count": 1, "revenue": 6750}, {"_id": "2025-11", "count": 2, "revenue": 515000}, {"_id": "2025-12", "count": 2, "revenue": 1075000}], "count": 3, "appliedLimits": []}
```

</details>

**Answer:**

Here are the internal sales figures for **Q4 2025** (October–December 2025), pulled from our `sales_records` collection.

## Summary

| Metric | Value |
|---|---|
| **Number of sales (Q4 2025)** | **5** |
| **Total revenue (Q4 2025)** | **1,596,750** |

## Monthly breakdown

| Month | Sales | Revenue |
|---|---|---|
| October 2025 | 1 | 6,750 |
| November 2025 | 2 | 515,000 |
| December 2025 | 2 | 1,075,000 |
| **Q4 total** | **5** | **1,596,750** |

## Sales detail

| Sale ID | Drug ID | Date | Qty | Unit price | Total amount | Region |
|---|---|---|---|---|---|---|
| 8 | 4 | 2025-10-18 | 150 | 45 | 6,750 | Southwest China |
| 10 | 5 | 2025-11-01 | 5,000 | 100 | 500,000 | Northeast China |
| 16 | 8 | 2025-11-11 | 500 | 30 | 15,000 | Northwest China |
| 4 | 2 | 2025-12-05 | 5,000 | 15 | 75,000 | East China |
| 20 | 10 | 2025-12-20 | 50,000 | 20 | 1,000,000 | Nationwide |

## Notes on how this was calculated

- **Source:** internal database — collection `sales_records`. No public sources or knowledge-base documents were used, since this is purely an internal-records question.
- **Date field:** `sale_date` (native date type). Filtered inclusively on `2025-10-01` → `2025-12-31`. All Q4 records fall comfortably inside the range (no boundary ambiguity).
- **Revenue field:** `total_amount`. This was cross-checked against `quantity_sold × unit_price`, which totals **exactly 1,596,750** as well — the two agree perfectly, so the figure is reliable.
- **Data quality:** no nulls or missing values in the relevant fields; no records were excluded. The full `sales_records` collection contains 20 records (all 2025), of which 5 fall in Q4.

**Answer: 5 sales, totaling 1,596,750 in revenue.** December was the strongest month by far, driven largely by sale ID 20 (1,000,000).

Let me know if you'd like this exported as a Markdown or PDF report, or broken down by drug or region.

---

## 10. db-24 (db, hard)

**Question:** Compare our sales revenue in the first half of 2025 with the second half.

**Gold answer:** H1 475,000; H2 1,678,200.

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[3] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[4] tool find_documents returned:
{"documents": [{"sale_id": 19, "drug_id": 10, "sale_date": {"$date": "2025-01-10T00:00:00.000Z"}, "quantity_sold": 10000, "unit_price": 20, "total_amount": 200000, "region": "North China"}, {"sale_id": 9, "drug_id": 5, "sale_date": {"$date": "2025-01-15T00:00:00.000Z"}, "quantity_sold": 2000, "unit_price": 100, "total_amount": 200000, "region": "North China"}, {"sale_id": 3, "drug_id": 2, "sale_date": {"$date": "2025-01-20T00:00:00.000Z"}, "quantity_sold": 1000, "unit_price": 15, "total_amount": 15000, "region": "East China"}, {"sale_id": 1, "drug_id": 1, "sale_date": {"$date": "2025-02-15T00:00:00.000Z"}, "quantity_sold": 200, "unit_price": 25, "total_amount": 5000, "region": "North China"}, {"sale_id": 15, "drug_id": 8, "sale_date": {"$date": "2025-02-28T00:00:00.000Z"}, "quantity_sold": 200, "unit_price": 30, "total_amount": 6000, "region": "Northwest China"}], "queryResultsCount": 20, "appliedLimits": []}

[5] tool aggregate_documents returned:
{"documents": [{"_id": null, "min_date": {"$date": "2025-01-10T00:00:00.000Z"}, "max_date": {"$date": "2025-12-20T00:00:00.000Z"}, "total_docs": 20, "total_revenue_all": 2153200}], "count": 1, "appliedLimits": []}

[6] tool aggregate_documents returned:
{"documents": [{"_id": {"half": "H1 2025", "drug_id": 10}, "revenue": 200000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 5}, "revenue": 200000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 7}, "revenue": 18000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 2}, "revenue": 15000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 3}, "revenue": 10500, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 9}, "revenue": 10000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 8}, "revenue": 6000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 6}, "revenue": 6000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 1}, "revenue": 5000, "transactions": 1}, {"_id": {"half": "H1 2025", "drug_id": 4}, "revenue": 4500, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 10}, "revenue": 1000000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 5}, "revenue": 500000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 2}, "revenue": 75000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 7}, "revenue": 36000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 8}, "revenue": 15000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 3}, "revenue": 14000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 1}, "revenue": 12250, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 9}, "revenue": 12000, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 6}, "revenue": 7200, "transactions": 1}, {"_id": {"half": "H2 2025", "drug_id": 4}, "revenue": 6750, "transactions": 1}], "count": 20, "appliedLimits": []}

[7] tool aggregate_documents returned:
{"documents": [{"_id": "2025-01", "revenue": 415000, "transactions": 3, "quantity": 13000}, {"_id": "2025-02", "revenue": 11000, "transactions": 2, "quantity": 400}, {"_id": "2025-03", "revenue": 20500, "transactions": 2, "quantity": 1300}, {"_id": "2025-04", "revenue": 4500, "transactions": 1, "quantity": 100}, {"_id": "2025-05", "revenue": 6000, "transactions": 1, "quantity": 500}, {"_id": "2025-06", "revenue": 18000, "transactions": 1, "quantity": 1000}, {"_id": "2025-07", "revenue": 7200, "transactions": 1, "quantity": 600}, {"_id": "2025-08", "revenue": 48250, "transactions": 2, "quantity": 2500}, {"_id": "2025-09", "revenue": 26000, "transactions": 2, "quantity": 1600}, {"_id": "2025-10", "revenue": 6750, "transactions": 1, "quantity": 150}, {"_id": "2025-11", "revenue": 515000, "transactions": 2, "quantity": 5500}, {"_id": "2025-12", "revenue": 1075000, "transactions": 2, "quantity": 55000}], "count": 12, "appliedLimits": []}

[8] tool aggregate_documents returned:
{"documents": [{"_id": "H1 2025", "revenue": 475000, "transactions": 10, "quantity": 16300}, {"_id": "H2 2025", "revenue": 1678200, "transactions": 10, "quantity": 65350}], "count": 2, "appliedLimits": []}

[9] tool aggregate_documents returned:
Exception Captured: pipeline must be valid JSON: Expecting ',' delimiter

[10] tool find_documents returned:
{"documents": [{"drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "therapeutic_area": "Antibiotic"}, {"drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "therapeutic_area": "Analgesic/Antipyretic"}, {"drug_id": 3, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "therapeutic_area": "Diabetes"}, {"drug_id": 4, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "therapeutic_area": "Cardiovascular"}, {"drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "therapeutic_area": "Antiviral"}, {"drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "therapeutic_area": "Antibiotic"}, {"drug_id": 7, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "therapeutic_area": "Digestive System"}, {"drug_id": 8, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat", "therapeutic_area": "Hypertension"}, {"drug_id": 9, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin", "therapeutic_area": "Cardiovascular"}, {"drug_id": 10, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "therapeutic_area": "TCM / Cold & Flu"}], "queryResultsCount": 10, "appliedLimits": []}

[11] tool count_documents returned:
{"count": 0}

[12] tool count_documents returned:
{"count": 0}
```

</details>

**Answer:**

## Sales Revenue Comparison — H1 vs H2 2025

This question needed only our **internal sales records**, so I queried the company database directly (`sales_records` joined to `drugs`). No public or knowledge-base sources were relevant. The database returned a complete year of data with no nulls.

### Headline result

| Period | Revenue (`total_amount`) | Transactions | Quantity sold |
|---|---|---|---|
| **H1 2025** (Jan 1 – Jun 30) | **475,000** | 10 | 16,300 |
| **H2 2025** (Jul 1 – Dec 31) | **1,678,200** | 10 | 65,350 |
| **Difference (H2 − H1)** | **+1,203,200** | 0 | +49,050 |
| **Change** | **+253.3%** | — | +300.9% |

H2 revenue is roughly **3.5×** H1 revenue. Note the correct phrasing: H2 is an increase of ~253%, **not** "253% of H1."

### Monthly breakdown

| Month | Revenue | Txns | | Month | Revenue | Txns |
|---|---|---|---|---|---|---|
| 2025-01 | 415,000 | 3 | | 2025-07 | 7,200 | 1 |
| 2025-02 | 11,000 | 2 | | 2025-08 | 48,250 | 2 |
| 2025-03 | 20,500 | 2 | | 2025-09 | 26,000 | 2 |
| 2025-04 | 4,500 | 1 | | 2025-10 | 6,750 | 1 |
| 2025-05 | 6,000 | 1 | | 2025-11 | 515,000 | 2 |
| 2025-06 | 18,000 | 1 | | 2025-12 | 1,075,000 | 2 |
| **H1 total** | **475,000** | **10** | | **H2 total** | **1,678,200** | **10** |

All 12 months have at least one record — no empty months.

### Top products by revenue

| Product | H1 2025 | H2 2025 | Change |
|---|---|---|---|
| Lianhua Qingwen Capsules | 200,000 | 1,000,000 | +400% |
| Tamiflu / Oseltamivir | 200,000 | 500,000 | +150% |
| Fenbid / Ibuprofen SR | 15,000 | 75,000 | +400% |
| Smecta / Montmorillonite | 18,000 | 36,000 | +100% |
| Adalat / Nifedipine CR | 6,000 | 15,000 | +150% |
| Glucophage / Metformin | 10,500 | 14,000 | +33% |
| Amoxin / Amoxicillin | 5,000 | 12,250 | +145% |
| Bayaspirin / Aspirin EC | 10,000 | 12,000 | +20% |
| Rocephin / Ceftriaxone | 6,000 | 7,200 | +20% |
| Lipitor / Atorvastatin | 4,500 | 6,750 | +50% |

The same 10 products appear in both halves, with Lianhua Qingwen and Tamiflu holding #1 and #2.

### Important caveats

1. **The +253% headline is driven by two transactions.** A December Lianhua Qingwen sale (**1,000,000**) and a November Tamiflu sale (**500,000**) together account for ~89% of H2 revenue. Excluding them, H2 would be ~178,200 vs H1's 475,000 — i.e. a **decline**, not growth. The half-over-half surge is not broad-based.
2. **Very small dataset.** The collection holds only **20 transactions total** (10 per half, exactly one per drug per half). This looks like a **sample/demo dataset, not full company history**, so treat all figures as sample-level.
3. **Extremely uneven monthly distribution.** H1's January alone is ~87% of H1; H2's December alone is ~64% of H2. Month-over-month comparisons are volatile.
4. **Data integrity is good:** zero nulls in `total_amount`, `sale_date`, `drug_id`, `unit_price`, or `quantity_sold`, and `total_amount = quantity_sold × unit_price` holds consistently.
5. **Coverage:** `sale_date` ranges 2025-01-10 to 2025-12-20 (mid-Jan to mid-Dec); no data exists outside 2025.

**Bottom line:** On paper, H2 2025 revenue (1,678,200) beats H1 2025 (475,000) by 1,203,200 (+253.3%). But this is an artifact of two outsized Q4 transactions in a 20-record sample — it should **not** be read as a reliable company-wide growth trend.

If you'd like, I can turn this into a formatted Markdown/PDF report, or have the database agent pull the underlying transaction-level detail (region, sales rep, customer) behind the two large Q4 orders.

---

## 11. db-28 (db, hard)

**Question:** Which drug has the highest ratio of units sold to units currently on hand, and what is that ratio as a percentage?

**Gold answer:** Lianhua Qingwen Capsules, 37.5% (60,000 sold vs 160,000 on hand).

**Route:** expected ['database']; delegated {'Database Query Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[3] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[4] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[5] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[6] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802dc"}, "drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "approval_number": "H20051234", "specifications": "0.25g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "Used to treat upper respiratory tract infections, urogenital infections, and others caused by susceptible bacteria."}, {"_id": {"$oid": "6aabf437cb80345c469802dd"}, "drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "approval_number": "H10900089", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Analgesic/Antipyretic", "description": "Used to relieve mild to moderate pain such as headache, joint pain, migraine, toothache, muscle pain, neuralgia, and dysmenorrhea. Also used for fever caused by the common cold or influenza."}, {"_id": {"$oid": "6aabf437cb80345c469802de"}, "drug_id": 3, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "approval_number": "H20023345", "specifications": "0.5g*48 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Diabetes", "description": "First-line treatment for type 2 diabetes patients not adequately controlled by diet alone, especially those who are obese."}, {"_id": {"$oid": "6aabf437cb80345c469802df"}, "drug_id": 4, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "approval_number": "H20055567", "specifications": "20mg*7 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Cardiovascular", "description": "For patients with primary hypercholesterolemia, including familial hypercholesterolemia (heterozygous) or mixed hyperlipidemia."}, {"_id": {"$oid": "6aabf437cb80345c469802e0"}, "drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "approval_number": "H20090123", "specifications": "75mg*10 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antiviral", "description": "For the treatment of influenza A and B in adults and children aged 1 year and older."}], "queryResultsCount": 10, "appliedLimits": []}

[7] tool count_documents returned:
{"count": 20}

[8] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c46980304"}, "sale_id": 1, "drug_id": 1, "sale_date": {"$date": "2025-02-15T00:00:00.000Z"}, "quantity_sold": 200, "unit_price": 25, "total_amount": 5000, "customer_name": "Beijing Chaoyang Hospital", "region": "North China", "sales_rep": "Beijing Chaoyang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980305"}, "sale_id": 2, "drug_id": 1, "sale_date": {"$date": "2025-08-10T00:00:00.000Z"}, "quantity_sold": 500, "unit_price": 24.5, "total_amount": 12250, "customer_name": "Tianjin Pharmacy", "region": "North China", "sales_rep": "Tianjin Nankai Sales Branch"}, {"_id": {"$oid": "6aabf438cb80345c46980306"}, "sale_id": 3, "drug_id": 2, "sale_date": {"$date": "2025-01-20T00:00:00.000Z"}, "quantity_sold": 1000, "unit_price": 15, "total_amount": 15000, "customer_name": "Neptunus Pharmacy Chain", "region": "East China", "sales_rep": "Hangzhou Binjiang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980307"}, "sale_id": 4, "drug_id": 2, "sale_date": {"$date": "2025-12-05T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 15, "total_amount": 75000, "customer_name": "Shanghai Huashan Hospital", "region": "East China", "sales_rep": "Shanghai Jing'an Sales HQ"}, {"_id": {"$oid": "6aabf438cb80345c46980308"}, "sale_id": 5, "drug_id": 3, "sale_date": {"$date": "2025-03-10T00:00:00.000Z"}, "quantity_sold": 300, "unit_price": 35, "total_amount": 10500, "customer_name": "Guangzhou Sun Yat-sen Hospital", "region": "South China", "sales_rep": "Guangzhou Yuexiu Sales Dept."}], "queryResultsCount": 20, "appliedLimits": []}

[9] tool count_documents returned:
{"count": 30}

[10] tool count_documents returned:
{"count": 10}

[11] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e6"}, "inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e7"}, "inventory_id": 2, "drug_id": 1, "batch_number": "MY-250615-B", "quantity_on_hand": 8000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e8"}, "inventory_id": 3, "drug_id": 1, "batch_number": "MY-251120-C", "quantity_on_hand": 12000, "warehouse_location": "Tianjin Warehouse 1 - Zone A", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e9"}, "inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ea"}, "inventory_id": 5, "drug_id": 2, "batch_number": "MY-250615-B", "quantity_on_hand": 15000, "warehouse_location": "Beijing Warehouse 1 - Zone C", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}], "queryResultsCount": 30, "appliedLimits": []}

[12] tool aggregate_documents returned:
{"documents": [{"_id": 1, "total_units_sold": 700}, {"_id": 2, "total_units_sold": 6000}, {"_id": 3, "total_units_sold": 700}, {"_id": 4, "total_units_sold": 250}, {"_id": 5, "total_units_sold": 7000}, {"_id": 6, "total_units_sold": 1100}, {"_id": 7, "total_units_sold": 3000}, {"_id": 8, "total_units_sold": 700}, {"_id": 9, "total_units_sold": 2200}, {"_id": 10, "total_units_sold": 60000}], "count": 10, "appliedLimits": []}

[13] tool aggregate_documents returned:
{"documents": [{"_id": 1, "total_units_on_hand": 25000}, {"_id": 2, "total_units_on_hand": 47000}, {"_id": 3, "total_units_on_hand": 13500}, {"_id": 4, "total_units_on_hand": 7500}, {"_id": 5, "total_units_on_hand": 25500}, {"_id": 6, "total_units_on_hand": 10500}, {"_id": 7, "total_units_on_hand": 24000}, {"_id": 8, "total_units_on_hand": 9500}, {"_id": 9, "total_units_on_hand": 13500}, {"_id": 10, "total_units_on_hand": 160000}], "count": 10, "appliedLimits": []}

[14] tool aggregate_documents returned:
Exception Captured: pipeline must be valid JSON: Expecting value

[15] tool aggregate_documents returned:
{"documents": [{"drug_id": 10, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "total_units_sold": 60000, "total_units_on_hand": 160000, "ratio": 0.375}, {"drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "total_units_sold": 7000, "total_units_on_hand": 25500, "ratio": 0.27450980392156865}, {"drug_id": 9, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin", "total_units_sold": 2200, "total_units_on_hand": 13500, "ratio": 0.16296296296296298}, {"drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "total_units_sold": 6000, "total_units_on_hand": 47000, "ratio": 0.1276595744680851}, {"drug_id": 7, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "total_units_sold": 3000, "total_units_on_hand": 24000, "ratio": 0.125}, {"drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "total_units_sold": 1100, "total_units_on_hand": 10500, "ratio": 0.10476190476190476}, {"drug_id": 8, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat", "total_units_sold": 700, "total_units_on_hand": 9500, "ratio": 0.07368421052631578}, {"drug_id": 3, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "total_units_sold": 700, "total_units_on_hand": 13500, "ratio": 0.05185185185185185}, {"drug_id": 4, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "total_units_sold": 250, "total_units_on_hand": 7500, "ratio": 0.03333333333333333}, {"drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "total_units_sold": 700, "total_units_on_hand": 25000, "ratio": 0.028}], "count": 10, "appliedLimits": []}

[16] tool aggregate_documents returned:
{"documents": [], "count": 0, "appliedLimits": []}

[17] tool aggregate_documents returned:
{"documents": [], "count": 0, "appliedLimits": []}

[18] tool aggregate_documents returned:
{"documents": [{"_id": 1, "batches": 3, "qty": 25000}, {"_id": 2, "batches": 3, "qty": 47000}, {"_id": 3, "batches": 3, "qty": 13500}, {"_id": 4, "batches": 3, "qty": 7500}, {"_id": 5, "batches": 3, "qty": 25500}, {"_id": 6, "batches": 3, "qty": 10500}, {"_id": 7, "batches": 3, "qty": 24000}, {"_id": 8, "batches": 3, "qty": 9500}, {"_id": 9, "batches": 3, "qty": 13500}, {"_id": 10, "batches": 3, "qty": 160000}], "count": 10, "appliedLimits": []}
```

</details>

**Answer:**

**Answer: Lianhua Qingwen Capsules — 37.5%**

Among all drugs in the internal records, Lianhua Qingwen Capsules (brand: *Lianhua Qingwen*, `drug_id` 10) has the highest ratio of units sold to units currently on hand: **60,000 sold ÷ 160,000 on hand = 0.375 = 37.5%**.

| Rank | Drug | Brand | Units sold | Units on hand | Ratio |
|---:|---|---|---:|---:|---:|
| 1 | Lianhua Qingwen Capsules | Lianhua Qingwen | 60,000 | 160,000 | **37.50%** |
| 2 | Oseltamivir Phosphate Capsules | Tamiflu | 7,000 | 25,500 | 27.45% |
| 3 | Aspirin Enteric-Coated Tablets | Bayaspirin | 2,200 | 13,500 | 16.30% |
| 4 | Ibuprofen Sustained-Release Capsules | Fenbid | 6,000 | 47,000 | 12.77% |
| 5 | Montmorillonite Powder | Smecta | 3,000 | 24,000 | 12.50% |

*(Remaining: Ceftriaxone 10.48%, Nifedipine 7.37%, Metformin 5.19%, Atorvastatin 3.33%, Amoxicillin 2.80%.)*

### How this was computed
- Source: **internal business database only** (no public/web or knowledge-base sources were needed for this question).
- `sales_records.quantity_sold` summed per `drug_id` → total units sold.
- `inventory.quantity_on_hand` summed across all batches per `drug_id` → total units on hand.
- `drugs` joined on `drug_id` for `generic_name` / `brand_name`.
- Ratio = units sold ÷ units on hand, ×100 for percentage.

### Data-quality notes
- All 10 drugs have positive on-hand stock, so **no drug had to be excluded** for a zero/undefined ratio.
- No orphan or mismatched `drug_id` values between `sales_records`, `inventory`, and `drugs`.
- Dataset coverage is small and complete (10 drugs, 30 inventory batches, 20 sales records), so the ranking reflects the full data rather than a sample.

**Interpretation caveat:** this ratio measures sales volume relative to remaining stock, not the same as a sell-through rate against total supply received, and it ignores sales-timing effects — it's a useful signal but not a formal turnover/days-of-supply metric.

If you'd like, I can generate this as a Markdown/PDF report.

---

## 12. gov-04 (routing, hard)

**Question:** Find the public market price of ibuprofen sustained-release capsules and compare it with the unit price we charged Shanghai Huashan Hospital.

**Gold answer:** Our price to Shanghai Huashan Hospital: 15.0 per unit (5,000 units, 75,000). Public retail price from a pharmacy or pricing site, compared in the answer.

**Route:** expected ['database', 'internet']; delegated {'Database Query Agent': 1, 'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[1] tool ls returned:
No files found

[4] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[5] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[6] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[7] tool find_documents returned:
{"documents": [], "queryResultsCount": 0, "appliedLimits": []}

[8] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802dd"}, "drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "approval_number": "H10900089", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Analgesic/Antipyretic", "description": "Used to relieve mild to moderate pain such as headache, joint pain, migraine, toothache, muscle pain, neuralgia, and dysmenorrhea. Also used for fever caused by the common cold or influenza."}], "queryResultsCount": 1, "appliedLimits": []}

[9] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c46980306"}, "sale_id": 3, "drug_id": 2, "sale_date": {"$date": "2025-01-20T00:00:00.000Z"}, "quantity_sold": 1000, "unit_price": 15, "total_amount": 15000, "customer_name": "Neptunus Pharmacy Chain", "region": "East China", "sales_rep": "Hangzhou Binjiang Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c46980307"}, "sale_id": 4, "drug_id": 2, "sale_date": {"$date": "2025-12-05T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 15, "total_amount": 75000, "customer_name": "Shanghai Huashan Hospital", "region": "East China", "sales_rep": "Shanghai Jing'an Sales HQ"}], "queryResultsCount": 2, "appliedLimits": []}

[10] tool aggregate_documents returned:
{"documents": [{"_id": "Chongqing Pharmacy", "count": 1}, {"_id": "Hangzhou First Hospital", "count": 1}, {"_id": "Shijiazhuang Yiling Pharmaceutical", "count": 1}, {"_id": "Qingdao Municipal Hospital", "count": 1}, {"_id": "Changsha Xiangya Hospital", "count": 1}, {"_id": "Shenzhen People's Hospital", "count": 1}, {"_id": "National Pharmacy Chain Central Warehouse", "count": 1}, {"_id": "Neptunus Pharmacy Chain", "count": 1}, {"_id": "Jinan Central Hospital", "count": 1}, {"_id": "Nanjing Drum Tower Hospital", "count": 1}, {"_id": "Heilongjiang Provincial Hospital", "count": 1}, {"_id": "Beijing Chaoyang Hospital", "count": 1}, {"_id": "Shanghai Huashan Hospital", "count": 1}, {"_id": "Xi'an Xijing Hospital", "count": 1}, {"_id": "Tianjin Pharmacy", "count": 1}, {"_id": "Peking Union Medical College Hospital", "count": 1}, {"_id": "Wuhan Tongji Hospital", "count": 1}, {"_id": "First Hospital of Lanzhou University", "count": 1}, {"_id": "Chengdu West China Hospital", "count": 1}, {"_id": "Guangzhou Sun Yat-sen Hospital", "count": 1}], "count": 20, "appliedLimits": []}

[11] tool aggregate_documents returned:
{"documents": [{"sale_date": {"$date": "2025-12-05T00:00:00.000Z"}, "quantity_sold": 5000, "unit_price": 15, "total_amount": 75000, "customer_name": "Shanghai Huashan Hospital", "region": "East China", "sales_rep": "Shanghai Jing'an Sales HQ", "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule"}], "count": 1, "appliedLimits": []}

[12] web search for 'ibuprofen sustained-release capsules Fenbid 300mg 20 capsules price'; grounded search summary:
The price of **Fenbid (芬必得) Ibuprofen Sustained-Release Capsules (300 mg / 0.3 g, 20 capsules)** varies depending on the region and where you purchase it:

---

### **1. Domestic Retail in China (JD Health, Tmall, Local Pharmacies)**
* **Typical Price:** **¥20 – ¥35 RMB** (approx. **$3.00 – $5.00 USD**) per box.
* Discounts or multi-pack purchases (e.g., 2–3 boxes) often bring the unit cost down closer to **¥20 – ¥25 RMB**.

---

### **2. Overseas / Import Markets (e.g., US Asian Supermarkets, Yami, Import Pharmacies)**
* **Typical Price:** **$9.00 – $13.99 USD** per box.
* Prices are higher internationally due to import customs, international shipping, and retail distributor markup.

---

### **Product Overview**
* **Brand / Manufacturer:** Fenbid (中美史克 / Sino-American Tianjin Smith Kline & French)
* **Strength & Form:** 300 mg sustained-release capsule (formulated for up to 12-hour relief)
* **Common Indications:** Relief of mild-to-moderate pain (headaches, toothaches, joint pain, menstrual cramps) and reduction of fever.
sources:
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBMEl1GfOJBRClgpchHwpUBsts-pjOd8t6KxPdqAXDV5pa1B2B56tQw2pTVGGAxRzvQOXmqKxQeepTDRw1aGNaAozji0S-YxxLbWI6jIJceLlh6LxAhQtZ46FJEU2Cl7NFGzRk8Z2xKd8LevFLr_eSzoEBRjbN4QIAaSW-iQZOculFJ4qZ-3PAd0BeLtikZPQ9CVgYHYb9JJ72zmY9mxaNq-W397W6pIVUK3pFUnQd3-kcNzOZSrQklOwNOxjLuyJ2TWHDbhwTxORTq5YhBc6EhuuGcjlxKq-wIPJcw6_pmvO_vbeyhsKLy_uxdIjBuHV86jlqpegC9pVYYVIH52c=>
  - dealmoon.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtYkEOIej-Dljuadp-BghwC4UXBupy2dwP86dRzWQM9VVI6MLX6K4Xp3JLkf67opU-gAHXAZWPsEtK3U1I4NiFwi9uN8D_7iX4Eej8YL8FwFdcogGfcEpG__hDhkHIsyLyrJAsRgXEXIGsDQ==>
  - jd.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-0o91LZw_HWShdRKqIDXmz9h0k5zK3q5VH3x1IHIX31epyxwrptJe_KFDzDzDHm7-7c_5nwLbkbht51pxRB7CHT4QQSN8SprzD_bDoJhWY8OUuAsMQRgaPYLWKWc=>
  - 298.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYyMtypCMJtC1uFz5o-bLfCCk6WiWtw67WLJ5Y-DZbw_ZyI8H_q0dSMTtLpRwV0jY1yMTMGj9kuJNLRXSqiUF229wrr7ed9D_rVqZblZy9YDIS0Bx_1OQJDQ==>
  - yami.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy3fdoXUlFTQdnBQ4O2QMQHIvuHcNIUwF4YWqAegjaVRHMpl7LBKfZ039pj3Ckrd7fLCXGpdtkvQrq1WjGODA-mOglbMUz2OCgUUFrmEO2gMrBJXExutbp614uxyVyu_w=>

[13] web search for '布洛芬缓释胶囊 芬必得 0.3g 价格 京东'; grounded search summary:
在京东平台（包括京东大药房自营及平台合作药房），**中美史克 芬必得 布洛芬缓释胶囊（0.3g）** 的价格根据包装规格、促销活动及店铺类型略有不同：

---

### 1. 常见规格及参考价格

* **0.3g × 24粒装 / 20粒装**（最常见规格）：
  * **日常标价/单盒价**：约 **20 ～ 26 元**
  * **活动/促销到手价**：结合平台满减券、百亿补贴或首购礼金后，常在 **12 ～ 18 元** 左右
  * **多盒组合装（2~3盒装）**：折合单盒约 **15 ～ 20 元**

* **0.3g × 10粒装**（便携小包装）：
  * **价格**：约 **10 ～ 15 元**

---

### 2. 购买建议与比价提示

1. **自营 vs 第三方**：
   * **京东大药房（自营）**：正品保障高、发货快，但通常需要凑单或达到免运费门槛（一般满59元包邮）；
   * **第三方连锁药房专营店**：有时单盒包邮或有单独店铺券，单买一盒时总价可能更划算。
2. **秒杀 / 百亿补贴**：在京东 App 搜索进入“京东买药”频道或“百亿补贴”专区，常有单盒 15 元上下的特价补贴。

---

### 3. 用药安全提示
* **适应症**：用于缓解轻至中度疼痛（如头痛、牙痛、神经痛、痛经、关节痛等）及普通感冒或流感引起的发热。
* **使用疗程**：用于**止痛不得超过5天**，用于**解热不得超过3天**；如症状未缓解，请及时就医。
* **注意事项**：布洛芬对胃肠黏膜有一定刺激，建议饭后服用；有活动性消化道溃疡者禁用；请勿与同类非甾体抗炎药（NSAIDs）或含对乙酰氨基酚等成分的复方感冒药重复混用。
sources:
  - jd.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyYuy6cNON1q2qijkwSxey3exGJWKw_vSzZT2aZcIIO-1pEQg7Yf281GvggEtt0qLjIX31VLRXO_gLafhX8f-bkPQ94PBVe0RHOvllPhqM6IZltR8Clw1ga5Lj4Fs=>
  - cctv.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQER82MAJnTT7NKqkVzh4V-nzZoQa_4pQZPd_dN5ZMozPmfKUAn0L2SvO1Ho5kJHuUpWtiVCN1FBMEpZmGBiZJroWBpQIIu1nAfKBHqAxPLmClVsfCHGxl8_tEkoPTEyZYokZ75I7DBKkamjP9TpxCxDuUnXDt6jvi3vWFi_Ag==>
  - 111.com.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHHHHhEJhY0Li302JanVawHZNu6Ngwi4r51I7dCkxdMhnGlSuTHDyQy6aDHTGOD3EHzPOXIuyMZfozRhXB8QND8DEsgI7AFImTRHkRGsZfIF3ZpdWcHdmzGagfA_k=>
  - zol.com.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFjaalzz9J2XGyzeap_PF1ieneKzO6x2NkcLBgXYqwDmdoa2_q7kwgojOW7Dgoanqi6-oc2hTqo87DqG9NrtPN83pmfmHTg0G3zMhLCuXilrYL3hwlhsfw9rh1opjs-u1z>

[14] web search for '布洛芬缓释胶囊 价格 药品价格 参考价 医保'; grounded search summary:
关于**布洛芬缓释胶囊**（主要用于缓解轻至中度疼痛及解热）的价格、规格与医保报销信息如下：

---

### 一、医保属性与报销情况
1. **医保类别**：**国家医保乙类**。
   * 布洛芬的普通口服常释剂型（如普通片剂）通常为医保甲类，而**缓释控释剂型（缓释胶囊/缓释片）在国家医保目录中归为“乙类”**。
   * **国家基药**：已被纳入《国家基本药物目录》。
2. **报销规则**：
   * **门诊就医统筹**：在医院由医生开具处方时，乙类药品通常需要个人先自付一定比例（各省市政策略有不同，一般在 **0%～10%** 左右），剩余部分再按当地医保门诊比例进行报销。
   * **定点药店/线上买药**：布洛芬缓释胶囊多数属于**甲类 OTC（非处方药）**，在支持医保个账支付的线下定点药店或线上医保专区，可直接刷**职工医保个人账户余额**购买。

---

### 二、药品参考价格（常见规格：0.3g）

由于品牌、包装规格（10粒/20粒/24粒/30粒）以及购买渠道不同，价格区间差异较大：

| 渠道 / 品牌类型 | 常见包装规格 | 参考价格区间 | 说明 |
| :--- | :--- | :--- | :--- |
| **公立医院（集采中选药）** | 0.3g × 20粒/盒 | **约 3 ～ 8 元** | 国家/省级集中带量采购中选品种，医院实行零差率销售，价格最为实惠。 |
| **药店/电商（国产仿制品牌）**<br>*(如新华制药、仁和、修正等)* | 0.3g × 20粒/盒<br>0.3g × 30粒/盒 | **约 10 ～ 18 元**<br>**约 15 ～ 25 元** | 药效与原研一致，性价比高，普通平价药房常见。 |
| **知名品牌（中美史克·芬必得）** | 0.3g × 20粒/盒<br>0.3g × 24粒/盒<br>0.3g × 30粒/盒 | **约 20 ～ 28 元**<br>**约 24 ～ 32 元**<br>**约 28 ～ 38 元** | 市场知名度高，各线下连锁药店与电商平台均有售。 |

*注：部分地区可能存在 0.4g 规格，其价格通常会按药量比例略高 2～5 元左右。*

---

### 三、用药与购买建议
1. **成人常用剂量**：通常成人及 12 岁以上儿童为 **一次 1 粒，一日 2 次**（早晚各一次，因缓释特性药效应维持 12 小时左右），整粒温水吞服，**切勿咀嚼或掰开**。
2. **对症使用时限**：用于**退热不得超过 3 天**，用于**止痛不得超过 5 天**；若症状未缓解，请及时就医查明病因。
3. **购药省钱技巧**：如果有医保且就诊方便，在社区医院或公立医院开具“集采中选”的国产布洛芬缓释胶囊最为划算（单盒仅几元钱，且可走门诊统筹报销）。普通居家常备也可在定点药店使用医保个人账户支付。
sources:
  - nhsa.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBxe3qfS9QvbWx9yaDI9ptNObAVFhF9dUGH_b_MwDukyiuR-cb54aD0Tcu-wGcuqte1nYz_jZk0xRSUSDZ68_shqETotydMXnbrY47ECFaIsv-pYVdzE6Gonb3ydY7hVZwrdv3ArCyp3ExflKufIMMLlZG2JPj7WPi0LyS6iIBdM2uhivvoOrPuGsEhbXTB09aYSveP_YgDIGFV8X7G2PPMDc=>
  - sina.com.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGz9h5OXXSkJF9bvtbsn6hQ4E5-3KDr-rdUqtPM08PV5y1nN4VdQ9pM7_srWhnYOS2cEza1N6J8b3dl0ypqdRkepQhp71_WuYUYwEMDACunw24LVYf2cPjpVZMX9utCA_NF6mnMjiZ5suA0lbq0l4qRv6GKJiMqli-i10uD6Z9aVhm5DxfJ3MzD6dZ7>
  - gz.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELDRB2HRbvNFeZiKUOXE1jhEzkBHmCCO1QmFGN_3ZFcNBF_t6J4TLx_YBco5eX9fseggut0lQ9Qt3sz4fpSmrOnMkyjN3t-nGl-xouqXanDAXMVO1DPEUzTTD-Cv0YN9KmF8x4J80sIDDjc3_TkY99Sno=>
  - nhc.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhu5iSd4JFf5Hwi-pBXhNkw14oS8OUWOuKuaf46RxZ0zofjBURJkkFhUUVbJCpBnanY0G1Q6Pby893TyErz8idarAYhgT5SIRgpBq5G7QPFDbY9DdHr_K4DPg7EFbV63QxzsLh6sYNqXsWyzg2WzEJDS7DoZMfWEzvuuymuk-n1gSjaSl5flTlxOXuT7gYwaWjjb_QIhu9pfp8IjKK>
  - m12333.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH7y38ca1O0BDyQdlW3CZVbppeiMy0k1CkAXH6n_Q4ZBO_WBCsMyZgUz-U8W7Syk8HnnOXAwkO1LjVDeeCx9ruGOVj6g-SVFdipz1XwVnDQeCTpIc_2ZZfN61gMo1gVRLeohUBSAz8iq5ec3Cjzoq-VGrZ3qs6pzNqO1uAr40vdX3JBu3o>
  - nhsa.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoA-0KoqD26fyMRQ8IdZfvfY15yeGpM8se6YZ97otVANj4qXzFRBCT9rZV9dCZcjyPpauBS8Da9sEXoZuPWqKKRqCavBuddQiSQ-Wpza9mWBmVeLMWumViv10qaR6KF0t2LLXT_77uPSHAjg==>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpJSs6XijgZfu4vT5E0_hDLzuwLnHX5EpZNNWoHVUg4qJVI2fI8yQ3uccaH3ozcpgAX-_th9cTrjDCda0WofNyp0cKQtIEV0oPR61MDLF9Q38XKi-eKMpy6nda71J1r4hDTt7NAFOayY8R204RCRngT2s-TnxREQ==>
  - dgtungwah.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtVp5NVyEKsOJHTZ5tdlcPphWTcwORXaxSHCBWXG2zQyuiqNODVfUL5-E8oDO3KwvVO2rbXW0efb2YwebkqYpUr-6arXIHqPC60cEej1XYNbA-oB_UGaeh1I0S4dIWvPpl>

[15] web search for '芬必得 布洛芬缓释胶囊 0.3g*20粒 价格 多少钱一盒'; grounded search summary:
**中美史克 芬必得 布洛芬缓释胶囊（0.3g*20粒/盒）**的单盒价格通常在 **15元 ～ 30元** 之间。不同购买渠道的价格会有所差异：

### 1. 各渠道参考价格
* **线上电商药店（京东健康、阿里健康、天猫医药等）：**
  单盒价格一般在 **15元 ～ 22元** 左右（若叠加平台优惠券或购买2~3盒组合装，单盒价格可能更优惠）。
* **线下实体连锁药店 / 外卖送药（美团买药、饿了么等）：**
  单盒价格一般在 **20元 ～ 28元** 左右（因包含即时配送、门店租金及运营成本，通常略高于线上电商）。
* **公立医院 / 社区卫生服务中心：**
  受国家药品零差率及集中采购影响，医保报销前目录价格通常在 **12元 ～ 15元** 左右。

---

### 2. 购买与用药提示
1. **核对规格：** 芬必得布洛芬缓释胶囊市面上常见规格除了 **0.3g\*20粒** 外，还有 **0.3g\*24粒**（价格多在 25~32 元左右） 以及 **0.4g\*24粒**，购买时请看清包装规格。
2. **合理用药：** 
   * **用法用量：** 成人通常一次1粒，一日2次（早晚各一次，整粒吞服，切勿嚼碎）。
   * **用药周期：** 本品为对症缓解药物，**用于止痛一般不超过 5 天，用于解热（退烧）一般不超过 3 天**，若症状未缓解请及时就医。
   * **禁忌与注意事项：** 建议餐后服用以减少胃肠道刺激；孕妇、哺乳期妇女、活动性胃十二指肠溃疡或严重肝肾功能不全者禁用；服药期间切勿饮酒。
sources:
  - taobao.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqRAg_QUDX38wL3AypQmyLeJAPjXgkx0aKMx0M1Z5DAgWfyUxDbnAsXVd6KFJLNCJR23q5aZYyAVhFcOGGCGQ3UblmSarGWPbTGRmUoDfErCooNQ0afLxm5NYYW3PpHemkzFGMsYiIUK0DlZO_wa8r6dqERfhHSn1o-qI7OqFTLvj9qsTP50iNJ6wkKbZH2W59bLS21Q9nMikfFIL1aGY=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHktn-E0STT8m-zcEzTT3mMOaBPz1p6KHvFvBJcp6H69RFpF6QipL3LL0lvahIQHY6ME5D37Q7O3-L5T51qm2gOfY-qvMzIkarAhcXZI31Ft-xwXwze1HxrZ87wai7__Ifh5ZA_PlfLrYkxUEo=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxy47xWDg9StAf3AJG0Y4FwmZUHnYll6sEk66LXm9hNhiExSuQ8bC5DAmyPgzVkIAiZE68SJKkZYMaaa7rW9H_RWhuj2z9RFhq1bD-jwa0TFkhHrKHJN937271A_MQyTXWsRtXY7M1zEzO3yUKwwWIERoCBGaHe-tumBPZYkqbRAwmXyp8HJRX2lLh_b4W4xF2jo9p3OL8rzrFt2qS7DmiQvsU4mkDDCx-UtXQAP74XRZA67-EDWGXPTtZzq20AROHjwzDJSsfZCVngT603FLQz74JXkomGAmmH_aYRTNiX649rnyG9qJox8JqDzWmt3JYej4T9Hywv_hxUaqFaOo=>
  - zjhtcm1931.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPmQ6lsM54qGJ5j4siObeamzQCBdCzl8q2Jl4Yf34MEGnyStcrJ85aDpunPjg7xOexo69BGwjIWT8_TzjFYOfL2b6nnDu1BPiaLs0rpuuAtNS8c3ihMXNE3dbIyaA=>
  - suning.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBcg-Nidml6OlV1EN7luZNIiwEN71n3zFJZFhqD4b0kwgHKT_PhdpHnM02NwvS2vFcQXJkeYWT9ADjxw2VHpSSU6wqVg5ZtjZItJm97--EhEc4ZuuH_wyIphsFRVOt1NG0d1cLp_JgEUmryZZnJQPl8o2q>
  - 298.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFoChDetJK_jqetTKKoIAwTLCcCLp0uOLAwktZLw9N_-pbYCweJL2Qbp-WgCRTJ26x5jmMVGExvS_h9HKQUbVrfAJestHChxPNecxABecNoyVmS4oDG6h-jsQ==>
  - miaoshous.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEIEmY9MAbqSkJl51eDWmWAwvvqz-mvn4X3UGfLe5CIjplFzhrhNh66TurgSNLD06_811A54oyyCnYPVApl6_JcAy0gNpc6ni1PTr7ZYyvhyGxfcU9Sx3jjp-U9Gz6yJQ==>

[16] web search for '芬必得 布洛芬缓释胶囊 24粒 京东大药房 价格 元'; grounded search summary:
**芬必得 布洛芬缓释胶囊（24粒装）**在京东大药房的价格情况如下：

* **日常单盒标价：** 约 **24 ～ 30 元**（常见日常标价在 26 ～ 29.9 元/盒左右）。
* **促销/券后到手价：** 约 **16 ～ 22 元**（平台进行满减、多盒立减、换购或使用优惠券时价格更低）。

> **提示：** 
> 1. 该规格常见为 **0.3g × 24粒** 或 **0.4g × 24粒**，两者价格略有差异。
> 2. 线上药房价格会受实时满减、运费门槛（如非PLUS会员可能需运费）及促销活动影响，最终金额建议以京东大药房 App/网页端结算页面为准。同时请按药品说明书或在药师指导下合理用药。
sources:
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZ_yQCInu3F6XrHEEJ-Y0IhKLD_5WMhSCnQonws3vlSKwSR0X5ZY2lqquZ93a5tMgx6Cf_MEUmxdOu7HT2hA_GAMAOY3-cglWKDxOdJOIHJtTW0-GM_-VkpWWrIMpM65XZhGeEN5DiIAOBVw3w_qLKnNVyFtWhzpuqk1kK9oq2hXZ0Q-8A3koxIZymkEQqr3RlM2fW3kNtrzQqcL0IOdqbYHjH2Ok5J4Is4pbGFUL3_LxRW-rzLfxseD7xh4rifdGrMGgshFOsv2rboPKZTdvW8_Rw78vvTAj8DU9DY0KUdEM-f_E_bZZ-EiEDYm8=>
  - smzdm.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvdX9ac1rObMPyjepY-FIvkAyEdh5jwfEXKXaff0Dmji2DX0_mjzvDZlArR3MQby_UrTR7hMFuTNKK-jCASNBEym9ZwHlVA-yXsCH310Ep_zhe7GUEuERN>
  - smzdm.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEj4HXD-VwD7DSNlyTkRCtogYD79kcM5D4qXA8cz9w1x8-WCDEGqAGdTA57sG1nLDt9Cos1ihtgDApUmCdywMtU1BiEKWhY2Kto3eOWjtxDIwUpDYiCVM_K>
  - zol.com.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGSYc6YG0PkYTQtWv-l5rv8ErMp7O88ZcYpVqGQyxUXRv_bzi5ZHoIyaHjaPR_vbciYEZTnL9SP1SSM5G48MHynBaeo3magB-pImuB9EpBkXguTJb9KiiCYZm_0OBA1r6Hk>
  - jd.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLZe787N7iBeIvcud6K0xKdjc3YhAPsDbJXLPmneURfHcRpWQZhFIhV1qyqErLVudJ2M3KhU5uDieUOIP9sjd3a-z0Qw5MODcKLnrLnZbesHC6ibpHq1gj4Etc1A==>
  - jd.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEl_m6qrXLsHylNIUBGkJr9A8qY0Es1Jk7csS3YlL-9gIL3O8kNa4PfXA3RVf3fmExh-8NNMj8U8P4U67QAZrg_k8Uc9QJuI1vaz1ikYUgx2UENAu_ipkXTjhi0fj8ItxSgnqVyArCV>
  - cctv.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtQEjziDBFxarJCcvyGOBQkNndGHW2HhLytBWh_AIeF3bc7ddccnC0I5I4TrIEzHlKNi61yMHBA8yu8PISiVCtRQxGIoIq1t0Ib63gUJI7Ofh54WgXYNjTF-1pF8WN2DFZM6BZpCzVDfNXd8rAbpzgzGggfDOo7vHJdCfi>

[17] web search for 'ibuprofen extended release 300mg price per box fenbid buy'; grounded search summary:
**Fenbid (芬必得)** is the brand name for **ibuprofen sustained/extended-release capsules (300 mg / 0.3 g)**, manufactured primarily by Sino-American Tianjin Smith Kline & French (TSKF / Haleon / GSK).

---

### 1. Typical Price per Box

The price depends on the packaging size and whether you are purchasing domestically in China or through international importers:

* **In Mainland China (Local Pharmacies / JD / Taobao):**
  * **10–12 capsules/box:** ¥15 – ¥20 (~$2.00 – $2.80 USD)
  * **20–24 capsules/box:** ¥22 – ¥35 (~$3.00 – $5.00 USD)
  * **30–40 capsules/box:** ¥35 – ¥48 (~$5.00 – $6.80 USD)

* **In North America / Overseas (Imported via Asian Grocery & Pharmacy Sites like Yami):**
  * **20 capsules/box:** Typically **$8.50 – $13.00 USD** per box (plus shipping).

* **Other International Markets (e.g., UK/Middle East Fenbid Spansules):**
  * **30 capsules pack:** Approximately **$7.00 – $17.00 USD**.

---

### 2. Where to Buy

* **If you are in China:**
  * Available **Over-the-Counter (OTC Class A)**.
  * You can buy it at any local pharmacy chain (e.g., Dashenlin, Tongrentang, Nepstar) or online via **JD Health**, **Taobao/Tmall Medicine**, or on-demand delivery apps (Meituan/Ele.me).

* **If you are in the United States or Canada:**
  * **Online Retailers:** Sites catering to Asian goods (such as **Yamibuy / Yami.com**) frequently stock Fenbid 300 mg 20-capsule boxes.
  * **Local Asian Pharmacies:** Chinese pharmacies or herb shops in larger Chinatowns often carry imported OTC Chinese medications.
  * **US Over-the-Counter Alternatives:** In the U.S., standard OTC ibuprofen is 200 mg immediate-release (Advil, Motrin). If you need long-lasting 12-hour relief without importing Fenbid:
    * Look for **Advil 12-Hour** (extended-release ibuprofen).
    * Alternatively, **Naproxen sodium (Aleve 220 mg)** is an over-the-counter NSAID that inherently lasts 8–12 hours per dose.

* **International Online Pharmacies:**
  * Export pharmacies such as Kiwi Drug or regional pharmacy distributors ship Fenbid/Ibuprofen sustained-release capsules internationally.

---

### 3. Usage & Dosage Reminder
* **Dosage:** Standard dosage for Fenbid 300 mg sustained-release is **1 capsule every 12 hours** (maximum 2 capsules per 24 hours), swallowed whole with water (do not crush or chew).
* **Safety:** Take with or after food to minimize stomach upset. Do not combine with other NSAID pain relievers (like aspirin, standard ibuprofen, or naproxen).
sources:
  - pharmacompass.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH3JSt4rCqeOUJNzF2UliW71bqNKxigapynj3LEKNWq3R1XQvCX13gA3Fpi_YwD4PkgGr03Q-A2lKR0QzQ-RmXFFNejvGSISkqYxOB28_EBv-c7l4Y9TtAiZX0XzGczQqcUybg9xIVo-bwYk4HMy_76lw==>
  - dgdat.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF13dDtGKiO4NYpRTd7bi2ftyVlqqEE7Vs8bummzfRobZ-FEuGoL8qwmJ3Ntsg6k_ivbZNCi9hmEV6AfVuS49W95x42e5utv869--AJrGBwdeN0yA3EV6bulfbElt_JKaFvJxZRjqez9Mw3z8Ia6qc=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0_x_wkF9JocuOkwmwOee6SASibLdyk22bd6yxN1mynu5biDWXguciLgvC2fNu8rI9socHQCWUhkwWxH0kf8JySvJNqlsDL3YKUjK6I5RcTWNIaM2BomOox6D2gGXJJScJrPn59tNd9Wu3vaLZl6lr3GnOZCrkmg==>
  - zol.com.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFIVg1ZVELHfd8DnJUOOpwrshLaPOvsLLAsKlh1WyDAJBxHpmHv70MpiHhoP7Gek31GXAdIb1v3Ar1sGvu6OoPzPYjuDG7VZhSDYy1ZGa3jVHmTf7CjaiFuOf2sIvyzCQ=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpfTJJGpymrMNTQjpAv7kx3yK2lartAZiVUxrOvvcpBVm-kBJd_73-DSFUARv3ENeaQDkNhYzUhB98pFLWCK9KIrk_ouIM7vAyIHRTajY-NHMZ2lNtfdCELgn2m0Va0usAPGeA8N_TYOwgxg==>
  - yami.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcwXqYoo-U1potf5mICBPRowvGi9KCjfKB3nzzE-LU08khmdKPsNXYoKXfYZYvpnj6KsbYpKMAlsrfXjSMPK0CIaMqpA4PMmYwzq5N_E8MXrLxLY5OHQdSuHoxfSbpGERe>
  - pharmjordan.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHj0RgHa1DeHkpSisou3V7xw49fim8Vxuf9lSKvRPUSmLkb4rpve66NejuR3SucSAzooWWyesW-yLOi1GyiUiCR-RUczBbrNvUYYFrkqupiPy8u7CLCjmdDTz27WZHhXxAsC_Wpw38pEpK92yNtLxW4>
  - farmacoinc.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHw-UrCyl5thxG6AGQCodXvRV0KH2UYTj51leQNDNKFZ7Y8N1nsYg6zB5frPI89P2LIIhKIbzPAaRxmhQMGWNuFLAGkPJxjj9OSz0WFQXYr1IB1MCuymcJCe4MBY8QD1FgGHMynWN8w8qCf4Fg=>

[18] web search for '布洛芬缓释胶囊 集采 中选 价格 0.3g 20粒'; grounded search summary:
在国家组织药品集中采购（第三批国采）中，**布洛芬缓释胶囊（规格：0.3g × 20粒/盒）**的中选情况及价格如下：

### 1. 0.3g × 20粒/盒 中选价格
* **中选企业**：珠海润都制药股份有限公司（商品名：润都奥芬）
* **中选价格**：**4.05元 / 盒**
* **折合单价**：约 **0.2025元 / 粒**（约0.20元/粒）

---

### 2. 补充参考（同期其他规格及对比）
在第三批国家集采中，布洛芬缓释胶囊（0.3g规格）共有4家中选企业，各家申报的包装规格和单价略有差异：

| 中选企业 | 包装规格 | 中选价格 | 折合单粒价 |
| :--- | :--- | :--- | :--- |
| **珠海润都制药** | **0.3g × 20粒/盒** | **4.05元** | **0.2025元/粒** |
| 上海信谊天平药业 | 0.3g 相应包装 | — | 约 0.2025元/粒 |
| 南京易亨制药 | 0.3g × 24粒/盒 | 5.39元 | 约 0.2246元/粒 |
| 华北制药 | 0.3g × 30粒/盒 | 8.04元 | 约 0.268元/粒 |

*注：*
1. **公立医院执行价格**：在公立医院执行集采“零差率”政策下，润都制药的该规格产品售价即为 **4.05元/盒**（部分地区或接续采购中，因不同省份接续方案不同，个别地区价格可能在 4~5元 之间轻微浮动）。
2. **零售药店/未集采原研对比**：中美天津史克生产的“芬必得”（布洛芬缓释胶囊 0.3g × 20粒）未在中选名单中，公立医院挂网/零售药店非集采售价通常在 **12～20元/盒** 左右。
sources:
  - tengzhou.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRlxMZEbjUvE7Hq0ow4pnZmdNjcwHC5YEd05KZPC_HPoGbAdz3oK3yOqcP7coRVn3HOMHbUeBKxJH4kYaddTbe4E_DuHgdPFfu_P9AJb1x-sHCcfaFpvq9UIw6s-1aLbTofiV6WSh8wemBgQQShb8K8Ou9vSmwNNR8n8HLEMoqfKFUyxlXVB5plvX-twYcvJQoLvpcbS2l-arVork07A==>
  - ce.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgr6wqUIhR3fh5lhfEzm0yqbmJBZUC62WJrisusKEYZES7lgmcwuQCYI7iSVIkCKIK9vAoqvFbHrTTqiePeOkeW4hpT3189HDaTQfK7OuuFUu7Sa33bevAJTNRi77DYCCLA2kxT42X1hg_L4y7R87ft98Ivv1M>
  - toutiao.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGhE5IbCdtOxB8jtfyBee4N6yOPIDNWonNk-QQqT18LUlwOojfmMT2-vQm5TNfceys_jXS32YUitwn4TP122MNv8j0MW6u2OVDjoCo7Rf4DCcj2zJcqXLo1xvyPnAtIgkOvbgRBGalcmQ==>
  - jimo.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGiiOXF_ItoQmVetQ2ofLaaWOmJTMVLEFYWYRvFwm0Bu-LyuzndFMHxvHEagIl3NW-pXxtLmyg7s4ej0d9LV5VMmdddd7xmZfpKm0QFBvh7afTo-__CKbl1wTdndbJPoHvAL0emeYBYD-FFFkdTDD65yAHFY2rTCxPbK1Jc6vyh_PSE_xDppZvOHs93tlRKFVwLw==>
  - group-purchasing.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPuMiyba80jLC-c_RBO1dLe_jHWUS4F_p_1kqZczdzejwU5MiasQZ2r4J98K7n-LWLJFNJVygZ1V0jZWuvwxD0MzlMrQM1vpwiGrvmuEUNEemhZqySxdIHHG6W21q9Cg==>
  - ce.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXqgZrL7IH3J60U5bz0QWvibD7uOXsxA1OgomWuHwIs-YotZusCfUbm8sK_qwVN8vhRM2YAci8Nc_mTq-boyE_30GgASlVUDjVfBfZZcogkcyleRTfBBgovm1FruhsFutfdcN-50CuJyXv6_4BmtsUK3934HKH>
  - xinjiang.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuWcNq5Gw23qpATziNsuxG_hj_CMv8mZf7-sQOrJ0N3T-A5HOJ2HsBF3EkJVDQu-dekglXApAjolGmIML1wXEFHcUoyr2MqkiTTMgrP6YLYzM4wzYCH4GsAtGjcuECGgtklCFIPiUzqceVZXsUXNCfpA53dyzW3BN4vh-Kln_3xwf4THjbKzI1fJwZuvXRF3w=>
  - xinjiang.gov.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuWcNq5Gw23qpATziNsuxG_hj_CMv8mZf7-sQOrJ0N3T-A5HOJ2HsBF3EkJVDQu-dekglXApAjolGmIML1wXEFHcUoyr2MqkiTTMgrP6YLYzM4wzYCH4GsAtGjcuECGgtklCFIPiUzqceVZXsUXNCfpA53dyzW3BN4vh-Kln_3xwf4THjbKzI1fJwZuvXRF3w=>

[19] web search for '仁和 布洛芬缓释胶囊 0.3g 20粒 价格 阿里健康'; grounded search summary:
在阿里健康及天猫医药平台，针对您查询的药品及规格，价格与规格说明如下：

---

### 1. 规格说明
* **仁和品牌**：仁和（RENHE）市售主流的布洛芬缓释胶囊包装规格一般为 **0.3g × 22粒**（通常为 11粒×2板）；
* **20粒规格**：市面上最常见的“0.3g × 20粒”多为 **芬必得（中美天津史克）** 出品的布洛芬缓释胶囊。

---

### 2. 阿里健康平台参考价格

* **若为「仁和」布洛芬缓释胶囊（0.3g × 22粒）**：
  * **单盒日常售价**：约 **15元 ～ 25元 / 盒**
  * **促销/多盒活动价**：平台有满减、多件打折（如2~3盒套装）时，折算单盒约 **10元 ～ 15元**

* **若为「芬必得」布洛芬缓释胶囊（0.3g × 20粒）**（如为记忆规格偏差）：
  * **日常活动售价**：约 **16元 ～ 23元 / 盒**

---

### 3. 温馨提示
1. **价格浮动**：药品的最终实付金额会受到店铺优惠券、88VIP补贴、即时零售配送费（若选择小时达）等因素影响，建议直接打开手机淘宝搜索“**仁和 布洛芬缓释胶囊 阿里健康**”查看实时优惠。
2. **用药安全**：布洛芬缓释胶囊用于解热镇痛，服用时请整粒吞服，切勿嚼碎；注意遵照说明书剂量使用，避免与其它含有解热镇痛抗炎成分的复方感冒药同时过量服用。
sources:
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVu9faOB21-w_HKPj2N_56CsA0QueVqt3Oi9QPhsALg9ivn_8B3VJesHPAxWfP_I-fZ3ZiR8A1aW1QkDmjt2Ndiye2MXBf2VQgvQ52iJP1vtNOh6bMrlV_ALEdwbrJA9QcrqofGdmL9fO7iDwh6pE_IzHhmrdmfJ3aRww14AssQWN_yF4N>
  - 111.com.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLNv5yP467wWr-LhdLQBXbERvkpZecYfn6Vbdym_dvvWIB-BTkgsTq1Fo0LtpMcO0EwX5SUOL68cUL3qcnYP8YlXZdDLnK_DB8UTyKkX6fSuCXlY8YKGCaFfxkXlA=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLRAkebJFpLsDyY2CkYZNJQRmLHH8GSmRAxW4CPGUFSuIVN9nnxYLAsYzeXt_JlE64JK4L5YE1m_BU_st0BL7_U8aGlXdoowfqhWew0m1F62UB2U1URqtt-LCI_Ymp8NK0M75JbaUSWnjCGXasLByu3J2Ntc9E8as1hjp1Ts_wMyvEo5Im>
  - smzdm.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERlugsi1w__jkVSML0jzOyLhnYxZvIMppWb9NBrUx8QVQBF4OCbVR6aM4MwK_CAZkAK3C09Cog0pcw2o_yiWXLc7K-o37Rkt1Yxix3KiPB3v7gUsLpDQfF>
  - taobao.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHUd2wukQl4KNUxV-YgEZoesRQATol5_D6J2hmdovFSaNE5M8IPGuB85cPwFolOIVpOP5FOmikp2dYhQAMTeNe4Iw481FOUVZAzvPK0giepPnk1WcZ4cBieT0rdzMRnZFWZrpDzwt488tI7B9ny_miECKEcN9Z6_Yr2OrYWe2rklESmodqmbWKrfTHp2ECxDC9Hn2W3JL4u3xep_9bHvLg=>
  - dzlaa.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnKEs6HxZ-hN5tzIKd_quvVFxgLAWKe9BPu_qEyXjhuH12iu93vRWnTvXtOrXhet7HK4zhJth2_ycRec5F-WKdgP5WAvR6IgpI34o-T5bQvCNaMd7WMY5eafgS>
  - cctv.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbTnCoHJd0rFiW94k4B3QX9ir8PzZXGeepU_0lM73haGZAQuwb0mln2qFWVF4OIiFz_ACy3S1oobaiLGD9-q-eqnfu4G836rh1nB__IzTPte0uB_aeW0ZxhRi5gBtkk_fw5B5eJibaoAASs0zuN33i-nqUBzqAstiyTAGmGA==>

[20] web search for 'yami 芬必得 布洛芬缓释胶囊 20粒 price'; grounded search summary:
在亚米网（Yami）上，**芬必得 布洛芬缓释胶囊（20粒装 / 300mg）** 的价格通常在 **$8.60 ～ $12.99** 之间，具体取决于入驻商家和促销活动：

* **常见活动价/折后价：** 约 **$8.60 – $8.99**（原标价常为 $9.99 左右）
* **部分第三方卖家/直邮价格：** 标价在 **$12.99** 左右

*注：亚米网上的药品类商品多由第三方商家提供（如北美本地仓或直邮），价格会随库存情况、卖家运费政策及平台折扣券有所变动，建议以结算页面的实时价格为准。*
sources:
  - yami.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGWQYGe5D_HTa7EDRnedqmQOPW7FPF7BZe15eqrtDGBqT3ltmQdImQ8smBQ4UAQQeNL3D62-qoqAkl82oSf3gL8RwBwmQPZVSlcToj2hPZVWB9_zuouHvKC9ohZx1P2EMdJX_AAiy2RKCFX45bqoYtcwzg923Y-8phlASVVIChRKb1AqEroorV3H3HNn9EgXPaYIBTgY5oW5-FxKmLTgLqbJ0KWb_g8Gppf_2-tCC7lR-mjeRcw5YyuP4UQJSXZr7Q=>

[21] web search for '中美史克 芬必得 布洛芬缓释胶囊 30粒 价格 元 一盒'; grounded search summary:
中美天津史克生产的“芬必得”布洛芬缓释胶囊**并没有“30粒/盒”的官方独立包装**，常见的正规大包装规格为 **20粒装** 和 **24粒装**（由于单粒规格为 **0.3g（即300mg）**，常被误记为30粒）。

两款相近主流规格的参考市场价格如下：

---

### 1. 芬必得布洛芬缓释胶囊（0.3g × 24粒）
*这是目前市面上最常见的大包装规格：*
* **线上药房平台（如天猫、京东、美团买药等）：** 约 **18 ～ 26 元 / 盒**（促销活动叠加优惠券时常在 13～16 元左右）。
* **线下实体连锁药店：** 约 **25 ～ 32 元 / 盒**（线下药店普遍价格略高于线上）。

---

### 2. 芬必得布洛芬缓释胶囊（0.3g × 20粒）
* **线上药房平台：** 约 **14 ～ 20 元 / 盒**。
* **线下实体连锁药店：** 约 **18 ～ 25 元 / 盒**。

---

### 补充说明
1. **如果是其他品牌的“30粒装”布洛芬：** 部分国内药企（如华北制药、纽哈伯等）有生产 0.3g×30粒/盒 的规格，价格相对便宜，普通集采或平价款通常在 **5 ～ 10 元 / 盒** 左右。
2. **用药安全提醒：** 缓释胶囊须整粒吞服，切勿嚼碎；用于止痛通常不宜超过 5 天，用于退热不宜超过 3 天；有活动性胃溃疡史、哮喘病史或孕妇/哺乳期妇女禁用。
sources:
  - dealmoon.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErTM3kDu0us_CXKXleAvaofGJCcBsdboXRr0pMv3NO2Bjk9bxH3RYV3QVeTTsoupqW5VpNpwOfbV_HgRgWOMVIHC0l9DgrBrFDSVz5hgftIhXEGqXYEomHLBLP9IPvF5ONOSnWFDDpalaU_A==>
  - cctv.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxXmWzxZlYUBWJH0Hnxe0I_GTnQ5H3iFzDj8tvkIqS5HGhZ-6R4pwjepAq9Z4A_CapN9pnKvycVJHszxKsMigziYf2h_zOYOBLcoKA_axWYLeRkh4pc7Bx5Pq_m7MUqQ13B7AKgNpj9deOZR5qK-uUXC4pdS-lrDbvjdTZ6w==>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaojzIjgfORan9vm8R_YC5pKWK5eLhXgWShvmlGRe7cQt3ZwYx5Ei9wyU-ayxZWVzhZOEzf4Tnn3uBCC9sYar4b2p7NarKxb-JeUKMwiBpNcSvwKe2EN-m3jaq8RilAxuxHu0utwFX3Wnpni5Ekdc5rgJbozldwmdxJr6C7j7tKLvgJqyCAXzDLsknBSwOeyznJ77GaK3W87pGPBpFQpxkUOxuKQLz_6jSFseL_XCSvfMa8EZZKeEX9Bg5KjgCuI1ZO6oxL0y--OWN-StmMgVauy3B3hqjpZqvW5A6bVdyqdu-ru-HLwBh1pAnuYx9Fn5i7lhw8D6kL3vbtpIA-1A=>
  - 315jiage.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHal3aG82nieAb9bvINrc4dLz-M636HZj1xB1WhA2ckxED-_Fzl4H109HrvDZW6Ol2DyJWrfx19dFYWI5iEK_DOqQmkYkcL_70pFc1uj9xr_mXw7BTHtl8=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGprSbr1jeJwzRKm3Rlz6r4ddcPoSty3LFIeFUcpQ5tHekiex5wD1xSI_HKlGyBEfO5DDim5Nir_09yTvlm12Fz68Zr8oAyFIzBoMCXT-JPpnfPhpliBkowlnJHOUuY1UdCv2jHsExX400lqi7WAHzVrZdsa77vQxk=>
  - kowloonhospital.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvt2aVjvoIbTu4GdRI4ztf6swP6eVHxEzZUm5JGilDmU4MYuNSMOeCcd_jNWhJ7UXze5Vbe30QKHUlwcIK7ia5okGVUc-dws54pckJj0eiY2W0SUpE2IUTu6Ep7zT1r_SKbZU5z4ciU1K2hCcyXakQsgBrH7S-Dv5AIpTCwv39Lsl1rrWmG5gUNu7xv2Dt2jZkuzrWVFgBCPU=>
  - ifeng.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGIus_0Pvj7t6ebuNZKAmUb7ZVODxRRey0eUReZDcgDyzNwjq57bQoauZe06JJQlUsB4qO1Mnel33kpirbS7f7uz9J47Gk4vFXDkROqj2KoD7nV4lL9C-TL0Jrn-mA=>
  - med66.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaxHQtTQscOjmEb_HczfYuxe1EQnMJ68wk6m4ot6IFoYIH3I-ms1WUDqXdzRAMhL7SVJpybEPRFBHBZo6RquRtx1eVnO__GtJ1IVNhWYz8Hyio1bkqm7e4QNRuEEsrjGmBzNkDHVBFFQiYog==>

[22] web search for '芬必得 布洛芬缓释胶囊 0.3g*20粒 价格 药房网 叮当快药'; grounded search summary:
**中美史克 芬必得 布洛芬缓释胶囊（规格：0.3g*20粒）**在药房网和叮当快药等平台的大致价格范围及购买差异如下：

---

### 一、平台价格参考

| 平台 | 参考价格区间 | 配送方式及特点 |
| :--- | :--- | :--- |
| **药房网商城** | **15元 ～ 25元 / 盒** | • **快递发货（1~3天送达）**<br>• 聚集全国各入驻药房，比价后单盒药价相对更低。<br>• 注意：单买1盒通常需额外支付 **5~10元快递费**，凑单或多盒装购买更划算。 |
| **叮当快药** | **25元 ～ 35元 / 盒**<br>*(领券/促销活动后约 20~28元)* | • **同城即时配送（约28分钟送达）**<br>• 线下前置仓/实体店直发，适合夜间、高热或突发疼痛等急用场景。<br>• 药价略高于纯电商药房，通常需收取 **3~6元配送费**（夜间可能另有服务费）。 |

---

### 二、选购与比价提示

1. **注意核对规格**：
   * 芬必得布洛芬缓释胶囊常见规格除 **0.3g\*20粒** 外，还有 **0.3g\*24粒**（更常见，约22~35元不等）及 **0.3g\*10粒** 等包装。比价时请看清每板/每盒的具体粒数。
2. **时效性权衡**：
   * **不急用/常备药箱**：建议在 **药房网**、京东大药房或天猫健康购买，多盒拼单常有满减包邮。
   * **急需止痛/退烧**：建议优先选择 **叮当快药** 或美团买药/饿了么买药的同城急送，省时快捷。

---

### 三、用药安全提示
* **用法用量**：成人及12岁以上儿童，每次1粒，一日2次（早晚各1次），整粒吞服，切勿嚼碎或掰开。
* **使用时限**：用于退热不得超过 **3天**，用于镇痛不得超过 **5天**，若症状未缓解应及时就医。
* **配伍禁忌**：服药期间**切勿饮酒**，且不可与其它含有解热镇痛成分的复方感冒药（如感康、快克、泰诺等）同时服用，以免药物过量损伤肝肾。
sources:
  - 360lj.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3A4xzMNCVV6Eh8pgftOHuHTCc0mFzawZpFTsXWBztd_nKO7Xv5jQ16WbKVK0HyFFDWo8Jobv3IPUXpYsav2E2TVIzeWiQqD3znDrrtgAbzEmR59QMdMHUj-k_V3mMTCM6Ko-KcQ==>
  - taobao.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeL1b6BPup1yatmkwfbjYqw8KZ158-HINdK76ETtDgnGsHASiszcpdzkP8X0MPr32KzDGG5mhTmg4fnspfji_jQDfsQsExNIh5vY7Ed-SfG9_Gqr4vw8VouRbf1WKEZAo0HCGgb5aJeayBCA-7igVvzl9vBSj3aJruiFv52MyGEWY9dADVDDBahDkJFBCNLcVZyQabA4G1dZ-v3n_UqS0=>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9XcV5pHsItrm31mlB5ZBLjtPgrzbVRwlbaHPBRjxg2r4THhMG57pFZlQmECf2-T199v4hy-QJd9xE-1qQeMmGwz_IszuM4PMse19cKYpdUnLSPsr2uIZY6GX1qiMWQbyBDOJnjulteyNoqDqvZ-C8pjNbt3roCAM=>
  - cctv.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUjHgeYn5iAMT7D6_wU9qQ__yjC5wT-0AVe-lL5l7A2c96O7Tpa_b2Y0cW7p_0gHJ6431xKDYZJN0UWfvPLUXAEYC1VXtzpHc0q1iE4VNOVwcfRf4KEcE6_46t9UdGaqMpkWl9lFTlE08cqd0EsxevFRsP35my3hG-rlHsEA==>
  - 39.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFG-2MQbTPy15_ZkXCyC4zqx-4BNeP0mx7Rd2PnwFJPQEU3KSCDhnge23etuix44V0li6H-NbS7ZZIf1FJphZnbal51zWp4zJtluAdiDioYk7ztqFA-_E-WxFrmeSDn_B-G_Vc1>
  - baidu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE51ODiLm5TTX1BF0InS-qAtZeRAcSnvf5MhsyR4bagLpEGb6Y8acmj6yNjxWZGiOdFr0_Rlhj6z5oos75JiAWjeYQvrPni5Yiq36SWcXuO4FKQZFS2k2G8aYF9sPKVnThFPbdcUkIUoGOWrH4SEkd2nb08mko4at2WtRdrQegCyipTygZ4mNuEwSgPZ_iiiZQaxK2066cFNnxJgKIJq2v21Yo7_7Nt6UL-YD5Rgp4PcjCp4__xpaDBR70mHIns3L7fjT2UuPPqej1u7OrzvBnzLTzaAdfsLVm5gqZ8nUyZjIM1B4opfKgyGW2UF4OLqULylcdegMatOPQjzFxtmr7G2-5_c88hjNhgRUyp6_H6-g==>
  - oeeee.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCDLzqQGF7ICAJpxApB9cneT-geCxQ4cqy3kvpU0G6DPPmxPE5HaWA439K_1CAXU0UubWWqRpaDB5Dz3WSmo41DpuLKQ_OCBN6oY9gSlSiSzpyJvYxwJnkdKORWs2Qzp1DcvqC2j0=>
  - 298.cn <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdBHDGQBnQB44OMAnz4y0VNwbJ9nDZE0bK5wMNtHKE0u9ma05oKsF2WxKHOcw83D1CTQKMoVntnVL9dczoqyd48LIrZDVRQ3iTLMyoP36QZOhkSOba505YsQ==>
```

</details>

**Answer:**

# Ibuprofen Sustained-Release Capsules — Public Market Price vs. Our Price to Shanghai Huashan Hospital

## 1. Internal record — what we charged Shanghai Huashan Hospital
Source: **internal MongoDB business database** (`drugs` + `sales_records`).

| Field | Value |
|---|---|
| Drug (generic) | Ibuprofen Sustained-Release Capsules (布洛芬缓释胶囊) |
| Brand name | Fenbid (芬必得) |
| Specification | 0.3 g × 20 capsules / box |
| Approvals / maker | H10900089 · "Our Pharmaceutical Co." |
| Customer | Shanghai Huashan Hospital |
| Sale date | 2025-12-05 |
| Quantity | 5,000 (units) |
| **Unit price charged** | **CNY 15** (per 0.3 g × 20-capsule box) |
| Total amount | CNY 75,000 (= 5,000 × 15 ✓) |

Only **one** matching sales record exists. The database stores customer names in English; a Chinese "华山" search returned nothing, and the matched row is `Shanghai Huashan Hospital`. (A second sale of the same drug exists — Neptunus Pharmacy Chain, 2025-01-20, also at unit price 15 — but that is not Huashan Hospital.)

> **Implied per-capsule price: CNY 15 ÷ 20 = CNY 0.75 per capsule.**

## 2. Public market price — ibuprofen sustained-release capsules
Source: **public web search** (aggregated results referencing JD健康/京东, 天猫医药/Taobao, 药房网, 药采网, government procurement notices, Yami). These are search-engine summaries, not verified single product pages.

**Branded Fenbid (芬必得), 0.3 g × 20 capsules/box:**

| Channel | Price per 20-capsule box | ≈ per capsule |
|---|---|---|
| Online pharmacies (JD健康, 天猫医药) | ¥14 – 22 | ¥0.9 – 1.1 |
| Physical chain pharmacies (叮当/美团买药) | ¥18 – 28 | ¥1.1 – 1.5 |
| Public hospital (if stocked, retail) | ~¥12 – 20 | ~¥0.7 – 1.0 |

**Generic / government-procured (集采) brands, 0.3 g:**

| Product | Spec | Price/box | ≈ per capsule |
|---|---|---|---|
| 润都奥芬 (珠海润都) | 0.3 g × 20 | ¥4.05 | ¥0.20 |
| 易亨 (南京易亨) | 0.3 g × 24 | ¥5.39 | ¥0.22 |
| 华北制药 | 0.3 g × 30 | ¥8.04 | ¥0.27 |

Overall branded retail range in mainland China: roughly **¥14–28 per 20–24-capsule box**. Fenbid did not win centralized volume-based procurement, which is why its retail price sits far above the ~¥4–8/box procured generics.

## 3. Comparison

| Basis | Our price (Huashan Hospital) | Public market (Fenbid 0.3g×20) | Generic 集采 (0.3g×20) |
|---|---|---|---|
| Per box | **CNY 15** | CNY 14 – 22 (online) / 18 – 28 (physical) | CNY 4.05 |
| Per capsule | **CNY 0.75** | CNY 0.9 – 1.1 (online) / 1.1 – 1.5 (physical) | CNY 0.20 |

**Reading:** Our unit price of **CNY 15/box (CNY 0.75/capsule)** sits at the **low end of — and slightly below — the public retail range** for the branded Fenbid product (¥14–22 online; ¥18–28 in physical pharmacies). In other words, we did not overcharge relative to branded retail; if anything, Huashan's price is at or slightly under the cheaper end of the branded market. Against **government-procured generic** prices (~¥4/box, ¥0.20/capsule), however, our price is roughly **3–4× higher** — the usual branded-vs-generic gap.

## Caveats / limitations
- **Our unit price basis:** the DB `unit_price` = 15 corresponds to the spec "0.3 g × 20 capsules/box," i.e., treated as **per box**. The `quantity` field (5,000) was not explicitly labeled boxes vs. capsules, so the per-capsule figure assumes a box-of-20 basis.
- **Public prices are ranges from aggregated search summaries, not verified single listings.** The search tool returned only search-engine redirect links (all `vertexaisearch.cloud.google.com/...`), not canonical JD/Taobao/Yami product permalinks, so exact live prices and direct URLs could not be confirmed. OTC prices fluctuate with promotions.
- No RAGFlow knowledge-base documents were consulted for this question, as it turned on live internal sales data and public pricing only. Let me know if you'd like me to also check internal documentation (e.g., pricing policy) or produce this as a Markdown/PDF report.

---

## 13. route-07 (routing, medium)

**Question:** What tools does the IKEA GONATT crib manual say I need for assembly?

**Gold answer:** Not stated: the indexed GONATT manual is diagrams, and its text consists of part numbers and quantities only (e.g. 10135, 10006B, 11065, '4x'). A correct answer says the manual text lists no tools rather than inventing a tool list.

**Route:** expected ['ragflow']; delegated {'Network Search Agent': 1, 'RAGFlow Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[1] tool ls returned:
No files found

[2] tool glob returned:
No files found

[4] web search for 'GONATT baby cot assembly instructions PDF IKEA AA number'; grounded search summary:
Depending on the production year and model revision of the **IKEA GONATT** baby cot / crib, the assembly instruction manual corresponds to one of the following **AA numbers** (the number after the hyphen represents the revision version):

* **AA-2261432** (most common; revisions include **AA-2261432-2**, **AA-2261432-3**, and **AA-2261432-4**)
* **AA-2629396** (newer release; typically **AA-2629396-3**)
* **AA-2482071** (e.g., **AA-2482071-1**)
* **AA-943776** (older generation version; e.g., **AA-943776-6**)

---

### How to check which version matches your cot:
1. **Drawer Runners & Hardware:** Look at the small hardware parts on page 3 of the PDF (e.g., whether drawer hardware uses standard dowels/screws or newer cam fittings like `10006504` / `109504`). 
2. If searching IKEA’s database or customer service for replacement fittings, quoting **`AA-2261432`** or **`AA-2629396`** will cover the modern versions of the GONATT crib.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7jx9psHRk_RK9-w9b0FD5vPmx023T1y0ohoYtH8eLQdB0COflFK5wIYmf86u4IddSyXSyrGe79GHwPGQ1Uj76x9u2sgVczEL9C6f2R7vO4TMlUI4fuoTmm0y1YdMcdSAdR45q6UPCd4bXoySKE2IzNZn8wCRiXJd1-Xk9HD7xybPXNzYNCUSIgJYphb7e47O5sJhDUL1TD_Y=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzOdy-majeJXlp4zXs48x0ts0-ieT732ivELr6usehVS4rbDeXngV0_LbX_cA_N4DhXmuuAgH9789NVj28WaVLIwlIaggR4nh1ALhflDyMbKcuQ9RWDDMlGd34_zzRaONm7OOohvJG3xOMYfv6tYN1zMRQ9JFJebYJQksyhUF5_7O4218tjfqUgGY6SzwfKlDIyet2QVYr>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHdlE85-pKi8Ict8oHQyeFsmSMlSqb-L5yDI0I1ppdDrYb8hZntt3it2VQOPK4cQbP1DT4yilctP8JSAn1I7yEfh34kKjrmhaaeD50wsEtH_IkJJAPiu0aNFqC1_dZCRcsINMLS8AUJYd2DNpbWRfjzi7lH_ZFw3-as731An_QIdSzu-FZEWRj_Drh_F5W_l0xrhyE9npVi2w=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-nF9YBjM0m5vU3nd1EZ413fFu5IFA6skh90NAzBuaRsAoSRT0TgrBZa__iNvgyp_z88O8CpFdmoW1Y-wMUGXAmhONVSkx1mhPBLzrVCD_88lrrQy6ht_nuTzCCTfrbOJHohv21olC1IGvgM_rQlWgFNWzj073zMr2Np77aBshV7ujya_lakDtG_yNdiSoyn5eJiQHtXxQQsQ=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFOeXUUo9ZUeLnicJRxBCrBGt8jKC44xjRNfrMyrnekPB1rfA8ysfWnF4rnuUWrHX17auqxeOAV1fxaEbZ1_64iiElWroILp3nK4s4c-CGzgWy9ifu3VwCyqmdurFz77X7XZOaghDZeVoecbZEDBFujybXRbtKB8xvk7hP-rPcZ0jrhqUwjCLjQP0_yTM-u35vqPED-_ZBsVI0=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE34lNvacA-Om5YJYgTdZAIxO_yMlON0AMdeq6V68RTZfYSR0mR2dTZQU9H-o68im5DAqBvHwS5mDrkzQLdqSHeMMwsdbNDSgSNEmsEejnUFqqIKIJBmRX_ZhyaXi_v-j_rMqgtR1IGfVbjFWOIIil3u23XvJQZzuXjWd1qCqWb0YJEAKnvUg==>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzOdy-majeJXlp4zXs48x0ts0-ieT732ivELr6usehVS4rbDeXngV0_LbX_cA_N4DhXmuuAgH9789NVj28WaVLIwlIaggR4nh1ALhflDyMbKcuQ9RWDDMlGd34_zzRaONm7OOohvJG3xOMYfv6tYN1zMRQ9JFJebYJQksyhUF5_7O4218tjfqUgGY6SzwfKlDIyet2QVYr>

[5] web search for 'IKEA GONATT crib assembly instructions manual'; grounded search summary:
The official assembly instructions manual for the **IKEA GONATT Crib** (document reference **AA-2261432**) is available directly through the [IKEA GONATT Assembly Instructions PDF](https://www.ikea.com/us/en/assembly_instructions/gonatt-crib-anthracite__AA-2261432-4-2.pdf).

Below is an overview of the assembly process, hardware notes, and key steps covered in the manual.

---

### Tools & Preparation
* **Tools required:** Phillips-head screwdriver, flathead screwdriver, and the included Allen/hex key (part #100092 / #100001).
* **Recommendation:** Assemble on a carpet or soft blanket to avoid scratching the finish. Assembling the main frame is easiest with two people.

---

### Step-by-Step Assembly Overview

#### 1. Under-Crib Drawer Frame (Base)
1. Assemble the outer lower frame that holds the drawers using dowels and cam-lock screws.
2. Fasten the central drawer divider runners/rails inside the lower frame.
3. Attach the base legs/feet to the bottom corners.

#### 2. Headboard, Footboard & Sides
1. Screw the wooden dowels and connector bolts into the pre-drilled holes of the solid end panels (headboard and footboard).
2. Attach one slatted side panel to the end panels, securing them with the long connector bolts. Keep the other side open or loose to allow mattress base positioning.

#### 3. Mattress Support Base (Height Options)
The GONATT crib offers **two mattress base heights**:
* **High Position (Newborn / infant):** Use the higher set of pre-drilled holes so you can reach your baby easily without bending deeply.
* **Low Position (Older infant / toddler):** As soon as your baby can sit up, pull themselves up, or roll over, the base **must** be moved to the lowest position to prevent falls.
* Secure the four corner brackets/screws into the selected height holes and carefully drop the slatted mattress base into place, bolting it securely to the frame.
* Attach the remaining slatted side rail and tighten all bolts around the frame.

#### 4. Assembling and Inserting the Drawers
1. Fold/join the drawer sides to the drawer front using dowels and cam locks.
2. Slide the thin base board into the grooves of the side panels.
3. Fasten the drawer back panel and screw on the drawer knobs/pulls.
4. Slide each of the drawers into the lower tracks beneath the crib.

---

### Converting to a Toddler Bed (Daybed Mode)
When your child is ready to climb in and out independently:
1. Ensure the mattress base is in the **lowest position**.
2. Remove one of the long slatted side rails.
3. Install the included lower reinforcement guard rail across the open bottom edge (secured with bolts into the end posts) to maintain structural rigidity.

---

### Need Missing Hardware?
If you are missing screws, dowels, or cam locks, IKEA provides free replacement hardware. Look up the 6-digit part numbers listed on page 3 of the manual (such as `100514`, `101350`, `110630`, or `123492`) and order them through [IKEA’s Spare Parts Service](https://www.ikea.com/us/en/customer-service/spare-parts/).
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHFcwlLy29F-MXwWrTYXyBqkt0B5wVrJSft-tJa5kaXkb2tVXAE2Mt5wNiyW_6A0yxQaUIIeaj8Tb3PFnlozcj_cGoJfLG04Eu7kf3IcbrKsS53UW_xWHFj0aVuphaA7Q-FLD1sCEu7ob-sFym54n1xVP7lbtRG8OKP2_zwupuZErPl2vN0niNeKKHndZbJpB6vUei1jWo=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF41Qe7x3cU9Gqj0hGp8jIzANYji6v2FShbEeC3mDQudN5NGc3tQkZPQVQ3e7XxWphApNeAh9li5JFhs5zW-9j_HtajvNTgW9F4xzFatkwg5NZLd_15LFU45AZ0P87Wqq0VRzcNoZ71EU-gWF8bj0dlfnEtxlco5Mp2QeaeJfUoD8bZk_T7AliIbGijmB5jq6x4wQJ33ROG6A==>

[6] web search for 'GONATT crib IKEA product page assembly instructions download'; grounded search summary:
### 1. Official IKEA Product Page
* **US Product Page:** [IKEA GONATT Crib with Drawer (White, 27 ½ × 52″)](https://www.ikea.com/us/en/p/gonatt-crib-with-drawer-white-30467087/)
  * **Article Number (US):** `304.670.87`
  * **Article Number (UK / EU / International 70×140 cm):** `904.670.89`

---

### 2. How to Download the Official Assembly Instructions PDF
1. Open the [GONATT Crib Product Page](https://www.ikea.com/us/en/p/gonatt-crib-with-drawer-white-30467087/) on IKEA.
2. Scroll down below the description to the **Assembly and documents** section.
3. Click on **Assembly instructions** next to the corresponding article number to open and download the official PDF.

*(Manual version reference: **AA-2261432** / **AA-2482071**)*

---

### 3. Key Assembly & Conversion Notes
* **Recommended Setup:** Assembly requires two people.
* **Mattress Base Heights:** The base can be positioned at two different heights (highest setting for newborns, lowest setting once the infant can sit up).
* **Toddler Bed Conversion:** The included conversion kit allows you to remove one side rail once the child is ready to get in and out independently.
* **Replacement Hardware:** If you are missing screws, dowels, or cam locks, take your part number from the manual’s parts list (e.g., `101345`, `123492`, `110630`) to an IKEA customer service desk or order spare parts directly via the [IKEA Spare Parts](https://www.ikea.com/us/en/customer-service/spare-parts/) portal.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHK3JAoh0buLwcpftskS0Aq1DkpJUwRfza2ensasKcvSvrJt-MwQ5jM_c8lREAvYkyYnfizo6GoxD65U9ahC_roOu_0caI61FOLmdeGdxWnJTUh4HFLbyC5QreEGdodA6QhqbLefDg9tEF_BelG9axApHljRp30W5cI>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYrFhmrQ-oDgAyj_FWJgcDgtNzHlIeh9Uad137HlpEYqKJRWxFdJKijsPtsvrkFJikyzAY8YDDXaMVbw1qwlpi3KDbSLG58GC8YYfghW2zBDueTh5LiMK0-A_T0q3hQU-1k-genowXCpz67QcGM1EOPLn5yTUzv4WNEw==>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRaNYS3VzKkhEfx6xwjF6NTR77yx66S3Tdh6hKDRILtsMNBmBxlzdgr-sQEMWf9v2Fe41zHRcz_Ua1qBHE6ue1o94P4xoOT0m24A3LXdopcmuxvNh3vLsli3eNgEzUUOtr4t5yTOjVm3g6zcT8u9B7rxei-sW3vqBC>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHHHH7T149yqMuUwMCw-pKVpQgcx67KP7ae1pr854DJvBxGIk9klbaGO75jxHQGBP8aUa9s-UPhcVcHUiC7gAQbfTtkAWISlPS89eniwZb_xBPCBEdhlI_MDDYFT7w_21TzKIB17GypHW2AxVvAyNOWI4yQU7HuD5fvI2PPt5vGSQiardAaIH5QMQ7lZhVAhSRHcSgQbqQyHQ==>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8e4JRp2ST7ZmedqxqAxoCpbcyaT7od_VgM5j-X0Qis8fCnYVcLXt2p2JSQLK3sbJ1gd3KwjnqnYNUUS8gmo43rCPIuFfrvq0sf16omXHKhs3I0Pu_7bMZ2V-f1BR1ZzmaUgqVCmZSGuheKa1DNHES2mjToegWxMUpf_FHdPFbggKIyKXksSb5ovS09r2Rf3l2n5qMmBZsA3UA>
  - youtube.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqQWGUjAYqRf0iTz7ZREI6rdzVbRhsCswDcODjAwSVss4FTUEGiZSiMz1woF0GDpCqLgUlIfqFl-z3xY4310TOQUdDgFACs74KxDVfS_FZWB7cBnwKY_NISs9CjKr7J9w=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBOggLD9JvCwt2Q_xSpkNW5bN2nrD8MYZh4w4TwKWBd2rec7tQPUGM6EafRZQW5asJQXHNmsi8nENDI1vceFkRCPSRDr_iToYVCOzkOEIo-4WVYmjeq8r7zV31PdxTLai-po4b1J6HFf8oCq2V0B4OPKr299BSq2fpUD6G1fROTsfToolTARwYQ_KUFaKy9JhXlzF7Rq8=>

[7] web search for '"GONATT" crib tools required assembly "Phillips" OR "Allen key" OR "screwdriver"'; grounded search summary:
To assemble the **IKEA GONATT crib**, both a **screwdriver** and an **Allen key** are required:

* **Allen Key / Hex Key (Included):** 
  * IKEA includes a standard hex key (part #100001 / #100092) in the hardware pack.
  * It is used to drive the main structural hex bolts and frame screws that secure the side panels and mattress base.

* **Phillips Screwdriver (Required / Not Included):**
  * You will need to provide your own screwdriver (a standard **Phillips / cross-head #2** screwdriver is recommended, though a flathead screwdriver can also work for some cam locks).
  * It is needed to:
    * Tighten the cam locks (round locking fasteners).
    * Secure the drawer slides/runners.
    * Attach the drawer front handles/knobs.

*(A hammer/mallet is also occasionally indicated in the instructions to gently tap wooden dowels into place).*
sources:
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFcdUxB9FxHdKHvgdm9C_btgW6_PATnhQh9wEg2ItxO952gl-IzZ5sQMooN9KsjHcXlnW4uW_YF8GZAbsDd9MdF9GNDnTNWUgPRilK4v4CqThzSzqPH_cm_SXug5HczVAkdbZWgj-KD8i7iRMc3ZBcHbLo6a3OkxJ95V9fuZx-1nWpMxeYTW6HHz1OPWQ==>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFY-MOx7Nzbx9PROuo0JbtCOZrB51YmBE9XbtJP9yHn-sZVfDbu2465vgtIYdwTj9IlR5gZlP9hZD-EVAeAk-NeOyxirn_F4Iz8l1Lk0jRhJB2ZBLFYQ4CG3JwNNWfioua1iJ14vbKtQHxfQtWQBXw7VZfv7LydNJCGSx_a4HYVZlc1vDLtt1KD6n0CHw==>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2S3ibWPvvPB9tpJE4_lD1VSFH5SOI-uRcFAkexeAVP5bqmKFEDpasaNH8Hb5D4Lnv-tOazA9ov2YpjAwfO1Q1SxNOqdUixvjup65jGV0PqX6keUcdE4FAFHCI6IZVbWqSGZHSkgO6mgh8IneWyyw-SP65KXNUEHhHjQiKkZHKT56PCX0fUWCGAW371Vbbd7urkkbTYSClcw==>
  - thomaspark.co <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF38HoaJJmr2YgnVHfWLZVq0WhQb5628jssIX7rNbJrcGdFkX1j58Zj5P8z1F3y-uYnmSQDOMQ0gJMDdmRuq3kYKTbBXPG1REErRdBhMDMwJHkkDZlylo9wpzp3DZNd3r5GEXmu>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGxl7ytMmll_eXQVD8qf7v-fI4GeuM2_6CuXMbXMOUb08ookOO3vWucFKiEzrG3VNHrTqwziwvRHdMXOvAon5e1ZTVGZiA0ws3j1mYZc658NLq3JJEJEBZaHxthXL0w2ITyQHDp8FS4LE2ikLlFXeQ2i-FqeoyYn0P1eUyKWArRc7YiAJSSw0FvWOlYgj_TRYj3onl-MR4=>

[8] web search for 'IKEA GONATT spjälsäng monteringsanvisning verktyg'; grounded search summary:
Vid montering av spjälsängen **IKEA GONATT** (med lådor) behöver du följande verktyg:

---

### 1. Verktyg som ingår i förpackningen
* **Insexnyckel 4 mm** (IKEA artikelnummer: `100092`).

---

### 2. Verktyg du behöver ha själv (ingår ej)
Enligt anvisningens inledande sida (verktygsöversikten) behöver du:
* **Kryssmejsel / Stjärnskruvmejsel (PH2/PZ2):** För att skruva fast lådskenor, lådbottnar och lådknoppar.
* **Spårmejsel (flatmejsel):** Mycket användbar för att vrida och låsa excenterlåsen (de runda metallåsningarna som fäster skivorna).
* **Hammare (eller gummihammare):** För att försiktigt knacka in träpluggarna i hålen utan att skada träet.

---

### 3. Bra att tänka på vid montering
* **Skruvdragare rekommenderas inte:** IKEA varnar i regel för att använda eldriven skruvdragare eftersom det är lätt att överdra skruvar och spräcka trädetaljerna. Om du ändå använder det, ställ in ett mycket lågt moment.
* **Underlag:** Lägg ut en matta, filt eller själva kartongemballaget på golvet för att skydda lacken mot repor under monteringen.
* **Två personer:** Det rekommenderas att vara två personer när sängens gavlar och långsidor ska passas ihop.

*(Om du har tappat bort den tryckta manualen har instruktionen för GONATT dokumentnummer **AA-2261432** och finns tillgänglig som PDF på IKEAs hemsida under produktens dokumentsida).*
sources:
  - youtube.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjMou7omHbVYMxAyGDT-rlK7jsXw1xy9ryL-sCS5JJExELnnh6IWPMCpWjNC3zuxhfKGMhjNhPyG5x1EWY9_eckxJBi-kp6UhGD848sfELyHI2a9HP4pc9dcnJocai8Veh>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqeFmlD4R_dTB0QRxfmuNZQEtU0E0ZbZznE79aCWpCCy8CMFlpLbBxnkhTOJWCTVswDYLTANzkk2Ee7H7BaGxkX7gzZi8bIo9HqcTMZv0pHTXDgpsjz3GUcIRXGZFfJ17c73HJkzeop4u5wNaKQpNN7ccPVARSBcKo-8kCl-Ty-7R2J2hFpWNceGobFTY=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2gVZbyLHybCt09TA4GNv4B6NRZWg-CVNSR-_8LJ2XdVa-OGNxHnLA5L0alkxaw6fqNjTuzUPAsUYS0nPDr8esG1_bKcR8dh7gd_b3C5ANbQTuVTbMqOy-aelMt-IHClPiT-hTkUN29yD2O2rh7xx14u_SnS3WLr_289oi6DuCuXrYMbXil24RdRIpfk4=>
  - ebay.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF85VetAFv8jx1h63ws9L0xmsPqZhuuh6JknPMss-Y2ruJcZ588unxUg8hb0QdhUq5bEabQYfAK2OpyAozwMYYZLmRBdzDIbbYk8SV3vRDAl24gGgji6_0UmNIg>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHB8jc4yPGw64Ul7E2PrndO41pgxGGVWsHNtft2J7FMrup93aea6yZeBoUEJFlmEdR6Oc7Q-nI69SP_odlUgppkG8vr4sjWPnQsEWLOfergAQ_CH_50nWP5kD7Sz0bU4HS4oY4l2miNNllVwI547IjyizKG1-tE6t7lOoUDysj4LvErpGVR5rxjkFkc-qc=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGkauHsN7l7T-gDsy0onVaUZM5Sy6Z8HG5EK8Lu2DKcddDl4ZgOpciBKFV62IIGr5KvO2Q9C24Y-t6sh9qvdVroEW6RVGOlWG7-8pNadAEj4vVoMgQEmdT0r4lsElNaIJwyFfMQLs74Rbf-qr20PWLTqbi-oudnKVz08EV9>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7x5TzQJzt04MSNkEr85GQ7AX4HoBqnL1J_ppDAIT1eQW6HCLFnohOWynJfuIUX3YUI8mcpusuXJ4ayfWs48NQm2FrJPimUBNqBTKoMTRbjF-78kndEy5fYW-spmCkm_gRXIy5fwShOKpfw53OJFXmljrb5W0WNuEJEaCCDk6ni24RzEiSBXW7mmxH2vSSIYxDGYc_v0pfYsg=>

[9] web search for 'GONATT crib assembly "AA-2261432" tools'; grounded search summary:
For the assembly of the **IKEA GONATT crib** (manual reference **AA-2261432** / AA-2261432-2 / AA-2261432-4), you will need a mix of included tools and tools you must provide yourself:

---

### 1. Tools Included in the Box
IKEA provides the specialized hex keys needed for the structural bolts:
* **Allen / Hex Key (Part #100092):** Standard 4 mm L-shaped hex key.
* **Angled Allen / Hex Wrench (Part #195701 / #100001 depending on revision):** A specially shaped/stepped hex tool designed to tighten bolts in tighter clearance areas (such as the crib base and drawer rails).

---

### 2. Tools You Need to Provide (Not Included)
As indicated on Page 2 of the manual:
* **Phillips Screwdriver (Crosshead, size #2):** Required for securing the drawer hardware, drawer front cam fittings, and drawer runners.
* **Flathead Screwdriver:** Helpful for turning and locking the round cam-lock nuts (Part #110630).
* **Hammer or Rubber Mallet:** Indicated on page 2 to gently tap wooden dowels (Part #101350 / #101345) flush into place without damaging the finish.

---

### Assembly Tips:
* **Avoid power drills/drivers:** High torque can strip the pre-drilled holes in the MDF/wood and damage cam locks. Hand-tightening is strongly recommended.
* **Two people required:** As shown in the safety diagrams, having a second person to hold the side rails and mattress frame prevents stress on the joints during alignment.
* **Assemble on a soft surface:** Build the crib on a carpet, rug, or the flattened cardboard box to protect the painted finish from scratches.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2ipMXjis4uR0ibDSqkuMfuRMOtlvuQPfJCrXcAlS9Vhoxia4dEHbjJw1ZYXg8YEEOQ5CdSrT58UNWqpo0WXbGK9-sqT3qRiNMQk9E37s51dUspna3GE0pyYaWYYaX2je15vgS4-atjSyHTuL2M4gslOyN32DYRFtzKq6hLnkEe1-tllmQNo81_fsz_sCvRRJinXAOjkpi0tk=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmc9-tgkfBh9M0OYbx58IPmUtW3CwqGwuc7Z8YJDjOLHfkjWwAhOlpR0c6F6ccXIWAIiAzPhDT3ZdMfJCOVRbwciGT-KGHZG-dhVM_6DwONmDb9lxBgc4V5OuCXz-Dp3xQ5nzDLKeW1ppjIoEvblXT-0-u6rQT4p5oPe67CsCuLXAnhbuYGZhqbdvzaGT4KKBWq2HJugT4>
  - etsy.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp3aLABf1W1pgKMlalJHl-e06TRa2gBkSjwldseErsWTzPvsF5A7lPi7XaRVPX5pKvUMU-ZWDSWSPhbAJda4icQxeK6LSytsuTN1YPCPkGMyx4Nm2epGMOUbCOBy3Fucps5UBQ-W0CWwn8aiv4LXvjDPVNFEKtQFaXPPNcC4Uf8jD7ndrM>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcD3zp0bfFM5sWCNaF35nZ16JVIBZMR_D52V6n0FNu7ptwD70waE8tIj00nRMHJXSg6ZTfGQ6RYnwdN_AuPMJKmJGJCtczjGitUV-cqICCfPy05crlS-ty8pwgsGBS_3zUsAvrdOkI65PEn3lB9htt_gje-mz-Huz5rjlFzDbOYjUSIuQIeXlOGQwKUMqGFh7wyd0cOrnB3uA=>
  - thomaspark.co <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5NfM69HZgbJQCwpooVQoZQ4QwaJUCdkrQsFKH4c_k1X4KA0uioSyAJe_8F_6ey6xOAkuiBaVMxkQFVo4NR7f3TqIOPQf9U529WUd6VRVh3zrlKDe87tmwyG0MRu0FiDQq_oNhSw==>
  - etsy.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7zXZ7NioXcE_z_9vhMfuX_8js3puNauGzx2f_C0iYReCqhvJAUfAqamtHMkiDSHPW_vxRchMyq2iBsyqX-hQPFl2F3rr9ANsMleBgZSxtx0GuYlvAdyhmreZbYYV_qOUGNSMkCgYV7CxMTCP0oa_u013HJ27c-C7zbVsPfXB_WTU=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7TUEcj_IJP2uSV5l_9NH7B9t1tqK7jjEi2x3sXkZKrbeTJRwjus90hYHzo7ieOpWRN0WtEKSt-mPVeW-45BfIKXxk63KsyzwhY-nwH6xxd_Gv3YNI84chr5CTCq_IN_eWH9U8JNn96qWx7oG2XPpJzEqKq2D9tv6UAZ4qmLMXijzWuxprL4GlL5v4jsI=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE7TUEcj_IJP2uSV5l_9NH7B9t1tqK7jjEi2x3sXkZKrbeTJRwjus90hYHzo7ieOpWRN0WtEKSt-mPVeW-45BfIKXxk63KsyzwhY-nwH6xxd_Gv3YNI84chr5CTCq_IN_eWH9U8JNn96qWx7oG2XPpJzEqKq2D9tv6UAZ4qmLMXijzWuxprL4GlL5v4jsI=>

[10] web search for 'manuals.plus IKEA GONATT crib assembly instructions'; grounded search summary:
A step-by-step summary of the **IKEA GONATT Crib** assembly process outlines the procedure documented in the official IKEA manual (also indexed on Manuals+):

---

### Before You Begin
* **Tools Needed:** Flathead and Phillips-head screwdrivers, plus the included Allen (hex) key.
* **Setup:** Clear a large, carpeted or blanket-lined floor area to avoid scratching the painted finish. 
* **People:** Assembly is significantly easier and safer with **two people**.

---

### Step-by-Step Assembly Guide

#### 1. Assemble the Bottom Base & Drawer Divider
1. **Base Panels:** Insert the wooden dowels into the lower divider pieces and attach the bottom horizontal drawer framework.
2. **Drawer Runners:** Fasten the metal drawer runners to the inner walls of the base unit using the small screws provided, ensuring the wheels face forward and toward the bottom.
3. **Cams & Bolts:** Screw the connecting bolts into the base frame and secure the adjoining panels using the round cam-lock nuts. Turn clockwise to lock firmly.

#### 2. Attach the End Panels (Headboard & Footboard)
1. Insert the wooden dowels and connector bolts into the legs of both end panels.
2. Stand one end panel up and align it with the base drawer compartment.
3. Slide them together and tighten the barrel nuts/screws using the hex key.
4. Repeat for the opposite end panel.

#### 3. Attach the Back Slatted Side
1. Align the fixed slatted back wall with the slots/holes on both end pieces.
2. Secure the corners using the long connecting bolts into the embedded metal sleeve nuts. Do not fully tighten yet; keep them slightly loose until the mattress base is aligned.

#### 4. Install the Mattress Base (Choose Height)
The GONATT crib offers **two mattress height settings**:
* **High Position:** For newborns and infants who cannot yet roll over or push up on hands and knees.
* **Low Position:** Essential once your baby can sit up, kneel, or pull themselves up.

1. Screw the 4 metal corner bracket pins/supports into either the higher or lower pre-drilled holes on the side posts.
2. Lower the slatted mattress base into place so the metal brackets catch into the slots on the underside of the base frame.
3. Bolt the mattress frame securely to the corner posts.

#### 5. Attach the Front Slatted Side
1. Align the front slatted rail with the front legs.
2. Insert the bolts at all corners and tighten down all crib connections securely across the entire frame.

#### 6. Assemble and Insert the Drawers
1. **Drawer Boxes:** Fold or connect the drawer sides to the back panel using dowels and screws.
2. **Bottom Board:** Slide the thin drawer bottom panel into the grooves along the sides.
3. **Front Face:** Attach the drawer front using cam locks, then screw in the pull knobs.
4. **Slide In:** Angle the drawers into the lower rails and push until they roll smoothly into place.

---

### Converting to a Toddler Bed (Older Children)
When your child is ready to climb in and out independently:
1. Ensure the mattress base is set to the **lowest position**.
2. Unscrew and completely remove the **front slatted rail**.
3. Install the included lower reinforcement guardrail bar across the bottom front opening using the designated bolts to preserve structural integrity.

---

### Key Safety Checks
* Always ensure all screws and fittings are fully tightened before placing a child inside. Check periodic tightness every few months.
* Use a standard crib mattress size (typically 27 ½" × 52" for US models, or 60 × 120 cm for European models) with a thickness not exceeding the safety limit marked inside the crib end.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFb-sPbLq9evC0cKKUmymwy-v9OQDUQPXeJ7ALOv990DwX59MXYg8i6Ykga-7Q_20tVLrMXAem0tDs9OFwX-T8cgiprssl2GICDdfmDraOLLKVO-LI3DIRHpIvucE4vsrbm6k0n5bwjpXP4N72-I-MJl9R5_dQITuT2OFMqF44Lhy7z1kQLhaZ9naYw2ia9uryn2CAHr23w>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEevkVbFgCMI4MOi7suvuEBHbfC9LSUi_jW2I-gLmfTLDi_L-Z0jSyhOeavWcKTop5kJwRKxgMQwXm_B9H1h5KS_LNepu8eIXZWMIYpcGV0yT0bSKKJqcsaC0JtHKXpKu1BM5CJ7eMIsvucucG4l9CgTnYldN_ZS_m0dNbhIevV2ArFJl7wyH5y4ojvf1w=>
  - youtube.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBIvMQ_8dm1pvxFqCR6BwoMvZYEb43izsNu32wkPvsYZtiFTpErGk43a0rqKqp_dXO_oFGqCzdQWLbN-Tu3Y4V6_kZytAJ6rQPgN1or92Wtcv7O4Itz4n99Cx137xX6b2d>

[11] web search for 'GONATT crib review assembly how to put together tools'; grounded search summary:
### 1. Review Overview

The **IKEA GONATT** is one of IKEA’s most charming and functional cribs, distinguished by its vintage spindle design, rounded corners, and built-in under-crib storage.

* **Aesthetic & Design:** Soft, curved headboards with turned legs and contrasting knobs give it a classic nursery look.
* **Storage:** Features built-in under-bed drawer storage (equipped with drawer stops)—ideal for storing extra sheets, sleep sacks, and diapers in smaller rooms.
* **Convertibility:** Features two mattress heights (high for newborns, low for sitting/standing babies) and converts into a toddler daybed by removing one front rail (the conversion brace is included).
* **Pros:** Very sturdy solid beech and fiberboard construction; great value compared to boutique cribs; under-bed storage without losing floor space.
* **Cons:** Significantly heavier and more tedious to assemble than simpler cribs (like the IKEA Sniglar) due to the drawer rails and hardware; the drawers do not extend the entire depth of the crib.

---

### 2. Tools & Supplies Needed

| Tool / Item | Included? | Notes |
| :--- | :--- | :--- |
| **Hex / Allen Key** | **Yes** | Included in the hardware pack. |
| **Phillips Screwdriver (#2)** | **No** | Required for drawer slides, knobs, and cam locks. |
| **Flathead Screwdriver** | **No** | Needed to align barrel nuts so bolts thread properly. |
| **Rubber Mallet** *(optional)* | **No** | Useful for gently tapping wooden dowels without denting the paint. |
| **A Second Person** | — | IKEA specifies **two adults** are needed—holding the sides while aligning bolts is very difficult solo. |
| **Blanket or Rug** | — | Lay down a blanket to prevent scratching the painted finish while working on the floor. |

---

### 3. Step-by-Step Assembly Guide

#### Step 1: Prep & Separate Hardware
* Clear a wide floor area in or near the nursery.
* Group your bolts, dowels, cam-locks, and drawer slides. Notice that some bolts look very similar in diameter but differ slightly in length.

#### Step 2: Install Drawer Slides to the Base
* Attach the metal drawer runners to the inner bottom partition walls using small Phillips screws before the frame goes together.
* **Crucial check:** Ensure the little roller wheels face toward the **front** and orient them exactly as illustrated in the manual.

#### Step 3: Assemble the Lower Drawer Box / Base Frame
* Connect the bottom shelf, partition dividers, and base frame using the provided dowels and cam-lock fasteners.
* Tighten the cam locks by turning them about a half-turn clockwise with a Phillips or flathead screwdriver until snug.

#### Step 4: Attach the End Panels (Headboard & Footboard)
* With your partner holding the end panels upright, align the dowels and slide them onto the assembled drawer base.
* Insert the long bolts through the outer legs into the internal threaded inserts. Hand-tighten all bolts first before torquing them down completely with the Allen key.

#### Step 5: Install the Mattress Base
* **Choose your height:**
  * **Top position:** For newborns who cannot push up on hands and knees yet (easier on your back).
  * **Bottom position:** For babies who can sit or pull up (safest to prevent climbing out).
* Attach the 4 metal corner brackets at your chosen height setting.
* Rest the slatted mattress frame on the brackets and bolt it in firmly.

#### Step 6: Attach the Side Rails
* Slot the fixed back rail into place using dowels and long connector bolts.
* Slot the front crib rail into place and secure it.
* Once the entire frame is square, go around with the Allen key and securely tighten all bolts (do not overtighten to avoid stripping or cracking the wood).

#### Step 7: Build & Slide in the Drawer(s)
* Assemble the drawer box: screw the sides to the front, slide the bottom panel into the groove, attach the back, and screw on the knobs.
* Tilt the drawer slightly to hook the drawer wheels into the frame runners, then push it closed.

---

### 4. Pro Tips & Common Mistakes to Avoid

1. **Keep the Conversion Rail Safe:** 
   The GONATT includes a flat wooden bottom guard rail used to reinforce the frame when you eventually remove the front side to make a toddler bed. Place this rail, its extra bolts, and the instruction booklet inside a labeled bag taped underneath the drawer base so you don’t lose them 1–2 years down the road.
2. **Leave Screws Loose Until Square:** 
   Don’t torque bolts down 100% on the main frame until all four sides and the mattress base are aligned. Leaving slight wiggle room prevents cross-threading.
3. **Double-Check Drawer Runner Holes:** 
   The most common GONATT assembly mistake is installing the drawer runners upside down or in the wrong pre-drilled holes. Count the holes from the edge shown in the diagram carefully before driving in the screws.
4. **Mattress Fit:** 
   Like all IKEA cribs, standard crib mattresses fit, but IKEA’s own crib mattresses (like the *PELLEPLUTT* or *KRUMMELUR*) are guaranteed to fit the base with no dangerous perimeter gaps.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPb5Q2maXul8SFZHuy2U1PNNlTGgIAWgte9HyKesXkj58-SDyTSKlHBlXdB0w_I7XXVwmlDOfxvUboqVGayi6kHMElUS5VK3oyQr6Q9YxqipMmQzh2feEGzHh4NST2m6BiCg1X2lfrXeQgRY4Ac_LRf8L6XDhVjEg9nA==>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNcGG4PgTcJwMvPvaOG2B307XK3orLDHDYt8thNrUmLht2eMc5tgFSFiqze9chVnjshNQNzGJAnuwqlgWGD8p-g9h_DFNXSAcUXDZ3nYC7JljRc-MUQA1C6ycWfeROr8Jee6gbZw23hEwjHQVoB3kYag9apAfcnmMuG_0zHNt-OsXS4TH88jrmuEfGkzw=>

[12] web search for 'IKEA GONATT crib assembly instructions site:ikea.com pdf'; grounded search summary:
The official IKEA assembly manual PDFs for the **GONATT** crib are referenced by IKEA document numbers:

* **AA-2261432** (most common version, including revisions **AA-2261432-4**, **AA-2261432-3**, and **AA-2261432-2**)
* **AA-2482071-1** / **AA-2445620-1** (newer production models)
* **AA-943776-6** (older legacy production)

---

### How to download the PDF directly on IKEA:

1. Go to **[IKEA.com](https://www.ikea.com)** and search for **"GONATT"** or the article number (e.g., *904.431.35*).
2. Open the **GONATT Crib** product page.
3. Scroll down to the **Product details** section.
4. Click on **Assembly & documents** (or *Assembly instructions*).
5. Click the link to open or download the PDF manual directly.

*(Note: If the crib is out of stock or discontinued in your specific region, switch the country/region on IKEA to one where it remains active, or use IKEA's customer service search tool with document number **AA-2261432-4**.)*

---

### Key Replacement Part Numbers (if needed):
If you are assembling the crib and missing hardware, you can order replacement parts for free on IKEA’s [Spare Parts service](https://www.ikea.com/us/en/customer-service/spare-parts/) using these part codes from page 3 of the manual:
* **100224** – Wooden dowels
* **101345** / **101350** – Metal connection bolts / socket screws
* **110630** – Cam locks / fasteners
* **123492** – Threaded inserts
* **111401** – Drawer/base support brackets
* **147164** / **119245** – Crib rail connection fittings
* **153549** – Barrel nuts
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUyaY9znyuhfzRo1M2MVnBGN2rMNCNRzshxXUHSbXRQHYWL29ozyl80q9LkGOmxb8tH3LCn1ZEHaUZpTuKf5DqYLs-Z7ELTnnHexY8RoVShBpf2w6C9ETRVUf-wdeRPIwopWVEv7PWev0LBOQvBTkoAKK5l0PQjBGM2cZvagC63wNNcHQRILsistgXHrHI1YdvYkL5Z6aJ>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPHjbh1wjrfQsleJImoG6dtynN9-Lk-wEpoHtXPkAMSTi_FT4u_FOgMp0RUsEk6xb7_WUbI6UkV2oJVeR4fzEleWHvVrYVpe0RAbkLLXrqJzBDoWFpq9k8bwtpp-cv60lc7FjDbWOVPpXYLFaEDb-kBPFQ0q1134r6IzErN8cc7PNdxcocrQUvP3OFNVJLSFHZaJFQRXynzDI=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqcUIpQE8g8GRqDBEZheeyuAu5vXOQQlHJUNtTDaL1NqV6H-GV8CyfxH476rfBpjjXhuRucuz9S57KETSX0HqL7LKgVvCZVt0lTnXlg2viYOo2u0Tj5iMPyrzbsucrXeaTf2biaqhezwJcPJf73UAl_-P0M_9l0thsnz-NChZqk4IpLbgeVcKwJ6ED0iaOXZQfRDqLJCv7Lns=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEf5rpq6lAQ0lBNKmdBIQSEEi78p6omdhnUXlz2pdtutVg6-5Jxy1wkZzhuMhe6hOECo-p5Jo6cbVIrK4Vrr9zqrP77iHOTW9jEKfmGKR2JPOkVdKLyzypsEDf9LuWFI_P7bawpoRjtjaWcYQ3iQCSRNyzCHizWrWbpz5DfL28nBWY0CODDzfbqLvDQpcGTuMMDoXEm7o4hiPE=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLN8_WqtKHfiSIxUwuAD1xeH5-Xrei5Ff_PXHgtcQ8J3E6BKEzoNOIf_tMuD61VNMSz1qBJ4mdLZz016_AUySaPrFL5XqL3g8H1vhWDw_cvosJstatna2DbcOpyBzWIEri29L5Vs2iahG2C3MlXl85pfzUYJU9ARIzZLtkraa0C5ATA9KLoAUEFYWkxHFdU1RmHe30uqR9cUU=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5AvoXLnpQxu-CwT4tAnW4o1IxSNFzmjn02_eO5xHrMQMHur3gDiQzTu-hZOCkK6-EEfg2MUurmUY_XQvLYt-aGzRvjNT6CB_OQkKSc4kzkcGbd6V2UJIAMihBYKRW0Hgic7ZDbvuUXNCtNbr6yCiOc8w5NMRxCeTQ4H7c8M97TSw311W6Cg==>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvA7P___quCfFoNWwdJgCcmY9hoHun4tRb6AfYKkU2ZxSg1bM5TB2ZCj_vY06oLwv47-WFwlOGZ0N80vx9Un67mtz5QX-cTbUKWhn1-mbdoszs3NKXtY-evn_C7HC2J2irZIYZ0yeNnbi-_65NxbGgcewqUJ4w5HU3sc4G6UIULo7tNjZtTSFjubkYpwmvyt4XMrv5Z0xLD0uvCOcIvdJa>

[13] web search for '"GONATT" IKEA assembly instructions "Tools required" OR "Verktyg" page'; grounded search summary:
In the assembly manual for the **IKEA GONATT** crib/cot (e.g., manual refs *AA-2261432*, *AA-2482071*, or *AA-943776*), the preparation and tools section (pages 2–3) details the following [PerQueryResult(index="1.1.1", snippet="Page 1. GONATT. Page 2. 2. AA-2261432-2. Page 3. 100224. 101345. 101350. 110630. 123492. 153549. 111401. 147164. 123502. 119976. 119245. 100514. 10x. 4x. 5x. 3x. 8x. 4x. 4x. 1x. 8x. 8x. 12x. 12x. 3x. 4x. 10x. 195701. 105905. 106698. 4x. 110301. 4x. 105657. 4x. 4x. 100092. 1x. 130718. 1. 3. Page 4. 101345. 101350. 101350. 8x. 16. 21. 1. 2. 3. 4. AA-2261432-2.", url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE9OlgNPw4gAKEvfrIsHgVv7DOA0-hNToDNVVrQjzPmqNDFnQ4art-tMDlU5f8A_PJITJVMRDyhgXMRomLYLmbLBRs7JIKGQx3hYdz1_hG9NQnyTvPZbjqe_BuXWgqEJuBaaoC5FZq37TCk3xlwoQcPIhURF0pItqX2Iyri7IlIEPLvwU6NFT1g4V7qWtatK48wBZOYfxJWDy0="), PerQueryResult(index="2.2.2", snippet="IKEA GONATT Crib Assembly Instructions. This document provides assembly instructions for the IKEA GONATT crib with drawer. Parts List. The following parts are included in the package: 10x Screws (105657); 8x Screws (100224); 8x Dowels (100092); 12x Cam Lock (110630); 12x Cam Bolt (119245); 3x Screws (101350); 4x Screws (100514); 10x Screws (123502); 4x Cam Lock Nut (110301); 4x ... Page 2: Shows the tools required (screwdriver, hammer), and illustrates correct and incorrect assembly methods. It also depicts a scenario where assistance might be needed from IKEA customer service. Page 3: A detailed visual inventory of all hardware and components included in the package, with quantities specified for each item. Page 4: Illustrates the initial steps of assembling the crib frame, showing how to connect the side panels to the base and attach the mattress supports. Page 5: Continues ...", url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbq9ip4GbN_o-bPJJeKrQcKSNTBc_Zkgv1THrlO363k7FEkx_FmaFv7Jc4lMJ2n2gbd-igVOypH06aydZAr5E0GbUC6tca9zfm16xOQ0ZYZOilcNidq1HfrvZsXXbAYuN-qcTPfs-j2lh9X5DZiFjK8KNpLXSKGEhqEYDv0MpvvfMvi-Am1-fiwAVlzg=="), PerQueryResult(index="3.3.4", snippet="4x Feet (111401); 4x Drawer Support (153549); 5x Wheels (111401); 3x Drawer Knobs (123502); 1x Allen Key (195701). Advertisements. Assembly Steps. Step 1: Attach the side panels to the base using the provided screws and dowels. Ensure correct orientation as shown in the diagram. Step 2: Insert cam bolts into the designated holes on the side panels. Step 3: Attach the headboard and footboard to the side panels using cam locks. Step 4: Insert the slatted bed base supports into the grooves on the side panels. Step 5: Slide the back panel into the grooves of the side panels. Step 6: Attach the top panel to the assembled structure. Step 7: Secure the top panel with screws. Step 8: Attach the drawer runners to the side panels. Step 9: Assemble the drawer boxes. Step 10: Attach the drawer fronts to the assembled drawer boxes. Step 11: Insert the drawers into the cot frame. Step 12: Attach the wheels to the base of the cot. Step 13: Attach the drawer knobs. Step 14: Final check of all connections. Step 15: Ensure all screws are tightened and the cot is stable. Important Information. Always follow the assembly instructions carefully. Ensure all parts are present before starting assembly. If you encounter any issues, refer to the IKEA website or contact IKEA customer service. Advertisements. Safety Warning: Ensure the mattress fits snugly in the cot. Do not use a mattress thicker than specified to prevent suffocation hazards. Models: 904.670.89, AA-2482071-2, GONATT Baby Bed With Drawer, GONATT, Baby Bed With Drawer, Bed With Drawer, With Drawer. Ask a question about this manual. Ask about setup, troubleshooting, compatibility, parts, safety, or missing instructions. Manuals+ will review the question and use this page\'s manual context to help answer it. Advertisements.", url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF8c2s60OcqZ82MnN1togP9TfC32LlNQE2xOus6wRR1OXJYuwROpZeDZMAAUI5Jam1qrtjvVWj5E9NERzCY3oUh2fVSD9PEdNdoPGAokSg7FixnBA7WaC7r0uOBwMUDGo0XVBdG-xUWly9734NXoqH0rUQbJNgKbwgmt_Ue_KcOdidb1BnLezakXICMJQ=="), PerQueryResult(index="3.4.1", snippet="Page 1. GONATT. Page 2. 2. AA-943776-6. Page 3. 147164. 147168. 102372. 3. Page 4. 4. AA-943776-6. Page 5. 12x. 100347.", url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqOOZs8YCo5G6OsWX3cCkc4UEJVBNn072IqX2xxzr1JRLh3cLfM--mdLXO3E1UccX4tbADV1CQvir6qVBLPSmpTc9niSHZI3h1fNcJ2Izk___g0rO4AZCD_UQUPcfnqFF62dA9k8fW9NP4_6upqaz7VuMy4ejcDsliMWNFBYNtDpTS0ZaQ")]:

---

### **1. Tools Required (Verktyg som behövs) – Not Included**
*(Depicted on Page 2 via pictogram icons [PerQueryResult(index="2.2.2", snippet="IKEA GONATT Crib Assembly Instructions. This document provides assembly instructions for the IKEA GONATT crib with drawer. Parts List. The following parts are included in the package: 10x Screws (105657); 8x Screws (100224); 8x Dowels (100092); 12x Cam Lock (110630); 12x Cam Bolt (119245); 3x Screws (101350); 4x Screws (100514); 10x Screws (123502); 4x Cam Lock Nut (110301); 4x ... Page 2: Shows the tools required (screwdriver, hammer), and illustrates correct and incorrect assembly methods. It also depicts a scenario where assistance might be needed from IKEA customer service. Page 3: A detailed visual inventory of all hardware and components included in the package, with quantities specified for each item. Page 4: Illustrates the initial steps of assembling the crib frame, showing how to connect the side panels to the base and attach the mattress supports. Page 5: Continues ...", url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbq9ip4GbN_o-bPJJeKrQcKSNTBc_Zkgv1THrlO363k7FEkx_FmaFv7Jc4lMJ2n2gbd-igVOypH06aydZAr5E0GbUC6tca9zfm16xOQ0ZYZOilcNidq1HfrvZsXXbAYuN-qcTPfs-j2lh9X5DZiFjK8KNpLXSKGEhqEYDv0MpvvfMvi-Am1-fiwAVlzg==")])*

* **Phillips / Cross-head screwdriver** (*Stjärnskruvmejsel*) – Used for securing the drawer glide runners, drawer handles/knobs, and cam fittings [PerQueryResult(index="2.2.2", snippet="IKEA GONATT Crib Assembly Instructions. This document provides assembly instructions for the IKEA GONATT crib with drawer. Parts List. The following parts are included in the package: 10x Screws (105657); 8x Screws (100224); 8x Dowels (100092); 12x Cam Lock (110630); 12x Cam Bolt (119245); 3x Screws (101350); 4x Screws (100514); 10x Screws (123502); 4x Cam Lock Nut (110301); 4x ... Page 2: Shows the tools required (screwdriver, hammer), and illustrates correct and incorrect assembly methods. It also depicts a scenario where assistance might be needed from IKEA customer service. Page 3: A detailed visual inventory of all hardware and components included in the package, with quantities specified for each item. Page 4: Illustrates the initial steps of assembling the crib frame, showing how to connect the side panels to the base and attach the mattress supports. Page 5: Continues ...", url="https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGbq9ip4GbN_o-bPJJeKrQcKSNTBc_Zkgv1THrlO363k7FEkx_FmaFv7Jc4lMJ2n2gbd-igVOypH06aydZAr5E0GbUC6tca9zfm16xOQ0ZYZOilcNidq1HfrvZsXXbAYuN-qcTPfs-j2lh9X5DZiFjK8KNpLXSKGEhqEYDv0MpvvfMvi-Am1-fiwAVlzg==")].
* **Flathead screwdriver** (*Spårskruvmejsel*) – Useful for turning cam locks into locking position.
* **Hammer / Rubber mallet** (*Hammare / Gummiklubba*) – Indicated for gently seating wooden dowels into pre-drilled holes [PerQueryResult(index="2.2.2", snippet="IKEA GONATT Crib Assembly Instructions. This document provides assembly instructions for the IKEA GONATT crib with drawer. Parts List. The following parts are included in the package: 10x Screws (105657); 8x Screws (100224); 8x Dowels (100092); 12x Cam Lock (110630); 12x Cam Bolt (119245); 3x Screws (101350); 4x Screws (100514); 10x Screws (123502); 4x Cam Lock Nut (110301); 4x ... Page 2: Shows the tools required (screwdriver, hammer), and illustrates correct and incorr
sources:
  (none)

[14] web search for '"GONATT" spjälsäng monteringsanvisning "Verktyg" skruvmejsel PDF'; grounded search summary:
För montering av **IKEA GONATT spjälsäng** gäller följande avseende verktyg och monteringsanvisning:

---

### 1. Verktyg som behövs

* **Kryssmejsel / Stjärnskruvmejsel (ingår ej):**  
  * Behövs främst för att skruva ihop lådorna under sängen, montera expansionsbeslag/lådskenor samt fästa knoppar/handtag.  
  * En standard **PZ2**- eller **PH2**-skruvmejsel rekommenderas.
* **Insexnyckel (ingår i förpackningen):**  
  * Medföljer för att dra åt sänggavlarnas och sängbottnens genomgående bultar.
* **Ev. gummiklubba / plan yta:**  
  * Kan underlätta vid nedpressning av träpluggar (använd aldrig metallhammare direkt mot träet utan skydd).

---

### 2. Monteringsanvisning (PDF)

IKEAs officiella monteringsanvisningar har dokumentkod **AA-2261432** (eller tidigare **AA-943776** beroende på tillverkningsår).

* **Ladda ner via IKEA:** Sök på produktnamnet **GONATT** eller artikelnumret (t.ex. *605.441.45* eller *002.579.53*) under avsnittet *Montering och dokument* på [IKEA.se](https://www.ikea.se) för att ladda ned originalmanualen i PDF-format.
* **PDF-visning online:** Du kan även se och ladda ner instruktionsboken direkt via manualdatabaser såsom [Bruksanvisni.ng – GONATT PDF](https://www.bruksanvisni.ng/ikea/gonatt-60544145/bruksanvisning) eller [Manuals.se](https://www.manualsearcher.com).

---

### Viktigt vid montering av GONATT
1. **Två höjdlägen:** Sängbotten kan placeras i två olika höjder – välj det övre läget för spädbarn och det nedre så fort barnet kan sitta upp.
2. **Ombyggnad till småbarnssäng:** Den ena långsidan kan monteras bort när barnet är stort nog att klättra i och ur själv (se sista sidorna i manualen för hur täckbrädan monteras).
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXFyrDfC9sHICHN0r4NnoloVWpwo9dZyUb7odVRIFufosuxQ1532_ugZDKnQCU1ZH_MFSZuVitT3Alespkgn1bUs4vbYlFdEyAN9qhoCYr2OSJV5oobYkZdk3u6Rf6Od3kxWRaqcxekp-eX1Fen9L6HWzKCyRUnbvgFooMyRLbRpdsMsB_JqETe9Jz-P6P6zBfURUvxOVRwA==>
  - youtube.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFooJbOicZ0wpcpx3N32F1Iry_HBUk8jqZdD9GL7erY7_0RsPdGJwbbNi1M9_659HOEEegJEH4gtI7jXDuNyCN0sGZ3VcmVQ-9ocS8S1YmYrugvH3MFX61NxGQVCLey7TE=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4e_bSxc-_mxOviy7Ij11kVxuzIemmU9nc2WeLLCV0NqfDRmZLO5cQnYNlgCFv1LlIa5ZrmsN-jmdgwIySs_tiWUh8ODUwtXF78p9noio1y6cgshL4E27eBRA2mRHhFjd3D9U991JvTTki_RR65TdPWcDPNiGc3nxyiRCFaDyBUY5UG2_y>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrk2kEqCknSYlphFSLrR5AAgaEZNK1qjYPz5_AsqtG0J1xcP0OqaqfFKplWKkFZ6aAZhTovUWTXNlTJ182I1zgvwsx1FhNEjBS1aYQiqN7J8WBGK355Crokhrzcs1MNkGirHJbFOix4gd15m5P0MiNz-aHX9sphGLIlDisMlOFUIF94QiU2l6yPCpW2CyCmwAmoH0jsAE=>
  - bruksanvisni.ng <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEaycKHvUvHpZC5EJGhXrF-9NUtUH4ga1f6eWaXa61YFa_7A4tEyIXvUmAeFhb719Rk4Lcz2G1f51uGnUGteHrVLIhRBwwvvG2DOpDWBjnYqwZ_PIDjqkH-TobVGMKiCp-k2hYZ1yhHMHVZzDwh7FEWxtZRQ==>

[15] web search for '"GONATT" crib manual "screwdriver" OR "hammer" tools page 2'; grounded search summary:
In the **IKEA GONATT crib assembly manual** (manual references AA-2261432 / AA-943776), **Page 2** illustrates the standard preliminary instructions and required hand tools not included in the box:

---

### **Tools Shown on Page 2**
* **Screwdriver:** A **Phillips / cross-head screwdriver** is depicted as a required tool for tightening cam locks, drawer runners, and corner brackets.
* **Hammer / Mallet:** A **hammer** is depicted as recommended for gently tapping wooden dowels (such as parts #101345 and #101350) flush into their pre-drilled holes.

---

### **Tools Included vs. Needed**
* **Included in the box (shown on Page 3):** 
  * 1× Allen / Hex key (Part #195701).
* **Required from home (shown on Page 2):** 
  * Phillips head screwdriver
  * Hammer / mallet

---

### **Other Guidance on Page 2**
* **Two people required:** Graphic indicating two adults should assemble the crib.
* **Protective surface:** Instruction to assemble on a rug, blanket, or cardboard to avoid scratching the finish.
* **Customer support prompt:** The IKEA "person with a question mark and phone" icon for assistance if parts are missing or guidance is needed.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKWCvqor-0D9ft_2qsM5NowuKCwlB820wXHEqeI3kpUQQHVVns0VFW12EXozuiDoGyV99vx-pnQvZwrnYCxO3xsCNgkvYXfOBC2FyErevJBx1z8ZjtobT83nHvgAoyVokpa-gDUat5n7pL4X4ZtVFlstQ7xbHEMofCluN4qZWYGMMbgW_T1AVdJHV1B2p8vYyL7yAK5USw>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGh4waJJF_pJHPQa7FQY9fbPfGgYYaTtuhTfrnPQwM4GymHKZN7Pfwv9fZIqf5-V-z7TFdVCZLx1O5Y-ouj0CbWamhq0ryN8QCI00gtMRQoM85zF5xb7EOvvPfYeheKNanfXYvl-fmq2w5xnFvX9LoD843aD2obtSJGV8wz8QqbN6LjHdG1F0v3h6UUkIAlpv9Csp-bAM9gCco=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHuSGQwaDxmwP82JS6QMB-CSogQ4pd8ZtWVkOqNQfOxAMXUt4tPJoOjdXb7HqqTFBi4mmDyw_gIpHgMEb5wnyCywTsyZ0Fj0M9O6rxdNDHy2LvN0s8dF0ftjndNSf6JLTmsVMQ4qB44kfIoeuRhJ_DMMeL0URZGXgxpdAidz_qldzojxjR5lFeauesEdjs=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2LL3Ku9PoGoSJ2PEtv-ftLvEImbHCWjtHJfNdopMoGETXTd8XlMB0SE3ragvl3Dq6ThJWR_J_f3GNDi5fll8w4xtOV9D0uWwIgAdIKuvBfzs7ZwoJEHLCR6GEuylrNDtOApbww4sA7nFzkJHlkj_Xvk_c4N8OpYHGo84sob41970jXKrT8Qi3cNXkkEQ=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdRo1tkXv2Z79hOKFeNyUCsgWBMzb_-Z-59DMPKoX3TpUYPDdlFc1sIQReTP5krg6J3tXqrPGG-iKbpf4iJ9xwSFripzalvVTCjCxL66htUetmOD5G-IFwBWqarReSFXrso1l4MOESttdbR9lhC1R0yJ8oo_9pY7UT>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2LL3Ku9PoGoSJ2PEtv-ftLvEImbHCWjtHJfNdopMoGETXTd8XlMB0SE3ragvl3Dq6ThJWR_J_f3GNDi5fll8w4xtOV9D0uWwIgAdIKuvBfzs7ZwoJEHLCR6GEuylrNDtOApbww4sA7nFzkJHlkj_Xvk_c4N8OpYHGo84sob41970jXKrT8Qi3cNXkkEQ=>

[16] web search for 'ikea gonatt-crib assembly_instructions AA-2261432 pdf'; grounded search summary:
The assembly instructions manual for the **IKEA GONATT Crib / Cot with Drawers** is documented under IKEA code **AA-2261432** (published in revisions AA-2261432-2, AA-2261432-3, and AA-2261432-4).

---

### PDF Manual Links & Access

* **Direct Official PDF Downloads:**
  * [IKEA GONATT Crib Manual (AA-2261432-4)](https://www.ikea.com/us/en/assembly_instructions/gonatt-crib-white__AA-2261432-4-2.pdf)
  * [IKEA GONATT Crib Manual (AA-2261432-2)](https://www.ikea.com/us/en/assembly_instructions/gonatt-crib-light-gray__AA-2261432-2-2.pdf)
* **Alternative Mirror / Online Viewer:**
  * [Manuals+ Online Viewer for AA-2261432](https://manuals.plus/ikea/aa-2261432-2-100-gonatt-cot-with-drawer-manual)

*(If the PDF links do not automatically start downloading, search for product number `304.670.87` or `904.670.89` directly on the IKEA website under "Product details" > "Assembly & documents".)*

---

### Hardware & Spare Parts List (from Page 3)

If you are checking for missing hardware before assembling, or if you need to order free replacement parts from [IKEA Spare Parts](https://www.ikea.com/us/en/customer-service/spare-parts/), refer to the standard hardware codes from manual AA-2261432:

| Part Number | Description / Type | Quantity |
| :--- | :--- | :--- |
| **101345** | Large bolts (end panels) | 4x |
| **101350** | Bolts | 8x |
| **110630** | Connecting screws / barrel nuts | 12x |
| **123492** | Bolts | 12x |
| **123502** | Screws | 8x |
| **100224** | Wooden dowels | 10x |
| **111401** | Wooden dowels (long) | 5x |
| **153549** | Metal pins / shelf supports | 4x |
| **119245** | Drawer runners / brackets | 4x |
| **147164** | Screws for runners | 4x |
| **119976** | Drawer divider screws | 3x |
| **100514** | Cam lock screws | 4x–8x |
| **105905** | Cam locks | 4x–8x |
| **195701** | Drawer screws / fasteners | Multiple |
| **100092** | Hex/Allen key | 1x |

---

### Assembly Overview (28 Pages)

1. **Base & Drawer Section (Pages 4–10):**
   * Assemble the bottom drawer compartment frame using the dowels (`100224`), cam lock screws (`100514`), and cam locks (`105905`).
   * Attach the metal drawer slide rails (`119245`) to the inner uprights.
2. **Crib Frame (Pages 11–15):**
   * Connect the headboard, footboard, and side rails using the long barrel connectors (`110630`) and bolts.
   * **Mattress Height Selection:** The manual details two height configurations:
     * **High base:** Recommended for newborns until the child can sit independently.
     * **Low base:** Lower the support brackets once the child is mobile to prevent climbing out.
3. **Drawer Assembly (Pages 16–21):**
   * Construct the 3 bottom storage drawers and install the drawer front hardware.
4. **Toddler Bed Conversion (Pages 22–26):**
   * Shows how to remove one slatted side and install the included lower safety support board once the child is old enough to climb in and out independently.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4K6psw9ngXQGyu8bq5ZxkXEc4bP7fmfrKZsjoztiVLpdvG1NIFROUXq4B0ml9lYNOJ5EE9d0hv2R1-MFmcafAuirbKDsoqJM6fFZno3Z-ZLGT4s-6I0qyXoYGXsBFgCpnlxv4UUkO79ZQBZWjy4SbtFvT1ysiu35BmM1OryrCtpCkZVe84ZSYIL9yTRFlutVwu736j__r2g==>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOkW9Q9ym3LeTyQJZNSxarjg0XVAgkdbhET6qilMjxFdi0YaQW642z5gQuy-w_WwKniMqlliWzYkqsSxELnaeLoNl8QEQ6I4SW7CGT89K0aWjuA7v7dfg2CrI111ayJkmdBulvuKq0t177fsEdlrRPqoiVyj4o6UgL4QB0cZoLuOcg6i0KbUZiGSY_lIPiheorSJ5rjJY=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAEL6-9Jy4Af5qO6I3J6Kgur2APEpKJvLfcnJ-fEOY9y6wKNpmZRl03LlUNIIsn9tjmdyOfte4VzXv89fhOVabVPRweq7KcsE1uMp0fiCvOAbj3cAo8EUrgi8Tn_QpjfB-PCZ9IxIZjcbwLJwDU5tXhTZC10JVWFGA6p3RJr_pcmi9b83P8HhUIiv9-laIi2eC9nPc5zJN_w==>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1PkAWFCta4H4vvEvpFd4GxNIDkfjdtc-T2tTKetyO8fR-OGvNfrFUdRo5t6sKNN1WvFiyll5nUm2OjmwmMpL3_g6SNdeX4aKr6WeZCKRABZJfw5z9Gxfx31PBBPwAPplQi9OcQhv2CdunAsY1a3X8yyka1po4nHl824RYmA==>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG3OihVnmnFht-xtP-QiT9eYTNBET_S7OecZ0B5weDMW8439GkMxRFt2kQVtzVNgvjNcz7ehgUqVcOH_VYAnhZ_ysYVauCNRBlp3j0Poxq_Vh1nqbjjkVFBF6zjOGmuo_5eROJkIIw5jzBAQqTi7g==>

[17] web search for 'IKEA GONATT 304.670.87 assembly instructions tools required'; grounded search summary:
For the **IKEA GONATT Crib / Cot with Drawer** (Article No. **304.670.87** / Manual **AA-2261432**), the tools and assembly requirements are as follows:

---

### **1. Tools Included in the Box**
* **4 mm Allen Key / Hex Wrench** (IKEA Part #100092 / #100001) – Used to tighten the primary frame connector bolts and mattress base brackets.

---

### **2. Tools Required from Home (Not Included)**
* **Phillips Head Screwdriver (Crosshead, typically #2 / Pozidriv):**
  * Required for assembling the drawer runners/casters, securing the drawer bottom brackets (part #106698 / #10151990), and attaching the drawer knobs.
* **Flathead Screwdriver:** 
  * Required to rotate and lock the circular cam locks (*minifix* cams) in the drawer assembly and bed base frame.
* **Hammer or Rubber Mallet (Recommended):**
  * Helpful for gently tapping wooden dowels into pre-drilled holes flush without denting the wood.

---

### **3. Key Assembly Advice from the Manual**
* **Do NOT use a power drill or electric screwdriver:** The manual displays a crossed-out drill icon. Power tools can easily strip screw holes or crack the fiberboard and solid beech parts.
* **Two people required:** Due to the size and weight of the crib's side panels and headboard, two adults are recommended for safe assembly.
* **Assemble on a soft surface:** Put down the cardboard packaging, a blanket, or a rug to prevent scratching the painted finish while assembling panels on the floor.
sources:
  - thomaspark.co <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZMkncOBho8_i-kkEacc5l8Tl-vF7BTDow61nUqPkgokA4dJwWdDf6QEEGptjDsotT_lPFkv_7vXINLRWbHqAj3z-Dp-M8uaWWFhzVvO_bxm7CbrXZt_POHtXsUNESz-0BlaBA>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEruMiHsmMgEgPNxmkh3IpWPwcfVG0BGgaNo_deLl0LehfBHtEUMJC31RrXpIXdgIpwZCQwEE2aZ-DanAs5KhtWeDWDs4B6IQp9OYx5bsJDIloaBdg3BTKuoYCB9QC2qODgNwZv0hsIBeMWLiDzQuy3TtP2VkNhz1AD2T-9R4LfbGcJVwYeAafNp2Ie6Ds3O1tkjYWY46kuHA7c1Ew=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExU5wQ8dxtXonYy8hTcY8lN02Tj6gley80m0OWD5AeIZloMHTj9snbci7flCuWSBcPl20rjIgF228OBROYIXstHiSJCg8x1OUPgDoWY5Ie6-ytCCCM5e7ANZ_KD2xTSYnVO6WwPp36q_lfjVVcEZN0ujSaiCQuK2Oq1GI9-BW4_mK58Q7vwJ6qz4BcOK4pJjJgLlFnIVWQ>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqeJjhxxiwnM8wzCc0tiUOjhWbPU1i7rUgmVLfAD7-mn4qG-gGtQu20fLkz4GoaMyyUTYMOT9u7Ic16u0E_Yoc9CrleL3E95PSN8XYdmPGz0PtreuQqK5kn1quPr7b4rqZzhMlin83JFHeyKiJQ-UtUSHVH3QqLp11n8iGN9QaBhm29CsBd2ciNdIpz1k=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnCk41hbkza05vzMpW3Bay9snIfZlBcT2T7uwPyJKBMyLouf2RW9T4CXab1JoRoc_4mjel5qXqOsnYJZVWiwE5Eu88WSieDL2hqdGSX_LTKFZMasUNnEchY6-N1ferY_hWZrdtZDLissdWhNTaQuU1Zc9hUkDaVWzfXor8LKevcCVabZ05xxmnrY6UEeY=>
  - shein.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPxGvORNGUjYj1ox3-R12IGBtPBzBw5jFiGZ0qtd5DSlrPoCYFwI-5xUs81i6g3ARXbvTSNlWpzoxtxkMmxe-_CIt78MB3_q46bL6yDMF9LxjE2isFIU1CEybRENtjahls4yyGWoK2_eTfnCMRXAF93NcAdbt-kvKg-xGsq8q8inOz1lEWMd9mJp1xoylZvQ6Zv-E4i-uW_U6saZQQxUrQGqqpk6P_H0NnlD7ubLV_cM0t6JxYIPvRB9yUdRDWzg-W-Xid6m0eorniuA==>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxxhnFDrC-306dS-7i5NJbrRjid_RDhyc4zWexf5tIR_TSb1dCib4untB2OQeHa2EzkDrIa4i9Wh2KkFXYUsUANQsZwDbv35y4t44lr3o3WIMQv5xEYPRPt5ZbGlftXE3uKOgeeAQFIUWvBHrtFHWg8bSbWeFqK9wNNX1hFKyxS8AJlBqbGi4mZYRK-hw=>
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU920guUHA0Tbp08Py407jae7F7ZreixMMzHuRa2eXFDMtvJZGUHOKkX1y0ionO8wlD1MwhMmSbUNusEn80yIjx_s57I-bgBs_Dk_xkvDVxZlWina3UpEw-D8DoIVs-A9_ERS5AR4045K6u2Yp6TRplasMhfzuSrMSag==>

[18] web search for 'manuals.plus AA-2261432-2 gonatt cot with drawer manual tools required screwdriver hammer'; grounded search summary:
Based on the assembly manual for the **IKEA GONATT Cot with Drawer** (Document code: **AA-2261432-2**):

---

### **1. Tools Required (Not Included in the Box)**
* **Screwdriver:**
  * **Phillips head (cross-head) screwdriver:** Required for attaching drawer runners, brackets, and securing screws.
  * *(A flathead screwdriver is also useful for aligning cam locks/nuts)*.
* **Hammer / Mallet:**
  * A standard hammer (or rubber mallet) is needed to gently tap wooden dowels and corner joints into position flush with the wood without damaging the finish.

---

### **2. Tools Included in the Hardware Pack**
* **Hex / Allen Key:** (IKEA part #100092 / #130718 / #100001) for tightening the main structural bolts and frame fasteners.

---

### **3. Key Assembly Notes (From Page 2 of the Manual)**
* **Work Surface:** Assemble on a soft, clean surface (such as a blanket, rug, or the flattened cardboard packaging) to avoid scratching the painted surface.
* **Two-Person Job:** Having two people is strongly recommended when holding and aligning the crib side panels and mattress base.
* **Dowels & Fasteners:** Make sure wooden dowels are fully tapped into place before joining panels together to prevent wood splitting or misaligned gaps.
sources:
  - ikea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo9kVVsrWXFBGjlxkQGNqMWI1ZxGINwH5Tb_0Eu3po_yL7W1pqD7y2IfQmfPCZG7r0tx0HgzHWURIj0T7yJcptxlviVNdkBOZUgHDfL4kcYVZPgV_vQzoKRaPg1LkrpP-XZATGuWhHOVmL5gLLYmAQt_ew4Dv14HMzB93HtrvgGMZ9Sip5RGc4UxKGc0Siw2LAjSVEFMLwrN8=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlH2YcDrlhvEh2xF9h2ElcYrwQ5XmqUn7gw3W1w6FEel4ceeAJ6wQrImVEgOiAbp-EyJlK5925DaJH7mliLCqkmPP-LgKz1BM7WbbNugZtgRUKmSvq-mmFVQq3wLhlUEIh7pG0A-8VWRNXrr4g7oOX5Me0qq45xEx0E40cnwk=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp2bAZoZoIKsI_EnyUnRVqdlD7y8pxTMRKFMKmbOKrhiLPhQgNuJACb9QEqAr_b6uX_u4MCIHkKIorwStuHSFARc_9qM9e4q7hQGUq-hCn1k1dPODwgtAGXs8YIWsLdwepQy9V5YxBg_Qk66j7vZI_YwhMsMAB5WLEi8drzF9aMt3RJtwqoxFIH6jp5v4=>

[19] web search for '"GONATT" crib assembly video tools needed hex key screwdriver'; grounded search summary:
When assembling the **IKEA GONATT crib** (which features built-in lower drawers and an adjustable mattress base), having the right tools prepared in advance will make the process much smoother:

---

### 1. Tools Needed

* **Hex Key / Allen Wrench (Included):** 
  * IKEA supplies the standard L-shaped hex key (part #100092 / 4 mm) inside the hardware pack.
  * *Tip:* If you have a ratcheting screwdriver with a 4 mm hex bit or an Allen key with a T-handle, it will significantly speed up driving the long frame bolts.
* **Phillips Head Screwdriver (Not Included):** 
  * Required (size #2 is standard). You will need this for the drawer runner screws, drawer pulls/knobs, and cam-lock connectors.
* **Flathead Screwdriver (Helpful):** 
  * Useful for turning or aligning barrel nuts and cam locks into the pre-drilled holes so they properly catch the bolts.
* **Rubber Mallet / Light Hammer (Optional):** 
  * Helpful for gently tapping wooden dowels all the way in without damaging the wood or paint.

---

### 2. Key Assembly Steps & Overview

1. **Pre-Sort the Hardware:**
   * The GONATT contains several bolt lengths and screw sizes for the drawers and frame. Separate your dowels, drawer screws, and frame bolts before starting.
2. **Build on a Soft Surface:**
   * Assemble on a rug, blanket, or the flattened cardboard box to prevent chipping or scratching the painted finish.
3. **Assemble the Lower Drawer Enclosure First:**
   * Install the drawer runners onto the lower frame panels using your Phillips screwdriver. Pay close attention to the orientation arrows shown in the manual.
4. **Choose Your Base Height:**
   * **High Position:** For newborns and infants who cannot sit up or roll over yet.
   * *
[evidence truncated]
```

</details>

**Answer:**

## Short answer

I could **not confirm the tool list from the manual itself**. Two independent attempts hit the same wall:

- an internal document matching the manual exists, but the tool-list page is not text-extractable, and
- the public search found the manual's identity and URL pattern, but the tooling available to that search could not open the PDF.

So I have to be straight with you: **the specific list of tools printed in the GONATT assembly instructions is unverified in this session.** What follows is what is actually supported, and what is not.

---

## What we checked, and what each source yielded

| Source | Type | Finding |
|---|---|---|
| `gonatt-crib-with-drawer-white__AA-2261432-4-100.pdf`, knowledge base "Crib Assembly" | **Internal retrieved document** | The document exists and is confirmed as the GONATT crib-with-drawer instruction sheet. Its parsed content contains only fragmented part numbers and quantities (e.g. `4x`, `2x`, `1x`, `10006B`, `1059`, `19570`, `105657`, `11065`). A targeted query for "tools", "screwdriver", "wrench", "tools required" returned **nothing** — the answer "is not found in the dataset." |
| IKEA product page — `https://www.ikea.com/us/en/p/gonatt-crib-with-drawer-white-30467087/` | **Public (primary vendor page, not opened)** | Identifies the product; assembly documents are published under the page's "Assembly and documents" section. |
| Assembly-instruction PDF URL pattern, e.g. `https://www.ikea.com/us/en/assembly_instructions/gonatt-crib-anthracite__AA-2261432-4-2.pdf` | **Public (primary PDF, not opened)** | Confirms an official GONATT instruction document **AA-2261432** exists (revisions ‑2, ‑3, ‑4 cited). Content not readable by the search tool. |
| `https://manuals.plus/ikea/aa-2261432-2-100-gonatt-cot-with-drawer-manual` | **Public (secondary)** | Described page 2 as "Shows the tools required (screwdriver, hammer)." |

## The one recurring claim — flagged as unconfirmed

Secondary and AI-summarised sources repeatedly state that page 2 of the instruction sheet shows:

- a **screwdriver** (cross-head/Phillips; a flathead is occasionally mentioned for cam locks) — **not included**
- a **hammer** (some sources say rubber mallet) — **not included**
- an **Allen/hex key** — **included** in the box

I am deliberately not presenting this as fact. The same search returned contradictory summaries — one described part `111401` as simultaneously "4x feet" and "5x wheels"; another described `130718` as both a "hex key" and an "M6 bolt." Auto-generated summaries that self-contradict cannot be treated as a reliable quote of the manual.

## Document identity (as returned by search — treat version as uncertain)

- Instruction document: **AA-2261432** (revisions ‑2, ‑3, ‑4 cited)
- Internal file confirming the ‑4 revision: `AA-2261432-4-100.pdf`
- Product article numbers: **304.670.87** (US, crib with drawer, white), **904.670.89** (70×140 cm)
- Other numbers also surfaced but unconfirmed: AA-2482071, AA-2629396, older AA-943776 (‑6). **No reliable print/version date was returned.**

---

## Missing information and failures

1. **The manual's tool list is not readable from either channel.** The internal copy's tool page appears to be graphical/illustrative and was not captured as text during parsing. The public search tool returns synthesised summaries and links but cannot open or OCR the PDF.
2. **No verbatim quote is available.** I will not fabricate the heading wording ("Tools required" / "Verktyg som behövs") or the exact list.
3. **Version ambiguity unresolved** — four different document numbers appeared in search results, and I cannot say which is current for a given market.

## Suggested way to close the gap

Open the GONATT product page above → **Assembly and documents** → download the AA-2261432 instruction PDF and look at page 2. If you upload that PDF here, I can read it with the file tool and give you the exact tool list verbatim. Alternatively, if the graphical page can be re-parsed (OCR) in the "Crib Assembly" knowledge base, the answer may be recoverable from the internal copy without going public.

---

## 14. route-08 (routing, easy)

**Question:** What installation hardware does the Midea U air conditioner installation guide we uploaded list as required?

**Gold answer:** The guide's required-hardware table: 1/2" Type B screws (2), 1/4" Type B screw, main bracket, main support pin, cotter pins (2), 1/2" Type A screw, open window brackets (RH and LH), side arm foam.

**Route:** expected ['ragflow']; delegated {'Network Search Agent': 1, 'RAGFlow Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[1] tool ls returned:
No files found

[2] tool glob returned:
No files found

[3] tool ls returned:
No files found

[4] tool ls returned:
No files found

[5] tool glob returned:
No files found

[6] tool ls returned:
No files found

[7] tool ls returned:
No files found

[8] tool glob returned:
No files found

[11] knowledge base 'Air Conditioner Installation Assistant' answered:
Yes—the knowledge base contains an installation guide/manual for Midea U window air conditioners.

- Document title/filename: “Midea U AC Installation Guide.pdf” [ID:0]
- The guide is titled “Installation Guide” and covers “Window Type Air Conditioner,” with models “MAW08V1QWT MAW10V1QWT” and “MAW12V1QWT” [ID:0]
- Page identifier in the extracted content: “Page 2” [ID:1]
- The document references customer service at “1-866-646-4332” [ID:0]

Required Installation Hardware (verbatim table items and quantities as shown):

| Item | Quantity |
|---|---|
| 1/2" Type B Screw | 2 |
| 1/4" Type B Screw | (blank in table) |
| Main Bracket | (blank in table) |
| Main Support Pin | (blank in table) |
| Cotter Pin | 2 |
| 1/2" Type A Screw | (blank in table) |
| Open Window Bracket - RH | (blank in table) |
| Open Window Bracket - LH | (blank in table) |
| Side Arm Fam | (blank in table) |

These are listed under the section heading “Required Installation Hardware” [ID:3].

Additional optional installation hardware/accessories listed (verbatim items):

- Window Sash Lock
- Thick Window Sash Seal Foam
- Thin Window Sash Sea Foam
- Miscellaneous Sealing Foan
- Additional Side Arm Foam
- 1" Type A Screw

These are listed under “Optional Installation Hardware” [ID:1].

Also verbatim mentioned in the guide: “Use the provided 12 Tye A screws.” [ID:0]
retrieved chunks:
  - (Midea U AC Installation Guide.pdf) 
TOOL &HARDWARE
1. INSTALL THE SUPPORT BRACKET
! WARNING
Bracket should only be used for its intended purpose.
· You must follow the detailed installation instructions in the user manual
theright exte.
 WARNING
 WARNING
Metanthebrcketuntil
1.2  Adjust the
hthgled siportla.rmhseckthat tdoors. lnsta and right extension arms.
 WindOw reQuireMents
Installation Guide
Window Type Air Conditioner
Models
MAW08V1QWT MAW10V1QWT
detailed installation instructions
MAW12V1QWT
Before using your air conditioner, please read customer service at 1-866-646-4332.
3.4Extendbothw
1. INSTALL THE SUPPORT BRACKET (cont.)
 THE WINDOW3.SEALANDCLOSE
sashlock
Use the provided 12 Tye A screws.
1.3 Secure the bracket to the
ure, cut and install the side arm foam
NOTE: Drill 1/8" pilot h Screwing into thewindwsr.
of each extension arm as shown.
WARNING
Holes at the end or bottom of the Extension Arms can be used to secure the Support Bracket to the window.
 2. SECURE THE UNIT ON THE BRACKET
2.1 Set the air conditioner on the sup fold down the side arm hinges.
FAQ  Why does the air conditioner not start?
3.2 Secure the anti-tip brackets into the
- Wall plug disconnected. Push plug firmly into wall outlet.
 WARNING
 House fuse blown or circuit breaker tripped. Replace fusewith timdelaytyp
 Do not leave the unit unattended during instalation.
Remove the factory installed 1/2
reset circuit breaker.
Check if the light on the plug is on. If it is off, press the RESET button - Power is OFF. Turn power ON.
led 1/2
coulddamagethe
FAQWhy is there noise during cooling?
nustinstalltheOpelnWindowBrackets
- It is normal to hear airflow, set to a slower fan setting if too loud.
A WARNING
Window vibration - poor installation. Refer to installation instructions or check with installer.
Failing to do this could cause injury or property damage.
ect to wifi or App doe.FAQ  Unit will not co
 WArnING
 For additional support and troubleshooting tips,
  - (Midea U AC Installation Guide.pdf) idea
Optional Installation Hardware
Window Sash Lock
Thick Window Sash Seal Foam
Thin Window Sash Sea Foam
MiscellaneousSealingFoan
 Additional Side Arm Foam
1" Type A Screw
this manual.
Page 2

  - (Midea U AC Installation Guide.pdf) 
buame
follow the link in this QR code.
Jse the thick window
serious injury.
the windows
3.3
the
Ianygapsbetw
window and the air conditioner.
  - (Midea U AC Installation Guide.pdf) <table><caption> RequiredInstallationHardware</caption>
<tr><td></td><td  >1/2" Type B Screw</td><td  >2</td></tr>
<tr><td></td><td  >1/4" Type B Screw</td><td></td></tr>
<tr><td></td><td  >Main Bracket </td><td></td></tr>
<tr><td></td><td  >Main Support Pin </td><td></td></tr>
<tr><td  >CKK</td><td  >Cotter Pin </td><td  >2</td></tr>
<tr><td></td><td  >1/2"Type AScrew</td><td></td></tr>
<tr><td></td><td  >Open Window Bracket - RH </td><td></td></tr>
<tr><td></td><td  >Open Window Bracket - LH</td><td></td></tr>
<tr><td></td><td  >Side Arm Fam</td><td></td></tr>
</table>
  - (Midea U AC Installation Guide.pdf) Right
Arm
zontal Bracket
Doependngonte
either location below
to chec
level
 Center this part of the
nte
 of the windows.
Spring Pin Locks

  - (Midea U AC Installation Guide.pdf) Top view
Top of Unit

[12] web search for 'Midea U-shaped window air conditioner installation manual hardware parts list'; grounded search summary:
The hardware and installation parts included with the **Midea U-Shaped Inverter Window Air Conditioner** (models MAW08V1QWT, MAW10V1QWT, MAW12V1QWT series) are divided into bracket components, fasteners, and weather sealing foams:

---

### **1. Support Bracket Components**
* **Main Bracket Assembly** (Qty: 1) – Includes pre-attached left extension arm and adjustable exterior support legs.
* **Right Extension Arm – Long** (Qty: 1) – For standard window widths of 26” to 36”.
* **Right Extension Arm – Short** (Qty: 1) – For narrow window widths of 22” to 26”.
* **Main Support Pins** (Qty: 2) – Used to set the angle and lock the exterior bracket support legs in place.
* **Cotter Pins / Hairpin Clips** (Qty: 2) – Secures the main support pins.
* **Flat Sill Adapter** (Qty: 1; on select models) – Used if your window sill is flat rather than lipped.

---

### **2. Screws & Fasteners**
* **1/2” Type A Screws** (Qty: 3) – Self-tapping screws for securing the bracket/locks into wooden frames.
* **1/2” Type B Screws** (Qty: 2) – Machine screws used for mounting the Open Window Brackets to the unit chassis.
* **1/4” Type B Screws** (Qty: 2) – Machine screws used to secure the Open Window Brackets to the support bracket.
* **1” Type A Screws** (Qty: 2) – Longer wood screws for anchoring the bracket in wood sills or storm-window wood spacers.

---

### **3. Safety & Window Brackets**
* **Open Window Bracket – LH (Left Hand)** (Qty: 1) – Ties the unit to the support bracket on the left side to prevent tipping.
* **Open Window Bracket – RH (Right Hand)** (Qty: 1) – Ties the unit to the support bracket on the right side to prevent tipping.
* **Window Sash Lock** (Qty: 1 or 2) – Locks the lower window sash in the closed position for security.

---

### **4. Foam & Weather Sealing**
* **Side Arm Foam** (Qty: 2) – Applied over the left and right sliding arms.
* **Additional Side Arm Foam** (Qty: 1 or 2) – Cut-to-fit filler foam for wider window frames.
* **Thick Window Sash Seal Foam** (Qty: 1) – Non-adhesive foam installed between the window sash and glass/chassis.
* **Thin Window Sash Seal Foam** (Qty: 1) – Sponge seal placed across the top of the lower sash.
* **Miscellaneous / Adhesive Sealing Foam** (Qty: 1 roll/strip) – Adhesive-backed foam to seal remaining gaps along the sill or frame.

---

### **Tools Required for Installation (Not Included):**
* Phillips head screwdriver
* Drill and 1/8” drill bit
* Tape measure / ruler
* Level
* Pencil
* Scissors / utility knife (for trimming foam)
sources:
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNp7qSk80us1q-Zn4Pe8T3o2PrZCgldaY9iJpY2cbalAAa7nQkB8abdJMEWd8mcEMbvaINGwcA2FVd0cZbVh4Z37A_kIyBkhfJ92ztnKKiKX6HrHOdp6qF-sAKc35eRVoyMFVu5AqeYuqR0eb1MH2y39RDAXQORCIHc-SyjbGqC2RJwH5M2VkGgNepXLx7E5owqjBPQOhKaeeMkmx62I0YJ41bXRkIRqmbCBBPWFwUF0JPK7ggmWzf2X3mgYeaolWFe0qav44R-jR3qQ==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGNp7qSk80us1q-Zn4Pe8T3o2PrZCgldaY9iJpY2cbalAAa7nQkB8abdJMEWd8mcEMbvaINGwcA2FVd0cZbVh4Z37A_kIyBkhfJ92ztnKKiKX6HrHOdp6qF-sAKc35eRVoyMFVu5AqeYuqR0eb1MH2y39RDAXQORCIHc-SyjbGqC2RJwH5M2VkGgNepXLx7E5owqjBPQOhKaeeMkmx62I0YJ41bXRkIRqmbCBBPWFwUF0JPK7ggmWzf2X3mgYeaolWFe0qav44R-jR3qQ==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCF-BTd6YwZHCQVxidehcOhduh2YOsoFbIcDrQADSnA2ZYd6iz13JE8HOmhtmw72RPn-mOpKkji6xTpiG8bV_3YOzttt8uJbe9N0NiG3iWFYrLTBKy2lWF8oi6wIf_W8t3FVzAYMxMkTiTCUNEqj05F50u0FXt5Njy9wNTJkCmxGxuQdapbFe3ZTkoyGzUeb_uYFmtqWP7>
  - scribd.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjq68tagGwJENWyIQuMb9sgz5eLqQH_m-2qaooRr5ZS4huhgKZlJg0gv_zacM1zFL_Mj2ONeS87jm0eC9LxFhld4cc3GW8RtEBAwf_ONO2uOxrpHYqCQ7FRisy32Sd-CkwJqioXKzKB3Hk6mc2-2QqK99ZKjWxL5F3GQK0>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFabDqdHtpkBtlZPDlnesgV3aa9HXC-UA9boQWSZ1E6ySkYwbwF3N5EXKtuWzM7qZ5hHVMSSOxDUDcsO_FQ63pfCYZKEh0MLmI_m8TpPEHs_9Ybo8AorOoDWytUiN4NfWaZaX61nGavVuf9IgN1SLKSwGu5vptyXsmKTiONoQz24YVvVJCIJPyShblIUIl2fWxHtOd_-aVUL9TmHcZk_2mMOQvnJl9XSBUz3F4-NbngxsbImLM5zZ-vbUk=>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE0l9AFvQgEBsk5BEo59RwHyp7LvKpDEZUbICvVl1lapJ18vKaldS-SrndlyZgaSVzuCAKoAeELWC-N2ZvWORbw4stDx3EqDgQErEpw01V2OawejMBIxJ06LpbReMEzwrtikIwzBpAKzYF7HWfGqs8UbllyI_mhTMU9f8gBvh5kAOulrqorcPM9IzcJcJ0rNKXUuvNmMOnZ4y3B04Hpdm3QH-7UwuxNMKCSMojvixbAvvpmAg87G2VgziT5cPsiQ6cHxJk=>

[13] knowledge base 'Air Conditioner Installation Assistant' answered:
Based on the provided knowledge base, here is the information you requested.

**Required Installation Hardware (from ID:3, listed as appearing on the page labeled "Page 2" in ID:1):**

The table is quoted row by row exactly as it appears, including the Quantity column. Where a quantity cell is blank or unreadable in the document, this is stated explicitly.

| Column 1 | Column 2 (Item) | Column 3 (Quantity) |
|---|---|---|
| (blank cell) | 1/2" Type B Screw | 2 |
| (blank cell) | 1/4" Type B Screw | (quantity cell is blank) |
| (blank cell) | Main Bracket | (quantity cell is blank) |
| (blank cell) | Main Support Pin | (quantity cell is blank) |
| CKK | Cotter Pin | 2 |
| (blank cell) | 1/2"Type AScrew | (quantity cell is blank) |
| (blank cell) | Open Window Bracket - RH | (quantity cell is blank) |
| (blank cell) | Open Window Bracket - LH | (quantity cell is blank) |
| (blank cell) | Side Arm Fam | (quantity cell is blank) |

[ID:3]

Note: The first column is mostly blank or unreadable in the source, with only one row clearly showing "CKK". The Quantity column only shows values for the first row ("2") and the Cotter Pin row ("2"); all other quantity cells are blank or unreadable in the document [ID:3].

**Optional Installation Hardware (from ID:1):**

The document lists the following items, but no quantities are shown for any of them [ID:1]:

- Window Sash Lock
- Thick Window Sash Seal Foam
- Thin Window Sash Sea Foam
- MiscellaneousSealingFoan
- Additional Side Arm Foam
- 1" Type A Screw

[ID:1]

**Pages on which each table appears:**

- The "Optional Installation Hardware" list appears on the page labeled "Page 2" [ID:1].
- The "RequiredInstallationHardware" table (ID:3) is associated with the page labeled "Page 2" in ID:1, since ID:1 ends with "Page 2" and ID:3 immediately follows it in the document sequence.

Please note that the page labeling in the document is sparse, and only "Page 2" is explicitly stated in the provided content, so page attribution beyond this cannot be definitively confirmed from the dataset.
retrieved chunks:
  - (Midea U AC Installation Guide.pdf) 
TOOL &HARDWARE
1. INSTALL THE SUPPORT BRACKET
! WARNING
Bracket should only be used for its intended purpose.
· You must follow the detailed installation instructions in the user manual
theright exte.
 WARNING
 WARNING
Metanthebrcketuntil
1.2  Adjust the
hthgled siportla.rmhseckthat tdoors. lnsta and right extension arms.
 WindOw reQuireMents
Installation Guide
Window Type Air Conditioner
Models
MAW08V1QWT MAW10V1QWT
detailed installation instructions
MAW12V1QWT
Before using your air conditioner, please read customer service at 1-866-646-4332.
3.4Extendbothw
1. INSTALL THE SUPPORT BRACKET (cont.)
 THE WINDOW3.SEALANDCLOSE
sashlock
Use the provided 12 Tye A screws.
1.3 Secure the bracket to the
ure, cut and install the side arm foam
NOTE: Drill 1/8" pilot h Screwing into thewindwsr.
of each extension arm as shown.
WARNING
Holes at the end or bottom of the Extension Arms can be used to secure the Support Bracket to the window.
 2. SECURE THE UNIT ON THE BRACKET
2.1 Set the air conditioner on the sup fold down the side arm hinges.
FAQ  Why does the air conditioner not start?
3.2 Secure the anti-tip brackets into the
- Wall plug disconnected. Push plug firmly into wall outlet.
 WARNING
 House fuse blown or circuit breaker tripped. Replace fusewith timdelaytyp
 Do not leave the unit unattended during instalation.
Remove the factory installed 1/2
reset circuit breaker.
Check if the light on the plug is on. If it is off, press the RESET button - Power is OFF. Turn power ON.
led 1/2
coulddamagethe
FAQWhy is there noise during cooling?
nustinstalltheOpelnWindowBrackets
- It is normal to hear airflow, set to a slower fan setting if too loud.
A WARNING
Window vibration - poor installation. Refer to installation instructions or check with installer.
Failing to do this could cause injury or property damage.
ect to wifi or App doe.FAQ  Unit will not co
 WArnING
 For additional support and troubleshooting tips,
  - (Midea U AC Installation Guide.pdf) idea
Optional Installation Hardware
Window Sash Lock
Thick Window Sash Seal Foam
Thin Window Sash Sea Foam
MiscellaneousSealingFoan
 Additional Side Arm Foam
1" Type A Screw
this manual.
Page 2

  - (Midea U AC Installation Guide.pdf) 
buame
follow the link in this QR code.
Jse the thick window
serious injury.
the windows
3.3
the
Ianygapsbetw
window and the air conditioner.
  - (Midea U AC Installation Guide.pdf) <table><caption> RequiredInstallationHardware</caption>
<tr><td></td><td  >1/2" Type B Screw</td><td  >2</td></tr>
<tr><td></td><td  >1/4" Type B Screw</td><td></td></tr>
<tr><td></td><td  >Main Bracket </td><td></td></tr>
<tr><td></td><td  >Main Support Pin </td><td></td></tr>
<tr><td  >CKK</td><td  >Cotter Pin </td><td  >2</td></tr>
<tr><td></td><td  >1/2"Type AScrew</td><td></td></tr>
<tr><td></td><td  >Open Window Bracket - RH </td><td></td></tr>
<tr><td></td><td  >Open Window Bracket - LH</td><td></td></tr>
<tr><td></td><td  >Side Arm Fam</td><td></td></tr>
</table>
  - (Midea U AC Installation Guide.pdf) Right
Arm
zontal Bracket
Doependngonte
either location below
to chec
level
 Center this part of the
nte
 of the windows.
Spring Pin Locks

  - (Midea U AC Installation Guide.pdf) Top view
Top of Unit

[14] web search for 'Midea U window air conditioner installation instructions mounting bracket window kit contents'; grounded search summary:
Here is a complete breakdown of the **window kit contents**, **mounting bracket specifications**, and **step-by-step installation instructions** for the Midea U-Shaped Window Air Conditioner (8k, 10k, and 12k BTU models).

---

### 1. Window Kit Contents & Hardware List

#### **Bracket & Hardware**
* **Main Support Bracket** (horizontal frame with sliding support arms)
* **Extension Arms:**
  * Left Extension Arm (pre-attached)
  * Right Extension Arm – Long (for 26″ to 36″ wide windows)
  * Right Extension Arm – Short (for 22″ to 26″ wide windows)
* **Main Support Pins & Cotter Pins (2 each):** Secures the angled support legs under the bracket.
* **Open Window Brackets (Left & Right):** Secures the unit and keeps the window sash in the track groove.
* **Window Sash Lock & Screws:**
  * 1/2″ Type A screws (3)
  * 1/2″ Type B screws (2)
  * 1/4″ Type B screws (2)
  * 1″ Type A screws (2 – for wooden sills)

#### **Foam & Weatherproofing Seals**
* **Side Arm Foam Blocks (2):** Pre-shaped foam blocks for the left and right window openings.
* **Additional Side Arm Foam strips** (for flat/lipped sills).
* **Thick Window Sash Seal Foam** (goes along the base/sill).
* **Thin Window Sash Seal Foam** (goes between the glass panes of double-hung windows).
* **Miscellaneous / Adhesive Sealing Foam**.

---

### 2. Window Requirements & Compatibility
* **Window Type:** Standard double-hung or single-hung vertical sliding windows.
* **Window Width:** 22 inches to 36 inches (55.8 cm to 91.4 cm).
* **Minimum Opening Height:** 13.75 inches (34.9 cm).
* **Wall Thickness:** Compatible with walls 3 inches to 10.5 inches thick (distance from inner sill to exterior wall face).

---

### 3. Step-by-Step Installation Instructions

#### **Step 1: Prep the Window & Sill**
1. Clean the window sill and track thoroughly.
2. Measure and apply the **Thick Window Sash Seal Foam** across the inner sill where the bracket will sit.

#### **Step 2: Assemble and Mount the Support Bracket**
1. **Choose Extension Arm:** Select the short arm (22″–26″) or long arm (26″–36″) depending on your window width and slide it into the right side of the main bracket.
2. **Place Bracket in Window:** Set the bracket onto the sill. The indoor lip of the bracket hooks over the inner sill.
3. **Adjust the Angled Legs:** 
   * Swing down the exterior angled support arms until the feet rest firmly against the exterior siding/wall.
   * Align the pinholes so the bracket has a slight **downward tilt toward the outside** (about 1/4 bubble on a spirit level) to ensure condensate drains outdoors.
   * Lock the legs in place using the **Main Support Pins** and secure them with the **Cotter Pins**.
4. **Lock Side Extensions:** Slide both left and right extension arms outwards until they press firmly into the window frame side channels and the spring pins lock into position.
5. *(Optional for wooden sills)*: Secure the bracket feet to the sill using the provided 1″ screws (pre-drilling 1/8″ pilot holes is recommended).

#### **Step 3: Place the Air Conditioner on the Bracket**
*(Recommendation: Two people are advised for this step.)*
1. Lift the air conditioner and align the bottom base rails with the bracket tracks.
2. Slide the unit backward onto the bracket until it seats into place.
3. Lower the window sash down into the **U-groove channel** of the unit to help support and center the AC while you finish installation.

#### **Step 4: Secure the Unit (Crucial Safety Step)**
1. **Extend Anti-Tip Brackets:** In the bottom U-channel groove where the window sash rests, locate the two sliding metal anti-tip brackets. Extend them outward until they engage inside the vertical window tracks. Fasten them tightly using the pre-installed screws.
2. **Install Open Window Brackets:** Attach the Left (LH) and Right (RH) open window brackets to the sides of the unit using the 1/2″ and 1/4″ Type B screws to physically lock the unit to the window tracks.

#### **Step 5: Install Side Foam & Final Weatherproofing**
1. **Side Arm Foam:**
   * Fold down the side hinge flaps on the unit.
   * Measure the distance from the side flap to the window track, add 1/4″, and cut the provided **Side Arm Foam blocks** to size.
   * Stick the adhesive sealing strip to the foam blocks and insert them into the left and right flaps.
   * Push the hinge flaps shut against the frame to seal the side voids.
2. **Center Sash Foam:** Insert the **Thin Window Sash Seal Foam** between the upper and lower glass window sashes to block drafts.
3. **Sash Lock:** Install the window sash lock bracket with Type A screws on the upper window frame to prevent someone from opening the window from outside.
sources:
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFibWv0OYOpN8ee1fcHgb-Q-quQpAqygV8HEImcoVOXEOTaCOZ2FSRK9Vr0n_SDq8pm9L1ycDCIDDAUGuzDKgN22HW7B7lu-wVHCKb9yfY9Vxz6CkI9sbwURAOrrvPQd1307zwUUX8Jrn31AoT0Zcth-uSzTsA7RqfsQY9G9xYiB_5LMsNzG1L4zpJrnJS3eH_5wF_XGlLOwXI1er09a7MPMukSeFKuBzTcv0j1AXn0cjm3Woru1H4iI6tz3NVkcyzjRoOQ6bJ1Xc6I8R4=>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF7WhwCKBRLtcIZg9boy441NiH134TUGbYsRQ82SUFHbyRxZA0YGntmh8p29PDMQheWTQuDS66mCaHS1NsmLiBQNgDe5LStA1dgeALXx_amlS4Slu4HRmkOKW2iLC0OxNJL>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvveiNf6QgPGaKDvIVXwupTN3-Pa6wNPTR3GFM3C-XMw3tVC-qjxKIYBdtcgEeeBEFriGW5LvoCnbJnbWxtIIeAu3iP2Mw_FhoBMzS2CChZEtbjvxR2-VJSPlS-Ht-Zv3WLjcu6oDWNF2oBPa_S_oFMXgp5cgok5wKoDoif0Yg1PRrhCKrRAn25uRIYiQWl9gs_l_Y1A1XZd9nEi6MFoYSHuVuKgIG5N8e9Nz7dSyxBm9AXQ==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHvveiNf6QgPGaKDvIVXwupTN3-Pa6wNPTR3GFM3C-XMw3tVC-qjxKIYBdtcgEeeBEFriGW5LvoCnbJnbWxtIIeAu3iP2Mw_FhoBMzS2CChZEtbjvxR2-VJSPlS-Ht-Zv3WLjcu6oDWNF2oBPa_S_oFMXgp5cgok5wKoDoif0Yg1PRrhCKrRAn25uRIYiQWl9gs_l_Y1A1XZd9nEi6MFoYSHuVuKgIG5N8e9Nz7dSyxBm9AXQ==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL6t0mXIGk4xWyL6YgFCU4E8dXbBEtXKnveTk256CasL9C89RXqPQpJmrL0K-EqPylU3Az2yZXpIvHMgG7xXWwpOVpy0xS_V5wC-gHYh0bS5Zgs3ouMHQP0gkKH6qGkBFW7BcL0WT63e9L5JLFnKI9Yn89mglT8pYjBSscYFiZz7P3LJeA2l2UrZj7V52rIqcI_obe9uwKMWX6w3rc19oNB84JMNL1VZMt9AtuvjEK4H1Hcvh9rrS-He-A>
  - reddit.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLysxtFDpd8Ul_pAW6NGLXUtFvNUwTQcTeOaTPkKyFMXmj7xkYw5B7I5wPjYXTHNmN3h3_lczIDlWy2WkN8mS3TDsxyLSYuLN13Q5mDiHS9-0N8_HdA9YJOxpylqqkdduA4G9YmYGuxG_ET6k_TFYjnDrL3IG7_j6JmqXvKO6tsGuh_gV1ZCEyCfoMODxK>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFE4IAXSfFr3MQ-cOPpR8cCpS5OHvgv4WYgKxRN53I6iajt30Ex84Rn7phfiHzUnQrmX9cIU0szPZnL19S2M8hU6PKVq1sgIWfaN8f5rhz_Y70S65jC5U-uMXrfHxHVBpYALTv1JAtbfRdV4HuzHBqqLnHiHobohV6oN6DnjuszKpO8JVhkQaYYDP42MEVs507mbM_ffhrUy5hUtbmc-B8RisRcXknYrDIBeDCtqhJWYSROTiVlpL8AoJFhOgAj2UNg5-3h>

[15] web search for "Midea U MAW08V1QWT user manual pdf midea.com window air conditioner owner's manual download"; grounded search summary:
The official **Midea U-Shaped Smart Inverter Window Air Conditioner (Model: MAW08V1QWT / MAW08V1QWT-T)** User and Installation Manual is available directly through Midea's official product support:

---

### **How to Download Directly from Midea**
1. Visit the [Midea US Official Website](https://www.midea.com/us).
2. Navigate to **Air Conditioners** > **Window Air Conditioners** > **MAW08V1QWT** (or enter **MAW08V1QWT** into the top search bar).
3. Scroll down the product page to the **"User Manuals & Documents"** section.
4. Click **Download** next to **User Manual (PDF)**.

---

### **What is Covered in the Owner’s Manual**
* **Pre-Installation Requirements:** Window sill dimensions (fits hung windows 22" to 36" wide, minimum 13.75" opening clearance).
* **Quick-Snap Bracket Setup:** Step-by-step assembly of the exterior support bracket, setting proper outward tilt/pitch for condensate drainage, and locking the sash.
* **Control Panel & Remote Instructions:** Operating modes (Cool, Dry, Fan, Auto, Eco), Sleep timer, and Fan speed adjustments.
* **SmartHome / Wi-Fi App Setup:** Pairing instructions for the Midea SmartHome app, voice control with Alexa/Google Assistant, and Matter setup (on supported models).
* **Cleaning & Maintenance:** How to remove, wash, and reinstall the slide-out mesh air filter.
* **Troubleshooting:** Error codes, reset procedures, and resolving common cooling or noise issues.

---

### **Need Further Assistance?**
* **Midea Customer Support:** `1-866-646-4332` (Mon–Fri 8:00 AM – 7:00 PM EST, Sat 9:00 AM – 4:00 PM EST).
* **Interactive 3D Assembly:** Midea also provides interactive, step-by-step 3D installation instructions for this unit via the **BILT** mobile app.
sources:
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqEtFr0RrCwilF7E638ZQJMH1kW64I6Y0FxL8MnTuq1VfrvxiIyoMblDAEOXz9BN_AeCCfepfJaE66RA3IHxFyeuUNIIm_rOP4rF3uzpx3PYXjHKxMjf4SKQyRNjwGuXiYBS0=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGldmKd10QG65AgGpSnNkVwzRiFq8uXBl_cGurGMzbCofQ1sKdBepehvGysNDsNiy9w0WrAqqzdm9vPilAo2aKn2pB87fp0OU2ifXX92BCF0bYfT_cr1D7zDho=>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7G8lffxCP5CxHj2nmRmhnLC4cs4UPZA4PSWQC3yZ9rhJlLOZ5wMtE1oebpNbDmAO5I3g7GTDaoRk5HiOxWRB8DlRzbSJWq3YZv1eslCsHEe1vPjyQB2MBKaMPSnAIvo6OnOCUTcM060Vwk1Sil802dkaK89QkCuCmSJ7jRqESZhfibm0G8qTf2h3YW5tVigbbztHOuj9-Tw==>
  - teklib.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFI4jwYZQGomrgzBdakRrgRqKAwBrR25SSLrznWGcjFidkhSJCkVd11Q70y3buP3RZTtREFmR1ltUKK8ieLZz2QrQuo4n7_bvI-5ZL7lI9YJlHXKug-WXEtowU-ArA-tJgnxlnPxzJ3e0sYLozqoaKyFuuKAabybKIYshjuyvrk>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa2nUGZZurScrcrlFLo_xOMzmJbML4HPvrmDD3YrPgYej2es89AbsimOFdl-kZ0aYUXEV7eVvEu4KiqbnO4zpLN61RAY2nXxltzYAyLrNvqhvpXnMvooifJKnymcZP52WRnX3DlCWdWK8TGjfRuMJXYuaXAibD4qFzuDKM_ko_44mJsaSCqlR4knN-ozyui8kRBLSFj4PIvazNcju4MWVMfV_1hw6DBXBQ2c4Llc1qoZKDW0xIl-xFIK0l>
  - bilt.ai <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGXKYYQgfsrfhr0SwQd1jXgckr6p_4olOZqwoznvQwaiPoDeWMq-v9EzHXNYh6vB-H0XrMSDNnaLbfSaVV0puqHt_eO55Pngl_BdVeDRlOrG6ZaL6_f3O6LYA==>

[16] web search for '"Midea" U-shaped window air conditioner "drain hose" included or not condensation manual'; grounded search summary:
**No, a drain hose is not included** with the Midea U-shaped window air conditioner. 

The user manual and engineering design outline how condensation and drainage operate for this unit:

---

### 1. How Condensation Works
* **Slinger-Ring Evaporation:** Like most modern window air conditioners, the Midea U-shaped unit is engineered to collect indoor condensate in the outdoor base pan. The outdoor fan uses a “slinger ring” to pick up this pooled water and splash it onto the hot condenser coils.
* **Efficiency Boost:** This process evaporates the water into the outside air while naturally cooling the condenser coils, maximizing energy efficiency.
* **Normal Dripping:** On excessively humid days, the unit may extract moisture faster than it can evaporate it. The manual notes that **water dripping from the outdoor portion of the unit is completely normal** under high humidity.

---

### 2. The Drain Plug & Manual Instructions
* **Normal Operation:** The manual specifies that the drain plug at the bottom of the outdoor section **must remain installed** during cooling operation to maintain peak cooling performance and energy efficiency.
* **Long-Term Storage:** The manual directs users to remove the drain plug to drain all accumulated water from the base pan before packing or storing the unit away for the winter.
* **Tilt Requirement:** Proper drainage depends on the installation bracket. The manual requires the unit to have a slight downward slope/tilt toward the outside (using the included bubble level) so water does not pool toward the interior or spill over the window sill.
* **Updated Drain Plugs (Mold Prevention):** In response to standing water and mold concerns in exceptionally humid climates, Midea introduced replacement/vented drain plugs (a black drip-style plug instead of the solid plug) that allow water to slowly weep out rather than sit stagnant for long periods.

---

### 3. What if you need to attach a drain hose?
If your unit drips onto a high-traffic area, sidewalk, or balcony below:
* The factory drain hole does **not** feature standard garden-hose threading.
* To route water away, you will need to leave the drain plug removed and attach an aftermarket AC drain hose connector (typically a standard 1/2" or 5/8" barb elbow or a 3D-printed spout adapter) and tubing. Note that running the unit with an open drain hole may slightly lower the unit's cooling efficiency in extremely hot weather.
sources:
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4fHft82eEyvyysEw6h4b3r1Ss01kbN2k_nYbz2jlkilZM-v436HgG8ViT18n_HKP6WTO2XZQT3oD-r04E7qQqOQr7we1QMP-YgC4mu7U1v-XbMaGPTG-Ii-6XSpJ8-yFSMBYHqtq3msFG7pjg1iY3Noe66q1vnhX4fXTbrhHPnFNTra4A0EdE-7XYUKLFEW5-Fjdh3afScf27MMVc1_3-USbL2kTSRuawymbkK4OVYtBdxQ==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDyzTF9ekJ3R2cW12kirSHpjJR-_Tu7TmdLWGlSKXQ5HmfOHzVs0Fss68pP4iADW_QqLGK5eGru5mvCwYMX3HzyNkb_vMuxevUB3xUmqXjq5rXSvb7vUHAb4O6k8gh4JY=>
  - reddit.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyuWpPftKgXEMvLiwq38VYZBN2BMB3yKiLqGKn1emFeM7PgT63nDi780ICtdsy19bmqqDsn7EpcBLE4qUbTsUU1Jd_XNqkVch99CguTTwAy4RCuwxiVaEkhX5tb-a2mqNj-dZvEXHnRczbbuVtQ64SlhNNhSrBlhxioKwpoDJ1kSL-2U50_BZzGXJ_g8VSvz3dAvWb0uMl61g60du4kw==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHXamGXjcxOaGmQBGk8eH2fwH9vOO8DaPHXZBdU5iECxxtduzQV_CP463zgo8QU1rRJPn6gW3YxzjBff-LDllkZN5J0gLkYm15zermHXrfLmcZkSAuYR9Xk-dvc--w3DUZS8cLrgB7DSHhGYHVBh1Cq7JdxATT3Tpm0OsEgr8s8ZkLIuvutb3Fc0nY_0oKcWSeJkyX1oyuTG5NJYSCCkmigKeR9FjO3-G6-FXzG95fA4LU3HiDUh_ZuJ-TxN85CcJIrpi4=>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVseUayhtJ-Dnr_ePcIWL5-o5oJVGDFZr1oULZTcTplWVMJmejTehlUoSYbGGjUqWpxJYi7mCFxWJbawJnU_fIy0A_MqvqrOqoOOl4jqyf7rIz4iHodEtJ73UwNKEXYiS_UyLdz07GsBRGMD8LMo1naycupNpIiQSXUBKGWJOndIZo-T915H03n--EJRBaArLyBxNrZSFMz_5y3zFLJrhVubgMgm6QFrXfH-npKMYM1tnIRZA=>
  - youtube.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOufJ_heS4_yidAwynZX13mnYX2tZL2BwP9fLtJb0m15QXlspbNujfm5zmE6fL6WCYkKpm36zriDQM8NUQaJamuggG6lrUvctpXYlY3vaSrCkTsVuJmj9mq4v15jRuMLo=>

[17] web search for 'manuals.plus Midea U-shaped window air conditioner user manual'; grounded search summary:
The **Midea U-Shaped Smart Inverter Window Air Conditioner** user and installation manuals are available on Manuals+ as well as directly through Midea:

* **Manuals+ Guides:**
  * [Manuals+ Midea U-Shaped Air Conditioner User Manual](https://manuals.plus/midea/midea-u-shaped-air-conditioner-user-manual)
  * [Manuals+ Midea MAW08V1QWT U-Shaped AC User Manual](https://manuals.plus/midea/midea-maw08v1qwt-u-shaped-ac-window-air-conditioner-user-manual)
  * [Manuals+ Midea 8,000 BTU U-Shaped Inverter Manual](https://manuals.plus/midea/midea-8000-btu-u-shaped-smart-inverter-window-air-conditioner-manual)
* **Official Midea Direct PDF Manuals:**
  * [Midea MAW08V1QWT / MAW10V1QWT / MAW12V1QWT User Manual (PDF)](https://www.midea.com)

---

### Key Manual Sections & Highlights

#### 1. Window Requirements
* **Window Type:** Single-hung or double-hung vertical sliding windows only (not suitable for casement/slider windows).
* **Opening Width:** 22 in. to 36 in. (55.8 cm to 91.4 cm).
* **Minimum Opening Height:** 13.75 in. (35 cm).
* **Maximum Sill Width/Depth:** Bracket accommodates standard sills (extension blocks or wood shim required if blocked by a storm window frame).

#### 2. Installation Highlights
1. **Bracket Setup:** Install the quick-snap mounting bracket into the window sill first. Adjust the bracket legs against the exterior wall to ensure a slight downward tilt (approximately 1/4 bubble on a spirit level) toward the outside for proper condensate drainage.
2. **Placing the Unit:** Set the unit onto the bracket from the inside. The outdoor portion rests on the support bracket while the center U-channel aligns directly with the window sill.
3. **Securing the Sash:** Lower the window sash down into the U-shaped slot. Extend the built-in anti-tip arms and lock brackets into the window track.
4. **Sealing:** Slide the side foam blocks into the open spaces on either side of the U-channel and apply the top sash sealing foam between the upper and lower glass panes to prevent air leaks.

#### 3. Operation & Controls
* **Operating Modes:**
  * **Cool:** Standard compressor cooling with adjustable target temperatures (62°F–86°F / 17°C–30°C).
  * **Eco:** Cycles compressor and fan off once set temperature is achieved to conserve energy.
  * **Dry:** Dehumidification mode.
  * **Fan Only:** Circulates room air without cooling.
  * **Auto:** Automatically chooses between Cool and Fan modes depending on room temperature.
* **Special Features:** 
  * *Sleep Mode* (gradually adjusts temperature overnight).
  * *Swing* (moves louvers for even airflow).
  * *Follow Me* (senses temperature at the remote control rather than the AC unit).

#### 4. Smart App & Wi-Fi Setup
1. Download the **SmartHome** (or **MSmartHome**) app from the Apple App Store or Google Play Store.
2. Press and hold the **Connect** (or Fan/Display) button on the control panel for 3–5 seconds until the display flashes `"AP"`.
3. Follow the in-app prompts to connect the unit to your **2.4 GHz Wi-Fi** network (5 GHz is not supported).

#### 5. Routine Maintenance & Troubleshooting
* **Air Filter:** Slide the filter out from the front panel. Clean with warm water and mild detergent every 2 to 4 weeks. Let dry completely before reinstalling.
* **Drain Hole Note:** In normal cooling mode, the fan splashes condensation water onto the condenser coil to improve cooling efficiency. Only remove the rear drain plug if water buildup causes splashing noise or during winter storage.
* **Window Won't Fit in U-Slot:** Check that the mounting bracket pitch isn't slanted too steeply, and verify that the window track isn't obstructed by screws or framing.
sources:
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2-N9I52nK5_TLpaSNGZpVytVOJSo1Petx2BKLtkGdFkpvQF6bszpkwI9HrU0X-zViq6iwLgxAprwYzZ8mmENu19wPJeaA21uYXyR76_i6zURmZ0bNzD9Lyeq9GcITfQsVXoD-GRp4jJOXhbUlbMdk5FJgQsofBqubyVM=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEz7r6RIk89_EqL0TGJXvvqWqGpDmC9j38t8iZjUFcBiicZgqQFxKpcxhPv79WALYNgVqiFI-2_gQ7SKAXraoXa9AGlKpZakAmU-R-WKyJbAhLM3KZBhnZuMus=>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFA90PEqmlzuJlD6GOhuQhlgP7750YbaSosXqwWkOvY9dqxhJJindQpfkqI-HPI6jhLfvEw-DNsnW--7dDqbJvZjW5Ui72jL_jRWP27FviHe9HrNntBe_KHwoE=>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFITepAb8tBSpRwYTQpKKyPqGllZwKKmgFPa_ArUIrF8FZpoAkQQz4rC_a4bceLH0CdLUDIAH77U7orNYiIk3R-M-9q9ZwgxKn3Jl2ukoXcTdoMe-kJ8A1p2HoMsao5WQh8>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGm1eAJysT8Cw7wYpKYtn5nf0W2IyYpIsw6v2zMQFn4kUPkwUmxKQ8hgR2WDa28jvBF92mkAmQweChsXevMSaw6H_yVl2FjGGWdlRs-kEcsDrL9zOS3NirqEMiffFnzqRzn>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEs4NIfwBnB4XKD9rAhGFYgI_620AyAlenZO1oLHWy0lsvus-Y-3Nx5P_lzrGNft4gZm4ra4JIUOr7MwNhxrV9Caam1cyX_RV0Wu0Kh9qiAgTETjcLEJnZg4AwBs_zJDsViLd2oR9B-s-jecYsCIy8x9XCt0kobLZhZ3neBd5uBtjW5rfY8bR2RkRGXISZmcA-NtuJVmkgrLiyS6-XBqsnHziEc5XsfJM3Gh5XTAyeG5z8QlFmqWbv1dSSdT8XnCo4fiSro>

[18] web search for 'midea.com/us/support window air conditioner MAW08V1QWT manual download page'; grounded search summary:
To find and download the manual for the **Midea 8,000 BTU U-Shaped Smart Window Air Conditioner (Model: MAW08V1QWT / MAW08V1QWT-T)** from the official Midea US website:

---

### Direct Steps to Download on Midea US:

1. **Go to the Official Support Page:**
   * Visit the [Midea US Support Center](https://www.midea.com/us/support).
2. **Search by Model Number:**
   * In the **"Find the help you need"** search bar, type `MAW08V1QWT` (or `MAW08V1QWT-T`) and hit enter.
3. **Access Documents:**
   * On the product support/details page, scroll down to the **"User Manuals & Documents"** section.
   * Click **Download** next to **User Manual** (PDF). You can also download the **Energy Guide** here.

---

### Additional Installation & Support Resources:

* **Interactive 3D Installation (BILT App):**
  * Midea partners with the **BILT®** app to provide step-by-step interactive 3D assembly and installation guides for the `MAW08V1QWT` series. You can access this via the [Midea BILT Guide](https://www.midea.com/us/support) or by scanning the QR code in the manual.
* **Midea Customer Care:**
  * If the file fails to download or you need a replacement physical copy, call Midea US Support at **1-866-646-4332** (Monday–Friday 8:00 AM – 7:00 PM EST, Saturday 9:00 AM – 4:00 PM EST).
sources:
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHhO0-CbWmTMNYxQyLjmmTiq31asQP1lG1mTwvXZlEHuHAgFDsQh-kcGHfuMDzSJax2__-ITO8gTtf3l9nSkd6IixwsHq0eBEQE5z28MAa3tl7VDdBi>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnuQtuxL43w-ryLQbsaISlrQmvEG6IrOF3lqXRSUtEB4y1s1zCfUpR-irQCQM74bawTq88eokjLMAdeEvMFWqteP-TKMxm70M1f04CBwUAMROPiagk8N5x1WjsXiAcu0iW4Co=>
  - bilt.ai <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEif3WapbvDmJZ7scfk-7aqSmfbXCkes5ARIFigdyoOOQOgvoG2XRywTQbCFAHdd1ynRJfxek978g-_BZ6VVvD4AyyELY8fl_J3KlWSdRXscSU23DxTf_bx>
  - manuals.plus <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5qbnvt57DuK-Bj2d9Sm7gbq9dDuJUR3mXW0Qg73JV4ZW5kvc6YEoXBoY57LLuautysXAqHUvl4Sj3EJc6fGS3sEWwJDfAebW0-eaMdkGDbn1IUcdsztxrc9lj0ke2Q4N5QD9i>

[19] web search for '"manuals.plus" Midea U-shaped air conditioner user manual hardware list bracket screws'; grounded search summary:
According to the Midea U-Shaped Window Air Conditioner installation manual, the **bracket fasteners and screws hardware list** includes the following items:

---

### **1. Screws**
* **1/2” Type A Screws** – Quantity: **3**  
  *(Self-tapping/pointed wood screws; typically used to secure bracket arms into the wooden windowsill)*
* **1/2” Type B Screws** – Quantity: **2**  
  *(Machine/blunt-tip screws; used for attaching hardware such as the open window bracket/bracket assembly)*
* **1/4” Type B Screws** – Quantity: **2**
* **1” Type A Screws** – Quantity: **2**  
  *(Longer wood screws; used for installing the window sash lock into the upper/lower frame)*

---

### **2. Bracket Pins & Hardware**
* **Main Support Pins** – Quantity: **2** *(used to pin the angled support legs into position)*
* **Cotter Pins** – Quantity: **2** *(used to lock the main support pins in place)*
* **Open Window Bracket – LH (Left Hand)** – Quantity: **1**
* **Open Window Bracket – RH (Right Hand)** – Quantity: **1**
* **Main Support Bracket Assembly** – Quantity: **1**
* **Right Extension Arm** *(for 26”–36” window width)* – Quantity: **1**
* **Right Extension Arm – Short** *(for 22”–26” window width)* – Quantity: **1**
* **Window Sash Lock** – Quantity: **1**

---

### **3. Pre-Installed Chassis Screws (Note)**
* **Anti-Tip Bracket Screws**: There are **2 machine screws** already pre-installed in the U-channel/side flaps on the chassis of the unit itself. During installation, the manual instructs you to unscrew these, slide out the anti-tip brackets into the window track, and re-insert the screws to lock them in place.
sources:
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEWZDFb6OiWsEloxfA6SRnnVd3KARaP41ynLKAmJyWHjcima4PxsZDjzztcQe0DjBd39HL3_X9_LyYt3sX5b2dmP276T-Eqc1_XErXcRI9Ts0S_lfFvxUOYYLAubx6_eJkQ_bDZq-jwkzajO0bARLhYyJrli7PTw0N0OrlqiKOnvI4NnVrMS1u_VN4Ss4tODvCMXtMuhNNsQA1MRDkEAXHUCfT_oasMTNFPEQo6Id_C04MmMp5wWVX6Md7wQI1sHvEtQw=>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAQhg2a5iqJkp0-Ui3KvjskG2EYV7u2yV5CylQbeKWMUGhdoH5Z6_-EmAAvSwPgk4zBowcZWYoVbLbDfhWSIuCVM4fJRWzcN8EfQ8HFAJg4r5kElJ_gVaG_HjATJJyPvr8qNSV6xRrab3L2v4QFkkj97Hdxg9f_GhqTxMTARM0on2IzbH6STyRK4ygwlmkh2cCtLb02dlolmuCSEsCibIPvPXbtgyURbtVBsmgVn1sf6U3wbh20Xt3DrUbpsUddm-gZ_icOobqmZnFSw==>
  - reddit.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEN1AQ0QzZ0pCluWFaSzt5lgNXJCY0tPxoKyAJ_vilCwobi7rS4VAsZU4kdJuxfubdPDJCbq1NEaTBUbPpHuqka3zAfNO0AFNzLUU9FBJ6N86Bwesb6Q2Lb_NvHXyHj_PoEZg5M9vTz9kikzKxcBWzopvJbWcDcrPNY3Al3c5FZtw==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH8EryNrlpmAqhApXmaJQHw0i5v-azqL6Zd6-cB8kIW4IOBImUokjDfzTIfnV95V6U0qclUUsuHDIj9KGlkaT--85QB7vzjK8ICKSdhG08ihknynHsXIZwDQrDjI_846a73V2LgcXR3d3jkKPS5fm91Y5RIHrfJWHoggLZSQXJDW3ACtuzjnmQQW8H4kMw6y4Dt3S9WfRXgJwnspP9XELCOooxMT35Tj-7Q0thD5knfKSl8VA==>
  - midea.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFr0PqKjh7Fqgi-VWBDzUnRoCEgVFXbCUpH9N5PTrJzCKpfTRUMXjwXR2d9bWtnb2ogsUOB5QdKe5vaXiTLKLqYK-Yzjs5w19jdXThhFuAE8aorGkBB_fKhKmoG-BJawLyApmpuQPORhhAYxf_WVHB3RFWFZjPNfEhAgrRtVr7jRetX1dbVgdG-e_PtIwBkgAuh405cbrXS>
```

</details>

**Answer:**

## Midea U Air Conditioner — Required Installation Hardware

**Source status first:** No file was present in my local working directory (the workspace is empty), so I could not open an attachment directly. However, the guide you uploaded **was located in our internal knowledge base** (RAGFlow, knowledge base *"Air Conditioner Installation"*, document **"Midea U AC Installation Guide.pdf"**, covering Window-Type models **MAW08V1QWT / MAW10V1QWT / MAW12V1QWT**). Everything in the table below is quoted from that internal document.

### 1. Required Installation Hardware (per the uploaded guide)

Section heading in the guide: **"Required Installation Hardware"**

| # | Item (as listed in the guide) | Quantity |
|---|---|---|
| 1 | 1/2" Type B Screw | 2 |
| 2 | 1/4" Type B Screw | *not readable in source* |
| 3 | Main Bracket | *not readable in source* |
| 4 | Main Support Pin | *not readable in source* |
| 5 | Cotter Pin | 2 |
| 6 | 1/2" Type A Screw | *not readable in source* |
| 7 | Open Window Bracket – RH | *not readable in source* |
| 8 | Open Window Bracket – LH | *not readable in source* |
| 9 | Side Arm Foam (shown as "Side Arm Fam") | *not readable in source* |

The guide's body text also states: **"Use the provided 12 Type A screws."**

> The document separately lists an **"Optional Installation Hardware"** section: Window Sash Lock, Thick Window Sash Seal Foam, Thin Window Sash Seal Foam, Miscellaneous Sealing Foam, Additional Side Arm Foam, and 1" Type A Screw — with no quantities shown.

### 2. Public sources (for cross-reference only — not from your upload)

A public web search on the product name surfaced third-party manual sites (Manuals+ pages for the Midea U-Shaped / MAW08V1QWT units). Their lists broadly match the same bracket-and-foam kit (main support bracket with pre-attached left extension arm, long/short right extension arms, 2 main support pins, 2 cotter/hairpin pins, LH/RH open-window brackets, Type A/B screws, 1" Type A screws, side-arm foam, thick/thin sash seal foam, window sash lock), plus a stated note that **no drain hose is included** (the unit uses a slinger ring; there's also a mention of 2 pre-installed anti-tip machine screws reused at install).

**These public figures do not agree with the internal guide on quantities** (e.g., public sources cite "1/2" Type A = 3, 1/4" Type B = 2"), and the web tool returned mostly obfuscated redirect links rather than clean canonical URLs — so treat them as unverified. I am **not** blending them into the answer above.

### 3. Limitations you should know

- **Most quantity cells in the internal table were blank/unreadable** during extraction. Only two quantities are actually present: 1/2" Type B Screw = **2** and Cotter Pin = **2**. I did not guess the rest.
- The table appears to be **scanned/OCR'd**, so item names contain artifacts ("Side Arm Fam" → likely *Foam*; "1/2"Type AScrew" → missing space; "12 Tye A screws" → likely *Type*). I've quoted them as retrieved.
- There is an **internal inconsistency**: the Required list has a "1/2" Type A Screw", the Optional list has a "1" Type A Screw", and the body text says "12 Type A screws" — these can't be reconciled from the retrieved content.
- Page attribution is unverified (only "Page 2" was explicitly labelled).

**Recommendation:** to publish precise quantities, the original PDF needs a clean re-OCR (or a re-upload), since the quantity column did not extract reliably. If you'd like, I can have the knowledge base re-queried specifically for the page containing the "Required Installation Hardware" table, or produce a short Markdown/PDF summary — just say the word.

**Citations:**
- Internal: *Midea U AC Installation Guide.pdf*, contained in the "Air Conditioner Installation" knowledge base (chunk refs [ID:0], [ID:1], [ID:3]).
- Public (unverified, third-party): Manuals+ Midea U-Shaped AC / MAW08V1QWT manual pages; official entry point <https://www.midea.com/us/support>.

---

## 15. route-11 (routing, easy)

**Question:** When did the FDA first approve oseltamivir?

**Gold answer:** October 1999.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] tool ls returned:
No files found

[3] web search for 'FDA first approved oseltamivir Tamiflu approval date NDA 021087'; grounded search summary:
The U.S. Food and Drug Administration (FDA) first approved Tamiflu (oseltamivir phosphate) capsules under **NDA 021087** on **October 27, 1999**. 

### Key Details of the Initial Approval:
* **Application Number:** NDA 021087
* **Approval Date:** October 27, 1999
* **Applicant/Sponsor:** Hoffmann-La Roche Inc.
* **Dosage Form:** Oral capsule (75 mg)
* **Initial Indication:** Treatment of uncomplicated acute illness due to influenza infection in adults who have been symptomatic for no more than two days.
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGdf8XivSfree8Efm0O_7eDOZpLM8lfl4F990tPHu5ho68sI1Mn5us53H0f3H41Wp_SPE6b3Awi1Wv6Ebwx3qT19j6iAzZjsCzRDtWSe2ZoVKCY6u9YBRckhsu-fGPDYiZgY79IMgTpIdOsUAzi6BjOyle57zaaIHnBHJipI9qL7w==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3oLRmGHJh94zVtpIQ0eK0e4yztYQhv14ns_I0KhLHysquOwTd6QWvmu6E0N-y-eIuMY02Vc9Dknv6az4ww4jhrtpTwmvLjJNxFFaf0Vc3k4P6G4hCNwOCdflyuMvsAoI9KfsaKQbAaIabQfDiP-wv1Mk-OmKmOeiGOTDI4VLop8Q=>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGk3Jk8n4RhQgdFYDVu1bhMscOx_Qrh4jDOzPwohcJ5523IdWeNX4A6gZC25pSrvZInhuRlybVA7jz8sjrEJMNLA9R2dn4_vRqcfFKoyvkKnnfGJaUAPd-0nirsE8P263JT4euCujQ-ZN8EGLXRZlEsYjRudk0xgqglQB3uRIBkvx8=>

[4] web search for 'Tamiflu oseltamivir Drugs@FDA approval history NDA 021087 Roche'; grounded search summary:
The approval history and regulatory milestones for **Tamiflu (oseltamivir phosphate) capsules** under **NDA 021087**, held by **Hoffmann-La Roche Inc. (Roche / Genentech)**, according to Drugs@FDA records:

---

### **Product Overview**
* **Application Number:** NDA 021087 *(Note: The oral suspension formulation is registered under NDA 021246)*
* **Drug Name:** Tamiflu (oseltamivir phosphate)
* **Dosage Form / Route:** Oral Capsule
* **Available Strengths:** 30 mg, 45 mg, and 75 mg
* **Sponsor / Applicant:** Hoffmann-La Roche Inc.
* **Pharmacologic Class:** Influenza neuraminidase inhibitor

---

### **Key Approval Milestones & History**

#### **1. Initial FDA Approval**
* **Date:** **October 27, 1999**
* **Indication:** Treatment of uncomplicated acute illness due to influenza A and B infection in adults (18 years and older) who have had flu symptoms for no more than 48 hours.

---

#### **2. Adult Prophylaxis Expansion**
* **Date:** **November 20, 2000**
* **Approval:** Approved for the **prevention (prophylaxis)** of influenza in adults and adolescents 13 years of age and older (in close-contact/post-exposure and community outbreak settings).

---

#### **3. Pediatric Prophylaxis Expansion**
* **Date:** **December 2005** (Supplement S-030)
* **Approval:** Approved for the **prophylaxis** of influenza in pediatric patients **1 to 12 years of age**.

---

#### **4. Approval of Lower Capsule Strengths (30 mg and 45 mg)**
* **Date:** **July 2007 / 2008**
* **Approval:** Added **30 mg** and **45 mg** capsule formulations (in addition to the original 75 mg capsule). This provided weight-tiered dosing for children and patients with renal impairment, as well as a stable solid option with a longer shelf life for pandemic stockpiling.

---

#### **5. Infant Treatment Indication Extension**
* **Date:** **December 21, 2012** (Supplement S-062)
* **Approval:** Expanded the treatment indication to include infants **2 weeks of age and older** who have had flu symptoms for no more than 48 hours.

---

### **Notable Labeling & Safety Supplements**
* **Emergency Compounding Instructions:** Added validated instructions for pharmacists to compound an oral suspension directly from 75 mg Tamiflu capsules in the event of commercial oral suspension shortages.
* **Neuropsychiatric Adverse Event Warnings:** Labeling revisions to advise healthcare providers and patients regarding reports of delirium, hallucinations, and abnormal behavior in patients with influenza receiving Tamiflu (predominantly in pediatric patients).
* **Renal Dosing Adjustments:** Updated dosing regimens for patients with varying degrees of renal impairment and end-stage renal disease (ESRD) on hemodialysis or peritoneal dialysis.
* **Immunocompromised Patients:** Updates to clinical pharmacology and resistance profile data reflecting use and prophylaxis in immunocompromised individuals.

---

### **Current Approved Indications (NDA 021087)**
1. **Treatment:** Treatment of acute, uncomplicated influenza A and B in patients **2 weeks of age and older** whose flu symptoms started within 48 hours.
2. **Prophylaxis:** Prevention of influenza A and B in patients **1 year of age and older**.
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP0So8Xg5y4xOGLvu7KALQle4zjclRDskn0IEpe3oIOK8R98XgEgrtPBQBWpQZeoIDkQ42BohzQF4VaYFWdY8M1eKUI-0_wekP37Ma7br5NOo3sIiFz3KjncDd-3KsGKaPdNgdE15xCvdtVRdoO0GRmSDemy89-ucKtk8AJOhggbo=>
  - drugs.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5vsXE3e7cP4eHLR109GAuvDwRluOr94rbZnnUDtx9wM7CFEgCUJ77DYgNO36TbGibkYHnqo9iIXzxu5VuwH8GZGLKYE6RSft9A-V8fs27HqvdrKpEKowlK-UUWw==>
  - mdedge.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDUAi-PyF8WNhb4JO9PBqIM0kYl56Q78Egf92WpLrrU6ST63ZLqkLn2zrWq42PUdH2Sne-eVq0OwsIXxK3r7xKMocPlFcsvaxV1KczEKSG1_xVeDw85xLccyRKQnsdCdeVbGZyv4cYTJ18C5sgNjWqVKKCagCptlGU>
  - biospace.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHo-ZvtZNUwKRBzxKcKLRndDDh6vSOXrU0j7PwUS31WkKSYzbt1F_jYMxXz525WEvc5OCBCgXRX5vIkK6VdxkrEIKAp1QRoiM2_etfKxOJhXNrGK73a7QV5XeD3wgoJ6sTo76wtZGqs9zWfo2d1nFoLQwZWwFoqjATsQk431-E3bvXsQ4KvmA1LoKoFL1a5RoZx9SIYV3MNWkslOXY2vcTX2ssnZfdrfPTVVbEMYMelUw==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0HJwatqkOE86kWdohl_KoRFVt5Pr8ix6gS4CFIajyFWbTPCO68ZGtAl5PdZYjPx8N0h_Hz_4oaMIUIpKvwZLLMeR2iFTHjh5N8Jhlj03OBrvD4LAiYJG6GSQ9fGUjNdYdmI6WEUJ_alsC3-3bvUt3uhUv3oHFlsMM8LEp_mwZnPKd7RpbICSchcl-80MQMAQlaVzUAFGWNzSKaSzFVlA=>
  - gilead.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEWO3qKxADqrU6sz_eBDnx9qNQwQeONto6khni7-OOOdJW1nSfB9MbPt8w7PkhJhhtVLGd62Ya_eF7DCyShs3BkoV3TFwFWfJB2zSCAFqf8XXVpAf1wLXy6BUuQxX_t2taLXXMg6Ed3Pbny4W_JYiZIE2CxMGne178vdt7jq1eW-gd-4HVQCfMjaykrhr29Lsqo6nTlo18P7-2G86EYkRM2mk2eai07N7V9Jc3bLHNcX0Fpo97D9vjm88zEp6umi4uNYuYjzpny>

[5] web search for 'FDA Tamiflu oseltamivir approval infants 2 weeks December 2012 children 1 year prophylaxis'; grounded search summary:
In **December 2012** (specifically December 21, 2012), the U.S. FDA updated the approved indications for **Tamiflu (oseltamivir phosphate)**:

---

### 1. Expanded Approval for Treatment (Infants ≥ 2 Weeks)
* **What was approved:** The FDA expanded Tamiflu's approval for the **treatment** of acute, uncomplicated influenza (with symptom onset within 48 hours) to include infants **2 weeks of age and older**.
* **Prior status:** Tamiflu was previously approved to treat influenza only in individuals aged 1 year and older.
* **Safety limit:** Tamiflu was **not** approved for infants younger than 2 weeks of age, as safety and efficacy had not been established in that newborn population.

---

### 2. Prophylaxis (Prevention) Remains for Ages ≥ 1 Year
* **Prophylaxis status:** The FDA did **not** approve Tamiflu for influenza prevention (post-exposure or seasonal prophylaxis) in infants younger than 1 year of age.
* **Approved age:** Prophylaxis remains restricted to individuals **1 year of age and older** (a pediatric prophylaxis indication first approved in 2005).

---

### 3. Key Clinical & Dosing Differences

| Indication | Approved Age Range | Dosing Approach |
| :--- | :--- | :--- |
| **Treatment** | $\ge$ 2 weeks of age | • **Infants 2 weeks to < 1 year:** Exactly calculated by weight (3 mg/kg twice daily for 5 days) using an appropriate oral syringe/dispenser.<br>• **$\ge$ 1 year:** Weight-tiered dosing. |
| **Prophylaxis (Prevention)** | $\ge$ 1 year of age | Weight-tiered dosing once daily (typically for 10 days for post-exposure prophylaxis). |

---

### Summary
The December 2012 FDA action **lowered the minimum age for treatment from 1 year down to 2 weeks**, while **leaving the minimum age for prophylaxis unchanged at 1 year and older**.
sources:
  - fiercepharma.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFCeRhaGGGEmfK_BPgA33tsI9tk_Ig53Zhjoz7B_JuSraRy942QeAVYQl2f8aJfkegGFKUe-FDK-6FTqOeidyfZ_z0jonbaVZQ04ekeCV_wNFYO2qHQ2Tj1UtO8uWwyaKmVPrgGprLrlDc8NCFVDmdkV2iN6xLQPtsCAxOnLGK1ZqYosfuXjE4FEY4voeuI0CvriRDTit-AHR3rQsQlHU9qWC-pcPJ8swq>
  - uspharmacist.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPNHueTs3JKpe_bV2ol2_ySUEWXg4q4qqYI7jWpTxf6fA9vM8zDPsqoLMvxeRJ6qrYICKPYKejtFlwBrYNxXAJXIVSY1wt94BuyQKq-M_9gUhPdKQZIKD229kQJ_3mKBOfJR8N06IeefDd7LzGbw==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMOooWMxDoXzRkh_4H-flqsy8epsJPRuIYDFDWreRbmeKWq3zDMDAUlfuP5qDxeYYcDujIOEwpmOCC9YdzxvGZ5CepV0Ag-iybjTeowPQYqGkf-t9bdXwmQsWkd4S4Psp37QJ4i99taaNgHn15rywbceNbPDDQ8LYtIehFKJ6vs8NDuCbz8KSlGAAlM-hXPnbbdLpQfylb4siyIjN5Sg==>
  - biospace.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVD_VVH3qsvqIkhOK1RoZFenIwZFJq-O333deeeGxNFomUBP5lroz1odYfqshQI33w9F_XquuE2kJtsv_vDRnGT7sCijr-3i-NqcOvoKsoYwEt0g627fcBJk1jhIuPuD2hxcvVf5RAe0k-pcztTbf0jemxqHAf>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQESBQ85PJgwQfoeQ6a9rFji54bX6fm9uaRwBmsA9iz8mY9sAPy1JL2ea0rY6ogdXSba2WE03KQyIxgWVf9yTpEz8tVXkJcijB4mzbwdQhhGLagBdmZ8Eqg0e7tDCmGAvtrN-A==>
  - umn.edu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHzH9aJ87ioG5p-HI0Y6QYm_RzLj8qAWFG9L73sSYGEEUKKAqEtxagAwD6lwUkI8DJLa5HSIbAP3oseTjAHG46Gpr6-VyAIXHe0bafNygmAycvYQ6al-ttFFgL_OlvgvrFu02X_w0kgQhuOm0aT7okRHVU2fFdS4LWZzoNzalYKhAFrp5oVa7h5WPs=>

[6] web search for 'CDC oseltamivir Tamiflu FDA approved treatment prophylaxis ages recommendations'; grounded search summary:
### Overview of FDA Approval vs. CDC Recommendations

While the U.S. Food and Drug Administration (FDA) establishes strictly labeled indications, the Centers for Disease Control and Prevention (CDC) and the American Academy of Pediatrics (AAP) provide clinical recommendations that extend beyond FDA labeling based on broader clinical evidence and emergency guidelines.

---

### 1. Treatment of Influenza

| Metric | **FDA Approved** | **CDC / AAP Recommendations** |
| :--- | :--- | :--- |
| **Approved / Recommended Age** | **$\ge$ 2 weeks (14 days) old** | **All ages, including neonates from birth (< 14 days old)** (off-label) |
| **Symptom Onset Timing** | Within **48 hours** of symptom onset | Best if within 48 hours; however, **treatment is still recommended after 48 hours** for hospitalized patients, those with progressive/severe disease, or those at high risk for complications |
| **Standard Duration** | 5 days (taken twice daily) | 5 days (longer courses may be considered for critically ill or immunocompromised patients) |

#### Key CDC Treatment Recommendations:
* **High-Risk Groups:** CDC recommends antiviral treatment as soon as possible for any patient with confirmed or suspected influenza who:
  * Is hospitalized.
  * Has severe, complicated, or progressive illness.
  * Is at high risk for influenza complications (e.g., children under 2 years, adults 65 and older, pregnant or postpartum individuals, immunocompromised patients, and persons with chronic conditions such as asthma, heart disease, diabetes, or neurological disorders).
* **Low-Risk Outpatients:** Antiviral treatment can be considered for any previously healthy person with uncomplicated influenza if treatment can be started within 48 hours of illness onset.

---

### 2. Chemoprophylaxis (Prevention)

| Metric | **FDA Approved** | **CDC / AAP Recommendations** |
| :--- | :--- | :--- |
| **Approved / Recommended Age** | **$\ge$ 1 year old** | **$\ge$ 3 months old** (use in infants 3 months to 1 year is off-label) |
| **Infants < 3 Months** | Not approved | **Not routinely recommended** unless the clinical situation is judged critical due to limited safety data |
| **Timing to Start** | Within 48 hours of close contact | Within 48 hours of close contact |
| **Standard Duration** | Once daily for **at least 10 days** post-exposure (up to 6 weeks in community outbreaks, or up to 12 weeks in immunocompromised patients) | Typically 7–10 days post-exposure, or for institutional outbreak control (e.g., nursing homes) for a minimum of 2 weeks and continuing up to 1 week after the last detected case. |

#### Key CDC Prophylaxis Guidance:
* **Not a Substitute for Vaccination:** The CDC emphasizes that annual influenza vaccination is the primary method for preventing flu.
* **When Prophylaxis is Used:** Post-exposure chemoprophylaxis is primarily considered for:
  * Persons at high risk of complications who have had close contact with an infected individual during their infectious period, especially if they cannot receive the vaccine, were vaccinated within the previous 2 weeks, or have significant immunosuppression.
  * Controlling institutional influenza outbreaks (such as in long-term care facilities or nursing homes) regardless of vaccination status.

---

### Standard Dosing Guidelines

* **Treatment (5 days, twice daily):**
  * **Pre-term / Neonates (< 14 days):** Dosing is weight- and gestational-age-dependent per CDC/AAP tables (commonly 3 mg/kg once to twice daily based on postmenstrual age).
  * **14 days to < 1 year:** 3 mg/kg per dose twice daily.
  * **$\ge$ 1 year (weight-based):**
    * $\le$ 15 kg: 30 mg twice daily
    * \> 15 kg to 23 kg: 45 mg twice daily
    * \> 23 kg to 40 kg: 60 mg twice daily
    * \> 40 kg (and adults): 75 mg twice daily
* **Prophylaxis:**
  * Uses the same single-dose milligram amounts based on age/weight, but administered **once daily** rather than twice daily.
  * *Note: Renal dose adjustments are required for patients with significant renal impairment.*
sources:
  - cdc.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLXKckyGPMezAe_vKcgW8b9BNIXuk-re9LDkKiuVsLGqh-RERxqerZKMbj_MJ5nPsuwYOhU-KYyE6DyhMsknqW2D-qIAUB-yVXC4GVBlopmvP3q5iTDWiMoyDnx3k8wKOINWssAcBYwKYhtzxngThGDxMDv2VfAN3JDjqAak0_>
  - cdc.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDZiGBT7lY6XVef0t3e73khmzMQ-rZYrx4InJR8dxTVp5bCWXmr7amd3aNcxu25tb6LghQN6otBKnODWWVbP4uoglWwyEWepWUO_7sMyeGlIeGaGNuZasoo3ad_xMjfEQs7VO-VvqQ780QnaiEktXXbmRLQQ0N0eZPUAxTigi0zBmcomEwZMfzgEpi>
  - fostercaretx.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFT9FHxTZ9ZUDt_s3RAnBhDD6hWROPjwS4CXqcwIhm4g_iYMKWjSRnLZiR38K5iIegCK3ErFOSqgucmy074iE_dwHuOa73t00oQEH9kOuBu1OdFFmWnHUDNF2HmuJhMf5DXHDWU52MdqUvGC8KG92MXkike1K6ROLpi4AD1TYjEsTzv-CkY0K1us7LDMif3vyWq9QEklp6rz9rqQNvroTRhRxtY5k50i3Nq4qJ2ZR7YY-IngpOzMz8vH8qMi9g=>
  - cdc.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQELDL3YQfyElKzjPalBTfL1DdOt8vZTw3bWMz2POzYAxal8IkpJJ4e4AVpTMaeAfPX7IWnE4BI7RWeiubJPQD1eau00ry8aJmmYOHXkBtR_tSOv0oUMnTmXXF_uK84dCvJG1hQB_kSF>
  - mayoclinic.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMGR1jKRmhq6fpahmQCNzgvSPQkhwrD2UnjNb5DLfcEFVWHUgClzWk1v99wMHQiRZsnLYo5Uhd90GQpfEUE2PcJvJ_jVgBrZpYv7fc5j010hi1heL9Pc72rgIN5FrLj3r01llr8a6jTVS4Hc8aoptDPsBpV-qMipc7eQxWZUsn7EirwIXn9htrfiJChYW_Qih8HQ==>
  - umn.edu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEx9Wpxvw-3oOzPvr-rurPxati9A2b3aNfiy-RMjJVkDgg5Kj5epvikCU3TmsDPbgQNmo-UWo0TdEIMAVMXtruuNdXp48iLpRr6WeAwZN-jPXGLal2QGKm5jj1O9ioMbNN21nI9qvppWpvDLX4bnAGyqynmKUdDkOvnevpeCic2jJIyoWKIHvuxZIWZ>

[7] web search for 'Tamiflu oseltamivir EMA European Medicines Agency approval 2002 Japan approval comparison'; grounded search summary:
A comparison between the European Medicines Agency (EMA) and Japan’s Ministry of Health, Labour and Welfare (MHLW) / PMDA regarding the regulatory approval and lifecycle of **Tamiflu (oseltamivir)** highlights key differences in approval timelines, scope, clinical uptake, and safety responses:

---

### 1. Regulatory Approval Timeline and Scope

| Feature | European Union (EMA) | Japan (MHLW / PMDA) |
| :--- | :--- | :--- |
| **Initial Treatment Approval** | **June 20, 2002** | **December 2000** (Launched early 2001) |
| **Initial Prophylaxis Approval** | **June 20, 2002** (approved simultaneously with treatment) | **2004** (Adults); **2009** (Pediatrics) |
| **Initial Age Indications** | Adults and children $\ge$ 1 year (treatment); $\ge$ 13 years (post-exposure prophylaxis) | Adults initially (2000); pediatric dry syrup approved later in **2002** |
| **Marketing Authorization Holder** | F. Hoffmann-La Roche | Chugai Pharmaceutical (Roche subsidiary) |

* **Europe (EMA)**: Roche initially filed for EU marketing authorization in 1999, but withdrew the application in 2000 due to regulatory requests for stronger efficacy data. Roche refiled in 2001 with expanded clinical data (including pediatric treatment and adult/adolescent prophylaxis), leading to a single comprehensive approval across member states in **June 2002**.
* **Japan (MHLW)**: Japan was faster to market than Europe, granting initial approval for adult treatment in **December 2000**. However, its expansion was staggered: the pediatric dry syrup formulation was approved in 2002, and prophylaxis was not approved until 2004 for adults and 2009 for children. Prophylactic use was excluded from national health insurance reimbursement.

---

### 2. Clinical Practice, Diagnostic Culture, and Uptake

* **Japan (Mass Outpatient Use)**:
  * Following its 2001 launch, Japan quickly became the world’s largest market for Tamiflu, accounting for **over 70% to 75% of global consumption** by the mid-2000s.
  * Japanese outpatient clinics made standard use of **rapid diagnostic tests (RDTs)** for influenza, enabling early diagnosis (within 12–48 hours). Tamiflu was routinely prescribed to healthy outpatients, adults, and children under the universal National Health Insurance system.
* **Europe (Conservative and Stratified Use)**:
  * Prescription uptake across Europe remained low compared to Japan. 
  * European national bodies (such as NICE in the UK) issued restrictive guidance, discouraging routine Tamiflu use for otherwise healthy individuals and reserving it predominantly for vulnerable, high-risk populations (e.g., elderly, immunocompromised). 
  * European interest focused largely on **national governmental stockpiles** for pandemic preparedness (such as H5N1 avian flu and 2009 H1N1) rather than routine seasonal outpatient prescribing.

---

### 3. Safety Signals and Divergent Regulatory Responses (2005–2007)

The most notable difference between the two regulatory environments occurred several years post-approval regarding **neuropsychiatric adverse events (NPAEs)**:

* **Japan’s Precautionary Suspension (March 2007)**:
  * Because Japan had by far the highest per-capita exposure to Tamiflu, Japanese pharmacovigilance picked up clustering reports of sudden delirious/abnormal behavior (e.g., hallucinations, running into traffic, falling or jumping from buildings) primarily in adolescents.
  * In **March 2007**, after several fatal falls involving 14-year-olds, the MHLW issued an emergency administrative action warning physicians **not to prescribe Tamiflu to adolescents aged 10–19 years** (except in high-risk scenarios). This restriction remained in effect for over a decade until epidemiologic reassessments in 2018 lifted the ban.
* **EMA’s Assessment**:
  * The EMA (along with the US FDA) monitored the Japanese reports but did not restrict the age indication.
  * The EMA’s Committee for Medicinal Products for Human Use (CHMP) concluded that a direct causal link between oseltamivir and abnormal behavior was not established, noting that high fever and influenza itself can cause delirium and encephalopathy. 
  * The EMA opted to update the Summary of Product Characteristics (SmPC) with precautionary warnings advising patients—especially children and adolescents—to be closely monitored for abnormal behavior, but kept the drug approved for all indicated age groups.

---

### Summary
While the **EMA took a deliberate route** (withdrawing in 2000 and approving in 2002 for a broad combined indication of treatment and prophylaxis), **Japan moved earlier in 2000** for treatment, using a piecemeal approach for pediatric and prophylactic uses. Japan’s extensive clinical use made it the primary epicenter for post-marketing neuropsychiatric safety signals, prompting aggressive age-specific restrictions by the MHLW that the EMA did not adopt.
sources:
  - europa.eu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_ZklP-xiQr00Te2x1EKk4H0R6paA_DjCGL1i__r4fxSBir7mOmM3ucSHBk95ab_-kkSdiFXDil48aOb_UtmWxl1AIv3Zuh31GV9a89-b91An3tpJpxBSJOb-hKlFKkfLhAX2xDykpEFVpaXscuEw=>
  - chugai-pharm.co.jp <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9YvVAEvb6P5ltS_y0y_BuZ3eN2Ysz6vQjLDzubr1l86RwSSTZQGL-Y1JHUN1b13_8te5o_UNeczRk3V_4BgWS86FwsF2DLpI0CJEfB941JOo8Sriv75s0Nm54er27vyh7a5WWAAtoCszZX6Vwl_Lf3jD1eck_VomS3No4WgXpYg==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGc_uZaoPNIZLHjL_pZxZzRMEumi1-JERYNBr1bhQPQNPHHSO3Bybk33HycFNfvmy1kOz0TQh0McqVuLxhXxwbV4WvNYva8JWLhvYmzu5kqAhUDQOExuZo8l1ISFXjVqfOwDCX2yRqU>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQgQcVAmk4nxf7eh17R4KhSs4str1T-08DWcACpPVU6bmtUcnp2d62nVdz7d36NrJsXJ15xZ4PBAOd39eBb4J6zs6tS9w5mELWuWukH_rQ93-m20ab9FBr5m6LldJ7dA==>
  - nao.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJkI7F5X1ziAmSipB20mNTrQkAZ5K37Mq7XvXIuJmxKNWUHFaOnInjDUHMGIXRQrZwEO6SrxFXiHWh_zWZwdOiqCTfUYJh9IhIipXIFE1rUo47zpU3NR9svBNS5xFpV4EkVcIbMBZgiYf4qfaPf155paJp60LhM30nf9_QgjrkH9TT6KOBeltRX8UzNpDzLWAOSa9fcu-mSY1rFQoaLqtaqlE83E6cSf9RRnSj-qeHC64NQhH6d_Uzyg==>
  - chugai-pharm.co.jp <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5_1RDOFnV7w2Pq-fCoPZsTXKhahQqok6fC1Rcm50BpQPQ6-_b6v7n5SpvifiDtcTcqlTML4vAJ2cdPdGCiwNBHYAJ1u2kDoW0ihnAbqJXWnEXlk76z7W0AEyBt33-EUYGxxT08saLSiZLjLUtLlZDmhnGuOjzJIyLM1OEe9Yqiim86eb6IEizk3MGarEd5NLMq34knm-92PC43rAikxk=>

[8] web search for 'Tamiflu EMA EPAR oseltamivir authorised European Union 2002 ema.europa.eu'; grounded search summary:
The European Medicines Agency (EMA) European Public Assessment Report (EPAR) details the regulatory background and approval of **Tamiflu** (oseltamivir) in the European Union:

---

### **Overview & EU Authorisation**
* **Trade Name:** Tamiflu
* **International Nonproprietary Name (INN):** Oseltamivir (as oseltamivir phosphate)
* **Marketing Authorisation Holder (MAH):** Roche Registration GmbH (originally Roche Registration Ltd)
* **EU Authorisation Date:** **20 June 2002**
* **EU Procedure Number:** EU/1/02/222
* **Regulatory Pathway:** Centralised procedure (granting a single marketing authorisation valid across all EU member states)

---

### **Pharmacological Classification**
* **Pharmacotherapeutic Group:** Antivirals for systemic use, direct-acting antivirals
* **ATC Code:** `J05AH02` (Neuraminidase inhibitors)
* **Mechanism of Action:** Acts as a prodrug of oseltamivir carboxylate, a potent and selective inhibitor of influenza A and B virus neuraminidase enzymes, preventing the release of newly formed viral particles from infected host cells.

---

### **Approved Therapeutic Indications (Summary)**

1. **Treatment of Influenza:**
   * Indicated for adults and children (including full-term neonates) presenting with symptoms typical of influenza when the virus is known to be circulating in the community.
   * Efficacy is established when treatment begins within **48 hours (2 days)** after symptom onset.

2. **Prevention (Prophylaxis) of Influenza:**
   * **Post-exposure prevention:** In individuals aged 1 year and older following exposure to a clinically diagnosed influenza case during community transmission.
   * **Pandemic / Special Situations:** Post-exposure prevention in infants younger than 1 year during a declared pandemic outbreak, or seasonal prevention when there is a mismatch between circulating strains and the vaccine.
   * *Note:* Tamiflu is not a substitute for seasonal influenza vaccination.

---

### **Key Assessment Highlights from the EPAR**
* **Clinical Efficacy:** Early clinical trials evaluated across Europe demonstrated that initiating oseltamivir within 48 hours of symptom onset significantly reduced the duration of illness (by approximately 1 to 1.5 days in typical cases) and reduced viral shedding.
* **Safety Profile:** The most frequently reported adverse effects include nausea, vomiting, headache, and abdominal pain (which typically occur on the first or second day of treatment and resolve spontaneously within 1–2 days).
* **Extensions / Updates Post-2002:** The marketing authorisation was renewed and subsequently updated several times—notably extending indications to younger paediatric populations (down to infants and full-term neonates) and clarifying guidance for pandemic preparedness.

Full EPAR documentation, product characteristics (SmPC), and assessment history are available directly on the [EMA Tamiflu Medicine Page (ema.europa.eu)](https://www.ema.europa.eu/en/medicines/human/EPAR/tamiflu).
sources:
  - europa.eu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGsShu9LvnXUp-e7ny0nst9PGrE4eJRYVUwhxHiW9m12lCzMVTkodVbvNASN7CXSXdHDeafMlF8qzSj5czjOdzwSUWZBSxq88s905hfExNAQ_ac2-WTQ8Bj3kLD-iXNj4dTnq_R6s_aA2rZO1FPzHM=>
  - nao.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBpwJzB_bBaNIfPfWOlZpyyPPkdkM4qo5XxzzL4dAaYG0nW8oWTW3juYvbDTxBQPosUVAGwBT6AcPJoRIxQFJNs5m1mgQJLjFOHPjiKO3ioJqX7eKCzKttfrlfFfMhgAJB1ONtXdgBTVaz0bj5X47PPo_VrgYm280N1xnkOYseeFeSd-_Hi_Lavej5M3KBWhGQD1eDXePn6LU6tcgXuIGr3fJv5RwPHYHfzNipaP7CaLN0dsLAO774Qg==>
  - europa.eu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExGyTKynTwEjiC0SxiI-t1OQvKPlIc9dGKjQUj-5qNblaUccTuJ8yeOXCfrgiRR4SFFeLgQrdkcpqaeIgV5wfx3LQRw1qG5assKt6sAngff-Rt0mLIFPFeBboCULsyD9Eca_Vkzt33zhnDYxNNkV8syx436DJOF8Qb28Ln>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGM4_pI3ac43mhiLPuk4Mgtzq0Xo4Opc5X1MZqK6kzUkPzcVa1UAMMlCRUwlYeuCvoo_fAkDvAZazD53eBzr4cZhfi3QKh4RhZYnqaZGckVgRGkxxJd-jOhjbOw_RmrwL70V4VJukYNeBHuPmvo_HUUv-WtI-n0X9LprzMs3AuAMWRWYnKDSItP>
  - europa.eu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEoYiNdu_J2dNF9v9_SacM_QdgbDDJIxLdBtRunSXjUZZFWlaV3NXOHPo85POjYcW_YMn_f3deOx6Qw1yd6EBzUa3Py3Yw_KmphutfLla3GZkXXsd_4eDe6cFJ9DpR3>
  - gilead.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGUqlhUmA-jUlPsehkk-zgtCBXWk7oLGjxlat7ZnV7SqElz2oQ4g6eAnFgv1qhuBWOsZJiEozsCQix9kjGtXV8D1FFrFuadDqtKXe60g_oyhVabibPkiUh3P21oZCdXd2e2-Y4lPPB1NXwGkmQsa9iJNPgcTiP5o6PaD1dFdFqKxmGdmTwx1t0ZIQj5Ht-0MeHv5Q==>

[9] web search for 'FDA press release December 21 2012 Tamiflu approved infants two weeks influenza'; grounded search summary:
On **December 21, 2012**, the U.S. Food and Drug Administration (FDA) issued an approval expanding the use of **Tamiflu (oseltamivir phosphate)** to treat influenza in infants as young as **two weeks of age**. 

Key details of the announcement include:

---

### 1. New Indication
* **Treatment Scope:** Tamiflu was approved to treat acute, uncomplicated influenza in infants **2 weeks of age and older** who have exhibited flu symptoms for no longer than 48 hours (2 days).
* **Milestone:** This made Tamiflu the first and only FDA-approved antiviral medication to treat flu infection in children younger than 1 year of age.

---

### 2. Key Limitations
* **Not Approved for Prevention (Prophylaxis):** The FDA emphasized that Tamiflu was **not** approved to prevent flu infection in infants younger than 1 year old (prevention remained approved only for patients aged 1 year and older).
* **Not for Newborns:** Safety and efficacy had not been established in infants younger than 2 weeks of age.
* **Vaccination:** The FDA reiterated that antiviral treatment is not a substitute for the annual influenza vaccine.

---

### 3. Dosing and Pharmacy Guidance
* **Weight-Based Dosing:** Unlike older pediatric age groups that use fixed-dose tiers, dosage for infants under 1 year must be calculated using exact weight (**3 mg/kg twice daily for 5 days**).
* **Dispenser Alert:** The FDA cautioned that standard dispensers co-packaged with Tamiflu suspension at the time were not calibrated for these milligram-per-kilogram doses, requiring pharmacists to provide an appropriately calibrated oral dosing dispenser to avoid medication errors.

---

### 4. Safety and Clinical Evidence
* **Clinical Basis:** The expanded indication was supported by pharmacokinetic and safety data from pediatric clinical trials funded by the National Institutes of Health (NIH) and Roche/Genentech, alongside extrapolated efficacy data from older children and adults.
* **Side Effects:** The most common adverse effects reported in pediatric patients were vomiting and diarrhea.
sources:
  - fiercepharma.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFc5cj6kkM1tMfoRfQOzpnY51DKqItwNyWKX4y9Y7Nri_dAWysFlpD6gJ7XZ_2uvD4sEy3gCSs36uZtesK5v9GkT7pDne_xfQ1QZ3Kp3hHA2Hzl_yLBVFy82ZC-qezTZQNyh728NQ7sk6R60ON7TP-dFOFV3n63WooJHeWPkG5Ev5QfO9hB3lf1SWOEZY50fpgtSZtIRAt-6DpFrtK7rhoAS4aFKQpQZIhN>
  - foxnews.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF2ax8XannafFylIeQPtM5UJtV9UaeT_21ngIM1vtKTMhKM6YKiTuUZbAcfudY0dcgvlAB4SZHfG4lrGP7lVE7N__ZrTifKwTIHAFKhKEw__rTvZ-Q2cveOd5I5dCKyqQIu8fixu_5LCY695DwBfd-VmhQoniHF4t5EbnD5FkYwcu4hZi9WqXLDWjI=>
  - uspharmacist.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFK7VIk948W_-5sl-oMGump1BTSAzqtC2zD9w0OCOQVC-dsaFMvqZ8YJ9pFjFbISEOTmuMQb6PlVcyRsWoOtP0etFy7q9Rr1az1pWM3IY5i0_z04eMKzyRNq1tXlIoB82oyKlIEdSgScRS9MATM6Q==>
  - gene.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeaw1ZQifYQkJeJ7LYZA4l3JbUvdLKOeW0gvQG1iXCRhMtgj5CoUUrFXei60Z7hPpbD9ZCHdD5JIm8dn6FYoJ50Y3_YR1-7bvFlkMCnZememntuYqSHII9B7TfrO6dOaMxemxOm_hl6KDaUbh3PDeUkIBj8CoN>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOKW6HFS_Km9RkJ2cbRD91lhS-6iSdIp0eFiW62C-iI9qwYwKqwS42uXBMtS1cQIchv5Lt1P4ZEx0wpPe4wjgG-For4bPXzqIAg6AaK-a4dpxhzL6QEEShUQX_PjtggwDmiciXHO4Oqdq2J-hCPFggrweAOPk7XzVDrOqB8l1fBABl0rMFvrktuSOqppG78WtZVw0As_bczSDhE-xUtQ==>

[10] web search for 'accessdata.fda.gov Tamiflu label oseltamivir NDA 021087 021246 prescribing information'; grounded search summary:
The FDA Prescribing Information for **Tamiflu (oseltamivir phosphate)** is filed under two New Drug Applications (NDAs) on the FDA Drugs@FDA database (`accessdata.fda.gov`):

* **NDA 021087**: Tamiflu Capsules (30 mg, 45 mg, 75 mg)
* **NDA 021246**: Tamiflu for Oral Suspension (6 mg/mL when constituted)
* **Original Sponsor / Applicant**: Hoffmann-La Roche Inc. / Genentech

---

### Key Prescribing Highlights

#### 1. Indications and Usage
* **Treatment of Influenza:** Indicated for the treatment of acute, uncomplicated illness due to influenza A and B infection in patients **2 weeks of age and older** who have been symptomatic for no more than **48 hours (2 days)**.
* **Prophylaxis of Influenza:** Indicated for post-exposure and seasonal prophylaxis of influenza A and B in patients **1 year of age and older**.
* **Limitations of Use:**
  * Not a substitute for annual influenza vaccination.
  * Not effective against illnesses caused by viruses other than influenza A and B.
  * Not recommended for patients with end-stage renal disease (ESRD) who are not undergoing dialysis.

---

#### 2. Dosage and Administration Overview

*Tamiflu can be taken with or without food; taking it with food may improve gastrointestinal tolerability.*

* **Standard Treatment Regimen (for 5 days):**
  * **Adults and Adolescents (≥13 years):** 75 mg orally **twice daily**.
  * **Pediatric Patients (1 to 12 years) by weight:**
    * $\le$ 15 kg: 30 mg twice daily.
    * > 15 kg to 23 kg: 45 mg twice daily.
    * > 23 kg to 40 kg: 60 mg twice daily.
    * > 40 kg: 75 mg twice daily.
  * **Pediatric Patients (2 weeks to < 1 year):** 3 mg/kg orally twice daily.

* **Standard Prophylaxis Regimen (for at least 10 days post-exposure):**
  * **Adults and Adolescents (≥13 years):** 75 mg orally **once daily**.
  * **Pediatric Patients (1 to 12 years):** Same weight-based dose tiers as treatment, administered **once daily**.

* **Renal Impairment:** Dose adjustments are required for patients with a creatinine clearance ($\text{CrCl}$) $\le 60\text{ mL/min}$.

---

#### 3. Dosage Forms & Strengths
* **Capsules:** 30 mg, 45 mg, and 75 mg.
* **For Oral Suspension:** 6 mg/mL (supplied as white powder requiring reconstitution with water by a pharmacist).

---

#### 4. Warnings and Precautions
* **Neuropsychiatric Events:** Influenza itself, as well as postmarketing reports during Tamiflu use, have noted abnormal behavior, delirium, hallucinations, confusion, and self-injury, primarily in pediatric patients. Patients should be monitored for signs of abnormal behavior.
* **Serious Skin/Hypersensitivity Reactions:** Severe cutaneous adverse reactions (SCARs), including Stevens-Johnson syndrome (SJS), toxic epidermal necrolysis (TEN), and anaphylaxis, have been reported. Discontinue Tamiflu immediately if an allergic reaction occurs.
* **Bacterial Infections:** Bacterial superinfections may present with symptoms similar to or complicating influenza; Tamiflu does not treat bacterial infections.

---

#### 5. Adverse Reactions
* **Most common adverse events ($\ge 1\%$):**
  * Adults: Nausea, vomiting, headache, abdominal pain.
  * Pediatrics: Vomiting, diarrhea, abdominal pain.

---

#### 6. Drug Interactions
* **Live Attenuated Influenza Vaccine (LAIV, intranasal):** Antiviral agents may inhibit replication of LAIV. Avoid administration of LAIV within 2 weeks before or 48 hours after oseltamivir administration unless medically necessary. (Inactivated influenza vaccines can be administered at any time.)

---

### Accessing the Label on FDA Drugs@FDA
To retrieve the complete, unabridged Prescribing Information and Patient Medication Guide:
1. Visit **[Drugs@FDA (accessdata.fda.gov)](https://www.accessdata.fda.gov/scripts/cder/daf/)**.
2. Search by Application Number **`021087`** (capsules) or **`021246`** (oral suspension), or search by the brand name **`Tamiflu`**.
3. Select the latest approval link under **Label Information / Label (PDF)**.
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFS92Rd1bGxn4ca4Kr4DLIigchMID11lN1nsOl_7kSg-4oOomJWS2A5jsPOT48HRmr1ub22DcuD0x3Qw3Orv5I5AjMlBCdZz7o3gCfRqakO13oxYRr0AhoRFDQdBk2LWCo8oe8aY7ybY50VXwRsK2rYWyxoN-DF52pJPqJOPRxE9-ak1Wi4fSMkiwFYH9fu2EJv>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5F-ZMTfZCj0ePUj5amO3FiHUSpMGw-D0lEA8RuBtFMdEQBCC9gHbwfCaG8Rnn221csDdqzApAwFLWlrM07RLjfS-TAt6eB-zROTBAVnxPP6VqsNw3lvy8DwAJ62tI7qDgqls3PUgKitkCzIlbEMk-eanayeWmPJXelIK7jqC8nMPh4JRHxBhV2uJfbWDNhN5BrGwfX5TQ7lWY5eYq3g==>
  - tamiflu.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcyKO131oL8g9aXOOm8SG4AY4QkxVvahpSq-OKHRkGprnRG_zRuHeogXaRdGpjktWYB_nQGDClufZar4b_gqqmpFtskdPLKT1Z21EFgkaNmxtvFrcj8AIZq0yE9Psq7Bs=>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbjDYOYw7c4vOZLb-FPqLu6IPDHQy16R-wYYXuT6lAfW7QdIUSLJtRVf-BV_6hGFA9XBZrDGxzMJnSRJl3SbCQD8Af-5aQBkTlFdGdfOubO8Zurb1EFgC3rqyZX6zsnu3YHwvcfhYdwm4MeSDAjHKeDhMH8Nsnf5AnGZMvCr_sjQ==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFy2R9p-oQQ9pqQm3CH0gKZvuvqKxjiXkQE5fcQjpoj73EStcFBCD39T-ErSlf1bWp0RGLhf0QggZhsqi7ThySoXPthFrG9WfZ8eUb_E1edJ4C3IRfSzXEE0FCDyRLgb3dW4wxpddfF4g2wKLhuUhgLcpKct9UEgF1C6vJCTJCVcw==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaF8Mzj8eWLbC-i7trHespIcehDmGP4OuZsl4ktX_Pt2-HyJ_MUU8TzdGzqq8MZ5bagJ2JlHrc3rdXTJb_twONU6iBUi5UWbTDS3jUOjoKZjKP8-8DZUbL_h2ozES7Qc9qZkMG9XIDNkn6YWliyRnYWXz3qRDohGHJzFuvVTQgEA==>
```

</details>

**Answer:**

## Short answer

**The U.S. FDA first approved oseltamivir (brand name Tamiflu) on October 27, 1999** — as capsules (NDA 021087), sponsored by Hoffmann-La Roche, for treating uncomplicated influenza A and B in adults who had been symptomatic for no more than 48 hours.

## Details from the public search

| Item | Finding |
|---|---|
| First FDA approval date | **October 27, 1999** |
| Product / NDA | Tamiflu capsules, **NDA 021087** (30, 45, 75 mg) |
| Oral suspension | NDA **021246** (6 mg/mL) |
| Applicant | Hoffmann-La Roche Inc. (originally developed by Gilead Sciences, licensed to Roche) |
| Original indication | Treatment of uncomplicated influenza A/B in adults ≥18 years, symptomatic ≤2 days |
| Prophylaxis | **Not** in the original 1999 approval; added later (~Nov 2000 for adults/adolescents ≥13) |

Reported later FDA actions (treat as unverified — see caveats): pediatric prophylaxis extension (~2005), added capsule strengths (~2007–2008), and a **December 21, 2012** expansion of the treatment indication to infants ≥2 weeks of age.

For context on other regulators: the **EMA authorized Tamiflu on June 20, 2002** (centralized procedure EU/1/02/222), covering treatment *and* prophylaxis. Earlier Japanese approval (~December 2000) was reported only by secondary sources.

## Caveats — please note

- The search tool returned results aggregated at the **domain level** (fda.gov, accessdata.fda.gov, ema.europa.eu, etc.) rather than raw deep links. The date, NDA numbers, and applicant were consistently reported, but the **day-level 1999 date and the subsequent approval history were surfaced via summaries, not the original approval letters**, so they should be confirmed against the primary Drugs@FDA documents.
- The **EMA date (June 20, 2002) is well-attested**; the **Japan dates are unverified** (mixed-quality secondary sources, not confirmed against the PMDA).
- The direct source URLs the agent supplied are the standard destination pages (listed below), not confirmed deep links.

## Sources supplied by the agent (canonical pages to verify)

- Drugs@FDA — Tamiflu (NDA 021087): https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=021087
- Drugs@FDA — Tamiflu Oral Suspension (NDA 021246): https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo=021246
- Drugs@FDA search portal: https://www.accessdata.fda.gov/scripts/cder/daf/
- EMA — Tamiflu EPAR: https://www.ema.europa.eu/en/medicines/human/EPAR/tamiflu
- DailyMed — Tamiflu label: https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=tamiflu
- CDC — Influenza antivirals: https://www.cdc.gov/flu/treatment/antiviral/index.html

## Notes on this task

This was a public-information question only, so I consulted the **Network Search Agent** alone. No internal records, inventory, sales data, or knowledge-base documents were queried, and no company data was sent to the public search — only the drug name "oseltamivir." No files were found in the working directory and no report file was created. If you'd like, I can commission a follow-up search to pull the exact text of the 1999 approval letter or the 2012 FDA press release.

---

## 16. route-13 (routing, medium)

**Question:** Which company originally developed Lipitor?

**Gold answer:** Parke-Davis (Warner-Lambert), later Pfizer.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[1] tool ls returned:
No files found

[3] web search for 'Which company originally developed Lipitor atorvastatin discovered by'; grounded search summary:
* **Originally Developed By:** **Parke-Davis** (a division of **Warner-Lambert**).
* **Discovered By:** **Bruce D. Roth**, a medicinal chemist who first synthesized the compound in 1985.

---

### Additional Context
* In 1996, Warner-Lambert partnered with **Pfizer** to co-promote and market the drug. 
* In 2000, Pfizer acquired Warner-Lambert in a hostile takeover for approximately $90 billion, primarily to gain full ownership of Lipitor, which went on to become one of the top-selling prescription medications in pharmaceutical history.
sources:
  - oup.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGYmGMK2Mt7oNO6APMdRf3luRbljgXlQBYyfbxfxqaHr4unA-APBt1YaDpOZyoa8-yWZQXgyVevxxeHO89AGK-DG7KkvL-VU2x4Sdb5Yrm7ia1peFPNN-eZgjRoA_Nep1O79HONIwHMRChqdA==>
  - pmlive.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGr_yubEIC2OFQZ-T4XJZ3oWsvaK-BiyuU9-a9cRr6qebdXCrsm4vsz026uBgm19ITRZfES-3vJHyAqoJnRSGIOtkr11Rd_cVzU4g4VIEvChX_7biReYI703afyCrwOm9n9tfZC-xYcC84G_xvzoCAvSDFFo0CZnU_z1xHn1qwVdYEWhEBNTiGwNo_uTYpq_h0=>
  - the-scientist.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQECojNnXjR1NFX2U5iDoIZnWCnde17KzMnhytQ7OXpvFeNVzTPlHTlyBJnsgwSCi5K4APjBX6OTecYyyqN8jIReSkCHKmoPk3WAIxnIF5b2abpAqAHyusOtgMfT3mK8uyrlx8d5WsANS0UXoLAm_SyB>
  - soci.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmt-DgBVX_sYKWNnKNwZL-zD8AwBxKlk_BairPK2QmzR_jhA-M9Abj0tKfOrsLkq1tjHLfORm5CfXZNNW4AdnrI2R1uxUSfGcvP3JosfytCQ-YdwAlgfdOKyqevrwgJZEDmsmygNNkYcEnmajN>
  - gene.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_dIF0x-cvvi_SlHCss_n1I37Q5bfzeTc2FWJNWxob--UwjDz287bJMPQUgXKaxRrgbmQhYAcRbmrzljEPXCjS0IV0-KKZ8YujjfpHdy2duVNzWmR0cHR3oMAlRrr0WnIZxuei8R3dt9_e>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBPUPJE9cVYCUcOktKjSwr_wUe12D98U0do7YQQ5khYcifX9MjWqakJZkc8tFyi9785dX3G8BCuHYkLZFtkkN-HF6kuxgFOyJPsDp3RUGL0cdo_2UnYTKIS8Q_ekhx>

[4] web search for 'Lipitor atorvastatin Warner-Lambert Parke-Davis discovery chemists Bruce Roth FDA approval 1996'; grounded search summary:
The keywords you provided tell the story of the creation, development, and launch of **Lipitor (atorvastatin)**, which went on to become the best-selling prescription drug in pharmaceutical history. 

Here is an overview of how these elements connect:

---

### 1. The Discovery & Bruce Roth
* **The Chemist:** In 1982, organic chemist **Dr. Bruce Roth** joined the pharmaceutical research division of **Warner-Lambert / Parke-Davis** in Ann Arbor, Michigan.
* **The Breakthrough (1985):** Roth was tasked with synthesizing novel, fully synthetic inhibitors of the enzyme **HMG-CoA reductase** (the rate-limiting enzyme in cholesterol biosynthesis). Existing statins at the time (like lovastatin) were derived from fungal fermentation. In 1985, Roth synthesized a chiral pyrrole derivative designated as **CI-981**, which later became known generically as **atorvastatin**.

---

### 2. Overcoming Early Hurdles at Parke-Davis / Warner-Lambert
* **Internal Resistance:** Atorvastatin was the fifth statin to enter the pharmaceutical pipeline. Because rivals (such as Merck’s lovastatin and simvastatin, and Bristol-Myers Squibb’s pravastatin) were already on or nearing the market, Warner-Lambert executives questioned whether a "me-too" fifth statin was commercially viable.
* **Clinical Outperformance:** In early Phase I and Phase II clinical trials, atorvastatin demonstrated a dramatic, dose-dependent reduction in low-density lipoprotein cholesterol (LDL-C)—often lowering it by 40% to 60% at higher doses, outperforming competitors at comparable doses. It also significantly lowered triglycerides, which earlier statins did not do effectively. These results convinced leadership to fast-track development.

---

### 3. FDA Approval (December 1996)
* **The Approval:** On **December 17, 1996**, the U.S. Food and Drug Administration (FDA) approved atorvastatin calcium under the brand name **Lipitor** for the treatment of hypercholesterolemia.
* **Market Entry:** Lipitor officially launched in the United States in early **1997**.

---

### 4. Commercial Partnership and Legacy
* **The Pfizer Partnership:** Recognizing the immense scale of the market and the clinical strength of Lipitor, Warner-Lambert partnered with **Pfizer** to co-promote the drug, deploying one of the largest sales and marketing campaigns in pharmaceutical history.
* **Pfizer Acquisition (2000):** After a hostile takeover battle against American Home Products, Pfizer acquired Warner-Lambert in 2000 for roughly **$90 billion**—primarily to secure full, exclusive ownership of Lipitor.
* **Impact:** During its patent-protected lifecycle (which ended in late 2011), Lipitor generated over **$125 billion** in sales, becoming the first prescription medication to surpass $10 billion in annual revenue. Bruce Roth received numerous honors for the discovery, including the Perkin Medal in 2013 and the American Chemical Society’s Heroes of Chemistry Award.
sources:
  (none)

[5] web search for 'Atorvastatin Wikipedia discovery Parke-Davis Bruce Roth 1985 FDA approval December 1996'; grounded search summary:
The details of the discovery, development, and approval of **atorvastatin** (most famously marketed under the brand name **Lipitor**):

---

### **1. Discovery (1985)**
* **The Scientist:** Atorvastatin was first synthesized in **1985** by American medicinal chemist **Bruce Roth**.
* **The Company:** Roth was working at the pharmaceutical research division of **Parke-Davis**, which was a subsidiary of **Warner-Lambert** (located in Ann Arbor, Michigan).
* **The Class:** It belongs to the class of drugs known as **statins** (HMG-CoA reductase inhibitors), which work by blocking the rate-limiting enzyme in cholesterol biosynthesis in the liver.

---

### **2. Development & The Decision to Continue**
* **The Challenge:** By the late 1980s, several statins were already either on the market or far along in clinical pipelines (notably Merck's lovastatin and simvastatin). Internally, Parke-Davis debated whether developing a fifth statin ("me-too" drug) was financially viable.
* **The Breakthrough:** Early clinical trials in the early 1990s showed that atorvastatin had significantly higher potency and produced substantially greater reductions in low-density lipoprotein (LDL, or "bad" cholesterol) and triglycerides at comparable doses than any existing statin on the market.

---

### **3. FDA Approval (December 1996)**
* **Approval Date:** The U.S. Food and Drug Administration (FDA) approved atorvastatin calcium under the trade name **Lipitor** on **December 17, 1996**.
* **Launch:** It officially launched in the United States in early **1997**.

---

### **4. Commercial Impact & Pfizer Acquisition**
* **Co-Promotion:** Warner-Lambert entered into a co-promotion partnership with **Pfizer** to market Lipitor.
* **Hostile Takeover:** Following Lipitor's massive commercial success, Pfizer launched a hostile takeover of Warner-Lambert, completing the acquisition in **2000** for approximately $90 billion, largely to gain full rights to Lipitor.
* **Legacy:** Lipitor became the best-selling prescription drug in pharmaceutical history up to that time, generating over **$125–$130 billion** in global sales during its years under patent exclusivity before going off-patent in late 2011.
sources:
  (none)

[6] web search for 'Bruce Roth ACS Heroes of Chemistry atorvastatin Parke-Davis Warner-Lambert'; grounded search summary:
These keywords describe the discovery of **Lipitor (atorvastatin)** by medicinal chemist **Bruce D. Roth** at **Parke-Davis / Warner-Lambert**, and his subsequent recognition as an **ACS Hero of Chemistry**.

---

### 1. Bruce Roth and Parke-Davis / Warner-Lambert
* **The Role**: After completing his Ph.D. at Iowa State University and postdoctoral work at the University of Rochester, Dr. Bruce Roth joined the Atherosclerosis Chemistry Section of the Parke-Davis Pharmaceutical Research Division of Warner-Lambert (in Ann Arbor, Michigan) in 1982.
* **The Synthesis**: In **1985**, at the age of 31, Roth first synthesized the compound designated **CI-981**, which would become known generically as **atorvastatin**. 

### 2. The Breakthrough of Atorvastatin (Lipitor)
* **Design & Mechanism**: While first-generation statins (such as lovastatin and pravastatin) were derived from fungal metabolites, atorvastatin was a completely synthetic inhibitor of the enzyme **HMG-CoA reductase**, which controls the rate-limiting step in cholesterol biosynthesis. It features a central pyrrole ring decorated with functional groups designed to mimic the transition state of the substrate.
* **Clinical Efficacy**: Despite entering a crowded market as the fifth statin approved in the United States, atorvastatin proved to be substantially more potent and effective at lowering LDL cholesterol and triglycerides than competitors. 
* **Market Impact**: 
  * Approved by the FDA in late 1996 and launched in 1997, it was co-marketed by Warner-Lambert and Pfizer.
  * The explosive success of the drug was the primary driver of **Pfizer’s $90 billion hostile takeover of Warner-Lambert in 2000**.
  * Marketed as **Lipitor**, it became the best-selling prescription drug in history, generating more than $140–$150 billion in lifetime sales and significantly reducing cardiovascular morbidity and mortality worldwide.

### 3. ACS Heroes of Chemistry Recognition
* **The Honor**: In **2008**, the American Chemical Society (ACS) recognized Bruce Roth as an **ACS Hero of Chemistry** for the discovery and development of atorvastatin. 
* **Award Significance**: The *Heroes of Chemistry* award is given annually by the ACS to honor industrial chemical scientists whose work has led to the development of commercialized products that dramatically benefit humanity and public health.
* **Other Recognitions**: Roth was also awarded the **ACS Award for Creative Invention** (2003) and the **SCI Perkin Medal** (2013), the highest honor given in the U.S. chemical industry, for the same breakthrough.
sources:
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH02YeOzTu75v7gvvy_7GTXWkGcdPhqaLZfXJ4gbtbqOQnFHhkI90aBvogZoQ8FpBodFckbcYkjO73uiXNbd6gX_YNtPSR-Zd5iN7OFaq4wACbvdC2YatOhzagZkvI=>
  - vcs.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBM5Ru_yYp9ec6xCRZH2UrEQ1G4cK6zcomAGwSiLiU3d-G6nQAeVayBrVOThtAVq8VcJnpVYXZfW18PvBvDTRTOAlw_v6ot0wlO2nlYLnBm5cAyWe8ZPPVw8Lf_i_MFAusGzcm8yMhYcEVcRft_oZGpozTJA==>
  - soci.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvU9TS64xuLIbZkwoNWTAMNnClI1XgCeFNBzt1PxF8JF_cFCddY_KI6ZB3i1n9HirbmjpZmyC7LQR-iQru7Ox7YLcjiIhBpw_njK2q-x8fEs_SOrBtDwd6kd27Rp5zs3ZyRHIMdE0ss8dVf_c=>
  - substack.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEsL6aS_bEOlkAI7iXvkaZHkGLyGwpeD72BFGQ0_gNSRSfFhe94RseMVTp0EkInyqc89aqnW9qJyrUEJqfM6xIYj72mXfJAUKxPdfd96WrOaajdLR29PMpRYEtqe53lxP6bt_rqk9_AJ2dboJV2wEJtL_pwKDCrmoQ=>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFU8YTKs9quffr6Wh0nmCbkHD_CDIpDDtLUPmWZYl1eUl1kEoItbz1WkZteozeEKhRBmORQUHVESDnmmh9wbDXLxpWazTbA2X1c_y5DcR5nSqxegwaN1NrkWIn-zV-FxSjsyGDpPrjQ6kHlatWzMeiX9I1PMsePDBbRguXwlSyhf81K0zRUIf0-Vcx-wjl9awKekAO6ebdAvkQr2zVsp0dS3ty2u-RRutXN9MyM9q8E9o5QXvdm-HQ7Nog=>

[7] web search for 'Lipitor atorvastatin Pfizer Warner-Lambert acquisition 2000 history'; grounded search summary:
The acquisition of **Warner-Lambert by Pfizer in 2000 for approximately $90 billion** remains one of the largest and most consequential hostile takeovers in corporate history. At the center of this battle was a single molecule: **atorvastatin**, marketed as **Lipitor**, which went on to become the best-selling prescription drug in pharmaceutical history.

---

### 1. The Discovery and Doubts (1980s)
* **Parke-Davis & Bruce Roth:** In 1985, chemist Bruce Roth synthesized atorvastatin at Parke-Davis, the pharmaceutical research division of Warner-Lambert in Ann Arbor, Michigan.
* **The "Fifth Statin":** At the time, statins were a crowded field. Merck had already pioneered the class with Mevacor (lovastatin) and Zocor (simvastatin), followed by Bristol-Myers Squibb's Pravachol (pravastatin) and Novartis's Lescol (fluvastatin). 
* **The Breakthrough:** Atorvastatin initially faced skepticism internally, but early clinical trials revealed it was far more potent at lowering low-density lipoprotein (LDL) cholesterol across a wide dose range than any competing drug.

---

### 2. The Co-Promotion Alliance (1996)
* Despite having a potentially revolutionary drug, Warner-Lambert was a mid-sized pharmaceutical company that lacked the global commercial footprint and primary-care sales force needed to challenge Merck's dominance.
* In **1996**, Warner-Lambert entered into a **co-promotion agreement with Pfizer**. Pfizer had built what was widely regarded as the most aggressive and effective sales force in the industry.
* Under the deal, Pfizer agreed to help market Lipitor in exchange for a significant cut of the profits (initially around 50% in the U.S.).

---

### 3. Explosive Launch (1997–1999)
* Lipitor received FDA approval in December 1996 and launched in early 1997.
* Driven by Pfizer’s marketing engine and superior clinical data on cholesterol reduction, Lipitor became an unprecedented blockbuster:
  * It reached **$1 billion in global sales in its first full year**, faster than any drug in history up to that point.
  * By 1999, it was generating nearly $4 billion annually and was on track to become the world's top-selling drug.
* However, tensions grew between the two companies over long-term control, marketing expenses, and profit-sharing.

---

### 4. The 1999–2000 Hostile Takeover War

#### The Trigger: The AHP Merger
On **November 4, 1999**, Warner-Lambert shocked the industry by announcing a friendly, $72 billion "merger of equals" with **American Home Products (AHP)** to create a company called "American Warner." 

#### Pfizer’s Hostile Counter-Bid
Pfizer’s CEO, **William C. Steere Jr.**, recognized an existential threat:
1. Under the co-promotion contract, Pfizer believed a change in control of Warner-Lambert might disrupt Pfizer's rights to Lipitor or dilute its value.
2. Pfizer did not want to share the world's most lucrative drug with a combined Warner-Lambert/AHP rival.

Within hours of the AHP announcement, Pfizer launched an **unsolicited hostile counter-bid of $82.4 billion** in stock.

#### The Three-Month Battle
* **Hostility & Lawsuits:** Warner-Lambert’s CEO, Lodewijk J.R. de Vink, fiercely resisted Pfizer. Warner-Lambert sued Pfizer, alleging Pfizer breached their marketing contract. Pfizer countersued to invalidate Warner-Lambert’s "poison pill" and breakup fees.
* **Bidding War:** Pfizer steadily raised its offer, putting immense pressure on Warner-Lambert’s board from institutional shareholders who favored Pfizer's higher stock price.
* **The Surrender (February 2000):** Realizing resistance was futile and shareholder sentiment was heavily on Pfizer's side, Warner-Lambert terminated its pact with AHP. 

On **February 7, 2000**, Warner-Lambert accepted Pfizer’s revised offer, valued at approximately **$90 billion** in stock (often quoted up to $116 billion based on peak stock valuations around closing in June 2000).

#### The Historic Breakup Fee
As part of abandoning the deal with American Home Products, Pfizer/Warner-Lambert had to pay AHP a **$1.8 billion breakup fee**—at the time, the largest breakup penalty ever paid in corporate history.

---

### 5. Aftermath and Long-Term Impact

1. **Pfizer Became #1:** The acquisition instantly made Pfizer the largest pharmaceutical company in the world by revenue and market capitalization, a position it held for much of the following two decades.
2. **Lipitor’s Phenomenal Run:**
   * Fully owning the drug paid off massively. At its peak in 2006, Lipitor alone generated nearly **$13 billion in annual sales**, accounting for roughly a quarter of Pfizer’s entire revenue.
   * During its patent life (which expired in the U.S. in November 2011), Lipitor generated more than **$125–$130 billion in cumulative sales**, making it the most commercially successful pharmaceutical product of its era.
3. **Restructuring and R&D Consolidation:** The merger resulted in heavy consolidation, including job cuts and the eventual downsizing/closure of legacy Warner-Lambert/Parke-Davis facilities (such as the Ann Arbor research complex in 2007).
4. **Precedent for Big Pharma Mega-Mergers:** The deal cemented the playbook of using large-scale mergers and acquisitions to acquire late-stage or existing blockbusters to drive revenue growth, paving the way for Pfizer’s subsequent acquisitions of Pharmacia (2002) and Wyeth (2009).
sources:
  (none)

[8] web search for 'ACS "Heroes of Chemistry" Bruce Roth atorvastatin Lipitor award'; grounded search summary:
**Dr. Bruce D. Roth** was named an **American Chemical Society (ACS) “Hero of Chemistry” in 2008** for his discovery and development of **atorvastatin**, widely known by its brand name **Lipitor**.

---

### Key Details of the Discovery and Award

* **The Discovery (1985):**  
  Roth first synthesized atorvastatin in 1985 while working as a young medicinal chemist at Warner-Lambert’s Parke-Davis research facility in Ann Arbor, Michigan (later acquired by Pfizer). 
* **Mechanism and Impact:**  
  Atorvastatin is a synthetic statin that inhibits the enzyme HMG-CoA reductase, playing a crucial role in lowering low-density lipoprotein (LDL) cholesterol and preventing cardiovascular disease. It demonstrated superior efficacy in lowering LDL and triglycerides compared to earlier statins on the market.
* **Commercial and Clinical Significance:**  
  Approved by the FDA in late 1996 and launched in 1997, Lipitor went on to become the bestselling prescription drug in pharmaceutical history, with cumulative sales exceeding $130 billion over its lifespan and millions of patients benefiting worldwide.
* **The 2008 ACS Honor:**  
  The ACS *Heroes of Chemistry* program honors chemical scientists whose work leads to commercialized products that significantly improve human health, the environment, and the welfare of society. Roth received the award in August 2008 at the ACS National Meeting in Philadelphia.

---

### Additional Recognition
Beyond the 2008 Heroes of Chemistry award, Roth's invention of Lipitor earned him numerous prestigious honors in chemistry, including:
* **ACS Award for Creative Invention** (2003)
* **Gustavus J. Esselen Award for Chemistry in the Public Interest** (2003)
* **SCI Perkin Medal** (2013) – the highest honor in the U.S. chemical industry
* Induction into the **ACS Medicinal Chemistry Division Hall of Fame**
sources:
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF82PBSW1yaxLuiWP33-fkpMmlPeM1P18cqaLmYQvkTP1TO4iy0nyHyhLBC-P4xivdF_svn-dU9F7DwVLsekvQcIyY5bJCswre19FkqiR3wel5OygsVPhkAQERbUUk=>
  - vcs.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlyeT4j8T6HYU9amnqjZhXfBdhpG51VPAFUmIfHl_3TCZcOKNnWly-mI2q0HRONVv20f9KstbwIDjUgipMBZ2POAnqBaA20jIeCvSHERWfz0Jd4BTWGVM-esVEVGbS9VUJYupxdGWiYqkRu93Uz_N69IK03A==>
  - soci.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9l5-guKU3_JrcxW3885g3im4IEbnvCufC6Jkb3rxBhgAUGsF2NW6zY0P0dNVfeys-otSBP-Pbietn5ZCLZNwdpl3kp6oe5ydzr9Kc6q2GXXsKfeXn5OH1mwcIRGdaWSn3vALHM5JhUB6544g=>
  - gene.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH11S_MuRsT8sfJiXmPgD7pUl7iMD6o6wG0s1skBldY4EmJQqmqSnudl7OeWPRuMbXSG5uDNPXWyvO9LkuXT93g-WhdP--3n4J7gMo5QQQV7obQsIrkMDk48rWg_05ormlB7veMPCBuwOM=>
  - newdrugapprovals.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3Su1sESJBYF7NvAQDpOukJDbj12zF9StR0X5QR7LVjWpMSS9pqJjfCGsRdNYLj81pZx9VWrahIRuQr0Z_VhKFyicRuby9a4TnBHljxkNVd-w4FUiKn8189aD0oC2GrtISd95qhEo87HcuR1HcuVZz_KYaww==>
  - acs.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2SXsVh8ph9SlZ1COIWbiWlxF_1YTGG_MxyEA5nRuig4IS_NBqw9Uh5TdvuTqf0IgNimVA7Dm76aCEhKYE2bhPCXEWWxkl9kBcsJNCarRiggLOz_heliWE_tqqUkIsydJ9ZhxIOZsZm-sWe6rPGhuJopjBifGVAjjE7l2U6jogBIxeJdlrjR9M>
  - aarviktx.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJyoGyFywa7g6hiA5u5IykLBccKbqS2fH-f0su62V-J7ePwBIgz0GZMG_8lTRp_5WNL7j_E5I0SmLigq9tl-c78-y9nnAKNFAchVwE_xsbu_Qnj10odwHaLh9v>

[9] web search for 'en.wikipedia.org Atorvastatin history Parke-Davis Bruce Roth'; grounded search summary:
According to English Wikipedia's articles on **Atorvastatin** and **Bruce Roth**, the history of the drug’s discovery and development at Parke-Davis includes the following key details:

---

### 1. Discovery (1982–1985)
* **Background:** In 1982, American medicinal chemist **Bruce D. Roth** joined the Parke-Davis pharmaceutical research division of **Warner-Lambert** in Ann Arbor, Michigan. In 1984, Roth became chemistry co-chair of the company's statin research team alongside biologist Roger Newton.
* **Synthesis:** In August 1985, at the age of 31–32, Roth synthesized an experimental compound designated **CI-981**, which would later be named **atorvastatin**. The molecule was designed to inhibit HMG-CoA reductase, the rate-limiting enzyme in cholesterol biosynthesis.

---

### 2. Internal Skepticism & "Me-Too" Concerns
* At the time, Warner-Lambert management was hesitant to commit significant resources to CI-981. They considered it a potential "me-too" drug entering a market already dominated by Merck & Co., which had introduced the first commercial statin, lovastatin (Mevacor), and was well advanced in developing simvastatin (Zocor).
* Despite corporate doubts, Roth and research leaders **Roger Newton** and **Ronald Cresswell** persuaded Warner-Lambert executives to advance the compound into clinical trials.

---

### 3. Clinical Success and "Turbostatin"
* **Clinical Superiority:** Early clinical trials demonstrated that CI-981 lowered low-density lipoprotein (LDL) cholesterol significantly more effectively at equivalent or lower doses than existing statins, while maintaining a favorable safety profile.
* **Public Unveiling (1994):** In October 1994, Parke-Davis presented human trial data at a cardiovascular conference in Montreal. The LDL-lowering efficacy was so pronounced that an executive from competitor Merck famously remarked it should be called *"turbostatin"*.

---

### 4. Commercialization and the Pfizer Acquisition
* **FDA Approval (1996):** Atorvastatin was approved by the U.S. FDA in late 1996 and brought to market under the brand name **Lipitor** in 1997.
* **Pfizer Partnership and Takeover:** Warner-Lambert initially partnered with Pfizer to co-market Lipitor. After Lipitor quickly grew into an unprecedented blockbuster, Pfizer launched a hostile takeover of Warner-Lambert, acquiring the company in 2000 for approximately $90 billion to gain full ownership of the drug.
* **Legacy:** Lipitor became the best-selling prescription medicine in pharmaceutical history, generating over $125 billion in sales during its patent exclusivity (which expired in the U.S. in November 2011).

---

### 5. Recognition for Bruce Roth
For his discovery of atorvastatin, Bruce Roth received numerous major chemical and pharmaceutical industry awards, including:
* **ACS Award for Creative Invention** (2003)
* **ACS Hero of Chemistry** (2008)
* **Perkin Medal** (2013), the highest honor in the U.S. chemical industry
sources:
  - vcs.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGN7H2qiGaGM6z0hbmoN4puGD9y0PJWYv2lCCSySl_2scHeL5a1ndzSd5bS7GD0_V5vHS4WigfpsMSp93D_lgoBW7SHHzEuPLHs7rxjyOqfAiJSBj7inzv4cWu7Q5nfBXLSFFIvh1khXVHLl3qAZjRhMW8YtmE=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGzeGNrmGg9e66weiE368VDdebrrknRThBW2auznR30PyblT-ziyyCVIJx9CxD0DIueUq0-fFLyKsswSqywLhPOoZoVFnbZ0HGhokSlxuNkP38revOsr79OaGWXAxu>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDLCwfqDdML4HzyeMlYIvjRZ4PQzbxy2SyGhtU6imk6_yxKVj_aglECPJ8yTqSCKFZKzlv07d_jBCHS5bmOiGRyYGzX8Gxu1BuXUbM4M8-nRcY9SGXu2U4Zg47CspR>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy71eT6Q9b0Jl20B62MF82MrPlFjKBYDR4BSqNvAxhBTW90xoAgn0-cJ99H8xgqjCDwVxgzIIcqF4pObjz6l4zppCgwRv6RlPm45rkEIXZnx7xquRvvuDhTC57RampOPg=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGzeGNrmGg9e66weiE368VDdebrrknRThBW2auznR30PyblT-ziyyCVIJx9CxD0DIueUq0-fFLyKsswSqywLhPOoZoVFnbZ0HGhokSlxuNkP38revOsr79OaGWXAxu>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy71eT6Q9b0Jl20B62MF82MrPlFjKBYDR4BSqNvAxhBTW90xoAgn0-cJ99H8xgqjCDwVxgzIIcqF4pObjz6l4zppCgwRv6RlPm45rkEIXZnx7xquRvvuDhTC57RampOPg=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHy71eT6Q9b0Jl20B62MF82MrPlFjKBYDR4BSqNvAxhBTW90xoAgn0-cJ99H8xgqjCDwVxgzIIcqF4pObjz6l4zppCgwRv6RlPm45rkEIXZnx7xquRvvuDhTC57RampOPg=>
  - pmlive.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJLVfbfEINiL5T8k9rE6sRt7V_OgLJaRR9INTa8gClEGbJ51uxJTrx5MsYJIhqelao4lK45jCali_EEHv3hkQK7l_bpDpqc7s6qFZPq7KhYQg2wwZ0WJJ8Q9JheLHTaC44P9NtTzy2P_GRtYpPc6ODpVZUzb9fWqakLPzQaXchtZb-KtNU5az91ZApq0UvexU=>

[10] web search for 'Pfizer Warner-Lambert merger 2000 Lipitor press release history'; grounded search summary:
The **2000 Pfizer acquisition of Warner-Lambert** (valued at approximately **$90 billion**) was one of the largest and most dramatic hostile takeovers in corporate history. At the center of the battle was **Lipitor (atorvastatin)**, a cholesterol-lowering statin that went on to become the best-selling prescription drug in pharmaceutical history.

---

### 1. The Pre-Deal Foundation: The Lipitor Alliance (1996–1997)
* **The Drug:** Developed by Warner-Lambert’s Parke-Davis division, Lipitor showed exceptional efficacy in clinical trials at lowering low-density lipoprotein (LDL) cholesterol.
* **The Partnership:** Lacking a large global cardiovascular sales force to compete against Merck’s rival statin (Zocor), Warner-Lambert partnered with Pfizer in 1996 to co-promote Lipitor.
* **The Launch:** Launched in 1997, Lipitor quickly became the fastest-growing pharmaceutical in history, generating billions in annual revenue that was split between both companies.

---

### 2. The Spark: The American Home Products Deal (November 4, 1999)
* On the morning of **November 4, 1999**, Warner-Lambert announced a friendly, stock-for-stock "merger of equals" with **American Home Products (AHP)** valued at roughly $71 billion to form a combined entity called *AmericanWarner*.
* **The Threat to Pfizer:** Under the proposed merger, AHP would have inherited Warner-Lambert's share of Lipitor. Furthermore, Pfizer feared a prolonged legal fight over whether the change of control would jeopardize its co-marketing rights.

---

### 3. Pfizer’s Hostile Counter-Offer & Press Release (November 4, 1999)
Hours after the Warner-Lambert/AHP announcement, Pfizer gatecrashed the deal with an unsolicited **$82.4 billion hostile bid** ($96.40 per Warner-Lambert share, or 2.5 Pfizer shares per Warner-Lambert share).

* **From Pfizer’s Nov 4, 1999 SEC filing / Press Release:**
  > *"This combination would create the strongest, most dynamic pharmaceutical company in the world... The transaction would create superior, immediate and long term value, for the shareholders of both companies."*
  > — **William C. Steere, Jr.**, Chairman and CEO of Pfizer
* **The Strategic Justification:** Pfizer emphasized the shared operational success of Lipitor:
  > *"Since 1997, the two companies have partnered in a highly-successful marketing alliance for Lipitor, one of the most widely prescribed cholesterol-lowering agents in the world... Today, however, Warner-Lambert announced an agreement to merge with American Home Products Corp. This agreement terminates a prior standstill provision between Pfizer and Warner-Lambert..."*

---

### 4. The Hostile Takeover Battle (November 1999 – January 2000)
* **Defensive Lawsuits:** Warner-Lambert’s CEO, Lodewijk J.R. de Vink, vehemently opposed Pfizer’s bid. Warner-Lambert sued Pfizer in an attempt to terminate the Lipitor co-marketing agreement, citing breach of contract.
* **Pfizer's Retaliation:** Pfizer filed countersuits and launched an aggressive public-relations campaign, calling Warner-Lambert's lawsuits *"desperate defensive measures designed to deny its shareholders the opportunity to consider a superior offer"*.
* **Shareholder Pressure:** Institutional investors heavily favored Pfizer's higher premium and stronger stock currency over AHP’s offer.

---

### 5. The Definitive Agreement (February 7, 2000)
By late January 2000, Warner-Lambert’s board conceded that Pfizer's offer provided far greater shareholder value. 

* **The Breakup Fee:** Warner-Lambert terminated its merger agreement with AHP and was forced to pay AHP a record-setting **$1.8 billion breakup fee** (which Pfizer agreed to cover).
* **The Agreement:** On **February 7, 2000**, Pfizer and Warner-Lambert officially announced a definitive merger agreement:
  * Pfizer increased its offer to **2.75 shares of Pfizer stock** for each share of Warner-Lambert (valuing Warner-Lambert at roughly **$90 billion**, or $98.31 per share).
  * Pfizer shareholders retained ~61% of the merged company, and Warner-Lambert shareholders received ~39%.
  * William C. Steere, Jr. remained CEO of Pfizer; Lodewijk de Vink departed.

---

### 6. Closing and Aftermath (June 2000)
* **FTC Clearance (June 19, 2000):** The U.S. Federal Trade Commission cleared the deal after requiring Pfizer and Warner-Lambert to divest overlapping assets (including the Alzheimer’s drug Cognex, the antidepressant Celexa, and RID head-lice treatment).
* **The Lipitor Legacy:** By securing 100% of the rights to Lipitor, Pfizer turned the statin into an unprecedented commercial juggernaut. Lipitor became the first prescription drug to generate over **$10 billion in annual revenue**, eventually accumulating over **$125 billion in sales** before losing patent exclusivity in late 2011.
sources:
  - repec.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeOSZTGSdKeJgBzJRe3NhQmTi54SJrABy9xQXI65m4e1Id9EaxXVT0vXD8WwUE0EXNUs1p1SN3u3I1uJZvkTE0ZnGXlytfV-CKtfCp6k8yrwsdEv0TLlVN0Fgh2Ta_cK_XLr7_uS2qWGoSPLJvRn_wPHdw>
  - cbc.ca <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG0uCxPxIObZP73BzL39AjJ6H5_OHC8O-Asa-xBQtzikny6p5aW_-7om2aNzbDe_E5SE6KRApq5E7cEd5qJ93tEGQgdGIHLA1kPXkPkAMGNQXFOUVtG8pDcxh3clpRIB3SPMOK-Wz5V2ZfSEq4VzKC_Z6bXqvoAm_0MswiCyJbcBzvWyjoI4NWCfupVri_B>
  - pharmaceuticalonline.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE6_EXju5XJsZgYZ09l-PO2QNKvxn7cJRBMyK_wuAdWzpB0DP8QxPUdB2jTwIfqjOkROXnPTiR4EQl-2lVBCwHisaWMSBm7SMpTOwJy6QvylHbjl8rgWIeYN37cZ8VCCW-vytSiC_szmLvG86ZFJbWn0okDBVrhhLbTm5YCIGV1co4hTenpUY2MdTVH4AQnUJzs>
  - sec.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmUNBCn4Nk3ZwmFihuNQw3rIs1ktvUmfRxP-2crCQ4bkSP10btZEllp_yqAsV9F6I8OmVQ1r6zdux1N41c9q8I8nJazZB9Ps0jT4U-G05rYqdnjscymvUxMBPB9W9qychZm9yzlqBx-f_PRflw9VQkAY7vDTjq4jdOypNuikUcYRsHoQyNPNFUtzT6vFTyPhXrr88=>
  - umich.edu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGFTSIQxH5V4GorqUBaIUMi-OstPHzEmmiWALvkArDdgd1UYHjrlfn43BtOi6-luXQl9W33kk77pK9m264JAc13WGLuBRhRyonK87RCj20xRNz8qKiU9E9PcfqCtSnpFpsHtJitEOTYyCzhyiA=>
  - cbsnews.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFGNHn_gKJ9HJB77Bad_MAzL7SofrDCq1nBrEcfOkIz4CfHHRFFpH_84b3xUcpWfIpw2wzSDlJtdySRflQgCBWxSSF5oc881Ps-njNG_an-Rj3Z3x9juDSCm6LQQbn3tf8QuSlkuzTnGoE0ImI=>
  - washingtonpost.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1I4UDBRbCCMMA3WfklRhy4Xvje6_1ULKElDqk3oFKctx1qvtMS4ExTIAyPYwtN-PpNeynl-omMQUB47FORmvvy6AuucPRRVE5r1NJVOSqrip0JMscpB6Yvqtyz6Kr8TA3E9rjWvLLtyqL5IRy9DpUHSLhPvT4US-xiMa6tYy5nUiUMrKTe6ighAxx2dXepGXRxe5ATxE49kvWd8_CP31LvxrDwRcYZNALGIEwuyrdcHYEMHti33SE7FuQ1g==>
  - pharmexec.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH07cTx3lVhqwT1fnGvqNHkSIT-7w0FWV1fLPd3VgrD29ewC1fSJrxNKDviz26AY6Aksqy--7xpkv4HzuTKED5Z6pY9VsZIBFzRjxkm-_B7A9ZQ8RMPm-iFZ3We5Xjw5rCp6Sy5yMyKpqgv4_K2njWayKnRTzIJ>
```

</details>

**Answer:**

**Short answer: Lipitor (atorvastatin) was originally developed by Parke-Davis, the pharmaceutical research division of Warner-Lambert** — not by Pfizer.

## Key facts

| Fact | Detail |
|---|---|
| Original developer | **Parke-Davis** (Warner-Lambert's pharma research division), Ann Arbor, Michigan |
| Compound first synthesized | **1985** (development code CI-981) by medicinal chemist **Bruce D. Roth** |
| Co-promotion partner | **Pfizer**, via a 1996 co-marketing alliance |
| FDA approval | **December 17, 1996** (U.S. launch 1997) |
| Later ownership | Pfizer acquired Warner-Lambert (hostile bid announced **Feb 7, 2000**, ~**$90 billion**, completed 2000), giving Pfizer full ownership |
| Patent expiry | **November 2011** (U.S.) |

**So:** Warner-Lambert/Parke-Davis discovered and developed it; Pfizer co-promoted it from 1996 and later acquired the originator company in 2000, which is why Lipitor is commonly (but imprecisely) referred to as a "Pfizer drug."

## Sources

These come from a public web search (Network Search Agent). Note that the search tool returned redirect URLs that resolve to the underlying publications listed below:

- Wikipedia — "Atorvastatin" and "Bruce Roth"
- American Chemical Society (acs.org) — awards recognizing Bruce Roth's role in the discovery
- SEC filings (sec.gov) and Pfizer press materials — co-promotion and acquisition details
- Washington Post (washingtonpost.com) and CBC (cbc.ca) — Warner-Lambert/Pfizer acquisition coverage
- Pharmaceutical Executive (pharmexec.com) — Lipitor commercial history

## Caveats
- **No internal Wohua records or RAGFlow documents were used** for this question — it is purely public information, and your working directory contained no attachments to analyze.
- **Figures vary by source** for cumulative Lipitor sales (commonly cited as ~$125–130 billion, with some sources giving higher ranges) and for the acquisition value (~$90 billion offer value vs. higher figures based on peak stock valuation at closing). I've flagged rather than resolved these.
- For stable citation, use the canonical publisher pages named above, since the raw redirect links returned by the search are not permanent addresses.

---

## 17. route-14 (routing, medium)

**Question:** Compare our Atorvastatin Calcium Tablets specification with the Lipitor strengths sold on the market.

**Gold answer:** Ours: 20mg*7 tablets. Public Lipitor strengths: 10, 20, 40 and 80 mg.

**Route:** expected ['database', 'internet']; delegated {'Database Query Agent': 1, 'Network Search Agent': 1, 'RAGFlow Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[1] tool ls returned:
No files found

[2] tool glob returned:
No files found

[3] tool ls returned:
No files found

[4] tool ls returned:
No files found

[8] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[9] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[10] tool count_documents returned:
{"count": 10}

[11] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[12] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[13] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802df"}, "drug_id": 4, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "approval_number": "H20055567", "specifications": "20mg*7 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Cardiovascular", "description": "For patients with primary hypercholesterolemia, including familial hypercholesterolemia (heterozygous) or mixed hyperlipidemia."}], "queryResultsCount": 1, "appliedLimits": []}

[14] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802dc"}, "drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "approval_number": "H20051234", "specifications": "0.25g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "Used to treat upper respiratory tract infections, urogenital infections, and others caused by susceptible bacteria."}, {"_id": {"$oid": "6aabf437cb80345c469802dd"}, "drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "approval_number": "H10900089", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Analgesic/Antipyretic", "description": "Used to relieve mild to moderate pain such as headache, joint pain, migraine, toothache, muscle pain, neuralgia, and dysmenorrhea. Also used for fever caused by the common cold or influenza."}, {"_id": {"$oid": "6aabf437cb80345c469802de"}, "drug_id": 3, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "approval_number": "H20023345", "specifications": "0.5g*48 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Diabetes", "description": "First-line treatment for type 2 diabetes patients not adequately controlled by diet alone, especially those who are obese."}, {"_id": {"$oid": "6aabf437cb80345c469802df"}, "drug_id": 4, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "approval_number": "H20055567", "specifications": "20mg*7 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Cardiovascular", "description": "For patients with primary hypercholesterolemia, including familial hypercholesterolemia (heterozygous) or mixed hyperlipidemia."}, {"_id": {"$oid": "6aabf437cb80345c469802e0"}, "drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "approval_number": "H20090123", "specifications": "75mg*10 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antiviral", "description": "For the treatment of influenza A and B in adults and children aged 1 year and older."}, {"_id": {"$oid": "6aabf437cb80345c469802e1"}, "drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "approval_number": "H10920012", "specifications": "1.0g/vial", "dosage_form": "Injection", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "For lower respiratory tract, urinary tract, and biliary infections caused by susceptible pathogens, as well as intra-abdominal infections, pelvic infections, skin and soft tissue infections, bone and joint infections, sepsis, meningitis, and more."}, {"_id": {"$oid": "6aabf437cb80345c469802e2"}, "drug_id": 7, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "approval_number": "H20000456", "specifications": "3g*10 sachets", "dosage_form": "Powder", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Digestive System", "description": "For acute and chronic diarrhea in adults and children."}, {"_id": {"$oid": "6aabf437cb80345c469802e3"}, "drug_id": 8, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat", "approval_number": "H20100345", "specifications": "30mg*30 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Hypertension", "description": "1. Hypertension. 2. Coronary heart disease — chronic stable angina (exertional angina)."}, {"_id": {"$oid": "6aabf437cb80345c469802e4"}, "drug_id": 9, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin", "approval_number": "J20130078", "specifications": "100mg*30 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Cardiovascular", "description": "Reduces the risk of onset in patients with suspected acute myocardial infarction; prevents recurrence of myocardial infarction."}, {"_id": {"$oid": "6aabf437cb80345c469802e5"}, "drug_id": 10, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "approval_number": "Z20040063", "specifications": "0.35g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "TCM / Cold & Flu", "description": "Clears heat-toxin and disperses lung heat. Used to treat influenza with heat-toxin attacking the lung, presenting as fever or high fever, chills, muscle aches, nasal congestion and runny nose, cough, headache, dry and sore throat."}], "queryResultsCount": 10, "appliedLimits": []}

[15] knowledge base 'Drug Labels Assistant' answered:
The answer you are looking for is not found in the dataset!

The provided knowledge base does not contain any documents describing "Atorvastatin Calcium Tablets" product specifications. The documents present relate to different products entirely: Nifedipine extended-release tablets [ID:0][ID:3][ID:5] and Amoxicillin (AMOXIL) capsules, tablets, and powder for oral suspension [ID:2][ID:4].

While Nifedipine documents include some of the requested categories of information—marketed strengths of 30 mg, 60 mg, and 90 mg [ID:3][ID:5], round biconvex film-coated tablets [ID:3][ID:5], and package configurations in bottles of 30, 100, and 300 [ID:5]—these are for a different drug and therefore irrelevant to your query about Atorvastatin Calcium Tablets. No document in the dataset lists quality standards for any product.
retrieved chunks:
  - (20260409_4d3e11d2-d320-45d3-96c8-48322202b504.pdf) <table><caption> Revised:3/2026</caption>
<tr><td  >POLYETHYLENE GLYCOL 4000 (UNII: 4R4HFI6D95)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th  >TALC (UNIl: 7SEV7J4R1U)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td  >POLYVINYL ALCOHOL (UNI: 532B59J990)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >TITANIUM DIOXIDE (UNIl: 15FIX9V2JP)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >LECITHIN, SOYBEAN (UNIl: 1DI56QDM62)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >FERRIC OXIDE YELLOW (UNI: EX438O2MRT)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >FERRIC OXIDE RED (UNII: 1K09F3G675)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >FERROSOFERRIC OXIDE (UNII: XM0M87F357)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >METHACRYLIC ACID - METHYL METHACRYLATE COPOLYMER (1:2) (UNIl: 5KY68S2577)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >HYDROXYETHYL CELLULOSE (2000 MPA.S AT 1%) (UNIl: S38J6RZ N16)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th colspan=10 >Product Characteristics</th><th></th></tr>
<tr><td  >Color</td><td></td><td></td><td></td><td></td><td></td><td></td><td  >YELLOW Score</td><td></td><td  >no score</td><td></td></tr>
<tr><td  >Shape</td><td></td><td></td><td></td><td></td><td></td><td></td><td  >ROUND Size</td><td></td><td  >9mm</td><td></td></tr>
<tr><td  >Flavor</td><td></td><td></td><td></td><td></td><td></td><td></td><td  >Imprint Code</td><td></td><td  >30</td><td></td></tr>
<tr><td  >Contains</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td  >Packaging</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td  > Marketing Start</td><td></td><td></td></tr>
<tr><td  >#</td><td></td><td></td><td></td><td></td><td  >Item Code</td><td></td><td  >Package Description</td><td  >Date</td><td  >Marketing End Date</td><td></td></tr>
<tr><td  >1</td><td></td><td  >NDC:50742-260- 30 in 1 BOTTLE; Type 0: Not a Combination 30</td><td></td><td></td><td></td><td  >Product</td><td></td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td  >2</td><td></td><td></td><td  >NDC:50742-260-100 in 1 BOTTLE; Type 0: Not a Combination 01</td><td></td><td></td><td  >Product</td><td></td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td  >3</td><td></td><td></td><td  >NDC:50742-260-</td><td></td><td></td><td></td><td  >300 in 1 BOTTLE; Type 0: Not a Combination</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td  >03</td><td></td><td></td><td  >Product</td><td></td><td></td><td></td></tr>
<tr><th  >Marketing Information</th><th></th><th></th><th></th><th></th><th  >Marketing Category</th><th></th><th  >Application Number or Monograph Citation</th><th colspan=2 rowspan=2 >Marketing Start Marketing End Date Date 03/12/2019</th><th></th></tr>
<tr><td  >ANDA</td><td  >NIFEDIPINE</td><td></td><td></td><td></td><td></td><td></td><td  >ANDA210614</td><td></td></tr>
<tr><td></td><td  >nifedipine tablet, film coated, extended release</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th  > Product Information</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td  > Product Type</td><td></td><td></td><td></td><td></td><td></td><td  >HUMAN PRESCRIPTION DRUG</td><td  >Item Code (Source)</td><td  >NDC:50742-261</td><td></td></tr>
<tr><td></td><td colspan=6 >Route of Administration</td><td  >ORAL</td><td></td><td></td><td></td></tr>
<tr><td colspan=8 >NIFEDIPINE (UNII: I9Z F7L6G2L) (NIFEDIPINE - UNII:I19ZF7L6G2L)</td><td  >NIFEDIPINE</td><td  >60 mg</td><td></td></tr>
<tr><td></td><td  >Inactive Ingredients</td><td></td><td></td><td></td><td></td><td></td><td  > Ingredient Name</td><td></td><td></td><td  >Strength</td></tr>
<tr><th></th><th  >CELLULOSE, MICROCRYSTALLINE (UNIl: OP1R32D61U)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><th></th><th  >LACTOSE MONOHYDRATE (UNI: EWQ57Q8I5X)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><th></th><th  >HYPR0MELLOSES (UNIl: 3NXW29V3WO)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td  >ETHYLCELLULOSES (UNIl: 7Z8S9VYZ4B)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td  >SODIUM LAURYL SULFATE (UNIl: 368GB5141J)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th  >MAGNESIUM STEARATE (UNIl: 70097M6I30)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><th></th><th  >METHACRYLIC ACID - METHYL METHACRYLATE COPOLYMER (1:1) (UNIl: 74G4R6TH13)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><th></th><th  >POLYETHYLENE GLYCOL 4000 (UNII: 4R4HFI6D95)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td  >TALC (UNIl: 7SEV7J4R1U)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td  >POLYVINYL ALCOHOL (UNIl: 532B59J990)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td  >TITANIUM DIOXIDE (UNII: 15FIX9V2JP)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td  >FERRIC OXIDE YELLOW (UNI: EX438O2MRT)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th  >FERRIC OXIDE RED (UNIl: 1K09F3G675)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td  >HYDROXYETHYL CELLULOSE (2000 MPA.S AT 1%) (UNIl: S38J6RZ N16)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td colspan=8 >METHACRYLIC ACID - METHYL METHACRYLATE COPOLYMER (1:2) (UNIl: 5KY68S2577)</td><td></td><td></td><td></td></tr>
<tr><td></td><td  >Color</td><td></td><td></td><td></td><td></td><td></td><td  >BROWN (light brown)</td><td  >Score</td><td  >no score</td><td></td></tr>
<tr><td></td><td  >Shape</td><td></td><td></td><td></td><td></td><td></td><td  >ROUND</td><td  >Size</td><td  >9mm</td><td></td></tr>
<tr><td></td><td  >Flavor</td><td></td><td></td><td></td><td></td><td></td><td></td><td  >Imprint Code</td><td  >60</td><td></td></tr>
<tr><td></td><td  >Contains</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th  >Packaging</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td  >#</td><td></td><td></td><td></td><td  >Item Code</td><td></td><td  >Package Description</td><td  >Marketing Start Date</td><td  >Marketing End Date</td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td  >NDC:50742-261-30 in 1 BOTTLE; Type 0: Not a Combination</td><td  >30</td><td></td><td  >Product</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td  >2</td><td></td><td  >01</td><td></td><td  >NDC:50742-261-100 in 1 BOTTLE; Type 0: Not a Combination</td><td  >Product</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td  >3</td><td></td><td></td><td  >NDC:50742-261- 300 in 1 BOTTLE; Type 0: Not a Combination</td><td></td><td></td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td  >03</td><td></td><td  >Product</td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >Marketing Information</th><th></th><th></th><th></th><th  >Marketing Category</th><th  >Application Number or Monograph Citation</th><th  >Marketing Start Date</th><th  >Marketing End Date</th><th></th></tr>
<tr><td></td><td></td><td  >ANDA</td><td></td><td></td><td></td><td></td><td  >ANDA210614</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td  >NIFEDIPINE</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Product Information</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >Product Type</th><th></th><th></th><th></th><th></th><th  >HUMAN PRESCRIPTION DRUG</th><th  >Item Code (Source)</th><th  >NDC:50742-262</th><th></th></tr>
<tr><td></td><td></td><td  >Route of Administration</td><td></td><td></td><td></td><td></td><td  >ORAL</td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Active Ingredient/Active Moiety</td><td></td><td></td><td></td><td></td><td  >Ing redient Name</td><td  >Basis of Strength</td><td></td><td  > Strength</td></tr>
<tr><td colspan=9 >NIFEDIPINE (UNII: I9Z F7L6G2L) (NIFEDIPINE - UNII:19ZF7L6G2L) NIFEDIPINE</td><td></td><td  >90 mg</td></tr>
<tr><th></th><th></th><th  >Inactive Ingredients</th><th></th><th></th><th></th><th></th><th  >Ingredient Name</th><th></th><th></th><th  >Strength</th></tr>
<tr><td></td><td></td><td  >CELLULOSE, MICROCRYSTALLINE (UNIl: OP1R32D61U)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >LACTOSE MONOHYDRATE (UNIl: EWQ57Q8I5X)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >HYPR0MELLOSES (UNIl: 3NXW29V3WO)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >ETHYLCELLULOSES(UNI:7Z8S9VYZ4B)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >SODIUM LAURYL SULFATE (UNIl: 368GB5141J)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >MAGNESIUM STEARATE (UNIl:70097M6I30)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >METHACRYLIC ACID - METHYL METHACRYLATE COPOLYMER (1:1) (UNII: 74G4R6TH13)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td></td><td  >POLYETHYLENE GLYCOL 4000 (UNI: 4R4HFI6D95)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >POLYVINYL ALCOHOL (UNII: 532B59J990)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td></td><td  >LECITHIN, SOYBEAN (UNIl: 1DI56QDM62)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >FERRIC OXIDE YELLOW (UNI: EX438O2MRT)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td></td><td  >FERRIC OXIDE RED (UNII: 1K09F3G675)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >FERROSOFERRICOXIDE(UNII:XM0M87F357)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><th></th><th></th><th  >HYDROXYETHYL CELLULOSE (2000 MPA.S AT 1%) (UNIl: S38J6RZ N16)</th><th></th><th></th><th></th><th></th><th></th><th></th><th></th><th></th></tr>
<tr><td></td><td></td><td  >METHACRYLIC ACID - METHYL METHACRYLATE COPOLYMER (1:2) (UNIl: 5KY68S2577)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Color</td><td></td><td></td><td></td><td></td><td  >BROWN Score</td><td></td><td  >no score</td><td></td></tr>
<tr><td></td><td></td><td  >Shape</td><td></td><td></td><td></td><td></td><td  >ROUND Size</td><td></td><td  >9mm</td><td></td></tr>
<tr><td></td><td></td><td  >Flavor</td><td></td><td></td><td></td><td></td><td  >Imprint Code</td><td></td><td  >90</td><td></td></tr>
<tr><td></td><td></td><td  >Contains</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><th></th><th></th><th  >Packaging</th><th></th><th></th><th></th><th></th><th></th><th  >Marketing Start</th><th  >Marketing End</th><th></th></tr>
<tr><th></th><th></th><th  >#</th><th></th><th></th><th></th><th  >Item Code</th><th  >Package Description</th><th  >Date</th><th  >Date</th><th></th></tr>
<tr><td></td><td></td><td  >1</td><td></td><td></td><td  >NDC:50742-262- 30 in 1 BOTTLE; Type 0: Not a Combination 30</td><td></td><td  >Product</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td  >NDC:50742-262- 100 in 1 BOTTLE; Type 0: Not a Combination</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >2</td><td></td><td></td><td  >01</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td  >Product</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td  rowspan=3 >3</td><td></td><td></td><td  >NDC:50742-262-</td><td></td><td  >300 in 1 BOTTLE; Type 0: Not a Combination</td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td  >03</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td></td><td></td><td></td><td></td><td  >Product</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Marketing Information</td><td></td><td></td><td></td><td  > Marketing Category</td><td  >Application Number or Monograph Citation</td><td  >Marketing Start Date</td><td  >Marketing End</td><td  >Date</td></tr>
<tr><td></td><td></td><td  >ANDA</td><td></td><td></td><td></td><td></td><td  >ANDA210614</td><td  >03/12/2019</td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Labeler - Ingenus Pharmaceuticals, LLC (833250017)</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Registrant - Novast Laboratories, Ltd. (527695995)</td><td></td><td></td><td  >Na me</td><td  >Address</td><td  >ID/FEI</td><td  >Business Operations</td><td></td><td></td></tr>
<tr><td></td><td></td><td  >Novast Laboratories, Ltd.</td><td></td><td></td><td></td><td></td><td  >analysis(50742-260, 50742-261, 50742-262), label(50742-260, 50742-261, 527695995 50742-262),manufacture(50742-260, 50742-261, 50742-262) , pack(50742-260, 50742-261,50742-262)</td><td></td><td></td><td></td></tr>
</table>
  - (20260409_4d3e11d2-d320-45d3-96c8-48322202b504.pdf) ingenuss
Eachextended-releasefilm-coated tabletcontains:
LOT:00000000
90 mg Nifedipine, USP.
部
P:00/0000
00
Usual Dosage:See package insert for full prescribing
NDC50742-
-01
information.
000000000
32839-
NIFEdipine
haceu
003507422620
Tabletsshouldbeswallowedwholenotbittenor
Extended-Release
20
uticals,
-6408
divided.
Tablets,USP
Store at 20°to 25°C(68°to77°F);[See USP
2
90mg
Controlled RoomTemperature.]
EX
2
0000
PROTECTFROMLIGHT.PROTECTFROMMOISTURE.
二
Pharmacist:Dispenseina tight,light-resistant
N:
container as defined in theUSP.
S
WARNING:Keep this and all medicationsout of the
3
Rxonly
reach of children.
100Tablets
Rev.B Iss.05/2019 P0201
262-01 v2/05-2019
nifedipine tablet, film coated, extended release
Product Information
 Product Type
Item Code (Source)
HUMAN PRESCRIPTION DRUG
NDC:50742-260
ORAL
Route of Administration
Active Ingredient/Active Moiety
 Strength
Ingredient Name
Basis of Strength
30 mg 
NIFEDIPINE
NIFEDIPINE (UNII: I9ZF7L6G2L) (NIFEDIPINE - UNII:19Z F7L6G2L)
Inactive Ingredients
 Strength
Ingredient Name
CELLULOSE, MICROCRYSTALLINE (UNIl: OP1R32D61U)
LACTOSE MONOHYDRATE (UNIl:EWQ57Q8I5X)
HYPROMELLOSES (UNII: 3NXW29V3WO)
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
HOW SUPPLIED/STORAGE AND HANDLING16
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
250-mgCapsule
ThislabelmaynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
NDC 43598-025-01
Bottles of 100
NDC43598-025-05
Bottles of 500
500-mg Capsule
NDC 43598-005-01
Bottles of 100
NDC 43598-005-05
Bottles of 500
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
500-mg Tablet
NDC 43598-024-01
Bottles of 100
NDC 43598-024-05
Bottles of 500
875-mg Tablet
NDC 43598-019-01
Bottles of 100
NDC 43598-019-14
Bottles of 20
Powder for Oral Suspension: Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum-flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
125 mg/5 mL
NDC 43598-022-80
80-mL bottle
NDC 43598-022-52
100-mL bottle
NDC 43598-022-53
150-mL bottle
200 mg/5 mL
NDC 43598-023-50
50-mL bottle 75-mL bottle
NDC 43598-023-51
100-mL bottle
NDC 43598-023-52
  - (20260409_4d3e11d2-d320-45d3-96c8-48322202b504.pdf) 
DOSAGEANDADMINISTRATION
Dosage must be adjusted according to each patient's needs. Therapy for either hypertension or angina should be initiated with 30 or 60 mg once daily. Nifedipine extended-release tabletsshouldbe swallowedwhole andshould notbebittenor divided.
In general, titration should proceed over a 7-14 day period so that the physician can fully assess the response to each dose level and monitor blood pressure before proceedingtohigherdoses.Sincesteady-stateplasmalevelsare achievedonthe second day of dosing, titration may proceed more rapidly, if symptoms so warrant, provided the patient is assessed frequently. Titration to doses above 120 mg are not
recommended.
Angina patients controlled on nifedipine capsules alone or in combination with other antianginal medications may be safely switched to nifedipine extended-release tablets at the nearest equivalent total daily dose (e.g., 30 mg t.i.d. of nifedipine capsules may be changed to 90 mg once daily of nifedipine extended-release tablets). Subsequent titration to higher or lower doses may be necessary and should be initiated as clinically warranted. Experience with doses greater than 90 mg in patients with angina is limited.
Therefore, doses greater than 9o mg should be used with caution and only when clinically warranted.
Avoid co-administration of nifedipine with grapefruit juice (see CLiNiCAL PHARMACOLOGY andPRECAUTIONS: Other Interactions).
No "rebound effect" has been observed upon discontinuation of nifedipine extended- release tablets. However, if discontinuation of nifedipine is necessary, sound clinical practice suggests that the dosage should be decreased gradually with close physician supervision.
Care should be taken when dispensing nifedipine extended-release tablets to assure that the extended release dosage form has been prescribed
Co-Administration with Other Antianginal Drugs
Sublingual nitroglycerin may be taken as required for the control of acute manifestations of angina, particularly during nifedipine titration. See PRECAUTloNS, Drug Interactions, for information on co-administration of nifedipine with beta blockers or long-acting nitrates.
HOWSUPPLIED
Nifedipine extended-release tablets are supplied as 30 mg, 60 mg and 90 mg round, biconvex, film-coated tablets. The different strengths can be identified as follows:
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
Dosing for H. pylori Infection2.3
This label may not bethe latest approved byFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Triple therapy: The recommended adult oral dose is 1 gram AMOXIL, 500 mg clarithromycin, and 30 mg lansoprazole, all given twice daily (every 12 hours) for 14 days.
Dual therapy: The recommended adult oral dose is 1 gram AMOXIL and 30 mg lansoprazole, each given three times daily (every 8 hours) for 14 days.
Please refer to clarithromycin and lansoprazole full prescribing information.
2.4Dosing in Renal Impairment
● Patients with impaired renal function do not generally require a reduction in dose unless the impairment is severe.
· Severely impaired patients with a glomerular filtration rate of < 30 mL/min. should not receive a 875-mg dose.
· Patients with a glomerular filtration rate of 10 to 30 mL/min should receive 500 mg or 250 mg every 12 hours, depending on the severity of the infection.
· Patients with a glomerular filtration rate less than 10 mL/min should receive 500 mg or 250 mg every 24 hours, depending on severity of the infection.
· Hemodialysis patients should receive 500 mg or 250 mg every 24 hours, depending on severity of the infection.
They should receive an additional dose both during and at the end of dialysis.
Directions for Mixing Oral Suspension2.5
Tap bottle until all powder flows freely. Add approximately 1/3 of the total amount of water for reconstitution (see
This label may not be the latest approved by FDA For current labeling information,pleasevisit https://www.fda.gov/drugsatfda
After reconstitution, the required amount of suspension should be placed directly on the child's tongue for swallowing.
Alternate means of administration are to add the required amount of suspension to formula, milk, fruit juice, water, ginger ale, or cold drinks. These preparations should then be taken immediately.
NOTE: SHAKE ORAL SUSPENSION WELL BEFORE USING. Keep bottle tightly closed. Any unused portion of the reconstituted suspension must be discarded after 14 days. Refrigeration is preferable, but not required.
DOSAGE FORMS AND STRENGTHS
  - (20260409_4d3e11d2-d320-45d3-96c8-48322202b504.pdf) 
30 mg: Yellow round biconvex coated tablets, debossed "30" on one side
60 mg: Light brown round biconvex coated tablets, debossed "6o" on one side
90 mg: Brown round biconvex coated tablets, debossed "9o" on one side
Bottles of 30:
30mg(NDC50742-260-30)
60 mg (NDC 50742-261-30)
90 mg (NDC 50742-262-30)
Bottles of 100:
30 mg (NDC 50742-260-01)
60 mg (NDC 50742-261-01)
90mg(NDC50742-262-01)
Bottles of 300:
30 mg (NDC 50742-260-03)
60 mg (NDC 50742-261-03)
90 mg (NDC 50742-262-03)
Store at 20° to 25°C (68° to 77°F); excursions permitted to 15° to 30°C (59° to 86°F).
[See USP Controlled Room Temperature.]
Protect from moisture and humidity.
ingenus
Distributed by:
Ingenus Pharmaceuticals, LLC Orlando,FL 32839-6408 Made in China
Rx Only
10092 Iss. 11/2022 Rev. B
NIFEDIPINE
ETHYLCELLULOSES(UNII:7Z8S9VYZ4B) SODIUM LAURYL SULFATE (UNIl: 368GB5141J) MAGNESIUM STEARATE (UNII: 70097M6I30) METHACRYLIC ACID - METHYL METHACRYLATE COPOLYMER (1:1) (UNIl: 74G4R6TH13)
Active Ingredient/Active Moiety
 Strength
Basis of Strength
Ing redient Name
nifedipine tablet, film coated, extended release
Establishment

[16] tool count_documents returned:
{"count": 3}

[17] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802ef"}, "inventory_id": 10, "drug_id": 4, "batch_number": "MY-250101-A", "quantity_on_hand": 1000, "warehouse_location": "Tianjin Warehouse 1 - High-Value Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f0"}, "inventory_id": 11, "drug_id": 4, "batch_number": "MY-250615-B", "quantity_on_hand": 2500, "warehouse_location": "Beijing Warehouse 2 - High-Value Zone", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f1"}, "inventory_id": 12, "drug_id": 4, "batch_number": "MY-251120-C", "quantity_on_hand": 4000, "warehouse_location": "Tianjin Warehouse 2 - High-Value Zone", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}], "queryResultsCount": 3, "appliedLimits": []}

[18] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c4698030a"}, "sale_id": 7, "drug_id": 4, "sale_date": {"$date": "2025-04-05T00:00:00.000Z"}, "quantity_sold": 100, "unit_price": 45, "total_amount": 4500, "customer_name": "Chengdu West China Hospital", "region": "Southwest China", "sales_rep": "Chengdu Wuhou Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030b"}, "sale_id": 8, "drug_id": 4, "sale_date": {"$date": "2025-10-18T00:00:00.000Z"}, "quantity_sold": 150, "unit_price": 45, "total_amount": 6750, "customer_name": "Chongqing Pharmacy", "region": "Southwest China", "sales_rep": "Chongqing Yuzhong Sales Dept."}], "queryResultsCount": 2, "appliedLimits": []}

[19] tool count_documents returned:
{"count": 2}

[20] tool aggregate_documents returned:
{"documents": [{"_id": 4, "sales": 2, "total_qty_sold": 250, "total_revenue": 11250, "min_price": 45, "max_price": 45}], "count": 1, "appliedLimits": []}

[21] tool aggregate_documents returned:
{"documents": [{"_id": 4, "batches": 3, "total_qty": 7500}], "count": 1, "appliedLimits": []}

[22] web search for 'Lipitor atorvastatin calcium tablets strengths 10 mg 20 mg 40 mg 80 mg prescribing information'; grounded search summary:
Below is an overview of the clinically relevant **FDA Prescribing Information for Lipitor® (atorvastatin calcium tablets)**.

---

### **1. Available Strengths and Dosage Forms**
Lipitor is supplied as film-coated, white, elliptical tablets:
* **10 mg:** Debossed with “10” on one side and “PD 155” on the other.
* **20 mg:** Debossed with “20” on one side and “PD 156” on the other.
* **40 mg:** Debossed with “40” on one side and “PD 157” on the other.
* **80 mg:** Debossed with “80” on one side and “PD 158” on the other.

---

### **2. Indications and Usage**
* **Prevention of Cardiovascular Disease (CVD):**
  * **Secondary prevention:** To reduce the risk of stroke, nonfatal myocardial infarction (MI), revascularization procedures, and angina in patients with established coronary heart disease (CHD).
  * **Primary prevention:** In adults without clinically evident CHD but with multiple risk factors (or type 2 diabetes with risk factors), to reduce the risk of MI and stroke.
* **Hyperlipidemia & Dyslipidemia:**
  * Adjunct to diet to reduce elevated total cholesterol (total-C), low-density lipoprotein cholesterol (LDL-C), apolipoprotein B (apo B), and triglycerides (TG), and to increase high-density lipoprotein cholesterol (HDL-C) in primary hyperlipidemia (heterozygous familial and nonfamilial) and mixed dyslipidemia.
  * Primary dysbetalipoproteinemia (Type III).
  * Homozygous familial hypercholesterolemia (HoFH) as an adjunct to other lipid-lowering treatments.
* **Pediatric Patients (Aged 10 Years and Older):** Adjunct to diet in patients with heterozygous familial hypercholesterolemia (HeFH) or HoFH who meet specific LDL-C criteria.

---

### **3. Dosage and Administration**
* **Administration:** Oral, once daily, at any time of day, with or without food.
* **General Adult Dosage Range:** **10 mg to 80 mg once daily**.
  * **Starting dose:** Usually **10 mg to 20 mg once daily**.
  * Patients requiring large LDL-C reductions (e.g., >45%) may start at **40 mg once daily**.
* **Titration & Monitoring:** Assess lipid levels within **2 to 4 weeks** after initiation or dose titration and adjust accordingly.
* **Pediatric Patients (HeFH / HoFH, Age ≥10):**
  * Starting dose: 10 mg once daily.
  * HeFH maximum recommended dose: 20 mg once daily (range: 10 to 80 mg for HoFH).

#### **Dosage Adjustments for Drug Interactions:**
| Concomitant Drug | Atorvastatin Dosage Recommendation |
| :--- | :--- |
| **Cyclosporine, tipranavir + ritonavir, glecaprevir + pibrentasvir** | **Avoid** atorvastatin. |
| **Clarithromycin, itraconazole, darunavir + ritonavir, saquinavir + ritonavir** | Do not exceed **20 mg daily**. |
| **Nelfinavir** | Do not exceed **40 mg daily**. |
| **Lopinavir + ritonavir** | Use the lowest necessary dose. |

---

### **4. Contraindications**
* **Active liver disease**, which may include unexplained persistent elevations in hepatic transaminases.
* **Hypersensitivity** to atorvastatin or any inactive ingredients in the tablet formulation.

---

### **5. Warnings and Precautions**
* **Myopathy and Rhabdomyolysis:** 
  * Risk increases with higher doses (e.g., 80 mg), advanced age (≥65 years), uncontrolled hypothyroidism, renal impairment, and concomitant use of interacting drugs (CYP3A4 inhibitors, fibrates, cyclosporine).
  * Advise patients to promptly report unexplained muscle pain, tenderness, or weakness, particularly if accompanied by malaise or fever.
  * Discontinue immediately if markedly elevated creatine kinase (CK) levels occur or if myopathy is diagnosed or suspected.
  * Rare cases of **Immune-Mediated Necrotizing Myopathy (IMNM)** (an autoimmune myopathy characterized by persistent proximal muscle weakness and elevated CK despite statin discontinuation) have been reported.
* **Hepatic Dysfunction:** 
  * Perform liver enzyme tests before starting therapy and clinically thereafter as indicated. 
  * Serious hepatic injury is rare; discontinue if serious liver injury with clinical symptoms or hyperbilirubinemia/jaundice develops.
* **Endocrine Effects:** 
  * Slight increases in HbA1c and fasting blood glucose have been reported with statin therapy.

---

### **6. Common Adverse Reactions**
In clinical trials, the most commonly reported adverse reactions (incidence ≥2% and higher than placebo) included:
* Nasopharyngitis (8.3%)
* Arthralgia (6.9%)
* Diarrhea (6.8%)
* Pain in extremities (6.0%)
* Urinary tract infection (5.7%)
* Dyspepsia, nausea, musculoskeletal pain, and insomnia.

---

### **7. Significant Drug Interactions**
* **Strong CYP3A4 Inhibitors** (e.g., ketoconazole, clarithromycin, HIV/HCV protease inhibitors): Substantially increase atorvastatin AUC and peak plasma concentrations, elevating the risk of myopathy/rhabdomyolysis.
* **Fibrates (especially Gemfibrozil):** Increased risk of severe myopathy/rhabdomyolysis; concomitant use with gemfibrozil should generally be avoided.
* **Grapefruit Juice:** Co-consumption of large volumes (>1 to 1.2 liters/day) can significantly inhibit CYP3A4 and increase atorvastatin exposure; avoid excessive consumption.
* **Digoxin:** Co-administration may slightly increase steady-state plasma digoxin concentrations; monitor appropriately.
* **Oral Contraceptives:** May increase plasma concentrations of norethindrone and ethinyl estradiol.

---

### **8. Use in Specific Populations**
* **Pregnancy:** Discontinue atorvastatin as soon as pregnancy is recognized unless the potential benefit to the patient substantially outweighs the risk to the fetus (cholesterol biosynthesis is critical for fetal development).
* **Lactation:** Breastfeeding is **not recommended** during atorvastatin therapy due to the potential for serious adverse reactions in nursing infants.
* **Renal Impairment:** Renal disease does not significantly impact plasma concentrations or LDL-C reduction; dosage adjustments are not required solely for renal impairment, though renal impairment is a risk factor for statin-induced myopathy.
* **Hepatic Impairment:** Atorvastatin plasma concentrations are markedly increased (Cmax ~16-fold, AUC ~11-fold) in patients with chronic alcoholic liver disease (Child-Pugh B). Contraindicated in active liver disease.
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEXJy8n1YVdakBFRohAusdUEnQ0HtDnrV0jw-0Ki92G-FTi6S9Z5Y-ZnNTHsKZW0ScemHLbZInjVchbkz6-27tW39X-0kVUy-P-CWX4tdmwk5QGGtb9wIvFUilQX0M2oftrCVFOfYwvM9zVjKH-kelwLqZFR1R-oPHMwn3X7O8QjMMSsDO8KON5Z4cmnhib6-EB3aT3e55MMx3EwgGZ57N8pQyfwSo=>
  - lipitor.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3I_Jtz4wAvNTF-vRRAWDYt7W6UlTdQYojZgIZx-hOOZonMbqRxXsz6QpiIF-y7FoohIkRaeOa9vaN8uCUwwoKYMB26EIdpVcxdFXtPw==>
  - rxlist.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHc3Oz0BB0Yjg0UKyYXthwuE1CS41Kbq1QhDUYHiiuUwA1cilIYs_VlxBgJuC7QZIDckVMbenMDDjJMgrmI60evEggNpDBmIg9cedm1mKZyqtprjY7ElqixRYNidQ==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFFnzXexmRyWM4sQdOmkcyHq_g9IS_XniEBdtfCkTSrfo9yfe2PYTGuK0r_VOrVMVDA7HzlEDOOEHLpCI49mPmelRvJ2CIzPffPfXYpuouEgut6zfVDgcDTpKD6JvJYoRMKQ1fhwsYxVWIPBZftPUMFeiOxJvj2T6fcWNclpGjA0A==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9LnjMyKRAQOBPINp1UEX-LMP58GGxjx-mmmiq2kWJEMC0zJfwOQvyydd5twakdSMuUtlqM_VCleYBkLtTooq17LKgqaThMKVN2cX_NoJg7m4S4UG2NNKowU_dgXVZsui0--YA0xZXzhZOL2-5TOqxc471GlB7kzSUAa66pPVW1J0ZxmnYk4HDRFrL>

[23] web search for 'DailyMed LIPITOR atorvastatin calcium film-coated tablets NDC package configurations'; grounded search summary:
On DailyMed, official FDA labeling for brand-name **LIPITOR (atorvastatin calcium) film-coated tablets** is cataloged under both its current marketer (**Viatris Specialty LLC**, labeler code `58151`) and its originator (**Parke-Davis / Pfizer Inc.**, labeler code `0071`).

---

### 1. Viatris Specialty LLC Packaging Configurations

| Strength | NDC Package Code | Package Description | Tablet Appearance & Markings |
| :--- | :--- | :--- | :--- |
| **10 mg** | `58151-155-77` | Bottle of 90 tablets | White, elliptical; debossed **"10"** on one side and **"VLE 155"** on the other |
| **20 mg** | `58151-156-77` | Bottle of 90 tablets | White, elliptical; debossed **"20"** on one side and **"VLE 156"** on the other |
| **40 mg** | `58151-157-77` | Bottle of 90 tablets | White, elliptical; debossed **"40"** on one side and **"VLE 157"** on the other |
| **80 mg** | `58151-158-77` | Bottle of 90 tablets | White, elliptical; debossed **"80"** on one side and **"VLE 158"** on the other |

---

### 2. Parke-Davis (Division of Pfizer Inc.) Packaging Configurations

| Strength | NDC Package Code | Package Description | Tablet Appearance & Markings |
| :--- | :--- | :--- | :--- |
| **10 mg** | `0071-0155-23`<br>`0071-0155-40` | Bottle of 90 tablets<br>Carton of 100 (10 × 10 unit-dose blisters) | White, elliptical; debossed **"PD 155"** on one side and **"10"** on the other |
| **20 mg** | `0071-0156-23`<br>`0071-0156-40` | Bottle of 90 tablets<br>Carton of 100 (10 × 10 unit-dose blisters) | White, elliptical; debossed **"PD 156"** on one side and **"20"** on the other |
| **40 mg** | `0071-0157-23`<br>`0071-0157-40` | Bottle of 90 tablets<br>Carton of 100 (10 × 10 unit-dose blisters) | White, elliptical; debossed **"PD 157"** on one side and **"40"** on the other |
| **80 mg** | `0071-0158-23`<br>`0071-0158-92` | Bottle of 90 tablets<br>Carton of 64 (8 × 8 unit-dose blisters) | White, elliptical; debossed **"PD 158"** on one side and **"80"** on the other |

---

### Storage and Handling
* **Storage:** Store at controlled room temperature 20°C to 25°C (68°F to 77°F); excursions permitted between 15°C and 30°C (59°F and 86°F).
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGiN8x7fzNPN-K60n5FrPaQmke7YZMHDDBuHxl3IXcjPdCXI0_yhi7tDnPCI_5dWzK7kKvKShT1Dk_rayzhSSla-IqtezqjcQbLstw_bpb6wdDT7W5UoBwUoQEIAs-B7k8idLl7-kGmi1FbD1wb0v6NB_tBkJe4VoLf3q4ionI94Fzl>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHC8yR2AkOOFOmCNXkHk-9dj3tv9jrgIcyEKigrsGCbhY3qtrGUNItqpE8zSDyYB1M4v4-6bo7b0dAH9HEKM4MKKE2bqmGekvIo2ycUibaH-ol_ley7diRlA2aMQW7QIoUtKTI8CTpQ_gACGzZcsCWtRHeTdmKHArccMtPFK64aEJLNkwbBMgPQWynqI6xgR6bUiMk=>
  - origindrug.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEO_3MtG9xWW3xK-JqxjULox4fqq7f1CQBKyegld_NpvuEK5OIJelh_F-AVOZXovS0eoRW72B2CefVn8ilCD5gx0Po8MLt1R20Huqdg9PzAQKu2IqlDGYKF4PsemDtErSq98KVAuCmjxA==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHC8yR2AkOOFOmCNXkHk-9dj3tv9jrgIcyEKigrsGCbhY3qtrGUNItqpE8zSDyYB1M4v4-6bo7b0dAH9HEKM4MKKE2bqmGekvIo2ycUibaH-ol_ley7diRlA2aMQW7QIoUtKTI8CTpQ_gACGzZcsCWtRHeTdmKHArccMtPFK64aEJLNkwbBMgPQWynqI6xgR6bUiMk=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGPNP8o2IUJwVUI3WdC1Vf4Uu-q18kJxnFdWHfR5jGgPvRSJW1bqRJ8uv4LupoKzqJ8eAaC5irqy59OjZRzGC8nsigAbm8o9mjuRGIa51Ye6XHXQft-0XX7rXO2PoT9mFvbN2k77m3wS77QCg9aSVLNz0s_9OQE_tUXp_3nqsT9cZC0R5jfAu4G5XNsSxAX2SwFVo5G>

[24] web search for '"Lipitor" film-coated tablets "10 mg" "20 mg" "40 mg" "80 mg" marketing authorisation holder Viatris electronic medicines compendium'; grounded search summary:
According to the Summary of Product Characteristics (SmPC) published on the **electronic medicines compendium (emc)** for **Lipitor film-coated tablets** (10 mg, 20 mg, 40 mg, and 80 mg), the regulatory and licensing details are as follows:

---

### **1. Marketing Authorisation Holder (MAH)**
* **Holder:** Viatris Products Limited *(listed on emc under Viatris; formerly Upjohn / Pfizer / Mylan)*
* **Address:**  
  Station Close,  
  Potters Bar,  
  Hertfordshire,  
  EN6 1TL,  
  United Kingdom

---

### **2. Marketing Authorisation Numbers (UK / MHRA)**
* **Lipitor 10 mg film-coated tablets:** PL 46302/0298
* **Lipitor 20 mg film-coated tablets:** PL 46302/0301
* **Lipitor 40 mg film-coated tablets:** PL 46302/0303
* **Lipitor 80 mg film-coated tablets:** PL 46302/0305

---

### **3. Key Product Details**
* **Active Substance:** Atorvastatin (as atorvastatin calcium trihydrate)
* **Dosage Form & Appearance:**
  * **10 mg:** White, round (5.6 mm) film-coated tablets debossed with **"10"** on one side and **"ATV"** on the other.
  * **20 mg:** White, round (7.1 mm) film-coated tablets debossed with **"20"** on one side and **"ATV"** on the other.
  * **40 mg:** White, round (9.5 mm) film-coated tablets debossed with **"40"** on one side and **"ATV"** on the other.
  * **80 mg:** White, round (11.9 mm) film-coated tablets debossed with **"80"** on one side and **"ATV"** on the other.
* **Indications:** Adjunct to diet for the reduction of elevated total cholesterol, LDL-cholesterol, apolipoprotein B, and triglycerides in primary hypercholesterolaemia or combined hyperlipidaemia, and for the prevention of cardiovascular events in adult patients at high risk.
sources:
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLdgSnCnzFdN_tmi5RLG4vuf1SyojRLjVYZmIpOOuWkU3ctVnS99e2m5NMOyL0OoZy4KcApNmC4CwYsRA6GwaGBNX0Z1XuWkdXjqXjQIQ8QVbsJfjdlNu9-PBIgnrdevaV-C6SFqQzLg==>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHDxkZfPWathj8YTa3nRRJL44nhQYC3VkFpM2y-nIRYfTU7YOfB-CMF8sOF9R156e-YcSB5u3Ge4iKEmkuH-vxtURow2D59fGsYG72zYvbCrAVg2JJZyxlmRP5rehStWdBWiU7Ay3fIPQ==>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_rmhUoGET_-PTMHv-awjPHys-Hl5jyVrcpf1xQlUNaD-LdL62dnJEtZS9GfKetcg-PDI2x6dBkWQBuQJ14J_FYOked9Wpd5Wvhy0ZwGV6GPK30ET2Qh-Gc8TO1DFZb0I8nn52hY8J_A==>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGF0h6XzQyxXesjTmi3kaPlF4CRmq5FnZJinvSOoLNGnLVVfVPoxB7gOwlY-GCJtQ5JeKX7zvea7nwCkZP3o_pyFS69Og0s4LEuCn4VuqPfgF6tQpEvvfiT-VV3__GdqybXOMra0x0Qqg==>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLdgSnCnzFdN_tmi5RLG4vuf1SyojRLjVYZmIpOOuWkU3ctVnS99e2m5NMOyL0OoZy4KcApNmC4CwYsRA6GwaGBNX0Z1XuWkdXjqXjQIQ8QVbsJfjdlNu9-PBIgnrdevaV-C6SFqQzLg==>

[25] web search for 'EMA Lipitor atorvastatin summary of product characteristics film-coated tablets strengths 10 20 40 80 mg pack'; grounded search summary:
The European harmonised Summary of Product Characteristics (SmPC) details for **Lipitor (atorvastatin)** film-coated tablets (10 mg, 20 mg, 40 mg, and 80 mg) emphasize the packaging and container specifications:

---

### 1. Strengths and Tablet Descriptions (SmPC Section 3)
* **Lipitor 10 mg:** White, round, 5.6 mm film-coated tablets debossed **“10”** on one side and **“ATV”** on the other.
* **Lipitor 20 mg:** White, round, 7.1 mm film-coated tablets debossed **“20”** on one side and **“ATV”** on the other.
* **Lipitor 40 mg:** White, round, 9.5 mm film-coated tablets debossed **“40”** on one side and **“ATV”** on the other.
* **Lipitor 80 mg:** White, round, 11.9 mm film-coated tablets debossed **“80”** on one side and **“ATV”** on the other.

---

### 2. Packaging and Contents of Container (SmPC Section 6.5)
The approved packaging materials and pack configurations across the European Union include:

* **Blister Construction:**
  * **Forming foil:** Polyamide / Aluminium foil / Polyvinyl chloride (PA/Al/PVC).
  * **Lidding/Backing:** Aluminium foil with a vinyl heat-seal coating.
* **Bottle Construction:**
  * High-density polyethylene (HDPE) bottle containing a desiccant, fitted with a squeeze-and-turn child-resistant closure.
* **Pack Sizes Approved:**
  * **Standard blister packs:** 4, 7, 10, 14, 20, 28, 30, 50, 56, 60, 84, 90, 98, and 100 film-coated tablets.
  * **Hospital / Unit-dose blister packs:** 50, 84, 100, 200 (10 × 20), and 500 film-coated tablets.
  * **HDPE bottles:** Typically 90 film-coated tablets.

*(Note: Not all pack sizes may be commercially marketed in each individual EU member state.)*

---

### 3. Storage Precautions (SmPC Section 6.4)
* This medicinal product does not require any special storage conditions (some national licences specify storing in the original package to protect from moisture).

---

### 4. Qualitative Composition & Excipients of Note (SmPC Sections 2 & 6.1)
* **Active Substance:** Atorvastatin (as atorvastatin calcium trihydrate).
* **Core Tablets:** Calcium carbonate, microcrystalline cellulose, lactose monohydrate, croscarmellose sodium, polysorbate 80, hydroxypropylcellulose, magnesium stearate, and simethicone emulsion.
* **Film-Coating (Opadry White YS-1-7040):** Hypromellose, macrogol 8000 (polyethylene glycol), titanium dioxide (E171), talc, and traces of benzoic acid.
* **Excipient warning:** Contains **lactose monohydrate** (amounts proportional to strength: ~27.25 mg for 10 mg, ~54.5 mg for 20 mg, ~109 mg for 40 mg, and ~218 mg for 80 mg).
sources:
  - europa.eu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDa3pZsZGKGBBT3sUA5GmaBgWyMUMSl8-80GcG4aHEH17x7kPWOg9h6xwqM7JsnKyX8d-RXMhtRy8oQcvwwnarCoa01x9UguR0RGOGf4qbqblPJ2xnhjlPgFLeN2O7S-vpD68MGsoBMd9UM-QAMmKmtOWl2w==>
  - hpra.ie <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHtwgxyqF6WUU7zqgKro5uCHrce-kUyWxru3sECBmC_oooIUQR6HVkM97TY9ZkuBP4BLDPKht1FSIlgIs7aDUWW_-RpzpO4Eleh3gRYUsFt_FFXpkJNb1p2GDYyIQ6CpWDu0SmjFlTbGEPXNCfJYEZiyCv25j1Hh-BgInW-EMH7w4ZMDhEpPRc52f4C>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgYLdBZarxEWrqBCa8jkjLPucT5_NXWfonbpdeY9nCxWzJGqCqyFqPIETz1gSqkHnDHp8r8GGp79Tb5Q3_p7apWi3lOv9P3C-20Hlg-K7EutEw86NOGh8NjWLxpuUmYd2gw1laU6rL>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-Px3qdMI-BBW2sy3y1oo2JHD6DXMlRqj6Mh0vU1PWRWdL3JrJjuiP_Yh756twN71d_fSlLVyclOwuXjs04YJc63CVf73Q1m_HRZAfKFxNPFcD5kzjN2Gk4vpxra3Vlc2IbRgJFOm5CQ==>
  - medicines.org.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEfyh6Os-NcDmVP5Cq4TXS0CEEcdPRBjjNDCMS0ju2AUQYJ3ZstROfiD-0-FtPzkRES-bP78J4bB_sJntCvRIOzkIj16ViqxuVIg3HpVey0r1sTXxCUZ27z5Golvw6kP9EEEtdJNpm0>
```

</details>

**Answer:**

## Comparison: Our Atorvastatin Calcium Tablets vs. Lipitor Marketed Strengths

**Sources used:** internal MongoDB business database (drug master, inventory, sales) + public web sources for the branded product *Lipitor*. Note the internal RAGFlow knowledge base returned **no** document on this product (details in caveats). No attached reference files were present in the session working directory, so none could be analyzed.

---

### 1. Our product as recorded internally

From the `drugs` collection (exactly **one** matching product; no other atorvastatin variants exist in the database):

| Field | Value (verbatim) |
|---|---|
| `generic_name` | Atorvastatin Calcium Tablets |
| `brand_name` | Lipitor |
| `specifications` | **20mg × 7 tablets** |
| `dosage_form` | Tablet |
| `approval_number` | H20055567 |
| `manufacturer` | Our Pharmaceutical Co. |
| `therapeutic_area` | Cardiovascular |
| `description` | For patients with primary hypercholesterolemia, including familial hypercholesterolemia (heterozygous) or mixed hyperlipidemia. |

Supporting internal activity (linked only via `drug_id = 4`):

- **Inventory:** 3 batches (MY-250101-A, MY-250615-B, MY-251120-C), total on hand **7,500** units.
- **Sales:** 2 records, total **250** units sold, unit price **45** (revenue 11,250).
- Both the `inventory` and `sales_records` collections carry **no strength/spec field of their own** — the only attributable specification is the master-data value **20 mg × 7 tablets**.

---

### 2. Lipitor as sold on the market (public sources)

| Aspect | Lipitor (public sources) |
|---|---|
| Strengths | **10 mg, 20 mg, 40 mg, 80 mg** (all sources agree) |
| Dosage form | Film-coated tablets |
| Appearance | US: white **elliptical** ("PD 155/156/157/158", Viatris "VLE 155–158"); EU/UK: white **round** ("ATV"), 5.6–11.9 mm |
| Packaging (US) | Bottles of 90; unit-dose cartons (100-count; 64-count for 80 mg) |
| Packaging (EU/UK) | Blister packs 4–100; hospital/unit-dose 50–500; HDPE bottle ~90 |
| Marketer / MAs | US: Viatris Specialty LLC & Parke-Davis (Pfizer); UK MAH: Viatris Products Ltd (PL 46302/…) |

---

### 3. Head-to-head comparison

| Aspect | Our product (internal record) | Lipitor on the market (public) |
|---|---|---|
| Generic name | Atorvastatin Calcium Tablets | atorvastatin calcium |
| Brand (internal field) | Lipitor | Lipitor |
| **Strengths offered** | **1** (20 mg only) | **4** (10 / 20 / 40 / 80 mg) |
| Dosage form | Tablet | Film-coated tablet |
| Pack size | 20 mg × **7 tablets** | 90-tablet bottles, unit-dose, 4–100 blister ranges |
| Approval scheme | H20055567 (China-format approval number) | US NDC / UK PL numbers |
| Manufacturer / MAH | Our Pharmaceutical Co. | Viatris / Parke-Davis (Pfizer) |

**Key differences:**
- **Coverage gap:** We register/stock only **20 mg** — 1 of the 4 strengths Lipitor is marketed in (10/20/40/80 mg). The 10 mg, 40 mg, and 80 mg strengths have no internal counterpart.
- **Overlap:** Only the **20 mg** strength matches directly.
- **Packaging scale:** Our 7-tablet pack is far smaller than Lipitor's typical 90-tablet bottles / larger blister packs — consistent with a 7-day/one-week presentation rather than a chronic-use pack.
- **Form:** Both are oral tablets; public labeling specifies Lipitor as **film-coated**, whereas our internal record only states "Tablet" (no film-coating detail captured).

---

### 4. Caveats & missing information

- **No internal spec document:** The RAGFlow "Drug Labels" knowledge base returned *"The answer you are looking for is not found in the dataset"* — it contains **no** document for Atorvastatin Calcium Tablets. (It returned only unrelated products: nifedipine and amoxicillin/AMOXIL.) So the specification above rests solely on the database master record, with no supporting internal document.
- **Internal spec is single-valued:** Because `inventory` and `sales_records` reference the drug only by `drug_id`, they cannot independently confirm any strength beyond the single master-data entry.
- **Public source links:** The web search returned only **domain-level** sources (fda.gov, nih.gov/DailyMed, europa.eu/EMA, medicines.org.uk, hpra.ie, lipitor.com, rxlist.com) behind Google redirect links — **no canonical page URLs** were supplied. Treat NDC/PL codes and pack sizes as needing direct verification against the primary DailyMed/FDA and EMA/emc SmPC.
- **No attached files:** The session contained no uploaded reference documents to incorporate.

Would you like me to compile this into a downloadable **Markdown/PDF report**, or extend the comparison (e.g., check other dosage strengths or competitor generics)?

---

## 18. route-15 (routing, medium)

**Question:** Which of our antibiotics has the largest inventory, and what does the amoxicillin label in the knowledge base say about storage?

**Gold answer:** Amoxicillin Capsules (25,000 units on hand vs 10,500 for Ceftriaxone Sodium for Injection). The indexed AMOXIL label says to store the 250 mg and 500 mg capsules at or below 20 C (68 F) and dispense in a tight container.

**Route:** expected ['database', 'ragflow']; delegated {'Database Query Agent': 1, 'RAGFlow Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[3] tool ls returned:
No files found

[4] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[5] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[6] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[7] tool aggregate_documents returned:
{"documents": [{"_id": "Cardiovascular", "count": 2}, {"_id": "Antibiotic", "count": 2}, {"_id": "Digestive System", "count": 1}, {"_id": "Antiviral", "count": 1}, {"_id": "Hypertension", "count": 1}, {"_id": "Analgesic/Antipyretic", "count": 1}, {"_id": "Diabetes", "count": 1}, {"_id": "TCM / Cold & Flu", "count": 1}], "count": 8, "appliedLimits": []}

[8] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802dc"}, "drug_id": 1, "generic_name": "Amoxicillin Capsules", "brand_name": "Amoxin", "approval_number": "H20051234", "specifications": "0.25g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "Used to treat upper respiratory tract infections, urogenital infections, and others caused by susceptible bacteria."}, {"_id": {"$oid": "6aabf437cb80345c469802dd"}, "drug_id": 2, "generic_name": "Ibuprofen Sustained-Release Capsules", "brand_name": "Fenbid", "approval_number": "H10900089", "specifications": "0.3g*20 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Analgesic/Antipyretic", "description": "Used to relieve mild to moderate pain such as headache, joint pain, migraine, toothache, muscle pain, neuralgia, and dysmenorrhea. Also used for fever caused by the common cold or influenza."}, {"_id": {"$oid": "6aabf437cb80345c469802de"}, "drug_id": 3, "generic_name": "Metformin Hydrochloride Tablets", "brand_name": "Glucophage", "approval_number": "H20023345", "specifications": "0.5g*48 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Diabetes", "description": "First-line treatment for type 2 diabetes patients not adequately controlled by diet alone, especially those who are obese."}, {"_id": {"$oid": "6aabf437cb80345c469802df"}, "drug_id": 4, "generic_name": "Atorvastatin Calcium Tablets", "brand_name": "Lipitor", "approval_number": "H20055567", "specifications": "20mg*7 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Cardiovascular", "description": "For patients with primary hypercholesterolemia, including familial hypercholesterolemia (heterozygous) or mixed hyperlipidemia."}, {"_id": {"$oid": "6aabf437cb80345c469802e0"}, "drug_id": 5, "generic_name": "Oseltamivir Phosphate Capsules", "brand_name": "Tamiflu", "approval_number": "H20090123", "specifications": "75mg*10 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antiviral", "description": "For the treatment of influenza A and B in adults and children aged 1 year and older."}, {"_id": {"$oid": "6aabf437cb80345c469802e1"}, "drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "approval_number": "H10920012", "specifications": "1.0g/vial", "dosage_form": "Injection", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "For lower respiratory tract, urinary tract, and biliary infections caused by susceptible pathogens, as well as intra-abdominal infections, pelvic infections, skin and soft tissue infections, bone and joint infections, sepsis, meningitis, and more."}, {"_id": {"$oid": "6aabf437cb80345c469802e2"}, "drug_id": 7, "generic_name": "Montmorillonite Powder", "brand_name": "Smecta", "approval_number": "H20000456", "specifications": "3g*10 sachets", "dosage_form": "Powder", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Digestive System", "description": "For acute and chronic diarrhea in adults and children."}, {"_id": {"$oid": "6aabf437cb80345c469802e3"}, "drug_id": 8, "generic_name": "Nifedipine Controlled-Release Tablets", "brand_name": "Adalat", "approval_number": "H20100345", "specifications": "30mg*30 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Hypertension", "description": "1. Hypertension. 2. Coronary heart disease — chronic stable angina (exertional angina)."}, {"_id": {"$oid": "6aabf437cb80345c469802e4"}, "drug_id": 9, "generic_name": "Aspirin Enteric-Coated Tablets", "brand_name": "Bayaspirin", "approval_number": "J20130078", "specifications": "100mg*30 tablets", "dosage_form": "Tablet", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Cardiovascular", "description": "Reduces the risk of onset in patients with suspected acute myocardial infarction; prevents recurrence of myocardial infarction."}, {"_id": {"$oid": "6aabf437cb80345c469802e5"}, "drug_id": 10, "generic_name": "Lianhua Qingwen Capsules", "brand_name": "Lianhua Qingwen", "approval_number": "Z20040063", "specifications": "0.35g*24 capsules", "dosage_form": "Capsule", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "TCM / Cold & Flu", "description": "Clears heat-toxin and disperses lung heat. Used to treat influenza with heat-toxin attacking the lung, presenting as fever or high fever, chills, muscle aches, nasal congestion and runny nose, cough, headache, dry and sore throat."}], "queryResultsCount": 10, "appliedLimits": []}

[9] tool count_documents returned:
{"count": 10}

[10] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e6"}, "inventory_id": 1, "drug_id": 1, "batch_number": "MY-250101-A", "quantity_on_hand": 5000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e7"}, "inventory_id": 2, "drug_id": 1, "batch_number": "MY-250615-B", "quantity_on_hand": 8000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e8"}, "inventory_id": 3, "drug_id": 1, "batch_number": "MY-251120-C", "quantity_on_hand": 12000, "warehouse_location": "Tianjin Warehouse 1 - Zone A", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802e9"}, "inventory_id": 4, "drug_id": 2, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cold Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ea"}, "inventory_id": 5, "drug_id": 2, "batch_number": "MY-250615-B", "quantity_on_hand": 15000, "warehouse_location": "Beijing Warehouse 1 - Zone C", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802eb"}, "inventory_id": 6, "drug_id": 2, "batch_number": "MY-251120-C", "quantity_on_hand": 30000, "warehouse_location": "Tianjin Warehouse 1 - Zone A", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ec"}, "inventory_id": 7, "drug_id": 3, "batch_number": "MY-250101-A", "quantity_on_hand": 3000, "warehouse_location": "Beijing Warehouse 2 - Zone B", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ed"}, "inventory_id": 8, "drug_id": 3, "batch_number": "MY-250615-B", "quantity_on_hand": 4500, "warehouse_location": "Tianjin Warehouse 2 - Zone B", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ee"}, "inventory_id": 9, "drug_id": 3, "batch_number": "MY-251120-C", "quantity_on_hand": 6000, "warehouse_location": "Beijing Warehouse 1 - Zone A", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802ef"}, "inventory_id": 10, "drug_id": 4, "batch_number": "MY-250101-A", "quantity_on_hand": 1000, "warehouse_location": "Tianjin Warehouse 1 - High-Value Zone", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}], "queryResultsCount": 30, "appliedLimits": []}

[11] tool aggregate_documents returned:
{"documents": [{"_id": 10, "total_qty": 160000, "batches": 3}, {"_id": 2, "total_qty": 47000, "batches": 3}, {"_id": 5, "total_qty": 25500, "batches": 3}, {"_id": 1, "total_qty": 25000, "batches": 3}, {"_id": 7, "total_qty": 24000, "batches": 3}, {"_id": 9, "total_qty": 13500, "batches": 3}, {"_id": 3, "total_qty": 13500, "batches": 3}, {"_id": 6, "total_qty": 10500, "batches": 3}, {"_id": 8, "total_qty": 9500, "batches": 3}, {"_id": 4, "total_qty": 7500, "batches": 3}], "count": 10, "appliedLimits": []}

[12] knowledge base 'Drug Labels Assistant' answered:
The requested information about storage conditions is not found in the dataset. The document title is "50542s02950754s01950760s01950761s016lbl.pdf" and includes a section heading "HOW SUPPLIED/STORAGE AND HANDLING" [ID:0], but the provided content under that heading contains only packaging and NDC information, not storage conditions. Other sections in the dataset include CONTRAINDICATIONS [ID:1], WARNINGS AND PRECAUTIONS [ID:1], CLINICAL PHARMACOLOGY [ID:2], DOSAGE FORMS AND STRENGTHS [ID:5], and OVERDOSAGE [ID:3], but none provide storage temperature range, light/moisture protection, keep out of reach of children, refrigeration/freezing instructions, shelf life, or storage after reconstitution. Therefore, verbatim storage conditions for capsules, tablets, or powder for oral suspension cannot be provided from the dataset. The answer you are looking for is not found in the dataset!
retrieved chunks:
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
HOW SUPPLIED/STORAGE AND HANDLING16
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
250-mgCapsule
ThislabelmaynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
NDC 43598-025-01
Bottles of 100
NDC43598-025-05
Bottles of 500
500-mg Capsule
NDC 43598-005-01
Bottles of 100
NDC 43598-005-05
Bottles of 500
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
500-mg Tablet
NDC 43598-024-01
Bottles of 100
NDC 43598-024-05
Bottles of 500
875-mg Tablet
NDC 43598-019-01
Bottles of 100
NDC 43598-019-14
Bottles of 20
Powder for Oral Suspension: Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum-flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
125 mg/5 mL
NDC 43598-022-80
80-mL bottle
NDC 43598-022-52
100-mL bottle
NDC 43598-022-53
150-mL bottle
200 mg/5 mL
NDC 43598-023-50
50-mL bottle 75-mL bottle
NDC 43598-023-51
100-mL bottle
NDC 43598-023-52
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
3
Capsules: 250 mg, 500 mg. Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
Tablets: 500 mg, 875 mg. Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
Powder for Oral Suspension: 125 mg/5 mL, 200 mg/5 mL, 250 mg/5 mL, 400 mg/5 mL. Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum- flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
CONTRAINDICATIONS
4
AMOXIL is contraindicated in patients who have experienced a serious hypersensitivity reaction (e.g., anaphylaxis or Stevens-Johnson syndrome) to AMOXIL or to other β-lactam antibiotics (e.g., penicillins and cephalosporins).
5
WARNINGSANDPRECAUTIONS
5.1Anaphylactic Reactions
Serious and occasionally fatal hypersensitivity (anaphylactic) reactions have been reported in patients on penicillin therapy including amoxicillin. Although anaphylaxis is more frequent following parenteral therapy, it has occurred in patients on oral penicillins. These reactions are more likely to occur in individuals with a history of penicillin hypersensitivity and/or a history of sensitivity to multiple allergens. There have been reports of individuals with a history of penicillin hypersensitivity who have experienced severe reactions when treated with cephalosporins. Before initiating therapy with AMOXIL, careful inquiry should be made regarding previous hypersensitivity reactions to penicillins, cephalosporins, or other allergens.
5.2Clostridium difficile Associated Diarrhea
Clostridium difficile associated diarrhea (CDAD) has been reported with use of nearly all antibacterial agents, including AMOXIL, and may range in severity from mild diarrhea to fatal colitis. Treatment with antibacterial agents alters the normal flora of the colon leading to overgrowth of C. difficile.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
and 250; the cap and body of the 500-mg capsule are imprinted with AMOXIL and 500. Inactive ingredients: D&C Red No. 28, FD&C Blue No. 1, FD&C Red No. 40, gelatin, magnesium stearate, and titanium dioxide.
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side. Inactive ingredients: Colloidal silicon dioxide, crospovidone, FD&C Red No. 30 aluminum lake, hypromellose, magnesium stearate, microcrystalline cellulose, polyethylene glycol, sodium starch glycolate, and titanium dioxide.
Powder for Oral Suspension: Each 5 mL of reconstituted suspension contains 125 mg, 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate. Each 5 mL of the 125-mg reconstituted suspension contains 0.11 mEq (2.51 mg) of sodium. Each 5 mL of the 200-mg reconstituted suspension contains 0.15 mEq (3.39 mg) of sodium. Each 5 mL of the 250-mg reconstituted suspension contains 0.15 mEq (3.36 mg) of sodium; each 5 mL of the 400-mg reconstituted suspension contains 0.19 mEq (4.33 mg) of sodium. Inactive ingredients: FD&C Red No. 3, flavorings, silica gel, sodium benzoate, sodium citrate, sucrose, and xanthan gum.
12
CLINICALPHARMACOLOGY
12.1Mechanism of Action
Amoxicillin is an antibacterial drug. [see Microbiology (12.4)].
12.3Pharmacokinetics
Absorption: Amoxicillin is stable in the presence of gastric acid and is rapidly absorbed after oral administration. The effect of food on the absorption of amoxicillin from the tablets and suspension of AMOXIL has been partially investigated; 400-mg and 875-mg formulations have been studied only when administered at the start of a light meal
Orally administered doses of 250-mg and 500-mg amoxicillin capsules result in average peak blood levels 1 to 2 hours after administration in the range of 3.5 mcg/mL to 5.0 mcg/mL and 5.5 mcg/mL to 7.5 mcg/mL, respectively.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
8.6Dosing in Renal Impairment
Amoxicillin is primarily eliminated by the kidney and dosage adjustment is usually required in patients with severe renal impairment (GFR <30 mL/min). See Dosing in Renal Impairment (2.4) for specific recommendations in patients with renal impairment.
10
OVERDOSAGE
In case of overdosage, discontinue medication, treat symptomatically, and institute supportive measures as required. A prospective study of 51 pediatric patients at a poison-control center suggested that overdosages of less than 250 mg/kg of amoxicillin are not associated with significant clinical symptoms.
Interstitial nephritis resulting in oliguric renal failure has been reported in a small number of patients after overdosage
with amoxicillin'.
Crystalluria, in some cases leading to renal failure, has also been reported after amoxicillin overdosage in adult and pediatric patients. In case of overdosage, adequate fluid intake and diuresis should be maintained to reduce the risk of amoxicillin crystalluria.
Renal impairment appears to be reversible with cessation of drug administration. High blood levels may occur more readily in patients with impaired renal function because of decreased renal clearance of amoxicillin. Amoxicillin may be removed from circulation by hemodialysis.
11
DESCRIPTION
Formulations of AMOXIL contain amoxicillin, a semisynthetic antibiotic, an analog of ampicillin, with a broad spectrum of bactericidal activity against many Gram-positive and Gram-negative microorganisms. Chemically, it is (2S,5R,6R)-6-[(R)-(-)-2-amino-2-(p-hydroxyphenyl)acetamido]-3,3-dimethyl-7-ox0-4-thia-1-azabicyclo[3.2.0]heptane 2-carboxylic acid trihydrate. It may be represented structurally as:
The amoxicillin molecular formula is C16H19N3OsS·3H2O, and the molecular weight is 419.45.
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL
This label may not be the latest approved by FDA For current labeling information, please visit https://www.fda.gov/drugsatfda
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
Mean amoxicillin pharmacokinetic parameters from an open, two-part, single-dose crossover bioequivalence study in 27 adults comparing 875 mg of AMOXIL with 875 mg of AUGMENTIN° (amoxicillin/clavulanate potassium) showed that the 875-mg tablet of AMOXIL produces an AUCo-o of 35.4 ± 8.1 mcgohr/mL and a Cmax of 13.8 ± 4.1 mcg/mL.
Dosing was at the start of a light meal following an overnight fast.
Orally administered doses of amoxicillin suspension, 125 mg/5 mL and 250 mg/5 mL, result in average peak blood levels 1 to 2 hours after administration in the range of 1.5 mcg/mL to 3.0 mcg/mL and 3.5 mcg/mL to 5.0 mcg/mL, respectively.
Oral administration of single doses of 400-mg chewable tablets and 400 mg/5 mL suspension of AMOXIL to 24 adult volunteers yielded comparable pharmacokinetic data:
This label may not be the latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Administered at the start of a light meal.
 Mean values of 24 normal volunteers. Peak concentrations occurred approximately 1 hour after the dose.
Distribution: Amoxicillin diffuses readily into most body tissues and fluids, with the exception of brain and spinal fluid, except when meninges are inflamed. In blood serum, amoxicillin is approximately 20% protein-bound. Following a 1-gram dose and utilizing a special skin window technique to determine levels of the antibiotic, it was noted that therapeutic levels were found in the interstitial fluid.
Metabolism and Excretion: The half-life of amoxicillin is 61.3 minutes. Approximately 60% of an orally administered dose of amoxicillin is excreted in the urine within 6 to 8 hours. Detectable serum levels are observed up to 8 hours after an orally administered dose of amoxicillin. Since most of the amoxicillin is excreted unchanged in the urine, its excretion can be delayed by concurrent administration of probenecid [see DRUG INTERACTIONS (7.1)].
Microbiology12.4
Mechanism of Action
Amoxicillin is similar to penicillin in its bactericidal action against susceptible bacteria during the stage of active multiplication. It acts through the inhibition of cell wall biosynthesis that leads to the death of the bacteria.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
This label may not be the latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
HIGHLIGHTS OF PRESCRIBING INFORMATION
--DOSAGEFORMSANDSTRENGTHS---
Capsules: 250 mg, 500 mg (3)
These highlights do not include all the information needed to use AMOXIL safely and effectively. See full prescribing information
Tablets: 500 mg, 875 mg (3) Powder for Oral Suspension: 125 mg/5 mL, 200 mg/5 mL,
for AMOXIL.
250 mg/5 mL, 400 mg/5 mL (3)
AMOXIL? (amoxicillin) capsules, tablets, or powder for oral
--- CONTRAINDICATIONS ---
History of a serious hypersensitivity reaction (e.g., anaphylaxis or
suspension Initial U.S. Approval: 1974
Stevens-Johnson syndrome) to AMOXIL or to other beta-lactams (e.g., penicillins or cephalosporins) (4)
---- WARNINGS AND PRECAUTIONS ---
RECENTMAJORCHANGES-
Indications and Usage, Gonorrhea (1.5)
Removed 9/2015
Anaphylactic  reactions:  Serious  and  occasionally  fatal
Dosage and Administration, Gonorrhea (2.1)
Removed 9/2015
anaphylactic reactions have been reported in patients on penicillin therapy.  Serious  anaphylactic  reactions  require  immediate emergency treatment with supportive measures. (5.1)
--INDICATIONSANDUSAGE-
Clostridium  difficile-associated  diarrhea  (ranging  from  mild
AMOXIL is a penicillin-class antibacterial indicated for treatment of infections due to susceptible strains of designated microorganisms.
diarrhea to fatal colitis): Evaluate if diarrhea occurs. (5.2)
Infections of the ear, nose, throat, genitourinary tract, skin and
-ADVERSE REACTIONS-
The most common adverse reactions (> 1%) observed in clinical trials
skin structure, and lower respiratory tract. (1.1 - 1.4)
of AMOXIL capsules, tablets or oral suspension were diarrhea, rash,
In combination for treatment of H. pylori infection and duodenal ulcer disease. (1.5)

[13] tool aggregate_documents returned:
{"documents": [{"_id": {"drug_id": 1, "generic_name": "Amoxicillin Capsules", "dosage_form": "Capsule", "specifications": "0.25g*24 capsules"}, "total_qty": 25000, "batches": 3}, {"_id": {"drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "dosage_form": "Injection", "specifications": "1.0g/vial"}, "total_qty": 10500, "batches": 3}], "count": 2, "appliedLimits": []}

[14] tool aggregate_documents returned:
{"documents": [{"_id": null, "grand_total": 35500}], "count": 1, "appliedLimits": []}

[15] knowledge base 'Drug Labels Assistant' answered:
Based on the provided knowledge base, there is one amoxicillin label document titled **50542s02950754s01950760s01950761s016lbl.pdf** [ID:0][ID:1][ID:2][ID:3][ID:4][ID:5]. The label does not include a version date or approval date; it only states that it “may not be the latest approved by FDA” and directs readers to the FDA website for current labeling information [ID:0][ID:1][ID:5].

**Amoxicillin products listed, with storage statements where provided:**

- **Capsules: 250 mg** [ID:0][ID:1][ID:2][ID:3].  
  Storage: Store at or below 20° C (68° F) — for 250 mg and 500 mg capsules and 125 mg and 250 mg unreconstituted powder [ID:5].

- **Capsules: 500 mg** [ID:0][ID:1][ID:2][ID:3].  
  Storage: Store at or below 20° C (68° F) — for 250 mg and 500 mg capsules and 125 mg and 250 mg unreconstituted powder [ID:5].

- **Tablets: 500 mg** [ID:0][ID:1][ID:2][ID:3].  
  Storage: Store at or below 25° C (77° F) — for 500 mg and 875 mg tablets and 200 mg and 400 mg unreconstituted powder [ID:5].

- **Tablets: 875 mg** [ID:0][ID:1][ID:2][ID:3].  
  Storage: Store at or below 25° C (77° F) — for 500 mg and 875 mg tablets and 200 mg and 400 mg unreconstituted powder [ID:5].

- **Powder for Oral Suspension: 125 mg/5 mL** [ID:0][ID:1][ID:2][ID:3].  
  Storage: Store at or below 20° C (68° F) — for 250 mg and 500 mg capsules and 125 mg and 250 mg unreconstituted powder [ID:5].

- **Powder for Oral Suspension: 200 mg/5 mL** [ID:0][ID:1][ID:2][ID:3].  
  Storage: Store at or below 25° C (77° F) — for 500 mg and 875 mg tablets and 200 mg and 400 mg unreconstituted powder [ID:5].

- **Powder for Oral Suspension: 250 mg/5 mL** [ID:1][ID:2][ID:3][ID:5].  
  Storage: Store at or below 20° C (68° F) — for 250 mg and 500 mg capsules and 125 mg and 250 mg unreconstituted powder [ID:5].

- **Powder for Oral Suspension: 400 mg/5 mL** [ID:1][ID:2][ID:3][ID:5].  
  Storage: Store at or below 25° C (77° F) — for 500 mg and 875 mg tablets and 200 mg and 400 mg unreconstituted powder [ID:5].

Additionally, the labeling states: “Dispense in a tight container” [ID:5].
retrieved chunks:
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
HOW SUPPLIED/STORAGE AND HANDLING16
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
250-mgCapsule
ThislabelmaynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
NDC 43598-025-01
Bottles of 100
NDC43598-025-05
Bottles of 500
500-mg Capsule
NDC 43598-005-01
Bottles of 100
NDC 43598-005-05
Bottles of 500
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
500-mg Tablet
NDC 43598-024-01
Bottles of 100
NDC 43598-024-05
Bottles of 500
875-mg Tablet
NDC 43598-019-01
Bottles of 100
NDC 43598-019-14
Bottles of 20
Powder for Oral Suspension: Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum-flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
125 mg/5 mL
NDC 43598-022-80
80-mL bottle
NDC 43598-022-52
100-mL bottle
NDC 43598-022-53
150-mL bottle
200 mg/5 mL
NDC 43598-023-50
50-mL bottle 75-mL bottle
NDC 43598-023-51
100-mL bottle
NDC 43598-023-52
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
This label may not be the latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
HIGHLIGHTS OF PRESCRIBING INFORMATION
--DOSAGEFORMSANDSTRENGTHS---
Capsules: 250 mg, 500 mg (3)
These highlights do not include all the information needed to use AMOXIL safely and effectively. See full prescribing information
Tablets: 500 mg, 875 mg (3) Powder for Oral Suspension: 125 mg/5 mL, 200 mg/5 mL,
for AMOXIL.
250 mg/5 mL, 400 mg/5 mL (3)
AMOXIL? (amoxicillin) capsules, tablets, or powder for oral
--- CONTRAINDICATIONS ---
History of a serious hypersensitivity reaction (e.g., anaphylaxis or
suspension Initial U.S. Approval: 1974
Stevens-Johnson syndrome) to AMOXIL or to other beta-lactams (e.g., penicillins or cephalosporins) (4)
---- WARNINGS AND PRECAUTIONS ---
RECENTMAJORCHANGES-
Indications and Usage, Gonorrhea (1.5)
Removed 9/2015
Anaphylactic  reactions:  Serious  and  occasionally  fatal
Dosage and Administration, Gonorrhea (2.1)
Removed 9/2015
anaphylactic reactions have been reported in patients on penicillin therapy.  Serious  anaphylactic  reactions  require  immediate emergency treatment with supportive measures. (5.1)
--INDICATIONSANDUSAGE-
Clostridium  difficile-associated  diarrhea  (ranging  from  mild
AMOXIL is a penicillin-class antibacterial indicated for treatment of infections due to susceptible strains of designated microorganisms.
diarrhea to fatal colitis): Evaluate if diarrhea occurs. (5.2)
Infections of the ear, nose, throat, genitourinary tract, skin and
-ADVERSE REACTIONS-
The most common adverse reactions (> 1%) observed in clinical trials
skin structure, and lower respiratory tract. (1.1 - 1.4)
of AMOXIL capsules, tablets or oral suspension were diarrhea, rash,
In combination for treatment of H. pylori infection and duodenal ulcer disease. (1.5)
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
3
Capsules: 250 mg, 500 mg. Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
Tablets: 500 mg, 875 mg. Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
Powder for Oral Suspension: 125 mg/5 mL, 200 mg/5 mL, 250 mg/5 mL, 400 mg/5 mL. Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum- flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
CONTRAINDICATIONS
4
AMOXIL is contraindicated in patients who have experienced a serious hypersensitivity reaction (e.g., anaphylaxis or Stevens-Johnson syndrome) to AMOXIL or to other β-lactam antibiotics (e.g., penicillins and cephalosporins).
5
WARNINGSANDPRECAUTIONS
5.1Anaphylactic Reactions
Serious and occasionally fatal hypersensitivity (anaphylactic) reactions have been reported in patients on penicillin therapy including amoxicillin. Although anaphylaxis is more frequent following parenteral therapy, it has occurred in patients on oral penicillins. These reactions are more likely to occur in individuals with a history of penicillin hypersensitivity and/or a history of sensitivity to multiple allergens. There have been reports of individuals with a history of penicillin hypersensitivity who have experienced severe reactions when treated with cephalosporins. Before initiating therapy with AMOXIL, careful inquiry should be made regarding previous hypersensitivity reactions to penicillins, cephalosporins, or other allergens.
5.2Clostridium difficile Associated Diarrhea
Clostridium difficile associated diarrhea (CDAD) has been reported with use of nearly all antibacterial agents, including AMOXIL, and may range in severity from mild diarrhea to fatal colitis. Treatment with antibacterial agents alters the normal flora of the colon leading to overgrowth of C. difficile.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
and 250; the cap and body of the 500-mg capsule are imprinted with AMOXIL and 500. Inactive ingredients: D&C Red No. 28, FD&C Blue No. 1, FD&C Red No. 40, gelatin, magnesium stearate, and titanium dioxide.
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side. Inactive ingredients: Colloidal silicon dioxide, crospovidone, FD&C Red No. 30 aluminum lake, hypromellose, magnesium stearate, microcrystalline cellulose, polyethylene glycol, sodium starch glycolate, and titanium dioxide.
Powder for Oral Suspension: Each 5 mL of reconstituted suspension contains 125 mg, 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate. Each 5 mL of the 125-mg reconstituted suspension contains 0.11 mEq (2.51 mg) of sodium. Each 5 mL of the 200-mg reconstituted suspension contains 0.15 mEq (3.39 mg) of sodium. Each 5 mL of the 250-mg reconstituted suspension contains 0.15 mEq (3.36 mg) of sodium; each 5 mL of the 400-mg reconstituted suspension contains 0.19 mEq (4.33 mg) of sodium. Inactive ingredients: FD&C Red No. 3, flavorings, silica gel, sodium benzoate, sodium citrate, sucrose, and xanthan gum.
12
CLINICALPHARMACOLOGY
12.1Mechanism of Action
Amoxicillin is an antibacterial drug. [see Microbiology (12.4)].
12.3Pharmacokinetics
Absorption: Amoxicillin is stable in the presence of gastric acid and is rapidly absorbed after oral administration. The effect of food on the absorption of amoxicillin from the tablets and suspension of AMOXIL has been partially investigated; 400-mg and 875-mg formulations have been studied only when administered at the start of a light meal
Orally administered doses of 250-mg and 500-mg amoxicillin capsules result in average peak blood levels 1 to 2 hours after administration in the range of 3.5 mcg/mL to 5.0 mcg/mL and 5.5 mcg/mL to 7.5 mcg/mL, respectively.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
8.6Dosing in Renal Impairment
Amoxicillin is primarily eliminated by the kidney and dosage adjustment is usually required in patients with severe renal impairment (GFR <30 mL/min). See Dosing in Renal Impairment (2.4) for specific recommendations in patients with renal impairment.
10
OVERDOSAGE
In case of overdosage, discontinue medication, treat symptomatically, and institute supportive measures as required. A prospective study of 51 pediatric patients at a poison-control center suggested that overdosages of less than 250 mg/kg of amoxicillin are not associated with significant clinical symptoms.
Interstitial nephritis resulting in oliguric renal failure has been reported in a small number of patients after overdosage
with amoxicillin'.
Crystalluria, in some cases leading to renal failure, has also been reported after amoxicillin overdosage in adult and pediatric patients. In case of overdosage, adequate fluid intake and diuresis should be maintained to reduce the risk of amoxicillin crystalluria.
Renal impairment appears to be reversible with cessation of drug administration. High blood levels may occur more readily in patients with impaired renal function because of decreased renal clearance of amoxicillin. Amoxicillin may be removed from circulation by hemodialysis.
11
DESCRIPTION
Formulations of AMOXIL contain amoxicillin, a semisynthetic antibiotic, an analog of ampicillin, with a broad spectrum of bactericidal activity against many Gram-positive and Gram-negative microorganisms. Chemically, it is (2S,5R,6R)-6-[(R)-(-)-2-amino-2-(p-hydroxyphenyl)acetamido]-3,3-dimethyl-7-ox0-4-thia-1-azabicyclo[3.2.0]heptane 2-carboxylic acid trihydrate. It may be represented structurally as:
The amoxicillin molecular formula is C16H19N3OsS·3H2O, and the molecular weight is 419.45.
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL
This label may not be the latest approved by FDA For current labeling information, please visit https://www.fda.gov/drugsatfda
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
250 mg/5 mL
NDC43598-009-80
80-mL bottle
NDC 43598-009-52
100-mL bottle
NDC 43598-009-53
150-mL bottle
400 mg/5 mL
NDC 43598-007-50
50-mL bottle
NDC 43598-007-51
75-mL bottle
NDC 43598-007-52
100-mL bottle
Store at or below 20° C (68° F) - 250 mg and 500 mg Capsules and 125 mg and 250 mg unreconstituted powder.
Store at or below 25° C (77° F) - 500 mg and 875 mg Tablets and 200 mg and 400 mg unreconstituted powder.
Dispense in a tight container.
17PATIENTCOUNSELINGINFORMATION
InformationforPatients
Thislabel maynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Patients should be advised that AMOXIL may be taken every 8 hours or every 12 hours, depending on the dose prescribed.
Patients should be counseled that antibacterial drugs, including AMOXIL, should only be used to treat bacterial infections. They do not treat viral infections (e.g., the common cold). When AMOXIL is prescribed to treat a bacterial infection, patients should be told that although it is common to feel better early in the course of therapy, the medication should be taken exactly as directed. Skipping doses or not completing the full course of therapy may: (1) decrease the effectiveness of the immediate treatment, and (2) increase the likelihood that bacteria will develop resistance and will not be treatable by AMOXIL or other antibacterial drugs in the future.
Patients should be counseled that diarrhea is a common problem caused by antibiotics, and it usually ends when the antibiotic is discontinued. Sometimes after starting treatment with antibiotics, patients can develop watery and bloody stools (with or without stomach cramps and fever) even as late as 2 or more months after having taken their last dose of the antibiotic. If this occurs, patients should contact their physician as soon as possible.
Patients should be aware that AMOXIL contains a penicillin class drug product that can cause allergic reactions in someindividuals.
AMOXIL is registered trademark of GlaxoSmithKline and is licensed to Dr. Reddy's Laboratories Inc.

[16] knowledge base 'Drug Labels Assistant' answered:
Based on the provided dataset, here is the requested information.

**Verbatim text of "HOW SUPPLIED/STORAGE AND HANDLING" (combining the relevant content from IDs 0, 1, and 2):**

The section heading appears as:

HOW SUPPLIED/STORAGE AND HANDLING16 [ID:0]

The content includes the following text with NDC numbers, packaging, and storage statements exactly as written in the dataset:

Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
250-mgCapsule
ThislabelmaynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
NDC 43598-025-01
Bottles of 100
NDC43598-025-05
Bottles of 500
500-mg Capsule
NDC 43598-005-01
Bottles of 100
NDC 43598-005-05
Bottles of 500
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
500-mg Tablet
NDC 43598-024-01
Bottles of 100
NDC 43598-024-05
Bottles of 500
875-mg Tablet
NDC 43598-019-01
Bottles of 100
NDC 43598-019-14
Bottles of 20
Powder for Oral Suspension: Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum-flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
125 mg/5 mL
NDC 43598-022-80
80-mL bottle
NDC 43598-022-52
100-mL bottle
NDC 43598-022-53
150-mL bottle
200 mg/5 mL
NDC 43598-023-50
50-mL bottle 75-mL bottle
NDC 43598-023-51
100-mL bottle
NDC 43598-023-52 [ID:0]

250 mg/5 mL
NDC43598-009-80
80-mL bottle
NDC 43598-009-52
100-mL bottle
NDC 43598-009-53
150-mL bottle
400 mg/5 mL
NDC 43598-007-50
50-mL bottle
NDC 43598-007-51
75-mL bottle
NDC 43598-007-52
100-mL bottle
Store at or below 20° C (68° F) - 250 mg and 500 mg Capsules and 125 mg and 250 mg unreconstituted powder.
Store at or below 25° C (77° F) - 500 mg and 875 mg Tablets and 200 mg and 400 mg unreconstituted powder.
Dispense in a tight container. [ID:1]

Additionally, the table of contents lists the section as:

16 HOW SUPPLIED/STORAGE AND
HANDLING [ID:2]

**Regarding the appearance of specific words in that section:**

- **"store"** — Yes. It appears in the storage statements: "Store at or below 20° C (68° F)" and "Store at or below 25° C (77° F)" [ID:1].
- **"storage"** — Yes. It appears in the section heading "HOW SUPPLIED/STORAGE AND HANDLING" [ID:0][ID:2].
- **"25"** — Yes. It appears in the storage statement "Store at or below 25° C (77° F)" and in NDC 43598-025-01 and NDC 43598-025-05 [ID:0][ID:1].
- **"refrigerat"** — No. This word (or any word beginning with "refrigerat") does not appear in that section based on the provided dataset content [ID:0][ID:1][ID:2].
- **"freez"** — No. This word (or any word beginning with "freez") does not appear in that section based on the provided dataset content [ID:0][ID:1][ID:2].
- **"light"** — No. This word does not appear in that section based on the provided dataset content [ID:0][ID:1][ID:2].
- **"moisture"** — No. This word does not appear in that section based on the provided dataset content [ID:0][ID:1][ID:2].
- **"children"** — No. This word does not appear in that section based on the provided dataset content [ID:0][ID:1][ID:2].
retrieved chunks:
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
HOW SUPPLIED/STORAGE AND HANDLING16
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
250-mgCapsule
ThislabelmaynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
NDC 43598-025-01
Bottles of 100
NDC43598-025-05
Bottles of 500
500-mg Capsule
NDC 43598-005-01
Bottles of 100
NDC 43598-005-05
Bottles of 500
Tablets: Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
500-mg Tablet
NDC 43598-024-01
Bottles of 100
NDC 43598-024-05
Bottles of 500
875-mg Tablet
NDC 43598-019-01
Bottles of 100
NDC 43598-019-14
Bottles of 20
Powder for Oral Suspension: Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum-flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
125 mg/5 mL
NDC 43598-022-80
80-mL bottle
NDC 43598-022-52
100-mL bottle
NDC 43598-022-53
150-mL bottle
200 mg/5 mL
NDC 43598-023-50
50-mL bottle 75-mL bottle
NDC 43598-023-51
100-mL bottle
NDC 43598-023-52
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
250 mg/5 mL
NDC43598-009-80
80-mL bottle
NDC 43598-009-52
100-mL bottle
NDC 43598-009-53
150-mL bottle
400 mg/5 mL
NDC 43598-007-50
50-mL bottle
NDC 43598-007-51
75-mL bottle
NDC 43598-007-52
100-mL bottle
Store at or below 20° C (68° F) - 250 mg and 500 mg Capsules and 125 mg and 250 mg unreconstituted powder.
Store at or below 25° C (77° F) - 500 mg and 875 mg Tablets and 200 mg and 400 mg unreconstituted powder.
Dispense in a tight container.
17PATIENTCOUNSELINGINFORMATION
InformationforPatients
Thislabel maynotbethelatestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Patients should be advised that AMOXIL may be taken every 8 hours or every 12 hours, depending on the dose prescribed.
Patients should be counseled that antibacterial drugs, including AMOXIL, should only be used to treat bacterial infections. They do not treat viral infections (e.g., the common cold). When AMOXIL is prescribed to treat a bacterial infection, patients should be told that although it is common to feel better early in the course of therapy, the medication should be taken exactly as directed. Skipping doses or not completing the full course of therapy may: (1) decrease the effectiveness of the immediate treatment, and (2) increase the likelihood that bacteria will develop resistance and will not be treatable by AMOXIL or other antibacterial drugs in the future.
Patients should be counseled that diarrhea is a common problem caused by antibiotics, and it usually ends when the antibiotic is discontinued. Sometimes after starting treatment with antibiotics, patients can develop watery and bloody stools (with or without stomach cramps and fever) even as late as 2 or more months after having taken their last dose of the antibiotic. If this occurs, patients should contact their physician as soon as possible.
Patients should be aware that AMOXIL contains a penicillin class drug product that can cause allergic reactions in someindividuals.
AMOXIL is registered trademark of GlaxoSmithKline and is licensed to Dr. Reddy's Laboratories Inc.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
7.5 Other Antibacterials
16 HOW SUPPLIED/STORAGE AND
7.6 Effects on Laboratory Tests
HANDLING
8USEIN SPECIFIC POPULATIONS
17 PATIENT COUNSELINGINFORMATION
8.1 Pregnancy
*Sections or subsections omitted from the full prescribing
8.2 Labor and Delivery
information are not listed.
8.3 Nursing Mothers
This label may notbethe latest approved by FDA For current labeling information, please visit https://www.fda.gov/drugsatfda
FULLPRESCRIBINGINFORMATION
INDICATIONS AND USAGE
1
1.1
Infections of the Ear, Nose, and Throat: AMOXIL? is indicated in the treatment of infections due to susceptible (ONLY   β-lactamase-negative) isolates  of  Streptococcus  species.  (α-  and  β-hemolytic  isolates  only), Streptococcus pneumoniae,Staphylococcus spp.,orHaemophilus influenzae.
1.2
Infections of the Genitourinary Tract: AMOXIL? is indicated in the treatment of infections due to susceptible (ONLY β-lactamase-negative) isolates of Escherichia coli, Proteus mirabilis, or Enterococcus faecalis.
Infections of the Skin and Skin Structure: AMOXIL? is indicated in the treatment of infections due to susceptible
1.3
(ONLY β-lactamase-negative) isolates of Streptococcus spp. (α- and β-hemolytic isolates only), Staphylococcus spp., or E. coli.
1.4
Infections of the Lower Respiratory Tract: AMOXIL? is indicated in the treatment of infections due to susceptible (ONLY β-lactamase-negative) isolates of Streptococcus spp. (α- and β-hemolytic isolates only), S. pneumoniae, Staphylococcus spp., or H. influenzae.
1.5
Helicobacter pylori Infection
Triple therapy for Helicobacter pylori with clarithromycin and lansoprazole: AMOXIL, in combination with clarithromycin plus lansoprazole as triple therapy, is indicated for the treatment of patients with H. pylori infection and duodenal ulcer disease (active or 1-year history of a duodenal ulcer) to eradicate H. pylori. Eradication of H. pylori has been shown to reduce the risk of duodenal ulcer recurrence.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
8.6Dosing in Renal Impairment
Amoxicillin is primarily eliminated by the kidney and dosage adjustment is usually required in patients with severe renal impairment (GFR <30 mL/min). See Dosing in Renal Impairment (2.4) for specific recommendations in patients with renal impairment.
10
OVERDOSAGE
In case of overdosage, discontinue medication, treat symptomatically, and institute supportive measures as required. A prospective study of 51 pediatric patients at a poison-control center suggested that overdosages of less than 250 mg/kg of amoxicillin are not associated with significant clinical symptoms.
Interstitial nephritis resulting in oliguric renal failure has been reported in a small number of patients after overdosage
with amoxicillin'.
Crystalluria, in some cases leading to renal failure, has also been reported after amoxicillin overdosage in adult and pediatric patients. In case of overdosage, adequate fluid intake and diuresis should be maintained to reduce the risk of amoxicillin crystalluria.
Renal impairment appears to be reversible with cessation of drug administration. High blood levels may occur more readily in patients with impaired renal function because of decreased renal clearance of amoxicillin. Amoxicillin may be removed from circulation by hemodialysis.
11
DESCRIPTION
Formulations of AMOXIL contain amoxicillin, a semisynthetic antibiotic, an analog of ampicillin, with a broad spectrum of bactericidal activity against many Gram-positive and Gram-negative microorganisms. Chemically, it is (2S,5R,6R)-6-[(R)-(-)-2-amino-2-(p-hydroxyphenyl)acetamido]-3,3-dimethyl-7-ox0-4-thia-1-azabicyclo[3.2.0]heptane 2-carboxylic acid trihydrate. It may be represented structurally as:
The amoxicillin molecular formula is C16H19N3OsS·3H2O, and the molecular weight is 419.45.
Capsules: Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL
This label may not be the latest approved by FDA For current labeling information, please visit https://www.fda.gov/drugsatfda
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
This label may not be the latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
HIGHLIGHTS OF PRESCRIBING INFORMATION
--DOSAGEFORMSANDSTRENGTHS---
Capsules: 250 mg, 500 mg (3)
These highlights do not include all the information needed to use AMOXIL safely and effectively. See full prescribing information
Tablets: 500 mg, 875 mg (3) Powder for Oral Suspension: 125 mg/5 mL, 200 mg/5 mL,
for AMOXIL.
250 mg/5 mL, 400 mg/5 mL (3)
AMOXIL? (amoxicillin) capsules, tablets, or powder for oral
--- CONTRAINDICATIONS ---
History of a serious hypersensitivity reaction (e.g., anaphylaxis or
suspension Initial U.S. Approval: 1974
Stevens-Johnson syndrome) to AMOXIL or to other beta-lactams (e.g., penicillins or cephalosporins) (4)
---- WARNINGS AND PRECAUTIONS ---
RECENTMAJORCHANGES-
Indications and Usage, Gonorrhea (1.5)
Removed 9/2015
Anaphylactic  reactions:  Serious  and  occasionally  fatal
Dosage and Administration, Gonorrhea (2.1)
Removed 9/2015
anaphylactic reactions have been reported in patients on penicillin therapy.  Serious  anaphylactic  reactions  require  immediate emergency treatment with supportive measures. (5.1)
--INDICATIONSANDUSAGE-
Clostridium  difficile-associated  diarrhea  (ranging  from  mild
AMOXIL is a penicillin-class antibacterial indicated for treatment of infections due to susceptible strains of designated microorganisms.
diarrhea to fatal colitis): Evaluate if diarrhea occurs. (5.2)
Infections of the ear, nose, throat, genitourinary tract, skin and
-ADVERSE REACTIONS-
The most common adverse reactions (> 1%) observed in clinical trials
skin structure, and lower respiratory tract. (1.1 - 1.4)
of AMOXIL capsules, tablets or oral suspension were diarrhea, rash,
In combination for treatment of H. pylori infection and duodenal ulcer disease. (1.5)
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
Mean amoxicillin pharmacokinetic parameters from an open, two-part, single-dose crossover bioequivalence study in 27 adults comparing 875 mg of AMOXIL with 875 mg of AUGMENTIN° (amoxicillin/clavulanate potassium) showed that the 875-mg tablet of AMOXIL produces an AUCo-o of 35.4 ± 8.1 mcgohr/mL and a Cmax of 13.8 ± 4.1 mcg/mL.
Dosing was at the start of a light meal following an overnight fast.
Orally administered doses of amoxicillin suspension, 125 mg/5 mL and 250 mg/5 mL, result in average peak blood levels 1 to 2 hours after administration in the range of 1.5 mcg/mL to 3.0 mcg/mL and 3.5 mcg/mL to 5.0 mcg/mL, respectively.
Oral administration of single doses of 400-mg chewable tablets and 400 mg/5 mL suspension of AMOXIL to 24 adult volunteers yielded comparable pharmacokinetic data:
This label may not be the latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Administered at the start of a light meal.
 Mean values of 24 normal volunteers. Peak concentrations occurred approximately 1 hour after the dose.
Distribution: Amoxicillin diffuses readily into most body tissues and fluids, with the exception of brain and spinal fluid, except when meninges are inflamed. In blood serum, amoxicillin is approximately 20% protein-bound. Following a 1-gram dose and utilizing a special skin window technique to determine levels of the antibiotic, it was noted that therapeutic levels were found in the interstitial fluid.
Metabolism and Excretion: The half-life of amoxicillin is 61.3 minutes. Approximately 60% of an orally administered dose of amoxicillin is excreted in the urine within 6 to 8 hours. Detectable serum levels are observed up to 8 hours after an orally administered dose of amoxicillin. Since most of the amoxicillin is excreted unchanged in the urine, its excretion can be delayed by concurrent administration of probenecid [see DRUG INTERACTIONS (7.1)].
Microbiology12.4
Mechanism of Action
Amoxicillin is similar to penicillin in its bactericidal action against susceptible bacteria during the stage of active multiplication. It acts through the inhibition of cell wall biosynthesis that leads to the death of the bacteria.
```

</details>

**Answer:**

Both internal sources responded. Here's the combined answer.

---

# Antibiotic Inventory & Amoxicillin Label Storage

## 1. Antibiotic with the largest inventory — *internal database record*

Our `drugs` collection contains only **10 products total**, of which exactly **2** carry the category `therapeutic_area = "Antibiotic"`. Summing `inventory.quantity_on_hand` across all batches per drug:

| Rank | Drug name | Form / Spec | Total qty on hand | #Batches |
|------|-----------|-------------|-------------------|----------|
| **1** | **Amoxicillin Capsules (Amoxin)** | Capsule, 0.25 g × 24 caps | **25,000** | 3 |
| 2 | Ceftriaxone Sodium for Injection (Rocephin) | Injection, 1.0 g/vial | 10,500 | 3 |

**➡️ The antibiotic with the largest inventory is Amoxicillin Capsules (Amoxin): 25,000 units on hand across 3 batches** — more than double the next antibiotic (Ceftriaxone, 10,500).

*Method:* `$match` (therapeutic_area) → `$lookup` (`drugs.drug_id` = `inventory.drug_id`) → `$unwind` → `$group` (sum quantity, count `batch_number`).
*Caveats:* No dedicated unit-of-measure field exists — units above are inferred from `specifications`, not authoritative DB values. The two quantities are in different native units (capsules vs. vials), so no like-for-like total is meaningful. No other antibiotic names (azithromycin, ciprofloxacin, doxycycline, penicillin) exist in the database.

## 2. What the amoxicillin label says about storage — *retrieved knowledge-base document*

Source: **`50542s02950754s01950760s01950761s016lbl.pdf`**, §16 "HOW SUPPLIED/STORAGE AND HANDLING" (brand: AMOXIL / amoxicillin trihydrate). Verbatim statements:

| Product / Strength / Form | Storage statement |
|---|---|
| Capsules 250 mg & 500 mg | Store at or below **20 °C (68 °F)** |
| Tablets 500 mg & 875 mg | Store at or below **25 °C (77 °F)** |
| Oral Suspension 125 & 250 mg/5 mL (unreconstituted) | Store at or below **20 °C (68 °F)** |
| Oral Suspension 200 & 400 mg/5 mL (unreconstituted) | Store at or below **25 °C (77 °F)** |

> "Store at or below 20° C (68° F) - 250 mg and 500 mg Capsules and 125 mg and 250 mg unreconstituted powder."
> "Store at or below 25° C (77° F) - 500 mg and 875 mg Tablets and 200 mg and 400 mg unreconstituted powder."
> "**Dispense in a tight container.**"

**Not stated in the label:** no "protect from light", no "protect from moisture", no "keep out of reach of children", no refrigeration/freezing instructions, no shelf-life/expiry, and no post-reconstitution storage guidance. The label also carries the standard note that it *"may not be the latest approved by FDA."* Version/date is not given in the document.

## 3. Two notes on scope

- **Source separation:** §1 comes from our **private internal database**; §2 from an **internal knowledge-base document** (a retrieved PDF label). Nothing was sent to public search.
- **A slight tension worth flagging:** the internal DB lists Amoxin **capsules** (0.25 g), while the KB label gives capsule storage as *≤20 °C* — i.e., if operational storage runs warmer (e.g., room temp ~25 °C), the label's capsule requirement is the stricter one to check against. This is an observation, not a compliance determination.

Want me to compile this into a Markdown or PDF report?

---

## 19. web-01 (web, easy)

**Question:** Who discovered penicillin, and in what year?

**Gold answer:** Alexander Fleming, 1928.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] web search for 'Who discovered penicillin and in what year Alexander Fleming'; grounded search summary:
**Alexander Fleming** discovered penicillin in **1928** (specifically in September 1928).

### Key Details:
* **The Discovery:** Fleming, a Scottish bacteriologist working at St. Mary's Hospital in London, returned from a vacation to find that a Petri dish containing *Staphylococcus* bacteria had been contaminated by a mold (*Penicillium notatum*). He noticed that the bacteria immediately surrounding the mold were being destroyed. 
* **Development into Medicine:** While Fleming discovered the substance and published his findings in 1929, it wasn't until the late 1930s and early 1940s that scientists **Howard Florey** and **Ernst Chain** (along with Norman Heatley) developed a way to purify and mass-produce penicillin for medical treatment.
* **Nobel Prize:** Fleming, Florey, and Chain jointly received the Nobel Prize in Physiology or Medicine in 1945 for their work on penicillin.
sources:
  (none)

[3] web search for "Alexander Fleming penicillin 1928 St Mary's Hospital observation mold Penicillium notatum"; grounded search summary:
These keywords capture the famous story of the discovery of **penicillin** in September 1928, an event that revolutionized modern medicine and launched the antibiotic era. 

Here is how the discovery unfolded:

---

### 1. The Setting: St. Mary’s Hospital (September 1928)
* **Who:** Dr. Alexander Fleming, a Scottish physician and microbiologist.
* **Where:** His laboratory at **St. Mary’s Hospital** in London.
* **What he was studying:** Strains of ***Staphylococcus*** bacteria, common pathogens responsible for wound infections, abscesses, and sore throats.

### 2. The Accidental Observation
Before leaving for a two-week summer holiday in August 1928, Fleming stacked several inoculated agar culture plates on a side bench in his laboratory. 

Upon returning on **September 3, 1928**, he began sorting through the plates to discard contaminated ones. He noticed that one petri dish had been contaminated by a bluish-green mold spore blown in through an open window or drifting from a mycologist’s lab downstairs.

### 3. The "Eureka" Moment
Fleming observed something striking on the contaminated plate:
* Surrounding the mold was a distinct, transparent halo—a **zone of inhibition** where the *Staphylococcus* colonies had dissolved or failed to grow.
* Farther away from the mold, the bacteria grew normally.
* Fleming famously remarked, *"That's funny,"* recognizing that the mold was secreting a substance capable of lysing (destroying) the bacteria.

### 4. Identifying the Mold: *Penicillium notatum*
* Fleming isolated and cultured the mold, which was initially identified as ***Penicillium notatum*** (now classified as *Penicillium chrysogenum* / *Penicillium rubens*).
* He named the antibacterial substance released by the mold **"penicillin"** on March 7, 1929.
* In his 1929 paper published in the *British Journal of Experimental Pathology*, he reported that penicillin was non-toxic to human cells and white blood cells, but potent against Gram-positive bacteria like staphylococci, streptococci, and diphtheria bacilli.

### 5. From Laboratory Curiosity to Wonder Drug
* Fleming was unable to isolate or stabilize the active chemical compound in large enough quantities for practical clinical use, and his findings initially received little attention.
* A decade later (late 1930s to early 1940s), a team of researchers at the University of Oxford led by **Howard Florey**, **Ernst Chain**, and **Norman Heatley** succeeded in purifying penicillin and proving its life-saving efficacy in human trials.
* During World War II, mass-production techniques developed in the United States made penicillin widely available, saving millions of wounded soldiers and civilians.

### Legacy
In **1945**, Alexander Fleming, Howard Florey, and Ernst Chain were jointly awarded the **Nobel Prize in Physiology or Medicine** *"for the discovery of penicillin and its curative effect in various infectious diseases."*
sources:
  (none)

[4] web search for 'Nobel Prize 1945 penicillin Fleming Florey Chain nobelprize.org'; grounded search summary:
According to **NobelPrize.org**, the **1945 Nobel Prize in Physiology or Medicine** was awarded jointly to:

* **Sir Alexander Fleming**
* **Ernst Boris Chain**
* **Sir Howard Walter Florey**

---

### **Official Citation**
> *"for the discovery of penicillin and its curative effect in various infectious diseases"*

---

### **Summary of Their Contributions**

* **Alexander Fleming (1881–1955):**  
  Discovered penicillin in September 1928 at St. Mary’s Hospital in London. He observed that a fungal contamination (*Penicillium notatum*) had inhibited the growth of a *Staphylococcus* culture plate. Although he demonstrated its antibacterial properties and lack of toxicity to human cells, he was unable to isolate or stabilize the active compound in large enough quantities for clinical use.

* **Howard Walter Florey (1898–1968) & Ernst Boris Chain (1906–1979):**  
  Working at the Sir William Dunn School of Pathology at the University of Oxford (beginning in 1938), biochemist Ernst Chain and pathologist/pharmacologist Howard Florey (along with team member Norman Heatley) succeeded in:
  1. Purifying and stabilizing the penicillin molecule.
  2. Demonstrating its therapeutic efficacy in laboratory mice (1940).
  3. Conducting the first successful human clinical trials (1941).
  4. Collaborating with American scientists and pharmaceutical companies to scale up mass production, which saved countless lives during World War II and revolutionized modern medicine.
sources:
  (none)

[5] web search for 'penicillin discovery disputed earlier observations before Fleming 1875 John Tyndall'; grounded search summary:
The credit for the discovery of penicillin is traditionally given to **Sir Alexander Fleming in 1928**, but the antibacterial action of *Penicillium* molds—and the broader phenomenon of microbial antagonism (antibiosis)—had been observed, documented, and debated by scientists decades before him. 

Among the most prominent early observers was the British physicist **John Tyndall in 1875**.

---

### John Tyndall’s 1875 Observations
In 1875, John Tyndall was conducting experiments at the Royal Institution to refute the doctrine of spontaneous generation (working in parallel with Louis Pasteur). While examining the purity of air and the behavior of bacterial putrefaction in organic infusions (such as turnip, mutton, and hay broth), he noticed a recurring pattern:

* **The Observation**: In test tubes where blue-green mold (*Penicillium*) established itself on the surface, the liquid remained clear, and bacterial growth was halted or eliminated.
* **Presentation to the Royal Society**: In late 1875 (and published in early 1876 in the *Philosophical Transactions of the Royal Society*), Tyndall formally presented his findings. He described a literal *"struggle for existence"* between the mold and the bacteria.
* **His Explanation**: Tyndall initially hypothesized that the mold mechanically cut off oxygen to the bacteria, suffocating them. However, correspondence in 1875 with biologist **Thomas Henry Huxley** suggested that the mold was actively producing a substance that suppressed bacterial vitality independent of oxygen deprivation.
* **Why He Did Not Pursue It**: Tyndall was a physicist, not a physician or pharmacologist. His primary objective was winning the scientific debate over spontaneous generation and biogenesis; once that point was made, he moved on.

---

### The Chain of Pre-Fleming Discoveries (1870–1920)
Tyndall was part of a larger continuum of 19th-century scientists who observed this antagonism:

1. **Sir John Scott Burdon-Sanderson (1870)**: At St. Mary’s Hospital in London (coincidentally where Fleming later worked), Burdon-Sanderson noted that culture fluids covered with mold failed to produce bacteria.
2. **Joseph Lister (1871–1877)**: Inspired by Burdon-Sanderson, the pioneer of antiseptic surgery experimented with *Penicillium glaucum*. In 1877, Lister recorded successfully treating an infected wound in a nurse with a crude mold dressing after standard antiseptics had failed.
3. **William Roberts (1874)**: A Manchester physician whose work preceded Tyndall’s, Roberts noted that nutrient media overgrown with *Penicillium glaucum* could not easily be contaminated by bacteria.
4. **Louis Pasteur & Jules Joubert (1877)**: Demonstrated that anthrax bacilli failed to grow when paired with certain common air-borne molds and microbes, famously remarking that this antagonism might offer *"great hopes in therapeutics."*
5. **Vincenzo Tiberio (1895)**: A naval physician at the University of Naples who published a detailed study on mold extracts from a cistern well, proving they had bactericidal properties against typhoid and cholera *in vivo* in animals.
6. **Ernest Duchesne (1897)**: A French military medical student who wrote his entire doctoral thesis on the antagonism between *Penicillium glaucum* and bacteria. Duchesne cured guinea pigs inoculated with lethal doses of *E. coli* and typhoid using mold broths. His work was ignored by the Institut Pasteur, likely because he was young, unknown, and died shortly after of tuberculosis.

---

### Why Fleming Still Gets the Credit
Despite Tyndall and others seeing the effect decades earlier, historians generally distinguish Fleming’s work for several reasons:

1. **The Catch-All "Penicillium glaucum"**: 
   Nineteenth-century researchers (including Roberts, Tyndall, and Duchesne) referred to almost all green-blue surface molds as *Penicillium glaucum*. Later analysis suggests many of these molds were producing other mycotoxins—such as **patulin**, which is toxic to human tissue—rather than true penicillin.
2. **Isolation and Naming**: 
   Fleming was the first to name the active exudate **"penicillin"** (1929) and specifically isolate it from *Penicillium notatum* (now classified as *Penicillium rubens*). 
3. **Non-Toxicity to Human Cells**: 
   Earlier researchers knew molds could kill microbes, but antiseptics (like carbolic acid) did that too—while also destroying human white blood cells. Fleming was the first to demonstrate that penicillin juice was completely non-toxic to human leukocytes, proving it could be used safely internally in the human body.
4. **The Oxford Development**: 
   Fleming could not isolate or chemically purify penicillin into a stable drug. It was not until **Howard Florey, Ernst Chain, and Norman Heatley** at Oxford took up Fleming's published paper in 1939–1940 that penicillin was chemically isolated, mass-produced, and turned into the miracle drug used during World War II.
sources:
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8o4AtJK1cwQrTAF0sh4CLxJCCvWkl21eCE30OPGKNADn4cdXzB7BAUQeocTHE8YA-MToeZHSf61_UUxjqm5UvWJ0cE8XTgxS7m0S6I-Um6VXqdTQEsMS5IzzLhwuB9tZm12_Xm6LltA==>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEcs8z3o1X1lj9duExYY7SiuOt82wNAt8yKym7eig5Fbc5cXgTq_yziev-BoJ6W4dBXgfj7CPK9Hlr3gMEZeH5rJ6BfM6sI09F1tIkpE54DtIE2pEjGauE-H8m65hmSjNrM4Xgpua0cBpFzoDFYAG9bbj_4iKN_ARJswqvG6gJ3KQwUs0jZ1408AG3pvaBwY4Y=>
  - bluesci.co.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwzBCD9b0W5qvJg6svZdgWpIALQaR4O62uCk8V2YEk4glczSsp9Yv0-08Z_6bbqpdSYSuST3tUWsNAA_3Y_bUnpimhOrAmnkbZPCJijpZMUuOambUYLPDSjPi4vsnoOOj92WKfnd67tnLSEnnLdnrhtDlCIYlaHA==>
  - wikidoc.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFWytsVVbP_tvtW6IhHZNwdTM2oosJWESCl3cpwWguKdql9N3000RE6obohV_AImKVciWe0Wwk3fbZEIWD4rzj71C7kJ45BEm4La7RS0_l5JVZ6IVDUaQWknaf0WxyABnTg-sAQ_sBg9erKdVxMpA==>
  - theguardian.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-p3HjQPHHVLJiS1mfxsVAC2dMz_z6QCwtYunu5YJMIOPZXibywWM-c4ukdcg_IZxYN1AmNJfWDiOXBBJae_NV__PMwmCfWgGwipgPvdnGCVk6dfhWUPf2prFpG_N1rBD3S5DkF7eUbXU3O72MGseepWzy-5dcRMgyvc_Gwoxv3EsTA4oly3djS61-8pWhdysL2HKZR1p1Ybk5kLCdMAIlRezSXd5P8m62iW6b3LH3JEMnEnnWqXnG5Arw1NIro2mvuokhYL7QVm4=>

[6] web search for 'Alexander Fleming biography britannica penicillin discovery'; grounded search summary:
**Sir Alexander Fleming** (August 6, 1881 – March 11, 1955) was a Scottish bacteriologist best known for discovering **penicillin**, the world’s first widely effective antibiotic, as well as the antibacterial enzyme **lysozyme**. His work revolutionized modern medicine and earned him the 1945 Nobel Prize in Physiology or Medicine.

---

### 1. Early Life and Education
* **Birth and Background:** Fleming was born on a remote farm in Lochfield, Ayrshire, Scotland. After early schooling, he moved to London at age 13 and later worked as a shipping clerk for several years.
* **Medical Training:** An inheritance allowed him to pursue a medical career. In 1901, he enrolled at **St. Mary’s Hospital Medical School** in London, graduating with distinction in 1906. 
* **Research with Almroth Wright:** Fleming was recruited into the Inoculation Department at St. Mary’s by Sir Almroth Wright, a pioneer in vaccine therapy and immunology. Fleming remained affiliated with St. Mary's for the rest of his career.

---

### 2. Wartime Experience and the Search for Antibacterials
* **World War I:** Fleming served as a captain in the Royal Army Medical Corps, treating wounded soldiers in field hospitals in France. 
* **Limits of Antiseptics:** He observed that harsh chemical antiseptics (such as carbolic acid) often did more harm than good in deep wounds because they destroyed the patient's protective white blood cells faster than they destroyed bacteria. This experience drove his search for an agent that was toxic to bacteria but harmless to human tissue.
* **Discovery of Lysozyme (1921–1922):** Fleming accidentally discovered lysozyme after examining a culture plate contaminated with his own nasal mucus, finding that bodily secretions contain an enzyme capable of dissolving certain bacteria. While lysozyme was not potent against most disease-causing bacteria, the discovery sharpened his interest in natural antibacterial substances.

---

### 3. The Discovery of Penicillin (September 1928)
* **The Accidental Contamination:** In September 1928, Fleming returned to his laboratory at St. Mary’s Hospital following a summer vacation in Suffolk. Before leaving, he had stacked Petri dishes inoculated with ***Staphylococcus aureus*** (a common cause of boils, abscesses, and blood poisoning) on a lab bench.
* **The Observation:** Upon inspecting the plates, Fleming noticed that one had been contaminated by an airborne fungal spore. Surrounding the growing mold was a clear ring or "halo" where the staphylococci colonies had dissolved or failed to grow.
* **Identification:** Fleming isolated the mold, identifying it as a member of the genus *Penicillium* (initially identified as *Penicillium notatum*, now classified with *Penicillium chrysogenum*). He referred to the broth produced by the fungus as "mould juice" before officially naming the antibacterial agent **penicillin**.
* **Laboratory Findings:** Fleming discovered that penicillin was effective against many Gram-positive pathogens (including streptococci, staphylococci, and diphtheria bacilli) while remaining non-toxic to human cells. He published his findings in 1929 in the *British Journal of Experimental Pathology*.

---

### 4. Purification and Mass Production
While Fleming recognized the medical promise of penicillin, he was a bacteriologist rather than an organic chemist. He faced severe hurdles:
* Penicillin was chemically unstable, difficult to isolate in pure form, and produced only in tiny amounts by the mold.
* For nearly a decade, penicillin remained mostly an experimental curiosity used in laboratory culture separation.
* **The Oxford Team:** In the late 1930s, a team at Oxford University led by Australian pathologist **Howard Florey** and German-born biochemist **Ernst Boris Chain** revisited Fleming's research. They successfully purified penicillin, proved its effectiveness in mice and human patients, and worked with U.S. government laboratories and pharmaceutical firms to scale up mass production during World War II.

---

### 5. Recognition and Legacy
* **Nobel Prize:** In **1945**, Alexander Fleming, Howard Florey, and Ernst Chain were jointly awarded the **Nobel Prize in Physiology or Medicine** "for the discovery of penicillin and its curative effect in various infectious diseases".
* **Honors:** Fleming was knighted by King George VI in 1944.
* **Warning on Resistance:** In his 1945 Nobel lecture, Fleming presciently warned against the dangers of underdosing antibiotics, cautioning that bacteria could mutate and develop resistance to penicillin if the drug was misused.
* **Death:** Sir Alexander Fleming died of a heart attack on March 11, 1955, at age 73, and was buried in St. Paul’s Cathedral in London.
sources:
  - britannica.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGQO1H4CAAMAUGBIxKRkSVBXr92KF_XRUdFhE0uopd4fuHLp0EH86oIuMPrGUurUFyY0vSHV05Il-Hoz1MmeL5V-aSk4HFccjfOjOiMXEhuJYE4MOv5d0AmiyD3AyswH8uQ_14kRdvTQBDQwgo=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGi_w-c3-vbohnNVeA3jmjbB6u2Nk9eQFsQKE8FlX6NSDaUHBXbJwv5wokfPUU8U5H2xva90Dxp-cfPrO-5Zeyegxy1Y9OWmsKDgNdqi7lynPQXuy1mGRGcGHpDa7P0F7YTZgaxWPBk>
  - britannica.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcH8tXUzGyuJXRKSVDDxVYCJYyztMa2G1tL6bK99SahZXcFinnn5CzI6qUhCQ7E3UdJIfVjr89rumFRrI1nKFuaJ1Ocp3Q-0ZHktjaRluJ1zc3ldk6NpofalDUwFJe_NBxIqTjVqZXM27WKhhOocnaiygoG2I-dGlYnWc=>
  - britannica.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGAOzY0zAadiB7sszk0NIe77_KxR_Muoiy5geTgtMktn2dvPaxRzWSHknIqXQ5tOTak2zjvn7XMem-1Z3dYl84pohKvG9S5gXi-ljqY65tc4PrUMCnLJ2KAEqWa_OVrxmKhDkLqOBxdu0h1KXz8RGVEU3qbxQiy9W97q48xzeVWgzZJXBgAhRcVmPYF1GzGpN_-labPA==>
  - pbs.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE4Z-HprOI2L__YQR4HbfFPO56dA16thPn8eHnnYNzlHhdycKLn1O7_lnq0vfHLtjnU2rSuKQdsH7p2KSyNzw4xtmXcQ6Tw6exQD_Yqk2SzV6drZyE7TkGGxXv8yID_ywstFAwBQq4zsR2Qg9bIH8l-c8oHSde1gM3fvPKix1duCpAVE7-3-Njc9lfK>

[7] web search for 'penicillin discovery history.wikipedia.org Fleming Florey Chain Oxford Heatley'; grounded search summary:
The discovery and development of penicillin—often regarded as one of the greatest medical breakthroughs in human history—was not the work of a single scientist, but a multi-stage effort spanning over a decade. It began with **Alexander Fleming’s** serendipitous observation in London and culminated in the groundbreaking biochemistry, engineering, and clinical trials conducted by the **Oxford team** led by **Howard Florey**, **Ernst Boris Chain**, and **Norman Heatley**.

---

### 1. Alexander Fleming’s Initial Discovery (1928)
* **The Accidental Observation:** In September 1928, Alexander Fleming, a Scottish bacteriologist at St. Mary’s Hospital in London, returned from a vacation to find that a petri dish of *Staphylococcus* bacteria had been accidentally contaminated by a blue-green mold. Around the mold, the bacterial colonies had dissolved into a clear zone.
* **Identification:** Fleming identified the mold as belonging to the genus *Penicillium* (specifically *Penicillium notatum*). He named the antibacterial broth produced by the fungus **penicillin**.
* **The Dead End:** Fleming published his findings in the *British Journal of Experimental Pathology* in 1929. However, penicillin was notoriously unstable, broke down rapidly, and could only be produced in tiny amounts. Unable to purify or concentrate it, and believing it was too unstable to serve as an internal systemic therapeutic, Fleming largely set the project aside.

---

### 2. The Oxford Team Takes Over (1938–1939)
Nearly a decade later, researchers at the **Sir William Dunn School of Pathology at the University of Oxford** revisited Fleming’s paper while surveying naturally occurring antibacterial substances:

* **Howard Florey (The Leader):** An Australian pathologist who directed the department. Florey was a formidable administrator and scientist who secured crucial funding (notably from the Rockefeller Foundation) and assembled an interdisciplinary team of biochemists, pathologists, and technicians.
* **Ernst Boris Chain (The Biochemist):** A brilliant German-Jewish refugee who fled Nazi Germany in 1933. Chain recognized the chemical potential of penicillin and championed the effort to isolate and chemically purify the unstable active molecule.

---

### 3. Norman Heatley: The Unsung Engineering Genius
While Florey provided the direction and Chain tackled the chemistry, **Norman Heatley**—a versatile biochemist and biophysicist—solved the practical physical problems of production and measurement:

* **Back-Extraction Technique:** Penicillin was easily destroyed by temperature and pH changes. Heatley devised a multi-stage solvent extraction process: shifting the broth's pH to extract penicillin into an organic solvent (ether/amyl acetate) and then shifting it back to extract it into neutral water. This yielded the first stable, concentrated form of penicillin.
* **The Cylinder-Plate Assay:** Heatley created a standardized way to measure the potency of penicillin batches using small porcelain or glass cylinders placed on bacterial agar plates (measuring the clear zone of inhibition). This gave rise to the **"Oxford Unit"** (or Heatley unit).
* **Improvised Production:** Because wartime Britain lacked industrial fermenters, Heatley transformed the Oxford lab into a makeshift factory. He grew mold in whatever flat-surfaced containers were available: milk bottles, biscuit tins, hospital bedpans, and eventually thousands of custom-designed ceramic vessels.

---

### 4. Animal Trials and First Clinical Tests (1940–1941)
* **The 1940 Mouse Experiment:** In May 1940, the Oxford team conducted a landmark trial: eight mice were injected with lethal doses of virulent *Streptococcus*. Four were treated with penicillin; four were untreated controls. Within 17 hours, all four untreated mice died, while all four treated mice survived.
* **First Human Trial (Albert Alexander, 1941):** In February 1941, the drug was administered to Albert Alexander, a 43-year-old Oxford police constable dying of a severe staphylococcal and streptococcal infection (contracted from a scratch). Alexander made an astonishing recovery within days. However, supplies were so limited that Heatley had to recycle penicillin from the patient’s urine. When supplies completely ran out, the infection returned, and Alexander died. 
* **Subsequent Successes:** Later in 1941, with more supply accumulated, the team treated several more patients—including children with terminal bacterial infections—with complete success, proving penicillin’s efficacy in humans.

---

### 5. The American Industrial Scale-Up (1941–1944)
With Britain under heavy bombardment during World War II, British pharmaceutical companies lacked the capacity to produce penicillin at scale.

* In the summer of 1941, **Florey and Heatley traveled to the United States** with a flask of the mold spores smeared into the linings of their coats to prevent losing the strain.
* They partnered with the **USDA Northern Regional Research Laboratory (NRRL)** in Peoria, Illinois.
* **Crucial Breakthroughs in Peoria:**
  1. **Corn Steep Liquor:** Adding this byproduct of corn processing to the growth medium increased penicillin yields by more than tenfold.
  2. **A Better Mold Strain:** Lab worker Mary Hunt ("Moldy Mary") found a moldy cantaloupe in a local market that yielded *Penicillium chrysogenum*, producing hundreds of times more penicillin than Fleming’s original strain.
  3. **Deep-Tank Fermentation:** U.S. pharmaceutical giants (including Pfizer, Merck, Squibb, and Abbott) developed massive submerged-aerobic fermentation tanks.
* By D-Day in June 1944, millions of doses were available, dramatically reducing battlefield fatalities and amputations from bacterial wound infections.

---

### 6. Nobel Prize and Legacy
* **The 1945 Nobel Prize in Physiology or Medicine:** Awarded jointly to **Sir Alexander Fleming**, **Ernst Boris Chain**, and **Sir Howard Walter Florey** *"for the discovery of penicillin and its curative effect in various infectious diseases."*
* **Recognition for Norman Heatley:** Under Nobel rules, a maximum of three individuals could share a single prize, leaving Heatley out. In 1990, Oxford University made amends by awarding Heatley an honorary doctorate of medicine—the first in the university’s 800-year history granted to a non-physician. Heatley was also appointed an Officer of the Order of the British Empire (OBE).
sources:
  (none)
```

</details>

**Answer:**

**Alexander Fleming** discovered penicillin in **1928** (commonly cited as **September 1928**).

## Key facts

| Item | Detail |
|---|---|
| Discoverer | Sir Alexander Fleming (1881–1955), Scottish bacteriologist and physician |
| Year | 1928; published in 1929 |
| Where | St. Mary's Hospital Medical School, London (Inoculation Department) |
| Organism | A mold, originally *Penicillium notatum* (now classified as *Penicillium rubens*) |
| Substance named | "Penicillin" (name in use from ~March 1929) |
| Publication | *British Journal of Experimental Pathology*, 1929 |

## The discovery story
Fleming was studying *Staphylococcus aureus*. On returning to his bench after leaving inoculated agar plates, he found one contaminated by an airborne bluish-green mold, and around it a clear "halo" — a zone where the staphylococci had been destroyed. He isolated and cultured the mold and showed that the active substance killed many Gram-positive bacteria (staphylococci, streptococci, diphtheria bacilli) while not harming human cells. He could not purify or stabilize the fragile compound, so it stayed a laboratory curiosity for about a decade.

## Later development (not by Fleming alone)
- From ~1938–39 at Oxford's Sir William Dunn School of Pathology, **Howard Florey** and **Ernst Boris Chain** purified and stabilized penicillin.
- **Norman Heatley** devised the back-extraction method, the assay ("Oxford Unit"), and improvised mass culture.
- 1940: mouse protection experiment; 1941: first human trial; scale-up in the U.S. enabled mass production by 1944.
- **1945 Nobel Prize in Physiology or Medicine** went to Fleming, Florey, and Chain "for the discovery of penicillin and its curative effect in various infectious diseases." Heatley was excluded by the three-recipient rule.

## Nuances worth flagging
- **Earlier observations of mold–bacteria antagonism** predate Fleming — e.g., Burdon-Sanderson (1870), Lister, Pasteur & Joubert (1877), Vincenzo Tiberio (1895), and notably **Ernest Duchesne (1897)**, whose ignored thesis described a *Penicillium* mold curing infections in guinea pigs. Fleming's credit rests on isolating the mold, naming the substance, and being first to demonstrate its **non-toxicity to human cells**, with his paper directly seeding the Oxford work.
- **Exact date:** not definitively documented; September 3, 1928 is the commonly cited date from Fleming's own later accounts, but some historians question details of the "plates left before vacation" narrative.

---

**Notes on this answer**
- **No attached reference files were present** in the working directory, so nothing was analyzed from uploads.
- **Sources:** provided by the public web search specialist, originating from these publishers: nobelprize.org (1945 Nobel details), britannica.com (Fleming biography), nih.gov and pbs.org (penicillin history), wikipedia.org (pre-Fleming observations), plus theguardian.com, researchgate.net, bluesci.co.uk, wikidoc.org (dispute background). The search tool returned these as redirect links rather than clean canonical URLs, so I have cited the originating **domains** only and have not fabricated exact links.
- **No internal database or knowledge-base data was used** — this is entirely public knowledge, as appropriate for a general historical question.

---

## 20. web-03 (web, medium)

**Question:** What is the primary mechanism of action of metformin?

**Gold answer:** It lowers hepatic glucose production (suppresses gluconeogenesis) and improves insulin sensitivity; AMPK activation is the commonly cited pathway.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] web search for 'metformin FDA label mechanism of action pharmacology prescribing information'; grounded search summary:
Below is a summary of the **FDA Prescribing Information** for **metformin hydrochloride**, focusing on its mechanism of action, clinical pharmacology, and key prescribing parameters.

---

### 1. Boxed Warning: Lactic Acidosis
* **Risk:** Metformin-associated lactic acidosis (MALA) is a rare but serious, potentially fatal metabolic complication.
* **Risk Factors:** Severe renal impairment, concomitant use of certain drugs (e.g., carbonic anhydrase inhibitors), age $\ge 65$ years, radiological studies with iodinated contrast media, surgery/other procedures, hypoxic states (e.g., acute congestive heart failure), excessive alcohol intake, and hepatic impairment.
* **Management:** If lactic acidosis is suspected, metformin must be discontinued immediately, and prompt supportive measures (including hemodialysis) instituted.

---

### 2. Mechanism of Action (FDA Label Section 12.1)
Metformin is a biguanide antihyperglycemic agent that improves glucose tolerance in patients with type 2 diabetes, lowering both basal and postprandial plasma glucose. Its mechanisms include:

1. **Decreasing hepatic glucose production:** Inhibits hepatic gluconeogenesis and glycogenolysis.
2. **Decreasing intestinal absorption:** Reduces the absorption of glucose from the gastrointestinal tract.
3. **Improving insulin sensitivity:** Increases peripheral glucose uptake and utilization in skeletal muscle and adipose tissue.

*Metformin does not stimulate insulin secretion (unlike sulfonylureas or meglitinides) and therefore does not cause hypoglycemia when used as monotherapy, nor does it cause hyperinsulinemia.*

---

### 3. Clinical Pharmacology & Pharmacokinetics (Section 12.3)

* **Pharmacodynamics:**
  * Insulin secretion remains unchanged; however, fasting insulin levels and day-long plasma insulin response may decrease due to improved peripheral sensitivity.
* **Absorption:**
  * **Bioavailability:** Absolute bioavailability of an immediate-release 500 mg dose under fasting conditions is approximately **50% to 60%**.
  * **Food effect:** Food slightly delays the extent and rate of absorption (decreased peak concentration and AUC).
* **Distribution:**
  * Negligible binding to plasma proteins (unlike sulfonylureas, which are heavily protein-bound).
  * Apparent volume of distribution ($V_d$) averages $654 \pm 358\text{ L}$.
  * Partitions into erythrocytes, likely as a function of time.
* **Metabolism:**
  * **Not metabolized by the liver:** No metabolites have been identified in humans.
  * No biliary excretion.
* **Elimination:**
  * **Renal clearance:** Excreted unchanged in the urine via glomerular filtration and tubular secretion.
  * Approximately **90%** of the absorbed drug is eliminated within 24 hours.
  * **Plasma elimination half-life:** Approximately **6.2 hours** (blood elimination half-life is ~17.6 hours, reflecting distribution into red blood cells).

---

### 4. Indications and Usage (Section 1)
* Adjunct to diet and exercise to improve glycemic control in:
  * **Adults** with type 2 diabetes mellitus (immediate-release and extended-release formulations).
  * **Pediatric patients aged 10 years and older** with type 2 diabetes mellitus (immediate-release formulation only).

---

### 5. Contraindications (Section 4)
* **Severe renal impairment:** eGFR $< 30\text{ mL/min}/1.73\text{ m}^2$.
* **Hypersensitivity:** Known severe hypersensitivity to metformin hydrochloride.
* **Metabolic acidosis:** Acute or chronic metabolic acidosis, including diabetic ketoacidosis (DKA), with or without coma.

---

### 6. Dosage and Administration (Section 2)

#### Recommended Dosing (Immediate-Release)
* **Starting dose:** 500 mg orally twice daily or 850 mg once daily, administered with meals to minimize gastrointestinal upset.
* **Titration:** Increase in increments of 500 mg weekly or 850 mg every 2 weeks, based on glycemic control and tolerability.
* **Maximum recommended daily dose:** 2,550 mg/day (in divided doses).

#### Recommended Dosing (Extended-Release)
* **Starting dose:** 500 mg orally once daily with the evening meal.
* **Titration:** Increase by 500 mg weekly.
* **Maximum recommended daily dose:** 2,000 mg once daily.

#### Renal Impairment Guidelines
* Assess renal function (eGFR) prior to initiation and at least annually thereafter.
* **eGFR $\ge 45\text{ to }< 60\text{ mL/min}/1.73\text{ m}^2$:** Monitor renal function more frequently (e.g., every 3–6 months).
* **eGFR $30\text{ to }< 45\text{ mL/min}/1.73\text{ m}^2$:**
  * Initiating metformin is **not recommended**.
  * For patients already taking metformin whose eGFR falls into this range, assess the benefits and risks of continuing therapy; consider dose reduction (e.g., maximum 1,000 mg/day).
* **eGFR $< 30\text{ mL/min}/1.73\text{ m}^2$:** **Contraindicated.**

---

### 7. Warnings and Precautions (Section 5)
* **Radiological Imaging with Iodinated Contrast:** Discontinue metformin at the time of or prior to an iodinated contrast imaging procedure in patients with an eGFR between 30 and 60 mL/min/1.73 m², a history of liver disease, alcoholism, or heart failure, or in patients receiving intra-arterial contrast. Re-evaluate eGFR 48 hours after the procedure before restarting.
* **Surgical Procedures:** Withhold metformin while patients have restricted food and fluid intake.
* **Hypoxic States:** Cardiovascular collapse, acute congestive heart failure, acute myocardial infarction, and other conditions characterized by hypoxemia have been associated with lactic acidosis.
* **Vitamin $\text{B}_{12}$ Deficiency:** Long-term metformin use may decrease serum vitamin $\text{B}_{12}$ levels; periodic hematologic monitoring is recommended.
* **Hypoglycemia with Concomitant Use:** Increased risk when used in combination with insulin or insulin secretagogues (e.g., sulfonylureas).

---

### 8. Adverse Reactions (Section 6)
* **Most common ($\ge 5\%$):** Diarrhea, nausea, vomiting, abdominal distention, flatulence, asthenia, indigestion, abdominal discomfort, and headache.
* Taking the drug with meals and gradual dose titration reduces gastrointestinal adverse effects.
sources:
  (none)

[3] web search for 'metformin mechanism of action mitochondrial complex I inhibition AMPK hepatic gluconeogenesis'; grounded search summary:
The mechanism of action of **metformin** centers on its ability to alter cellular energy status, suppress hepatic glucose production (gluconeogenesis), and improve insulin sensitivity. 

While historically viewed as purely an **AMPK (AMP-activated protein kinase)**-dependent drug, modern molecular pharmacology demonstrates that metformin acts through both **AMPK-dependent** and **AMPK-independent** pathways, initiated by the **mild inhibition of mitochondrial respiratory Complex I**.

---

### 1. Cellular Uptake and Mitochondrial Accumulation
* **Uptake via OCT1:** Metformin is a positively charged hydrophilic biguanide. It does not cross the lipid bilayer passively; instead, it is actively transported into hepatocytes primarily via **Organic Cation Transporter 1 (OCT1 / SLC22A1)**.
* **Mitochondrial targeting:** Because of its positive charge and the steep inside-negative electrical transmembrane potential across the inner mitochondrial membrane, metformin accumulates inside the mitochondrial matrix at concentrations up to 1,000-fold higher than in the extracellular space.

---

### 2. Mild, Reversible Inhibition of Mitochondrial Complex I
* In the mitochondrial matrix, metformin weakly and reversibly inhibits **Complex I (NADH:ubiquinone oxidoreductase)** of the electron transport chain (ETC).
* **Consequences of Complex I inhibition:**
  1. **Reduced ATP synthesis:** Disruption of proton pumping reduces the proton-motive force, blunting oxidative phosphorylation and slowing ATP generation.
  2. **Elevated AMP:ATP and ADP:ATP ratios:** As ATP levels decline slightly, cellular adenylate kinase converts 2 ADP $\rightleftharpoons$ ATP + AMP, causing a significant relative increase in intracellular **AMP** and **ADP**.

---

### 3. Activation of AMPK (The Canonical Pathway)
The altered cellular adenylate charge triggers the activation of **AMPK**, the master cellular energy sensor:

1. **Binding to the $\gamma$-subunit:** Increased concentrations of AMP and ADP bind to the regulatory CBS (cystathionine $\beta$-synthase) domains on the AMPK $\gamma$-subunit.
2. **Phosphorylation by LKB1:** AMP/ADP binding induces a conformational change that promotes phosphorylation of Thr-172 on the catalytic $\alpha$-subunit by the upstream tumor suppressor kinase **LKB1**.
3. **Protection from phosphatases:** AMP binding sterically shields Thr-172 from dephosphorylation by protein phosphatases (such as PP2C).
4. **Allosteric activation:** AMP binding directly activates phosphorylated AMPK by up to tenfold.

---

### 4. Mechanisms of Hepatic Gluconeogenesis Suppression
Gluconeogenesis is an energetically expensive pathway (consuming 6 high-energy phosphate bonds—4 ATP and 2 GTP—per molecule of glucose synthesized). Metformin shuts down gluconeogenesis via complementary mechanisms:

#### A. AMPK-Dependent Regulation (Transcriptional Control)
Activated AMPK downregulates the transcription of key rate-limiting gluconeogenic enzymes:
* **Phosphorylation of CRTC2 / TORC2:** AMPK phosphorylates CRTC2 (CREB-regulated transcription coactivator 2), sequestering it in the cytoplasm via 14-3-3 proteins. This prevents CRTC2 from entering the nucleus to co-activate CREB.
* **Phosphorylation of Class IIa HDACs:** HDAC4 and HDAC5 are exported from the nucleus, blunting MEF2/FOXO-driven transcription.
* **Downregulation of *PCK1* and *G6PC*:** The net result is decreased expression of **PEPCK** (phosphoenolpyruvate carboxykinase) and **G6Pase** (glucose-6-phosphatase).
* **Inhibition of Lipogenesis:** AMPK also phosphorylates and inactivates **Acetyl-CoA Carboxylase (ACC)**, reducing hepatic steatosis and mitigating hepatic insulin resistance.

#### B. AMPK-Independent Regulation (Acute Allosteric & Redox Control)
Studies using liver-specific AMPK knockout mice demonstrated that metformin still acutely suppresses hepatic gluconeogenesis in the absence of AMPK, primarily through:

1. **Direct Allosteric Inhibition of FBPase-1 by AMP:**
   * **Fructose-1,6-bisphosphatase-1 (FBPase-1)** is a rate-limiting gluconeogenic enzyme that converts fructose-1,6-bisphosphate into fructose-6-phosphate.
   * Elevated cytosolic **AMP is a potent allosteric inhibitor** of FBPase-1, rapidly shutting down gluconeogenic flux independent of gene transcription or AMPK.

2. **Antagonism of Glucagon Signaling (cAMP Suppression):**
   * Elevated intracellular AMP directly binds to and inhibits **adenylyl cyclase**, preventing glucagon-stimulated production of cyclic AMP (cAMP).
   * This blunts **Protein Kinase A (PKA)** signaling, thereby blocking glucagon-mediated upregulation of gluconeogenesis.

3. **Inhibition of Mitochondrial Glycerol-3-Phosphate Dehydrogenase (mGPD):**
   * Metformin inhibits **mGPD**, an enzyme of the glycerol-phosphate shuttle.
   * This alters the cytosolic redox state, leading to an increased cytosolic **NADH/NAD⁺ ratio**.
   * An elevated cytosolic NADH/NAD⁺ ratio prevents the conversion of **lactate to pyruvate** and **glycerol-3-phosphate to dihydroxyacetone phosphate (DHAP)**, blocking these substrates from entering the gluconeogenic pathway.

---

### Summary Pathway Flowchart

```
Metformin (oral)
       │
       ▼ (Uptake via OCT1)
Hepatocyte Cytosol
       │
       ▼ (Accumulation in mitochondria via membrane potential)
Mitochondrial Matrix
       │
       ▼
Inhibition of Complex I (ETC)
       │
       ▼
Decreased ATP Synthesis ──► [↑ AMP / ATP Ratio]
                                  │
         ┌────────────────────────┴────────────────────────┐
         │                                                 │
         ▼                                                 ▼
[AMPK Activation (via LKB1)]                    [Allosteric & Direct Effects]
         │                                                 │
 ├─ Phosphorylates CRTC2/HDACs                      ├─ Allosteric inhibition of FBPase-1 (by AMP)
 ├─ Prevents CREB transcription                     ├─ Adenylyl cyclase inhibition (blunts Glucagon/cAMP)
 └─ Downregulates PEPCK & G6Pase                    └─ Direct energy depletion (lack of ATP for synthesis)
         │                                                 │
         └────────────────────────┬────────────────────────┘
                                  ▼
               Inhibition of Hepatic Gluconeogenesis
                                  │
                                  ▼
            Lowered Fasting & Postprandial Blood Glucose
```
sources:
  (none)

[4] web search for 'DailyMed metformin hydrochloride prescribing information section 12.1'; grounded search summary:
In the DailyMed / FDA Full Prescribing Information for **Metformin Hydrochloride**, **Section 12.1** falls under **12 CLINICAL PHARMACOLOGY**.

The text of **12.1 Mechanism of Action** generally reads as follows:

---

### **12.1 Mechanism of Action**

> **Metformin is an antihyperglycemic agent [or biguanide] which improves glucose tolerance in patients with type 2 diabetes mellitus, lowering both basal and postprandial plasma glucose.**
>
> **Metformin decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity by increasing peripheral glucose uptake and utilization.** 
>
> **With metformin therapy, insulin secretion remains unchanged while fasting insulin levels and day-long plasma insulin response may actually decrease.**

---

*(Depending on the specific manufacturer/label and whether it is an immediate-release tablet, extended-release tablet, or oral solution, the section may also include the following statement):*

> *"Metformin does not produce hypoglycemia in patients with type 2 diabetes or in healthy subjects except in special circumstances [see Warnings and Precautions (5)] and does not cause hyperinsulinemia."*
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEdDHVg2BtxbhvN9oolxP7KGBznkx5l2uhh0ybWIM8UMoMAeO1LNVknQpvWB6NWbk2r1RCCs17bCr8WNxpPigCx1zHq4AaREVo3rUGra0Y7LhFTnek3pb_xYNm6xC_rzOQyV2Ui8kZms1YcyYW-of4PIJGIAQNcCnJhydcIrMaS4pzrVwN7gZg_aQzikYu5YebMsJY=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBGXzijKTKSDJYf_Vm_VH5Dsw0iPiryEyk5sqpltQ78Ily14q0mj9n5lXGBsC7Eqn6kZpQ2Zod_YCCQotsLF2l_CoinxP1bVevO9JlxgqxCsTl-1EYrXRyT1XwQKjO6Mj41VTMaZdufim7j2U0bvffBsVUcSg7z1wUQlVOlI7-xS4ISOOmMtvRU6whLiTFtEx8>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHRjF4x0Up4ESL7Jzou-evukufq62h3rzANFXtHd--TzzGpO96Wfat7AkJve4NSEB-ef78CNnKG8NUU9jqmojccP8Rg197DSzuFaYwefc13Zue4wWQUGJMfjGkGUzbcACTx6t2C1FxVZqoYnuIUE1S1NqmX94IWGE88Xz3yYpwzwhCRoDvgdFVY1e9LtCWP5UI7>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCLdSo8QXFP9ScU9vNnmkjYRnwh7RT-gZdqfRnyMMIuK-4JXx3p5Nwaitn3nf5mkzYXk2gRB1SUU9FTnqmNhCZZz5wypgzbpsRcZF996LpFsXYDc-iMOGdVV6S5PFj_8bb0YH4vm4POGFEDGqYlt83LX3QjtYjDenzjBgTCsk-y2s=>

[5] web search for 'StatPearls metformin NCBI bookshelf mechanism of action'; grounded search summary:
According to the **StatPearls** reference on the NCBI Bookshelf (*Metformin*, Bookshelf ID: NBK518983, by Calette Corcoran and Tibb F. Jacobs):

---

### **1. StatPearls Core Mechanism of Action**
Metformin is an oral antihyperglycemic medication belonging to the **biguanide** class. It lowers blood glucose levels primarily through three distinct physiological actions:

* **Decreasing hepatic glucose production:** Inhibits gluconeogenesis and glycogenolysis in the liver.
* **Diminishing intestinal absorption:** Reduces the absorption of glucose from the gastrointestinal tract.
* **Enhancing insulin sensitivity:** Improves peripheral glucose uptake and utilization (particularly in skeletal muscle and adipose tissue).

As a result of these actions, metformin effectively lowers both **basal** and **postprandial** blood glucose without stimulating insulin secretion (which accounts for its low risk of causing hypoglycemia when used as monotherapy).

---

### **2. Mechanism in Polycystic Ovary Syndrome (PCOS)**
StatPearls also highlights metformin's mechanism in off-label management of PCOS:
* By improving insulin sensitivity, metformin **reduces circulating insulin levels**.
* Lower insulin levels lead to a subsequent **reduction in luteinizing hormone (LH) and circulating androgen levels**.
* This hormonal normalization helps restore ovulatory function and regulate the menstrual cycle (clinicians must counsel premenopausal patients regarding the increased likelihood of pregnancy).

---

### **3. Cellular & Molecular Basis (Underlying Biochemistry)**
While the StatPearls chapter focuses on the clinical pharmacology, the molecular mechanism is widely recognized as follows:
* **Mitochondrial Complex I Inhibition:** Metformin mildly inhibits Complex I of the mitochondrial respiratory chain, slowing ATP synthesis and increasing cellular AMP:ATP and ADP:ATP ratios.
* **AMPK Activation:** The increased AMP-to-ATP ratio activates **AMP-activated protein kinase (AMPK)**, a master metabolic sensor.
* **Suppression of Gluconeogenic Genes:** Active AMPK suppresses transcription of key gluconeogenic enzymes (e.g., phosphoenolpyruvate carboxykinase and glucose-6-phosphatase) and opposes glucagon-mediated signaling.
* **Increased GLUT4 Translocation:** Promotes the recruitment of GLUT4 glucose transporters to the plasma membrane in peripheral tissues, facilitating glucose uptake.
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7b7zq0DCpY2_S63Cfm1DJoQjtb-3lSs8mtWOidbcHXs8iiIKV6agAGUMrDwfTr_ars3OfTjSVoQ0xwdgbv_hZcciFNy0xyeDq05lOU-fAiuexl0pRkpq9rNRPuOpf1Q==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRBRavPDFFrnsN_RXg0u5i69D9im-4W0-tc3MdOULvA-pYjnnokjwdydnhO6lNx-Ugsdg5bhOAKucYhQvvtK8QgxTx_PcDFsOvQ6p0MG3-qDae9jVJTI4ObWShl0NPL1NEU55gDkuzWpUB8sPClAon5pMtr0cwV4jo>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHEkRrW3XWFKSyV_CeYQlL8DFkm5UEsKO83BJ9B4SQdx2N0cJA6j2ylfPAJeZ3c8njyItUMyCv5PGhkBAbPIVH-uPuZN27Jno9Gh9DtHmcM4387EsblDTxSkdLXugAXXJNNsEdQZmoMZNOKnG-_-CmyQjBEKGXGQZqzalGSiqfSjsI=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH919m1JUZ-IP37jdCOJCIl7a-4XtiuefSUvnHATIQHr3SO2GsB5NdjWEB6Qk3I0oY6aJoALdGoDmonBDavTsiZwPtdRkMG_e48GNo19sjWSLDSXa8V_SaSs_IRD18sTw==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6uC7JLoDHyJ2oSnxNjFkA3eFoPihz0qBLEBL4UWbil1tDwQ48NoDjft0hDuRnMYbckKMf7uUgdj_tTLi7fJXsIong6PbZJVwh_rgfSAadve_0QxkMc8WBiPeBjKzuzir9itqhhtP1>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGurZKX-GvF8rEudNyZXIVrtz_iOLFp03ty_L8lxXYLkVV-hU_g-UXu3XIYFMRbHJ9uOfJ3LUgTtBAE-uPyqiO3MerAn2a43AtnaLqOiXtWIWsCr3iZ4wL6odPhj93fFQ==>

[6] web search for 'metformin review molecular mechanism complex I AMPK-independent lysosomal pathway 2023'; grounded search summary:
A comprehensive overview of metformin’s molecular mechanisms synthesizes the latest understanding, highlighted in the landmark 2023 review by **Marc Foretz, Bruno Guigas, and Benoît Viollet** (*Nature Reviews Endocrinology*, 2023), along with foundational discoveries on lysosomal signaling.

---

### 1. Mitochondrial Complex I Inhibition and the "Concentration Conundrum"

* **Mechanism of Action:** 
  Metformin is a positively charged hydrophilic biguanide. Driven by the mitochondrial membrane potential ($\Delta\psi_m$), it accumulates inside the mitochondrial matrix up to 1,000-fold relative to extracellular concentrations. Once in the matrix, metformin weakly and reversibly inhibits **Complex I** (NADH:ubiquinone oxidoreductase) of the electron transport chain (ETC).
* **Energetic Consequences:**
  Inhibition of Complex I impairs proton pumping, reducing the proton motive force and slowing ATP synthase activity. This leads to a drop in intracellular ATP and an increase in **ADP:ATP** and **AMP:ATP** ratios. Elevated AMP binds the $\gamma$-subunit of AMPK, promoting its phosphorylation at Thr172 by LKB1, protecting it from dephosphorylation, and allosterically activating the kinase.
* **The Pharmacological vs. Suprapharmacological Debate:**
  A central focus of the 2023 review is the **dosing discrepancy**:
  * Clinically therapeutic concentrations in humans reach only **10–40 µM** in systemic circulation and **50–100 µM** in portal circulation.
  * Significant Complex I inhibition and detectable cellular ATP depletion often require **millimolar** (1–5 mM) concentrations *in vitro*.
  * This realization led researchers to search for pathways responsive to micromolar concentrations, uncovering the lysosomal route and tissue-specific actions (e.g., concentrated effects in the gut epithelium).

---

### 2. The Lysosomal Pathway: PEN2–v-ATPase–AXIN–LKB1 Axis

The discovery of the **lysosomal pathway** (first identified by Sheng-Cai Lin’s group, Ma et al., *Nature* 2022, and contextualized in 2023 reviews) resolved how metformin operates at low, clinically relevant concentrations (~1–5 µM) without disrupting cellular adenine nucleotide ratios:

1. **Direct Molecular Target (PEN2):**
   * Metformin binds directly to **presenilin enhancer 2 (PEN2)**, a component of the $\gamma$-secretase complex localized on the lysosomal membrane.
2. **Coupling to v-ATPase:**
   * Metformin-bound PEN2 forms a complex with **ATP6AP1** (ATPase H+ transporting accessory protein 1), an essential accessory subunit of the vacuolar $H^+$-ATPase (**v-ATPase**).
   * This interaction inhibits the proton-pumping activity of v-ATPase without altering global lysosomal integrity.
3. **Scaffold Translocation and AMPK Activation:**
   * v-ATPase inhibition initiates a conformational change on the lysosomal surface that recruits the scaffold protein **AXIN** and **LKB1** (liver kinase B1) to the lysosomal Ragulator complex.
   * AXIN-bound LKB1 physically complexes with lysosome-associated AMPK, directly phosphorylating its $\alpha$-subunit at **Thr172**.
4. **Significance:**
   * This mechanism functions **independently of AMP/ATP shifts**.
   * Tissue-specific knockout of PEN2 abolishes the glucose-lowering and lipid-clearing effects of low-dose metformin in mice, confirming that this lysosomal axis is a genuine pharmacological target *in vivo*.

---

### 3. AMPK-Independent Molecular Mechanisms

While AMPK is a prominent downstream mediator, genetic deletion of AMPK catalytic subunits ($\alpha1/\alpha2$) or its upstream activator LKB1 in mouse liver does not completely abolish metformin’s ability to suppress hepatic gluconeogenesis. Several **AMPK-independent** mechanisms explain these metabolic actions:

#### A. Direct Allosteric Inhibition of Gluconeogenic Enzymes
* **Fructose-1,6-Bisphosphatase-1 (FBP1):** Even subtle, localized increases in AMP (below thresholds required for global energetic collapse) directly bind the allosteric AMP-binding site of hepatic FBP1, immediately halting gluconeogenic flux from substrates such as lactate and pyruvate.

#### B. Alteration of Cellular Redox State (NADH/NAD⁺)
* **mGPD Inhibition:** Metformin non-competitively inhibits **mitochondrial glycerol-3-phosphate dehydrogenase (mGPD)**. 
  * Inhibiting mGPD blocks the glycerol-phosphate shuttle, preventing the transfer of reducing equivalents from the cytosol into the mitochondria.
  * This causes cytosolic accumulation of NADH, shifting the cytosolic **$\text{NADH}/\text{NAD}^+$ ratio** toward a more reduced state.
  * An elevated cytosolic $\text{NADH}/\text{NAD}^+$ ratio shifts the equilibrium of lactate dehydrogenase toward lactate, restricting pyruvate availability for gluconeogenesis and inhibiting conversion of glycerol to dihydroxyacetone phosphate (DHAP).

#### C. Antagonism of Glucagon / cAMP Signaling
* **Adenylate Cyclase Suppression:** Metformin decreases cyclic AMP (cAMP) accumulation in hepatocytes in response to glucagon.
  * Trace elevations in AMP allosterically inhibit **adenylate cyclase**, blunting intracellular cAMP production.
  * This blocks Protein Kinase A (PKA) activation, preventing CREB phosphorylation and blocking transcriptional induction of critical gluconeogenic genes (*PCK1* [PEPCK] and *G6PC* [glucose-6-phosphatase]).

#### D. Intestinal and Gut-Microbiome Axis
* High luminal concentrations of metformin (where drug levels reach millimolar range in enterocytes) alter gut microbial diversity, stimulate the secretion of **glucagon-like peptide-1 (GLP-1)** via L-cells, and modify bile acid pools, contributing to glycemic control independently of liver AMPK.

---

### Summary of Metformin's Dual Concentration Paradigm

| Feature | Lysosomal Pathway (Low Dose: ~1–50 µM) | Mitochondrial / Complex I Pathway (High Dose: >100 µM – mM) |
| :--- | :--- | :--- |
| **Primary Target** | **PEN2** (presenilin enhancer 2) on lysosome | **Complex I** of the ETC in mitochondria |
| **Effector Complex** | ATP6AP1 / v-ATPase $\rightarrow$ AXIN–LKB1 recruitment | Respiratory Chain $\rightarrow$ decreased ATP synthesis |
| **AMP/ATP Ratio** | **Unchanged** (energy charge maintained) | **Increased** (energetic stress) |
| **AMPK Dependency** | **AMPK-dependent** via lysosomal LKB1 phosphorylation | **Both AMPK-dependent** (via AMP/LKB1) & **independent** (FBP1 allostery, mGPD redox shifts, cAMP reduction) |
| **Primary Sites** | Systemic tissues, physiological hepatic signaling | Intestinal epithelium (where high transit concentrations exist), suprapharmacological lab settings |
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbDbadosnSa0LBoTKb0EiCRlyrBB_KgpCqDIgXXMrjYDjR2ConghIIivMrIce3-JicbF4LlKzYx4C5NABDYp1F250q3zxzd48o1Fe4XUgM0hjFJx7x8r2blHscBxGHtA==>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEH7iw-XtXOSO6sE56RDJ6NTkiPBzrcPFw4rbrKCptJB_BJ9QK4A70Y-WxtwDDgrN-uSqWFTSWHJG9GbKUdq2Y2siORCx6jO_7DlvXF3DRYMRz7aLleNhdviLE9MdeCNj71YWJXsNNHveKfrLAfTbNt6uQNP2Q1_PyYn-V5v8GPGVgBFpY0PTh0MwZooEtkf_-bpaGoasdz3GZDSo03LnipF47CcMiMFYKcFL0=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5al__ZPb6jG50JeRhUfhltGVAgE2Q8E8lZxv_zM0vq71ZNknjTZCZBr8toixb-HcNQJe-Vi3AV_DCGoIeRciAGj9p1RSg8BtnJPxJc2wcspKGgjm-KAGu1_T1FXWgmyNpQqaoXxP1>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFeF6X3i3iHC7y53avCK5a3-u1_ao5N76HinlaJR2QVtjo_MTMcpv91Osc8eOB3ToJ9ZlcacEJoE6oOl8KFBfqGi3gFdRw2qgn9nrmcw72X7cekKGGstGw5HNL_vt6I4Gi0Qfq7M-HqpA==>
  - frontiersin.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGizfYU--oAyLyVVhvo0X75OnMb0kJQuQxOdE79_gSeHlmwqi_AK55tBfTausQhFKrw1-S93VFWjoXt7kwL0hucldERJtonCV_jbnP9LiKBwZmUE83eJCaZE6JaO0XfyyPoAk93C3xOgX2afTHI0sbDxY38nMPNmx7ll6lpYIibtGUIIlRILyMCpOc4NkoFbg==>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFZdSF2-nICIhSkc8YivR-OasZXm9BqtRNOz6UVIm76SQEjyR_3tY34S2KRcPOxPQoj2BpsflxTLR_78Sph-5nSz3rijjk4obRCmzjKWk9YdW23R291JwraVer7ismgJi8mqg7Z0aZV5Rt9AOKoD7ve0OePbUlSSQMyezj58lmS74SM7TOLzgh9UN-E>

[7] web search for 'Foretz Guigas Viollet "Metformin: update on mechanisms of action and repurposing potential" Nature Reviews Endocrinology 2023 doi'; grounded search summary:
The DOI for the article is:

**10.1038/s41574-023-00833-4**

---

### Citation Reference:
* **Authors:** Marc Foretz, Bruno Guigas, and Benoit Viollet
* **Title:** *Metformin: update on mechanisms of action and repurposing potential*
* **Journal:** *Nature Reviews Endocrinology* (2023), 19(8), pp. 460–476
* **Link:** [https://doi.org/10.1038/s41574-023-00833-4](https://doi.org/10.1038/s41574-023-00833-4)
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFnejHDICdD_9p1DKJP5J8ho2x4b6GPGu8nv0WMKOpSOGe3IYxMq96VXUAkeLK4iRMHMU8gHIznfHdJaFbDL0ccKH5qTumgy5buzb-bJa8biMy4wJlz2mHbewkoB_cOig==>

[8] web search for 'Ma et al Nature 2022 PEN2 metformin lysosomal AMPK doi link'; grounded search summary:
**Paper Title:** Low-dose metformin targets the lysosomal AMPK pathway through PEN2  
**Authors:** Teng Ma, Xiao Tian, Baoding Zhang, Mengqi Li, Yu Wang, ..., Chen-Song Zhang, Sheng-Cai Lin  
**Journal:** *Nature* (2022), Vol. 603, Iss. 7899, pp. 159–165  

* **DOI:** `10.1038/s41586-022-04431-8`
* **Direct DOI Link:** [https://doi.org/10.1038/s41586-022-04431-8](https://doi.org/10.1038/s41586-022-04431-8)
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdkd79_0p26p5i3dn0ARnepDDYzgNn9VGTGZbqN12joeVZvicyXr_RVrDmg0mFaNT2x_bDMMK7H732GDclhYColElOXvA9ozC0KZ9p2zrlnAGR-dgEoiOdIMCyjkvyGA==>
  - addgene.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR9mLL33VP1dTCs2OtJwwkxwQSExD-eLe7z1wA1wd_quEPYFC2Kc90Vn7T_v_CkVMPV0p2dTvXfMcmts1pnB2bPM1HdWMkHMwXjx5dTONHs3AOPEaE6A1oB71oZrKpHIcF8sKJ7nw=>

[9] web search for 'metformin hydrochloride tablets FDA label accessdata drugsatfda_docs lbl pdf'; grounded search summary:
The official FDA Prescribing Information (package insert) for metformin hydrochloride tablets can be accessed through the FDA **Drugs@FDA** database and the National Library of Medicine’s **DailyMed** system. 

---

### Accessing the Label on Drugs@FDA (`accessdata.fda.gov`)

Metformin hydrochloride tablets were originally approved under the brand name **Glucophage** (immediate-release) and **Glucophage XR** (extended-release), as well as brand-name formulations like **Fortamet** and **Glumetza**:

* **FDA Application Numbers:** 
  * NDA **020357** (GLUCOPHAGE – Metformin HCl Tablets: 500 mg, 850 mg, 1,000 mg)
  * NDA **021202** (GLUCOPHAGE XR – Metformin HCl Extended-Release Tablets: 500 mg, 750 mg)
  * NDA **021574** (FORTAMET Extended-Release Tablets)
  * NDA **021748** (GLUMETZA Extended-Release Tablets)
* **Drugs@FDA Database Link:**
  * Search directly via the [FDA Drugs@FDA Database](https://www.accessdata.fda.gov/scripts/cder/daf/) by entering **"metformin"** or NDA number **"020357"**.
  * The PDF files archived under the `drugsatfda_docs/label/` directory correspond to the specific supplement approval packets (e.g., standard labeling updates for lactic acidosis / eGFR dosing).
* **Current Generic Labels (DailyMed / SPL):**
  * Generic labels from various manufacturers (such as Teva, Aurobindo, Sun Pharma, etc.) are available on [NIH DailyMed](https://dailymed.nlm.nih.gov/).

---

### Key Prescribing Information Summary (FDA Label)

#### 1. Boxed Warning: Lactic Acidosis
* **Risk Factors:** Metformin-associated lactic acidosis (MALA) is a rare but serious metabolic complication that can occur due to metformin accumulation. Risk factors include renal impairment, concomitant use of certain drugs (e.g., carbonic anhydrase inhibitors), age $\ge$ 65 years, undergoing radiologic studies involving intravascular iodinated contrast, surgery, hypoxic states, and excessive alcohol intake.
* **Management:** If suspected, promptly discontinue metformin and institute general supportive measures in a hospital setting; hemodialysis is recommended.

#### 2. Indications and Usage
* Indicated as an adjunct to diet and exercise to improve glycemic control in adults (and pediatric patients 10 years and older for immediate-release tablets) with type 2 diabetes mellitus.
* **Limitations of Use:** Not indicated for type 1 diabetes or diabetic ketoacidosis.

#### 3. Dosage and Administration
* **Immediate-Release (Tablets):**
  * Starting dose: 500 mg orally twice daily or 850 mg once daily with meals.
  * Titration: Increase by 500 mg weekly or 850 mg every 2 weeks as tolerated.
  * Maximum recommended daily dose: 2,550 mg/day (given in divided doses).
* **Renal Function Assessment (eGFR):**
  * Obtain eGFR prior to initiation and at least annually thereafter.
  * **eGFR < 30 mL/min/1.73 m²:** Contraindicated.
  * **eGFR 30–45 mL/min/1.73 m²:** Initiation is not recommended; if already taking metformin, assess benefit-risk and consider dose reduction.
* **Iodinated Contrast Procedures:**
  * Discontinue metformin at the time of or prior to iodinated contrast imaging in patients with eGFR between 30–60 mL/min/1.73 m², a history of hepatic impairment, alcoholism, or heart failure, or those receiving intra-arterial contrast. Re-evaluate eGFR 48 hours post-procedure before restarting.

#### 4. Contraindications
* Severe renal impairment (eGFR below 30 mL/min/1.73 m²).
* Known hypersensitivity to metformin hydrochloride.
* Acute or chronic metabolic acidosis, including diabetic ketoacidosis.
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlNjJKGiT5V9S4anvzoZLTWhnK8iPni7nbhDQOjo8GKXZGDKLF8yJZYESMnwEO8DwnhD87wkcJBBXMzOau0BTqcSEPsQTFkYJMqkN6qeu6AbcaqdTH3txwn4h12IOWBrXxtvKyDV6lx21jRBMWxWpOvM3w631e1zA4qqzQIlyFjcTEgx_QLUu2NgDxrdcSTmFDNTM=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQETmeno0CZkd_sPc33O3yzFD95mCMIWT3FjYJUL5NbBayU5X0BxPwf6e-lNvINc2Kq472te6IT3xoE1Bno3bVXPLa0qIwDuRz3V187CxMw8vSGtfrOYl44V_R4HV07TNLGgD30yGyAO4ochYudfX5I_OJVT1MmsUDCQK8Hov1zUj3HeuVl0rXfwPZbCXph5yX0=>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4kmnMRHIDPTSjrbUj9w3sc2hkWA85Kt4ynYwGaFxbo8oLrJv1P9JTDcaF5yJHm81WeTcHmI1xYlzsHxjf1jTLNWbAjhCCMgyIRhPxuSHLe67zyZV9ZvIarVahBu75TqlPNMwnbNeZswKJPYygfLB0f6N11y9tB2lah0ceoC1rGw==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEVx2txSiFElBWidKiYPL31kXyBuy-82qe9eNq5Z6D09UbMk1wlioVbuU-IVJHkLgq08kSXpApDZzd5xqUXextlQRBT89DKC3tdb06Dwye2Jo7QJJKTdbY4mGeZJqd_v3gGUtIXT2u3c2NGySvJJjs37fjjNb85tjTX3gPz-zGFUQ==>
```

</details>

**Answer:**

Metformin is a biguanide antihyperglycemic drug, and its mechanism has both a well-established clinical description and a still-debated molecular basis. Here's a sourced summary.

## Primary mechanism of action

**Clinically (the accepted "headline" mechanism):** Metformin primarily **lowers hepatic glucose production** (reduces gluconeogenesis and glycogenolysis), while also **decreasing intestinal glucose absorption** and **improving insulin sensitivity** by increasing peripheral glucose uptake and utilization. Importantly, it **does not stimulate insulin secretion** — insulin levels are unchanged, so it does not cause hyperinsulinemia or (as monotherapy) hypoglycemia. This is the wording in the FDA-approved label (Section 12.1, Mechanism of Action).

**At the molecular level (most widely accepted):** Metformin accumulates in the mitochondrial matrix (taken up into hepatocytes largely via the **OCT1/SLC22A1** transporter) and causes **mild, reversible inhibition of mitochondrial respiratory Complex I**. This reduces the proton-motive force and ATP synthesis, raising cellular **AMP:ATP / ADP:ATP ratios**, which **activates AMP-activated protein kinase (AMPK)** via LKB1-mediated phosphorylation and allosteric AMP binding.

**Key nuance — concentration:** Measurable Complex I inhibition typically needs millimolar concentrations in vitro, whereas clinical plasma levels are only ~10–40 µM. To explain activity at low, pharmacologically relevant doses, a **lysosomal AMPK-activating pathway** was identified (Ma et al., *Nature* 2022): metformin binds **PEN2** (a γ-secretase component), which interacts with the v-ATPase subunit ATP6AP1 to recruit AXIN–LKB1 and activate AMPK **without** changing AMP/ATP ratios.

## Resulting effect on blood glucose

| Effect | Site / pathway |
|---|---|
| ↓ Hepatic glucose production (dominant effect) | Downregulation of gluconeogenic enzymes PEPCK (PCK1) and glucose-6-phosphatase (G6PC), largely via AMPK |
| ↑ Peripheral glucose uptake & utilization | Skeletal muscle and adipose tissue (improved insulin sensitivity) |
| ↓ Intestinal glucose absorption | Gut |
| Net result | Lower fasting (basal) and postprandial glucose; no hypoglycemia as monotherapy |

## Secondary / AMPK-independent mechanisms

Genetic studies (liver-specific AMPK/LKB1 knockouts) show metformin still suppresses gluconeogenesis without AMPK, via:
- Direct allosteric inhibition of **fructose-1,6-bisphosphatase-1 (FBP1)** by elevated AMP
- Inhibition of **mitochondrial glycerol-3-phosphate dehydrogenase (mGPD)**, altering cytosolic NADH/NAD⁺ redox and limiting gluconeogenic substrate supply (lactate, glycerol)
- Antagonism of **glucagon/cAMP signaling** (AMP-mediated inhibition of adenylate cyclase)
- **Gut/microbiome effects** — altered microbiota, increased GLP-1 secretion, bile-acid changes
- In **PCOS**, improved insulin sensitivity lowers circulating insulin, LH, and androgens

*Related pharmacology: metformin is not hepatically metabolized, is excreted unchanged renally, and carries a boxed warning for lactic acidosis (relevant to its mechanism via mitochondrial effects).*

## Sources (public)

1. **FDA prescribing information (label), Section 12.1 Mechanism of Action** — Drugs@FDA (metformin HCl, NDA 020357): https://www.accessdata.fda.gov/scripts/cder/daf/ ; DailyMed: https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=metformin
2. **NIH/NCBI StatPearls – Metformin** (NBK518983): https://www.ncbi.nlm.nih.gov/books/NBK518983/
3. **Foretz M, Guigas B, Viollet B.** "Metformin: update on mechanisms of action and repurposing potential." *Nat Rev Endocrinol* 2023;19(8):460–476. DOI: https://doi.org/10.1038/s41574-023-00833-4
4. **Ma T, et al.** "Low-dose metformin targets the lysosomal AMPK pathway through PEN2." *Nature* 2022;603:159–165. DOI: https://doi.org/10.1038/s41586-022-04431-8

---

**Notes on sourcing and scope:**
- This is a **general pharmacology question**, so I answered from **public sources** only (via the web-search specialist). No internal database records or uploaded documents were referenced or needed.
- No files were attached to this conversation (the working directory is empty), so there was nothing local to analyze.
- One caveat from the search: the web tool returned some Google redirect/grounding links rather than stable canonical URLs, so the citations above list the canonical public locations (FDA/DailyMed, NCBI Bookshelf, journal DOIs) for the underlying sources.

If you'd like, I can compile this into a Markdown report and export it to PDF.

---

## 21. web-04 (web, medium)

**Question:** Which company originally developed atorvastatin, and in what year did the FDA approve it?

**Gold answer:** Parke-Davis (a Warner-Lambert division, later Pfizer); FDA approval in December 1996.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] web search for 'atorvastatin Lipitor originally developed Warner-Lambert Parke-Davis FDA approval date'; grounded search summary:
The U.S. Food and Drug Administration (FDA) approved **Lipitor** (atorvastatin calcium) on **December 17, 1996** under New Drug Application (NDA) #020702.

### Key Background:
* **Developer:** Atorvastatin was first synthesized in 1985 by Bruce Roth at the **Parke-Davis Pharmaceutical Research Division of Warner-Lambert**.
* **Commercialization:** Warner-Lambert entered into a co-marketing agreement with Pfizer to market the drug starting in 1997, and Pfizer later acquired Warner-Lambert in 2000.
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwDPDIDGKI7Bh83VsyfDZq_1-oG0LdLYME4f3mYN4uKAyGko0QHS37_GbgtMeA6Q4OIN7umuJCKaJYjbcA2SSbcVeR31kuCHwEsxBSNcH4HWPEjcYd2FIjaVocO4Hxs3k1jVzffmy9jQeJCzMaDKwHFkjzOcdS0yThsFn7IyVQt0EOdw==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEYJCaNfZukZHWmIxhmOIIxXnck52tfx9Y1yc4fZEVIqWatlkPJwnwT0jP99LnqBT4HfLkdlu1fRMr7rbgdP6frkrvLFCQEwq9RgbdtGqfNf2vFrnMlyAySqO_SW-Jn588fMGJvBA_Nmd3q7lvC_O-GtZxvnxlRwGXO4yaQXGp4Ne1RMg==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGwDPDIDGKI7Bh83VsyfDZq_1-oG0LdLYME4f3mYN4uKAyGko0QHS37_GbgtMeA6Q4OIN7umuJCKaJYjbcA2SSbcVeR31kuCHwEsxBSNcH4HWPEjcYd2FIjaVocO4Hxs3k1jVzffmy9jQeJCzMaDKwHFkjzOcdS0yThsFn7IyVQt0EOdw==>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHL-Tcfhn5uX3v_4CQytrj7Fi0lRZrIbCffLzJVqYXghwxKKLc40782WaCDXmcui_SAsmSu6A-sUxhutoW10RZG-Znpc_nldOPDWsUlqHanOTEgQu2PmHdR3Tv8BbMBkNU=>

[3] web search for 'FDA approval Lipitor atorvastatin December 1996 new drug application'; grounded search summary:
The key details regarding the **U.S. Food and Drug Administration (FDA) approval** for **Lipitor (atorvastatin calcium)** in December 1996:

---

### **Overview of Approval**
* **Brand Name:** Lipitor
* **Generic Name:** Atorvastatin calcium
* **Application Type:** New Drug Application (NDA)
* **NDA Number:** **NDA 020702** (also cited as NDA 20-702)
* **Submission Date:** June 17, 1996
* **FDA Approval Date:** **December 17, 1996**
* **Review Timeline:** Approved in exactly **6 months**, a remarkably rapid review for a standard small-molecule NDA under the Prescription Drug User Fee Act (PDUFA) guidelines.
* **Applicant / Sponsor:** **Parke-Davis Pharmaceutical Research** (a division of the Warner-Lambert Company). *(Pfizer co-marketed the drug at launch and acquired Warner-Lambert in 2000).*

---

### **Initial Indications & Labeling**
The FDA approved Lipitor as an adjunct to diet to:
1. **Reduce elevated total cholesterol (Total-C), LDL cholesterol (LDL-C), apolipoprotein B (Apo B), and triglycerides (TG)** in patients with primary hypercholesterolemia (heterozygous familial and non-familial) and mixed dyslipidemia (Fredrickson Types IIa and IIb).
2. **Reduce Total-C and LDL-C** in patients with homozygous familial hypercholesterolemia as an adjunct to other lipid-lowering treatments.

---

### **Dosage & Administration at Launch**
* **Form:** Film-coated oral tablets
* **Approved Strengths:** Initially approved in 10 mg, 20 mg, and 40 mg tablets (an 80 mg strength was added soon after).
* **Recommended Starting Dose:** 10 mg once daily, taken at any time of day, with or without food.

---

### **Significance**
* **Class:** HMG-CoA reductase inhibitor (statin).
* Lipitor was the **fifth statin** approved in the United States (following lovastatin, pravastatin, simvastatin, and fluvastatin).
* Clinical trials demonstrated greater dose-for-dose LDL-C and triglyceride reduction compared to other statins available at the time. 
* Following its launch in early 1997, Lipitor went on to become the best-selling prescription pharmaceutical in history, generating more than $130 billion in sales before patent expiration in November 2011.
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG2JRMPPYcWo6t8E6_zhPcCfK9gL3BS_L37yZ9Ma2XNEVuAt3FJTFZlrARxCgr00msd1TKCzfO94l1ANnQmqsd-xQmsUEGyiChYd43uvjzUYTX8kX97tOfBEI9r9MYjCURy2NVea3Cw5oZWssjA5BzvYwwcSu18WV19F9q62vY914pdFQ==>
  - govinfo.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHsB3ibgpT3aJ-wswBAjsppKCeAHx_QlovefkV45fXhRRmJhjwPzqoWYUDxT0L8xdGUetD8jie2QcRKt1DdiheijZD--MxKFcMIfVxIlf3Hrwscw03-ZpVmodDOuKdHXCL4sUu4KtVGBz5oOmdR4afwMo00oC5L_Aec>
  - drugs.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqKtFxL2YLbTqC2mXWFw4B5G2ySjv4hGQYWd88D6wvUmkHXGAy3p7zzXrTEw_ToXLLBysGn2hvEeGeULsjTx7zYmyfBSTMs3gF6565z-_SGMfOmdR-Ct-4ch4zjw==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrIlR0Ws3W3zCNaQt4tRgswdPlX6uwVyjgCXq7VSJ17lIHKXEiGM0a9xGe46GpveGg-lVLn8MOeVBjduYsVY-l9BjLiZsx3HZHnpcLy0_MoIg9GPyqmLsJILC9eD6C-AJXeJiGBFk9BfUZpJnlFrZLrOLja5L8i2wmWJxJiv9JS14EPBHKguvWqZXGtiQAgY2_>
  - clinician.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHLGTze_uHpGBbzrde5ohs1n5ZWysDfevWl4YEt8WIPvbBp82vMDv4JBiSx05-T87y3eQ7nSQNWe39V8DXG_1gGy6yfEWo7W2vFUM_nKszGcrzt-M2khwRqa4qF-I1Qd5FVV4DysMklbx1Q3LxoMlAFIM5tJfW92oxA3woyIbnSOOrkbW3d>

[4] web search for 'Pfizer Warner-Lambert merger 2000 Lipitor acquisition'; grounded search summary:
The **Pfizer–Warner-Lambert merger of 2000** remains one of the largest and most consequential hostile takeovers in corporate history. Valued at approximately **$90 billion**, the transaction was almost entirely driven by a single asset: **Lipitor (atorvastatin)**, which went on to become the best-selling prescription pharmaceutical in history.

---

### 1. Background: The Discovery of Lipitor
* **Development:** Lipitor was synthesized in 1985 by Bruce Roth, a chemist at Parke-Davis, a subsidiary of Warner-Lambert. It belonged to the statin class of drugs designed to lower LDL ("bad") cholesterol.
* **Co-Promotion Agreement (1996):** Warner-Lambert recognized that Lipitor had superior efficacy compared to rival statins like Merck’s Zocor and Mevacor. However, Warner-Lambert lacked the massive global sales force needed to dominate the market. In 1996, it entered into a joint co-marketing agreement with Pfizer. 
* **Rapid Rise:** Launched in 1997, Lipitor quickly became an unprecedented commercial success, reaching blockbuster status (over $1 billion in annual sales) within its first full year.

---

### 2. The Catalyst: The American Home Products Deal (1999)
* In November 1999, Warner-Lambert announced an agreed **$72 billion "merger of equals" with American Home Products (AHP)** (which later became Wyeth).
* Warner-Lambert’s management aimed to scale up while maintaining independence from Pfizer, with whom relations had grown increasingly strained over commercial control of Lipitor.
* **The Threat to Pfizer:** Pfizer feared that an AHP–Warner-Lambert merger would jeopardize its co-marketing rights or result in litigation over Lipitor's profits, threatening Pfizer’s fastest-growing revenue stream.

---

### 3. Pfizer’s Hostile Counter-Bid
Hours after the Warner-Lambert/AHP deal was announced, Pfizer launched an **unsolicited hostile takeover bid** for Warner-Lambert:
* **The Legal Arena:** Pfizer immediately sued to invalidate Warner-Lambert’s deal protections (including a $2 billion breakup fee and cross-option agreements) and asserted that the AHP deal violated their Lipitor co-marketing contract.
* **The Bidding War:** Pfizer initially offered roughly $82 billion in stock, which it subsequently raised. Warner-Lambert’s board initially resisted, seeking other white knights (such as Procter & Gamble), but none materialized.
* **Capitulation:** Facing immense pressure from institutional shareholders who preferred Pfizer’s higher all-stock premium, Warner-Lambert ended talks with AHP in February 2000. 

---

### 4. Terms and Closing (June 2000)
* **Transaction Value:** Approximately **$90 billion** in stock (often cited between $87B and $116B depending on fluctuating stock valuations around the announcement and closing dates).
* **Breakup Fee:** Warner-Lambert paid American Home Products a **$1.8 billion termination fee**, the largest breakup fee in history at the time.
* **Closing:** The merger received regulatory clearance (subject to modest divestitures of overlapping consumer health and drug assets) and officially closed in **June 2000**.

---

### 5. Legacy and Business Impact

1. **Lipitor’s Dominance:**
   * Full ownership of Lipitor catapulted Pfizer's profits. At its peak in 2006, Lipitor generated nearly **$13 billion in annual sales** alone.
   * Over its patent life (which ran until late 2011 in the U.S.), Lipitor generated more than **$125 billion to $130 billion in cumulative revenue**, making it the first prescription drug to cross the $100 billion lifetime threshold.

2. **Pfizer as an Industry Titan:**
   * The acquisition instantly made Pfizer the **world’s largest pharmaceutical company by revenue**, surpassing Merck and Glaxo Wellcome.
   * It set a precedent for Pfizer’s corporate strategy over the next decade: executing massive, mega-mergers to acquire drug pipelines and offset patent cliffs (subsequently acquiring **Pharmacia in 2002** and ironically acquiring **Wyeth/AHP in 2009**).

3. **Restructuring and Consumer Brands:**
   * Alongside pharmaceuticals, Pfizer absorbed Warner-Lambert’s large consumer healthcare division (including brands like **Listerine, Halls, and Schick-Wilkinson Sword**), which Pfizer later divested to Johnson & Johnson and Energizer in the mid-2000s to refocus on core biopharmaceuticals.
sources:
  (none)

[5] web search for 'atorvastatin discovery Parke-Davis Warner-Lambert 1985 synthesis history'; grounded search summary:
The discovery and chemical development of **atorvastatin** (marketed as **Lipitor**) is one of the most famous case studies in modern medicinal chemistry and pharmaceutical history. It originated in the mid-1980s at the **Parke-Davis Pharmaceutical Research Division** of the **Warner-Lambert Company** in Ann Arbor, Michigan.

---

### 1. Historical Context (Early 1980s)
In the late 1970s and early 1980s, Akira Endo and Merck pioneered the first generation of HMG-CoA reductase inhibitors (statins), such as compactin (mevastatin) and lovastatin (Mevacor). These early statins were fungal fermentation products or semi-synthetic derivatives characterized by a complex, rigid hexahydronaphthalene (decalin) ring connected to a chiral $\beta$-hydroxy-$\delta$-lactone pharmacophore.

Recognizing the immense potential of cholesterol-lowering therapies, several pharmaceutical companies set out to design **fully synthetic statins** that did not rely on fungal fermentation. At Warner-Lambert/Parke-Davis, a young medicinal chemist named **Dr. Bruce D. Roth** was assigned to this project after joining the company in 1982.

---

### 2. The 1985 Synthesis and Discovery (CI-981)
In **1985**, Bruce Roth successfully synthesized the molecule that would become atorvastatin, designated internally as **CI-981**. 

#### Molecular Design Strategy
Roth and his team used early molecular modeling to hypothesize that the bulky, stereochemically intricate decalin core of natural statins was not strictly required for enzyme inhibition. What mattered most was:
1. The **dihydroxyheptanoic acid** side chain, which mimics the natural intermediate (HMG-CoA) and binds to the active site of HMG-CoA reductase.
2. A **hydrophobic anchor** that occupies a nearby lipophilic pocket in the enzyme.

Instead of a multi-ring fused system, Roth designed a **penta-substituted central pyrrole ring** bearing carefully oriented substituents:
* A **4-fluorophenyl** group
* An **isopropyl** group
* A **phenyl** group
* A **phenylcarbamoyl (anilide)** group
* The critical **$(3R, 5R)$-dihydroxyheptanoic acid** pharmacophore linked to the pyrrole nitrogen

#### The Discovery Synthesis
Roth’s original 1985 synthesis generated a **racemic mixture**. The pyrrole core was assembled using 1,3-dipolar cycloaddition chemistry (involving mesoionic intermediates known as münchnones) reacted with an alkyne, after which the side chain was installed. 

Biochemical testing revealed that the enzyme's binding pocket was stereospecific:
* The **$(3R, 5R)$-enantiomer** had an $\text{IC}_{50}$ of ~8 nM.
* The $(3S, 5S)$-enantiomer was essentially inactive ($\text{IC}_{50} > 400\text{ nM}$).

Parke-Davis filed the composition-of-matter patent for the racemate in 1986 (issued as **U.S. Patent 4,681,893** in 1987), followed later by filings for the active $(3R,5R)$-isomer and the hemi-calcium salt formulation.

---

### 3. Scaling the Chemistry: The Paal-Knorr Breakthrough
The original discovery route was not commercially viable: it was linear, low-yielding, and required tedious chiral separations. Parke-Davis chemical development teams (including Paul Brower, Donald Butler, and Bruce Roth) re-engineered the synthesis into a **highly convergent route**:

1. **The Core Reaction (Paal-Knorr Condensation):** 
   They devised a condensation between an elaborate **1,4-diketone** (bearing the isopropyl, phenyl, and fluorophenyl groups, prepared via a Stetter reaction) and a **primary amine** already containing the protected $(3R, 5R)$-diol side chain.
2. **Chiral Side Chain Construction:** 
   The side-chain synthon was initially prepared from chiral pool starting materials (such as isoascorbic acid or $(S)$-malic acid derivatives) and later produced on ton-scale using sophisticated asymmetric catalysis and biocatalysis (chemoenzymatic halohydrin dehalogenase steps).
3. **Salt and Polymorph Optimization:**
   The molecule was converted into its **calcium salt (atorvastatin calcium)** to ensure oral stability, bioavailability, and reproducible crystallization.

---

### 4. Near-Cancellation and Clinical Resurrection
Despite the chemical breakthrough in 1985, atorvastatin almost never reached the clinic:
* **The "Me-Too" Perception:** By the late 1980s, Merck already dominated the market with lovastatin and simvastatin, Bristol-Myers Squibb had pravastatin, and Sandoz was advancing fluvastatin. Atorvastatin was the fifth statin under development.
* **Misleading Animal Data:** In routine rat assays, atorvastatin did not appear significantly better than Merck's lovastatin. Warner-Lambert management debated terminating CI-981 to focus resources elsewhere.

However, Parke-Davis scientific leadership (notably Dr. Ronald Cresswell) insisted on testing CI-981 in human Phase I trials. 

The results were astonishing:
* Unlike its predecessors, atorvastatin reduced LDL-C by up to **40% to 60%** across its dose range (10 mg to 80 mg).
* It had an exceptionally long half-life (~14–20 hours) and yielded active circulating metabolites that extended its inhibitory action, meaning patients could take it at any time of day rather than strictly at night.

---

### 5. Launch and Pharmaceutical Impact
Recognizing they had a best-in-class molecule but lacked the commercial sales force to compete with Merck, Warner-Lambert entered into a co-promotion agreement with **Pfizer** in 1996. 

* **Approval:** Approved by the FDA in December 1996, atorvastatin launched in early 1997 under the brand name **Lipitor**.
* **Pfizer Acquisition:** Lipitor became a runaway success, quickly becoming the fastest-growing statin in history. In 2000, to gain full ownership of Lipitor, Pfizer completed a hostile **$90 billion takeover of Warner-Lambert**—one of the largest pharmaceutical acquisitions of all time.
* **Legacy:** Lipitor became the first pharmaceutical product to surpass $10 billion in annual sales, generating over $150 billion across its patent life, and cemented Bruce Roth’s 1985 synthesis as one of the most lucrative discoveries in corporate science.
sources:
  - newdrugapprovals.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTJyQXBxwWtPMISazd5Sldu7I8ZDamr1huOZ1VBcdVg7ojH9ouC9bFPe308Gl56YeAzg6W_-Nb6G_yKU4-bCvFJ7PzwQd5v449hBmCXuWxT9i0FNfKgQ0TEhUXPrQnzmbbShQe3rXziNzo1-T5qL9lCshV7mM=>
  - substack.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6Ai8L34gLvF3sOdWlE5bo1IdwXkydnDsclNMHxXgOFxeuAD-r69-Qgt5aXywohaWwkTayZJzaYdDGA-zoGR9sELtETx-IEdetSHhijFrd96uRDwFxX2H7wCRT-1um24l5i_jHNOCUeD-UJzWs3_VKCuWMhQ6eVSp->
  - gene.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmlJGrWasOChvX-YKjqKeTn8jUCDaNhzlVJd9de_Naut5GNb-gHf3PcYdPsVRngD4XIEFiiWZoi6WK942Zv7J8AN4RRcWJGgdPhN2Hd--tYsFBq6KsOtpBgkyTWDOiBJQIsUTpL3uySiOe>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFHbyHncvupLEkUuZEUsurOGbW5Tr-6JyqmGAmm7Ot7Vo0TVOOuJwYBw_zU0azoyAv-d2iUTnRhO83CFCiow_iy4ysDDS4tva-Cuc6xZAKE-DmkzOYdv1BS5q8BU2HLQvLfBBwqtctofCngcFnXchCX6L6CsthN51NYhefKNI_xr6h7NtxKqvuYl2iFdLKkyNS4n200ejjdSy82pfsmdXmPJ_Odpt157tQHhMqptabqnsVSfKsjv1iAhEl5>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHATAI_elE0vUAxXSfaerKK46Bpfug9kG3HPFwUBvDLGQtOFq2j6QURdq1t4M0_IIBVKHRbRlEie5UHub3UD5hU1eMrU6LOcvjbHh4bG0e4SAf23ef6cLl8cV3fa_QK>

[6] web search for '"atorvastatin" Wikipedia "Warner-Lambert" "Bruce Roth" developed Lipitor Pfizer'; grounded search summary:
The keywords refer to the history and development of **atorvastatin** (best known by the brand name **Lipitor**), one of the best-selling prescription medications in pharmaceutical history:

---

### **1. Discovery by Bruce Roth (1985)**
* **The Chemist:** Dr. **Bruce Roth**, a medicinal chemist at the Parke-Davis Pharmaceutical Research division of **Warner-Lambert**, synthesized atorvastatin for the first time in **1985**.
* **Initial Skepticism:** At the time, other statins (such as lovastatin and simvastatin) were already on the market or in clinical development. Warner-Lambert leadership initially doubted whether developing another statin would be commercially viable.
* **Breakthrough Data:** Clinical trials demonstrated that atorvastatin was significantly more potent at lowering low-density lipoprotein (LDL) cholesterol than competing statins at equivalent doses, prompting Warner-Lambert to fast-track its development.

---

### **2. FDA Approval and Co-Promotion with Pfizer (1996–1997)**
* **Approval:** The U.S. Food and Drug Administration (FDA) approved atorvastatin under the brand name **Lipitor** in December 1996, and it was launched in early 1997.
* **The Partnership:** Recognizing the need for massive marketing firepower to compete against Merck's established statins (Mevacor and Zocor), Warner-Lambert entered into a co-promotion agreement with **Pfizer**. Pfizer’s sales force helped propel Lipitor to rapid commercial dominance.

---

### **3. Pfizer’s Hostile Takeover of Warner-Lambert (2000)**
* In late 1999, Warner-Lambert announced plans to merge with American Home Products (AHP).
* Eager to gain complete, exclusive ownership of Lipitor—which was on track to become the most lucrative drug in the world—**Pfizer launched a hostile takeover bid**.
* In 2000, Pfizer completed the acquisition of Warner-Lambert for approximately **$90 billion**, which remains one of the largest pharmaceutical mergers in history.

---

### **4. Legacy and Commercial Impact**
* **Blockbuster Status:** Lipitor became the first prescription drug to generate more than $10 billion in annual sales, eventually surpassing **$125–$130 billion in total sales** over its patent life before facing generic competition in late 2011.
* **Recognition:** Bruce Roth received numerous honors for his invention, including the **Perkin Medal** (2013) and induction into the **ACS Heroes of Chemistry**.
sources:
  (none)

[7] web search for 'drugs@FDA Lipitor NDA 020702 approval letter accessdata.fda.gov'; grounded search summary:
For **Lipitor (atorvastatin calcium tablets)** under **NDA 020702** (also cited as NDA 20-702 in older FDA records) on **Drugs@FDA**:

---

### 1. Drugs@FDA Application Overview
* **Application Number:** NDA 020702
* **Drug Name:** Lipitor (atorvastatin calcium)
* **Original Approval Date:** **December 17, 1996**
* **Original Sponsor:** Parke-Davis Pharmaceutical Research (Division of Warner-Lambert Company, now Pfizer Inc.)
* **Initial Dosage Strengths:** 10 mg, 20 mg, and 40 mg oral tablets (the 80 mg strength was approved later)
* **Drugs@FDA Database Access:** You can access the entry directly by searching application number **020702** on the [Drugs@FDA Database](https://www.accessdata.fda.gov/scripts/cder/daf/).

---

### 2. Availability of the Original Approval Letter
* **Pre-1998 Documentation Status:** The FDA generally does not host scanned action packages or original approval letters online for NDAs approved prior to 1997–1998. Consequently, the **December 17, 1996** original approval letter for NDA 020702 is not hosted as a downloadable PDF in the Drugs@FDA archive; obtaining the original document typically requires a Freedom of Information Act (FOIA) request to the FDA.

---

### 3. Available Supplemental Approval Letters on `accessdata.fda.gov`
While the original 1996 letter is not posted, numerous **Supplemental NDA (sNDA) approval letters and review packages** for NDA 020702 are available for download on `accessdata.fda.gov`:

* **NDA 020702/S-003 & S-005 (Approved July 10, 1998):** Expanded indications for hypertriglyceridemia and primary dysbetalipoproteinemia.
  * [Download S-003/S-005 Approval Package (PDF)](https://www.accessdata.fda.gov/drugsatfda_docs/nda/98/020702_S003_LIPITOR%20TABLETS.pdf)
* **NDA 020702/S-014 (Approved August 28, 1998):** Labeling changes.
  * [Download S-014 Approval Package (PDF)](https://www.accessdata.fda.gov/drugsatfda_docs/nda/98/020702,S014_LIPITOR%20TABLETS.pdf)
* **NDA 020702/S-018 (Approved 1999):** Added the indication to increase HDL-C in patients with primary hypercholesterolemia and mixed dyslipidemia.
  * [Download S-018 Approval Letter (PDF)](https://www.accessdata.fda.gov/drugsatfda_docs/nda/99/020702-S018_Lipitor%20Tablets_approv.pdf)
* **NDA 020702/S-073 (Approved April 12, 2019):** Modern prior approval supplement updating protease inhibitor drug interaction labeling.
  * [Download S-073 Approval Letter (PDF)](https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2019/020702Orig1s073ltr.pdf)
sources:
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4Ge-g-QbA5g-PVkFSQLU1EUDTTZ7xBFfQjc-BHTYH27zK6mEM9Mod-fZQjink1BBL40B1g5x_4tXE0bN-Cb7842ZfnlQKJFDaq1f2C633BooBh_e9icQ8MT5nXGsd70BpYXH5EUEfy68R5EIFV0ASm_BWMZFKBwjAUs7ZPsVl9No176xpIn4q6WU=>
  - healthrx.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaEkemwwYvgVjZo1g3qEXxppXXcXre2_5fhIfcsDLD0D1pC97G9YsXFoZEAfKdfc3YwuNkcBRnjz8zMl3-NOUsVu08u46Hx7m5IiMKHUeQhycV-AEgnaJ7GFLzRRn1bc9Nmozot-ZnSNFsdL7Z3t0qaQZj87eP>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGZtzTXFYDssVccCeqDpu0iyHzCF1xHx4thgov2nbWPHUcWGegEogP6VvSkY5KrCW229X1k3ERVoSMxtqJSMTks17T79YajhgfuKaoNFl3XbOo2ueIrhyWvWB3mgMBBCst-rReUEo0PUh7L1V_T9gsa8REPpU-BfWMrG7trpg9I3xKZGw==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5hNxuYCDgFOEMmPAl4XQYVB2ZdGlVeldOlmBeQogLsKSLIlQ8UfhixzHHEclfb31Oflmjpt1J2GPtkquZY7txBVMRZOAJXc3ngxnME-oN7mrLHNyOXn1V8v_WWjApw94nlOtL4WklDArO2bWrSCFq0e67Di76r5dSSzfAvPHXkVaNvQ==>
  - fda.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH96fu0NaD77gsODVdo_9fAEc9zEovwtdBMZnGTps8T57CwVTLG_SBZmDXllp2n9xvgGWvKly3-UeDD7PNNi7tDz_LPqQd6hpeb-za8yAMtLzH2bLeY4ZOvRX7Qd1uFP6v4rEX4tL21p1P1TV0il0YrdL3B7dZM9r19N00Ja0hz0kecZkQ=>
```

</details>

**Answer:**

No reference files were attached to this conversation, so this answer is based entirely on public sources retrieved by the Network Search Agent.

## Answer

**Original developer:** **Warner‑Lambert / Parke‑Davis** — the molecule (internally code‑named **CI‑981**) was synthesized in **1985** by medicinal chemist Dr. Bruce Roth at the **Parke‑Davis Pharmaceutical Research** division in Ann Arbor, Michigan. Parke‑Davis filed the composition‑of‑matter patent in 1986 (U.S. Patent 4,681,893, issued 1987).

**FDA approval year: 1996** — specifically **December 17, 1996**.

### Key facts

| Item | Detail |
|---|---|
| Drug | Lipitor (atorvastatin calcium) tablets |
| Molecule discovery | 1985, Parke‑Davis (Warner‑Lambert) |
| NDA number | 020702 |
| Sponsor of record | Parke‑Davis Pharmaceutical Research (Warner‑Lambert) |
| NDA submitted | June 17, 1996 |
| **FDA approval** | **December 17, 1996** |
| U.S. launch | Early 1997 |

### Why the company name can be confusing

The molecule's owner changed hands after approval, which is why "Pfizer" is often (incorrectly) named as the developer:

- **1996** – Warner‑Lambert/Parke‑Davis signed a **co‑marketing agreement with Pfizer** (Warner‑Lambert lacked the sales force to compete with Merck's statins).
- **2000** – Pfizer **acquired Warner‑Lambert** (hostile takeover, ~$90 billion, closing June 2000), thereby becoming the brand owner/marketer of Lipitor.

So: **developed by Warner‑Lambert/Parke‑Davis; marketed today by Pfizer.**

### Sources actually retrieved

The search agent reported that the search tool returned **opaque redirect links** rather than clean canonical URLs, plus these domains: **FDA (fda.gov)**, **govinfo.gov**, **NIH (nih.gov)**, **Wikipedia**, drugs.com, newdrugapprovals.org, gene.com, researchgate.net, substack.com.

FDA resources surfaced inside the retrieved content (verifiable directly):
- Drugs@FDA search portal (search NDA **020702**): https://www.accessdata.fda.gov/scripts/cder/daf/
- Example NDA 020702 documents:
  - https://www.accessdata.fda.gov/drugsatfda_docs/nda/98/020702_S003_LIPITOR%20TABLETS.pdf
  - https://www.accessdata.fda.gov/drugsatfda_docs/appletter/2019/020702Orig1s073ltr.pdf

### Limitations to note

- The retrieved links were mostly **redirect URLs**, not clean citable sources — I have reported them as received rather than fabricating canonical citations.
- The FDA does **not publish original approval letters for pre‑1998 NDAs**, so the **December 17, 1996** date is corroborated via Drugs@FDA records and secondary sources (Wikipedia, NIH, govinfo, industry sites) rather than a downloadable original letter. A FOIA request would be needed for the primary document.

If you'd like, I can pull the internal records for any atorvastatin product in Wohua's database (inventory/sales) or check the RAGFlow knowledge base for related internal documents.

---

## 22. web-06 (web, easy)

**Question:** Which generation of cephalosporin is ceftriaxone?

**Gold answer:** Third generation.

**Route:** expected ['internet']; delegated {'Database Query Agent': 1, 'Network Search Agent': 1, 'RAGFlow Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[1] tool ls returned:
No files found

[2] tool glob returned:
No files found

[6] tool list_collections returned:
Found collections: sales_records,inventory,drugs

[7] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "generic_name": {"types": [{"bsonType": "String"}]}, "brand_name": {"types": [{"bsonType": "String"}]}, "approval_number": {"types": [{"bsonType": "String"}]}, "specifications": {"types": [{"bsonType": "String"}]}, "dosage_form": {"types": [{"bsonType": "String"}]}, "manufacturer": {"types": [{"bsonType": "String"}]}, "therapeutic_area": {"types": [{"bsonType": "String"}]}, "description": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[8] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e1"}, "drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "approval_number": "H10920012", "specifications": "1.0g/vial", "dosage_form": "Injection", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "For lower respiratory tract, urinary tract, and biliary infections caused by susceptible pathogens, as well as intra-abdominal infections, pelvic infections, skin and soft tissue infections, bone and joint infections, sepsis, meningitis, and more."}], "queryResultsCount": 1, "appliedLimits": []}

[9] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "sale_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "sale_date": {"types": [{"bsonType": "Date"}]}, "quantity_sold": {"types": [{"bsonType": "Number"}]}, "unit_price": {"types": [{"bsonType": "Number"}]}, "total_amount": {"types": [{"bsonType": "Number"}]}, "customer_name": {"types": [{"bsonType": "String"}]}, "region": {"types": [{"bsonType": "String"}]}, "sales_rep": {"types": [{"bsonType": "String"}]}}, "fieldsCount": 10}

[10] tool get_collection_schema returned:
{"schema": {"_id": {"types": [{"bsonType": "ObjectId"}]}, "inventory_id": {"types": [{"bsonType": "Number"}]}, "drug_id": {"types": [{"bsonType": "Number"}]}, "batch_number": {"types": [{"bsonType": "String"}]}, "quantity_on_hand": {"types": [{"bsonType": "Number"}]}, "warehouse_location": {"types": [{"bsonType": "String"}]}, "production_date": {"types": [{"bsonType": "Date"}]}, "expiry_date": {"types": [{"bsonType": "Date"}]}}, "fieldsCount": 8}

[11] knowledge base 'RAG Mini Wikipedia Assistant' answered:
The answer you are looking for is not found in the dataset!
retrieved chunks:
  - (rag_mini_wikipedia_0901-1000.txt) 
[[passage 971]] Taxonomy: Clarke et al. (2003) and Ksepka et al. (2006) apply the phylogenetic taxon Spheniscidae what here is referred to as Spheniscinae. Furthermore, they restrict the phylogenetic taxon Sphenisciformes to flightless taxa, and establish (Clarke et al. 2003) the phylogenetic taxon Pansphenisciformes as equivalent to the Linnean taxon Sphenisciformes, i.e., including any flying basal "proto-penguins" to be discovered eventually. Given that neither the relationships of the penguin subfamilies to each other nor the placement of the penguins in the avian phylogeny is presently resolved, this seems spurious and in any case is confusing; the established Linnean system is thus followed here.
  - (rag_mini_wikipedia_2401-2500.txt) 
[[passage 2441]] Research in this field is often published in peer-reviewed journals specific to the field of coleopterology, though journals dealing with general entomology also publish many papers on various aspects of beetle biology. Some of the journals specific to beetle research are:
[[passage 2442]] There is a thriving industry in the collection of beetle specimens for amateur and professional collectors. Many coleopterists prefer to collect beetle specimens for themselves, recording detailed information about each specimen and its habitat. Such collections add to the body of knowledge about the Coleoptera. Some countries have established laws governing or prohibiting the collection of certain rare (and often much sought after) species. One such beetle whose collection is illegal or restricted is the American burying beetle, Nicrophorus americanus.
  - (rag_mini_wikipedia_1401-1500.txt) 
[[passage 1405]] In the early research, Tesla devised several experimental setups to produce X-rays. Tesla held that, with his circuits, the "instrument will [... enable one to] generate Roentgen rays of much greater power than obtainable with ordinary apparatus." N. Tesla, "High frequency oscillators for electro-therapeutic and other purposes". Proceedings of the American Electro-Therapeutic Association, American Electro-Therapeutic Association. Page 25.
[[passage 1406]] He also commented on the hazards of working with his circuit and single node X-ray producing devices. Of his many notes in the early investigation of this phenomenon, he attributed the skin damage to various causes. One of the options for the cause, which is not in conformity with current facts, was that the ozone generated rather than the radiation was responsible. He early on stated,
  - (rag_mini_wikipedia_2301-2400.txt) 
[[passage 2377]] Beetles are a group of insects which have the largest number of species. They are placed in the order Coleoptera,which means "sheathed wing" and contains more described species than in any other order in the animal kingdom, constituting about twenty-five percent of all known life-forms. James K. Liebherr and Joseph V. McHugh in Resh, V. H. & R. T. CardÃ© (Editors) 2003. Encyclopedia of Insects. Academic Press. Forty percent of all described insect species are beetles (about 350,000 species ), and new species are frequently discovered. Estimates put the total number of species, described and undescribed, at between 5 and 8 million.
  - (rag_mini_wikipedia_0801-0900.txt) 
[[passage 850]] First built in the third or fourth century AD, the Hanging Church is Cairo's most famous Coptic church.
[[passage 851]] The Thirtieth Dynasty was the last native ruling dynasty during the Pharaonic epoch. It fell to the Persians in 343 BC after the last native Pharaoh, King Nectanebo II, was defeated in battle. Later, Egypt fell to the Greeks and Romans, beginning over two thousand years of foreign rule.
[[passage 852]] Before Egypt became part of the Byzantine realm, Christianity had been brought by Saint Mark the Evangelist in the AD first century. Diocletian's reign marked the transition from the Roman to the Byzantine era in Egypt, when a great number of Egyptian Christians were persecuted. The New Testament had by then been translated into Egyptian. After the Council of Chalcedon in AD 451, a distinct Egyptian Coptic Church was firmly established. Kamil, Jill. Coptic Egypt: History and Guide. Cairo: American University in Cairo, 1997. p. 39
  - (rag_mini_wikipedia_1401-1500.txt) 
[[passage 1404]] In April of 1887, Tesla began investigating what would later be called X-rays using his own single node vacuum tubes (similar to his patent ). This device differed from other early X-ray tubes in that they had no target electrode. The modern term for the phenomenon produced by this device is bremsstrahlung (or braking radiation). We now know that this device operated by emitting electrons from the single electrode through a combination of field emission and thermionic emission. Once liberated, electrons are strongly repelled by the high electric field near the electrode during negative voltage peaks from the oscillating HV output of the Tesla Coil, generating X-rays as they collide with the glass envelope. He also used Geissler tubes. By 1892, Tesla became aware of what Wilhelm RÃ¶ntgen later identified as effects of X-rays.

[12] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf438cb80345c4698030e"}, "sale_id": 11, "drug_id": 6, "sale_date": {"$date": "2025-05-20T00:00:00.000Z"}, "quantity_sold": 500, "unit_price": 12, "total_amount": 6000, "customer_name": "Wuhan Tongji Hospital", "region": "Central China", "sales_rep": "Wuhan Hankou Sales Dept."}, {"_id": {"$oid": "6aabf438cb80345c4698030f"}, "sale_id": 12, "drug_id": 6, "sale_date": {"$date": "2025-07-15T00:00:00.000Z"}, "quantity_sold": 600, "unit_price": 12, "total_amount": 7200, "customer_name": "Changsha Xiangya Hospital", "region": "Central China", "sales_rep": "Changsha Kaifu Sales Dept."}], "queryResultsCount": 2, "appliedLimits": []}

[13] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802f5"}, "inventory_id": 16, "drug_id": 6, "batch_number": "MY-250101-A", "quantity_on_hand": 2000, "warehouse_location": "Tianjin Warehouse 2 - Cool Storage", "production_date": {"$date": "2025-01-01T00:00:00.000Z"}, "expiry_date": {"$date": "2027-01-01T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f6"}, "inventory_id": 17, "drug_id": 6, "batch_number": "MY-250615-B", "quantity_on_hand": 3500, "warehouse_location": "Beijing Warehouse 2 - Cool Storage", "production_date": {"$date": "2025-06-15T00:00:00.000Z"}, "expiry_date": {"$date": "2027-06-14T00:00:00.000Z"}}, {"_id": {"$oid": "6aabf437cb80345c469802f7"}, "inventory_id": 18, "drug_id": 6, "batch_number": "MY-251120-C", "quantity_on_hand": 5000, "warehouse_location": "Tianjin Warehouse 1 - Cool Storage", "production_date": {"$date": "2025-11-20T00:00:00.000Z"}, "expiry_date": {"$date": "2027-11-19T00:00:00.000Z"}}], "queryResultsCount": 3, "appliedLimits": []}

[14] tool find_documents returned:
{"documents": [{"drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "therapeutic_area": "Antibiotic", "description": "For lower respiratory tract, urinary tract, and biliary infections caused by susceptible pathogens, as well as intra-abdominal infections, pelvic infections, skin and soft tissue infections, bone and joint infections, sepsis, meningitis, and more."}], "queryResultsCount": 1, "appliedLimits": []}

[15] knowledge base 'Drug Labels Assistant' answered:
The answer you are looking for is not found in the dataset!

Regarding the specific terms you mentioned:

- **"ceftriaxone"** — This exact term does not appear anywhere in the provided knowledge base.
- **"第三代头孢" (third-generation cephalosporin)** — This term and its English equivalents ("third-generation cephalosporin") do not appear in the knowledge base.
- **"cephalosporin"** — The term "cephalosporin" does appear, but only in two limited contexts:

1. **Contraindications section** [ID:3]: "AMOXIL is contraindicated in patients who have experienced a serious hypersensitivity reaction (e.g., anaphylaxis or Stevens-Johnson syndrome) to AMOXIL or to other β-lactam antibiotics (e.g., penicillins and cephalosporins)." This is a general reference to the β-lactam class, not to ceftriaxone specifically, and does not include any generation classification.

2. **References section** [ID:1]: "Swanson-Biearman B, Dean BS, Lopez G, Krenzelok EP. The effects of penicillin and cephalosporin ingestions in children less than six years of age. Vet Hum Toxicol. 1988; 30: 66-67." This is a bibliographic citation for a toxicology study, not a description of ceftriaxone's generation, indications, spectrum, or classification.

The knowledge base does contain information on "cephalosporin" only as part of a hypersensitivity contraindication warning and as a reference title, but it provides **no information about which generation ceftriaxone belongs to, no ceftriaxone indications, no ceftriaxone spectrum of activity, and no ceftriaxone drug classification**.

The document title for both mentions is **50542s02950754s01950760s01950761s016lbl.pdf**.

A summary of what the knowledge base actually addresses:
- It is primarily an **amoxicillin (AMOXIL)** prescribing information label [ID:3][ID:4].
- It covers amoxicillin's dosage forms (capsules, tablets, oral suspension) [ID:3], contraindications for β-lactam hypersensitivity [ID:3], warnings/precautions including anaphylaxis, CDAD, drug-resistant bacteria, and mononucleosis [ID:3][ID:5], pharmacokinetics [ID:4], and microbiology/susceptibility testing for organisms such as *H. pylori*, *E. coli*, *H. influenzae*, and *P. mirabilis* [ID:0][ID:2].
- Clinical studies focus on *H. pylori* eradication to reduce duodenal ulcer recurrence using amoxicillin with clarithromycin and lansoprazole [ID:0].

In short: **The exact information you requested about ceftriaxone and third-generation cephalosporins is not found in the dataset.**
retrieved chunks:
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
SusceptibilityTesting for Helicobacter pylori
Amoxicillin in vitro susceptibility testing methods for determining minimum inhibitory concentrations (MICs) and zone sizes have not been standardized, validated, or approved for testing H. pylori. Specimens for H. pylori and clarithromycin susceptibility test results should be obtained on isolates from patients who fail triple therapy. If clarithromycin resistance is found, a non-clarithromycin-containing regimen should be used.
Quality Control:
Standardized susceptibility test procedures 234 require use of laboratory controls to monitor and ensure the accuracy and precision of the supplies and reagents used in the assay, and the techniques of the individuals performing the test control. Standard amoxicillin powder should provide the following range of MIC values provided in Table 54. For the diffusion technique the criteria provided in Table 5 should be achieved.
b ATCC = American Type Culture Collection
Thislabel may notbethe latest approved byFDA For current labeling information,pleasevisit https://www.fda.gov/drugsatfda
13NONCLINICAL TOXICOLOGY
13.1Carcinogenesis, Mutagenesis, Impairment of Fertility
Long-term studies in animals have not been performed to evaluate carcinogenic potential. Studies to detect mutagenic potential of amoxicillin alone have not been conducted; however, the following information is available from tests on a 4:1 mixture of amoxicillin and potassium clavulanate (AUGMENTIN). AUGMENTIN was non-mutagenic in the Ames bacterial mutation assay, and the yeast gene conversion assay. AUGMENTIN was weakly positive in the mouse lymphoma assay, but the trend toward increased mutation frequencies in this assay occurred at doses that were also associated with decreased cell survival. AUGMENTIN was negative in the mouse micronucleus test and in the dominant lethal assay in mice. Potassium clavulanate alone was tested in the Ames bacterial mutation assay and in the mouse micronucleus test, and was negative in each of these assays. In a multi-generation reproduction study in rats, no impairment of fertility or other adverse reproductive effects were seen at doses up to 500 mg/kg (approximately 2 time the 3 g human dose based on body surface area).
14CLINICAL STUDIES
14.1
H. pylori Eradication to Reduce the Risk of Duodenal Ulcer Recurrence Randomized, double-blind clinical studies performed in the United States in patients with H. pylori and duodenal ulcer disease  (defined as an active ulcer or history of an ulcer within 1 year) evaluated the efficacy of lansoprazole in combination with amoxicillin capsules and clarithromycin tablets as triple 14-day therapy, or in combination with amoxicillin capsules as dual 14-day therapy, for the eradication of H. pylori. Based on the results of these studies, the safety and efficacy of 2 different eradication regimens  were  established:   Triple therapy:  Amoxicillin 1  gram  twice  daily/clarithromycin  500 mg twice daily/lansoprazole 30 mg twice daily (see Table 6). Dual therapy: Amoxicillin 1 gram three times daily/lansoprazole 30 mg three times daily (see Table 7. All treatments were for 14 days. H. pylori eradication was defined as 2 negative tests (culture and histology) at 4 to 6 weeks following the end of treatment. Triple therapy was shown to be more effective than all possible dual therapy combinations. Dual therapy was shown to be more effective than both monotherapies. Eradication of H. pylori has been shown to reduce the risk of duodenal ulcer recurrence.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
This label may notbethe latest approved by FDA For current labeling information, please visit https://www.fda.gov/drugsatfda
Patients were included in the analysis if they completed the study. Additionally, if patients dropped out of the study due to an adverse event related to the study drug, they were included in the analysis as failures of therapy.
b Patients were included in the analysis if they had documented H. pylori infection at baseline as defined above and had a confirmed duodenal ulcer (active or within 1 year). All dropouts were included as failures of therapy.
This analysis was based on evaluable patients with confirmed duodenal ulcer (active or within 1 year) and H. pylori
infection at baseline defined as at least 2 of 3 positive endoscopic tests from CLOtest , histology, and/or culture.
Patients were included in the analysis if they completed the study. Additionally, if patients dropped out of the study due
 to an adverse event related to the study drug, they were included in the analysis as failures of therapy.
Patients were included in the analysis if they had documented H. pylori infection at baseline as defined above and had a confirmed duodenal ulcer (active or within 1 year). All dropouts were included as failures of therapy.
REFERENCES15
Swanson-Biearman B, Dean BS, Lopez G, Krenzelok EP. The effects of penicillin and cephalosporin ingestions in1.S children less than six years of age. Vet Hum Toxicol. 1988; 30: 66-67.
2. Clinical and Laboratory Standards Institute (CLSI). Methods for Dilution Antimicrobial Susceptibility Tests for Bacteria that Grow Aerobically; Approved Standard - Tenth Edition. CLSI document Mo7-Aio, Clinical and Laboratory Standards Institute, 950 West Valley Road, Suite 2500, Wayne, Pennsylvania 19087, USA, 2015.
Clinical and  Laboratory Standards  Institute (CLSI).  Performance Standards for Antimicrobial Disk Diffusion3.
Susceptibility Tests; Approved Standard - Twelfth Edition. CLSI document M02-A12, Clinical and Laboratory Standards Institute, 950 West Valley Road, Suite 2500, Wayne, Pennsylvania 19087, USA, 2015.
4. Clinical and Laboratory Standards Institute (CLsI). Performance Standards for Antimicrobial Susceptibility Testing; Twenty-fifth Informational Supplement, CLSI document M100-S25. CLSI document M100-S25, Clinical and Laboratory Standards Institute, 950 West Valley Road, Suite 2500, Wayne, Pennsylvania 19087, USA, 2015.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
Thislabel maynotbethe latestapprovedbyFDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Gram-NegativeBacteria
Escherichiacoli Haemophilusinfluenzae Helicobacterpylori Proteusmirabilis
Susceptibility Test Methods:
When available, the clinical microbiology laboratory should provide cumulative in vitro susceptibility test results for antimicrobial drugs used in local hospitals and practice areas to the physician as periodic reports that describe the susceptibility profile of nosocomial and community-acquired pathogens. These reports should aid the physician in selecting the most effective antimicrobial.
Dilution Techniques: Quantitative methods are used to determine antimicrobial minimum inhibitory concentrations (MICs). These MICs provide estimates of the susceptibility of bacteria to antimicrobial compounds. The MICs should be determined using a standardized test method -(broth or agar)24. The MIC values should be interpreted according to thecriteriainTable 4.
Diffusion Techniques: Quantitative methods that require measurement of zone diameters can also provide reproducible estimates of the susceptibility of bacteria to antimicrobial compounds34. The zone size should be determined using a standardized test method'.
Susceptibility to amoxicillin of Enterococus spp., Enterobacteriaceae, and H. influenzae, may be infered by testing ampicillin. Susceptibility to amoxicillin of Staphylococcus spp., and beta-hemolytic Streptococcus spp., may be inferred by testing penicillin*. The majority of isolates of Enterococcus spp. that are resistant to ampicillin or amoxicillin produce a TEM-type beta-lactamase. A beta-lactamase test can provide a rapid means of determining resistance to ampicillin and amoxicillin4.
Susceptibility to amoxicillin of Streptococcus pneumoniae (non-meningitis isolates) may be inferred by testing penicillin or oxacillin. The interpretive criteria for S. pneumoniae to amoxicillin are provided in Table 44.
This label maynotbethelatest approvedbyFDA For current labeling information, please visit https://www.fda.gov/drugsatfda
A report of “Susceptible” indicates the antimicrobial is likely to inhibit growth of the pathogen if the antimicrobial compound reaches a concentration at the infection site necessary to inhibit growth of the pathogen. A report of “Intermediate” indicates that the result should be considered equivocal, and, if the microorganism is not fully susceptible to alternative, clinically feasible drugs, the test should be repeated. This category implies possible clinical applicability in body sites where the drug is physiologically concentrated. This category also provides a buffer zone that prevents small uncontrolled technical factors from causing major discrepancies in interpretation. A report of "Resistant’ indicates the antimicrobial is not likely to inhibit growth of the pathogen if the antimicrobial compound reaches the concentration usually achievable at the infection site; other therapy should be selected.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
3
Capsules: 250 mg, 500 mg. Each capsule of AMOXIL, with royal blue opaque cap and pink opaque body, contains 250 mg or 500 mg amoxicillin as the trihydrate. The cap and body of the 250-mg capsule are imprinted with the product name AMOXIL and 250; the cap and body of the 500 mg capsule are imprinted with AMOXIL and 500.
Tablets: 500 mg, 875 mg. Each tablet contains 500 mg or 875 mg amoxicillin as the trihydrate. Each film-coated, capsule-shaped, pink tablet is debossed with AMOXIL centered over 500 or 875, respectively. The 875-mg tablet is scored on the reverse side.
Powder for Oral Suspension: 125 mg/5 mL, 200 mg/5 mL, 250 mg/5 mL, 400 mg/5 mL. Each 5 mL of reconstituted strawberry-flavored suspension contains 125 mg amoxicillin as the trihydrate. Each 5 mL of reconstituted bubble-gum- flavored suspension contains 200 mg, 250 mg or 400 mg amoxicillin as the trihydrate.
CONTRAINDICATIONS
4
AMOXIL is contraindicated in patients who have experienced a serious hypersensitivity reaction (e.g., anaphylaxis or Stevens-Johnson syndrome) to AMOXIL or to other β-lactam antibiotics (e.g., penicillins and cephalosporins).
5
WARNINGSANDPRECAUTIONS
5.1Anaphylactic Reactions
Serious and occasionally fatal hypersensitivity (anaphylactic) reactions have been reported in patients on penicillin therapy including amoxicillin. Although anaphylaxis is more frequent following parenteral therapy, it has occurred in patients on oral penicillins. These reactions are more likely to occur in individuals with a history of penicillin hypersensitivity and/or a history of sensitivity to multiple allergens. There have been reports of individuals with a history of penicillin hypersensitivity who have experienced severe reactions when treated with cephalosporins. Before initiating therapy with AMOXIL, careful inquiry should be made regarding previous hypersensitivity reactions to penicillins, cephalosporins, or other allergens.
5.2Clostridium difficile Associated Diarrhea
Clostridium difficile associated diarrhea (CDAD) has been reported with use of nearly all antibacterial agents, including AMOXIL, and may range in severity from mild diarrhea to fatal colitis. Treatment with antibacterial agents alters the normal flora of the colon leading to overgrowth of C. difficile.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
Mean amoxicillin pharmacokinetic parameters from an open, two-part, single-dose crossover bioequivalence study in 27 adults comparing 875 mg of AMOXIL with 875 mg of AUGMENTIN° (amoxicillin/clavulanate potassium) showed that the 875-mg tablet of AMOXIL produces an AUCo-o of 35.4 ± 8.1 mcgohr/mL and a Cmax of 13.8 ± 4.1 mcg/mL.
Dosing was at the start of a light meal following an overnight fast.
Orally administered doses of amoxicillin suspension, 125 mg/5 mL and 250 mg/5 mL, result in average peak blood levels 1 to 2 hours after administration in the range of 1.5 mcg/mL to 3.0 mcg/mL and 3.5 mcg/mL to 5.0 mcg/mL, respectively.
Oral administration of single doses of 400-mg chewable tablets and 400 mg/5 mL suspension of AMOXIL to 24 adult volunteers yielded comparable pharmacokinetic data:
This label may not be the latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Administered at the start of a light meal.
 Mean values of 24 normal volunteers. Peak concentrations occurred approximately 1 hour after the dose.
Distribution: Amoxicillin diffuses readily into most body tissues and fluids, with the exception of brain and spinal fluid, except when meninges are inflamed. In blood serum, amoxicillin is approximately 20% protein-bound. Following a 1-gram dose and utilizing a special skin window technique to determine levels of the antibiotic, it was noted that therapeutic levels were found in the interstitial fluid.
Metabolism and Excretion: The half-life of amoxicillin is 61.3 minutes. Approximately 60% of an orally administered dose of amoxicillin is excreted in the urine within 6 to 8 hours. Detectable serum levels are observed up to 8 hours after an orally administered dose of amoxicillin. Since most of the amoxicillin is excreted unchanged in the urine, its excretion can be delayed by concurrent administration of probenecid [see DRUG INTERACTIONS (7.1)].
Microbiology12.4
Mechanism of Action
Amoxicillin is similar to penicillin in its bactericidal action against susceptible bacteria during the stage of active multiplication. It acts through the inhibition of cell wall biosynthesis that leads to the death of the bacteria.
  - (50542s02950754s01950760s01950761s016lbl.pdf) 
C. difficile produces toxins A and B which contribute to the development of CDAD. Hypertoxin-producing strains of C. difficile cause increased morbidity and mortality, as these infections can be refractory to antimicrobial therapy and may require colectomy. CDAD must be considered in all patients who present with diarrhea following antibacterial use.
This label may not bethe latest approved by FDA.
For current labeling information, please visit https://www.fda.gov/drugsatfda
Careful medical history is necessary since CDAD has been reported to occur over 2 months after the administration of antibacterial agents.
If CDAD is suspected or confirmed, ongoing antibiotic use not directed against C. difficile may need to be discontinued. Appropriate fluid and electrolyte management, protein supplementation, antibiotic treatment of C. difficile, and surgical evaluation should be instituted as clinically indicated.
5.3
Development of Drug-Resistant Bacteria
Prescribing AMOXIL in the absence of a proven or strongly suspected bacterial infection is unlikely to provide benefit to the patient and increases the risk of the development of drug-resistant bacteria
Use in Patients With Mononucleosis
5.4
A high percentage of patients with mononucleosis who receive amoxicillin develop an erythematous skin rash. Thus amoxicillin should not be administered to patients with mononucleosis.
5.5
Phenylketonurics
Amoxil chewable tablets contain aspartame which contains phenylalanine. Each 200 mg chewable tablet contains 1.82 mg phenylalanine; each 400 mg chewable tablet contains 3.64 mg phenylalanine. The oral suspensions of Amoxil do not contain phenylalanine and can be used by phenylketonurics.
ADVERSE REACTIONS
The following are discussed in more detail in other sections of the labeling:
·Anaphylactic reactions [see Warnings and Precautions (5.1)] ·CDAD [see Warnings and Precautions (5.2)]
Clinical Trials Experience
6.1
Because clinical trials are conducted under widely varying conditions, adverse reaction rates observed in the clinical trials of a drug cannot be directly compared to rates in the clinical trials of another drug and may not reflect the rates observed in practice.
The most common adverse reactions (> 1%) observed in clinical trials of AMOXIL capsules, tablets or oral suspension were diarrhea, rash, vomiting, and nausea.

[16] tool count_documents returned:
{"count": 3}

[17] tool find_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e1"}, "drug_id": 6, "generic_name": "Ceftriaxone Sodium for Injection", "brand_name": "Rocephin", "approval_number": "H10920012", "specifications": "1.0g/vial", "dosage_form": "Injection", "manufacturer": "Our Pharmaceutical Co.", "therapeutic_area": "Antibiotic", "description": "For lower respiratory tract, urinary tract, and biliary infections caused by susceptible pathogens, as well as intra-abdominal infections, pelvic infections, skin and soft tissue infections, bone and joint infections, sepsis, meningitis, and more."}], "queryResultsCount": 1, "appliedLimits": []}

[18] tool count_documents returned:
{"count": 2}

[19] tool aggregate_documents returned:
{"documents": [{"_id": {"$oid": "6aabf437cb80345c469802e5"}, "keys": ["_id", "drug_id", "generic_name", "brand_name", "approval_number", "specifications", "dosage_form", "manufacturer", "therapeutic_area", "description"]}, {"_id": {"$oid": "6aabf437cb80345c469802df"}, "keys": ["_id", "drug_id", "generic_name", "brand_name", "approval_number", "specifications", "dosage_form", "manufacturer", "therapeutic_area", "description"]}, {"_id": {"$oid": "6aabf437cb80345c469802e4"}, "keys": ["_id", "drug_id", "generic_name", "brand_name", "approval_number", "specifications", "dosage_form", "manufacturer", "therapeutic_area", "description"]}, {"_id": {"$oid": "6aabf437cb80345c469802dd"}, "keys": ["_id", "drug_id", "generic_name", "brand_name", "approval_number", "specifications", "dosage_form", "manufacturer", "therapeutic_area", "description"]}, {"_id": {"$oid": "6aabf437cb80345c469802de"}, "keys": ["_id", "drug_id", "generic_name", "brand_name", "approval_number", "specifications", "dosage_form", "manufacturer", "therapeutic_area", "description"]}], "count": 5, "appliedLimits": []}

[20] web search for 'MedlinePlus ceftriaxone third generation cephalosporin antibiotic'; grounded search summary:
An overview of **ceftriaxone injection** based on information from **MedlinePlus** (a service of the National Library of Medicine) covers the essential facts regarding its class, uses, administration, and safety:

---

### What is Ceftriaxone?
* **Drug Class:** Third-generation cephalosporin antibiotic.
* **Common Brand Name:** Rocephin (discontinued brand in the U.S., but generic forms are widely used).
* **How it works:** It works by interfering with the formation of the bacterial cell wall, killing susceptible bacteria. Like all antibiotics, ceftriaxone **does not** work against viral infections such as colds or the flu.

---

### Why is it Prescribed?
Ceftriaxone is used to treat a wide variety of bacterial infections, including:
* **Lower respiratory tract infections** (e.g., pneumonia)
* **Central nervous system infections** (e.g., bacterial meningitis)
* **Sexually transmitted infections** (e.g., gonorrhea, pelvic inflammatory disease)
* **Urinary tract infections (UTIs)**
* **Skin, soft tissue, bone, and joint infections**
* **Intra-abdominal infections**
* **Bloodstream infections (sepsis/bacteremia)**
* **Surgical prophylaxis** (given before certain operations to prevent post-surgical infections)

---

### How is it Administered?
* Ceftriaxone is **not available in an oral form** (pills/liquids). 
* It is given as an injection:
  * **Intravenously (IV):** Infused into a vein over 30 to 60 minutes.
  * **Intramuscularly (IM):** Injected deep into a large muscle (often mixed with lidocaine to reduce injection pain).
* Dosing typically ranges from once to twice daily, depending on the severity and site of infection.

---

### Important Precautions & Warnings

1. **Allergies:** 
   * Inform your doctor of any allergies to cephalosporins, penicillins, or other beta-lactam antibiotics. Cross-reactivity can occur.
2. **Neonates & Calcium Interaction:** 
   * Ceftriaxone must **never** be administered simultaneously with intravenous calcium-containing products (such as Ringer’s lactate or TPN), especially in newborns/neonates, as it can cause fatal calcium-ceftriaxone precipitates in the lungs and kidneys.
   * It should not be given to premature or jaundiced neonates due to the risk of bilirubin encephalopathy (kernicterus).
3. ***Clostridioides difficile*-Associated Diarrhea:** 
   * Ceftriaxone can alter normal bowel flora, leading to overgrowth of *C. difficile*. Watery or bloody stools (even weeks after stopping the drug) require immediate medical attention.
4. **Gallbladder / Biliary Sludge:** 
   * Ceftriaxone is largely cleared via bile, which can occasionally precipitate and form "biliary sludge" or pseudolithiasis, usually resolving after treatment ends.
5. **Kidney and Liver Health:**
   * Dose adjustments may be needed in patients with severe combined renal and hepatic impairment.

---

### Side Effects

#### Common Side Effects:
* Pain, swelling, or redness at the injection site
* Mild diarrhea, nausea, or vomiting
* Headache or dizziness
* Mild skin rash or itching

#### Serious Side Effects (Contact a Doctor Immediately):
* **Allergic reactions:** Hives, facial/throat swelling, difficulty breathing, or severe peeling skin rash (e.g., Stevens-Johnson syndrome).
* **Severe diarrhea:** Watery or bloody stools, abdominal cramping, or fever (symptoms of *C. diff* colitis).
* **Biliary/Liver issues:** Yellowing of the skin or eyes (jaundice), dark urine, upper right stomach pain.
* **Kidney issues:** Sudden decrease in urine output or blood in the urine.
* **Neurological effects:** Confusion, encephalopathy, or seizures (more common with excessive doses in impaired renal function).
sources:
  - medlineplus.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFm6-xl183srMcxi_hthUjw-eKLdakPeGeIkS0yXprN478W1TmPUHfAmtpQru856uXzjb3rECsUeDdHLiyoWkChQtLgcpGXZFy7HPqFbTcs0fuLQKea8sJwYzw19CSrqrRIzGeobidl4A==>
  - clevelandclinic.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHp5ka2gOAse1ZtbdcdO4Sfn8uqz03KGhg46bDiwDmc0AFcsOROJj7n7aZDthYUBke3-DSNFUhKL_RdaMRuIl7kuV_pHWVJ8CQ1pA7MXb0jXAccYORa8gfvWgi6zRNIScjEZiC0egU1hnY0z_Tmv2APWkKywKt6KH8mB6mRyA==>
  - mayoclinic.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCsuj4olQ0jucSyH3M3xDUKhVoDJpR6GTt1ktdkE4cXRhQDUqwxz5gWAkWgGWramzmMAKwn_L2_ou-sCHMklG0l5p93JSBpJK2q9FfjY83syXq3CXyLafVst9HX4Ns9x4XdBv2waabyS6qnUA7UeO_XV_AAUFY--CaxOSZnNr9XFbud7Btvit5Fr3TunSlquCWCNMFrfLL>
  - medlineplus.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyP-zx103MWcr_o_0UvdxvLZdu1eptF7IGT8ni4dhbxcWf3558Dyco1SfeXzL3g4mS2laZiDTeGPTKdIYGzun80uxK7p_fJgomi1T2jG-UZs3xf5LkNQ_korQJJkwErtFBAzBzUdocTA==>
  - cuh.nhs.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGfsBuGND0p2xzmm4thXUr1577FFfDVXzNl-gGA2Qi6730Mh913sTdsj_FbeOBrtSkoFrk4fFj9Y-iJBOnwC2rNmFngf-anpzn1_bigVWu258RzpIBP4VYaag7LhkfpSB3q4bcfw0KSu3gzWCRClG3xp7Khwu_VAlaKff1Z-RSUJYufX2k=>

[21] web search for 'ceftriaxone third generation cephalosporin classification spectrum of activity'; grounded search summary:
**Ceftriaxone** is a broad-spectrum, parenteral **third-generation cephalosporin** (a subclass of $\beta$-lactam antibiotics). 

Compared to first- and second-generation cephalosporins, third-generation agents feature **significantly expanded activity against Gram-negative bacteria**, enhanced resistance to many common $\beta$-lactamases, and superior penetration into the central nervous system (CNS), with a slight trade-off in potency against certain Gram-positive cocci (such as *Staphylococcus aureus*).

---

### 1. Mechanism of Action
* **Bactericidal:** Binds to and inhibits **penicillin-binding proteins (PBPs)** (primarily PBP-1a, PBP-1b, PBP-2, and PBP-3) involved in the terminal synthesis of the bacterial peptidoglycan cell wall.
* Inhibition of cell wall synthesis triggers bacterial autolytic enzymes, leading to cell lysis and death.

---

### 2. Spectrum of Activity

#### **A. Gram-Negative Pathogens (Major Strength)**
Ceftriaxone has potent activity against a wide range of aerobic and facultative Gram-negative bacteria:
* **Enterobacterales:**
  * Highly active against wild-type *Escherichia coli*, *Klebsiella pneumoniae*, and *Proteus mirabilis*.
  * Active against *Salmonella* spp. and *Shigella* spp. (first-line agent for severe enteric fever/typhoid).
  * Variable/risky against inducible AmpC producers (e.g., *Enterobacter*, *Citrobacter*, *Serratia*, *Providencia*) due to risk of selection for derepressed resistance mutants.
* **Respiratory Pathogens:**
  * *Haemophilus influenzae* (including $\beta$-lactamase–positive strains).
  * *Moraxella catarrhalis*.
* **Neisseria Species:**
  * *Neisseria meningitidis* (first-line/standard therapy for meningococcal disease).
  * *Neisseria gonorrhoeae* (first-line treatment for gonorrhea, administered IM as a single dose).

#### **B. Gram-Positive Pathogens (Moderate to Good)**
While 1st-generation cephalosporins (e.g., cefazolin) are generally more potent against staphylococci, ceftriaxone retains clinically useful Gram-positive coverage:
* **Streptococci:**
  * Excellent activity against *Streptococcus pyogenes* (Group A Strep) and *Streptococcus agalactiae* (Group B Strep).
  * *Streptococcus pneumoniae*: Active against penicillin-susceptible and many intermediate strains. (High-dose ceftriaxone is combined with vancomycin when resistant *S. pneumoniae* meningitis is suspected).
  * Viridans group streptococci.
* **Staphylococci:**
  * Active against Methicillin-Susceptible *Staphylococcus aureus* (MSSA) and coagulase-negative staphylococci, though anti-staphylococcal penicillins (e.g., oxacillin/nafcillin) or cefazolin are generally preferred.

#### **C. Spirochetes**
* *Borrelia burgdorferi* (agent of choice for disseminated or neurological Lyme disease).
* *Treponema pallidum* (neurosyphilis alternative in penicillin-allergic patients).

---

### 3. Critical Organisms NOT Covered (Notable Gaps)

Clinicians often use the acronym **LAME** for cephalosporin gaps, along with other notable exceptions:
* **L** – *Listeria monocytogenes* (inherently resistant to all cephalosporins; requires ampicillin).
* **A** – **Atypical pathogens** (*Mycoplasma pneumoniae*, *Chlamydia* spp., *Legionella pneumophila* — lack peptidoglycan cell walls or are obligate/facultative intracellular).
* **M** – **MRSA** (Methicillin-Resistant *Staphylococcus aureus*) and MRSE.
* **E** – *Enterococcus* species (*E. faecalis*, *E. faecium* — inherently resistant).
* ***Pseudomonas aeruginosa*:** Ceftriaxone has **no activity** against *P. aeruginosa* (unlike **ceftazidime** or **cefepime**).
* **Anaerobes:** Lacks reliable activity against intra-abdominal anaerobes like *Bacteroides fragilis* (requires addition of metronidazole).
* **ESBL Producers:** Inactive against Extended-Spectrum $\beta$-Lactamase–producing Enterobacterales (carbapenems typically required).

---

### 4. Key Distinguishing Pharmacologic Properties
* **Long Elimination Half-Life (~8 hours):** Allows for **once-daily** (or twice-daily for severe meningitis) dosing.
* **Dual Excretion:** Excreted roughly 40–60% via biliary/fecal routes and 40–60% renally. **No renal dose adjustment** is required for renal impairment alone.
* **Excellent CSF Penetration:** Effectively crosses inflamed meninges, making it a cornerstone for empiric bacterial meningitis therapy.
* **Adverse Event Note:** Can cause biliary sludging/pseudolithiasis and is contraindicated in neonates receiving IV calcium-containing products due to calcium-ceftriaxone precipitation risks.

---

### Summary of Primary Clinical Indications
1. **Community-Acquired Pneumonia (CAP):** Inpatient regimens (combined with a macrolide or doxycycline for atypicals).
2. **Bacterial Meningitis:** Empiric treatment (combined with vancomycin $\pm$ ampicillin).
3. **Sexually Transmitted Infections:** Uncomplicated and disseminated *N. gonorrhoeae*.
4. **Pyelonephritis / Complicated UTIs:** Caused by susceptible Gram-negative bacilli.
5. **Severe Lyme Disease:** Cardiac or neurologic manifestations.
6. **Intra-abdominal Infections:** In combination with an anti-anaerobic agent (e.g., metronidazole).
sources:
  (none)

[22] web search for 'WHO model list essential medicines ceftriaxone third generation cephalosporin'; grounded search summary:
On the **WHO Model List of Essential Medicines (EML)** and the **WHO Model List of Essential Medicines for Children (EMLc)**, **ceftriaxone** is listed as a vital antibacterial agent under the third-generation cephalosporin class. 

Key details regarding ceftriaxone on the WHO Model List:

---

### 1. Classification & Section
* **EML Category:** Section 6 (Anti-infective medicines) $\rightarrow$ Subsection 6.2 (Antibacterials) $\rightarrow$ 6.2.2 (Beta-lactam medicines).
* **Pharmacological Class:** Third-generation cephalosporin (broad-spectrum $\beta$-lactam antibiotic).
* **List Type:** **Core List** (essential for a basic healthcare system, prioritized based on disease prevalence, safety, efficacy, and comparative cost-effectiveness).

---

### 2. WHO AWaRe Classification: **"Watch" Group**
Under the WHO **AWaRe** (Access, Watch, Reserve) framework for antimicrobial stewardship:
* Ceftriaxone belongs to the **Watch** group.
* **Significance:** While critical as first- or second-choice empiric treatments for specific, severe clinical syndromes, Watch-group antibiotics have a higher potential for fostering antimicrobial resistance (e.g., extended-spectrum beta-lactamase [ESBL]-producing organisms). Their use is closely monitored and prioritized for antimicrobial stewardship programs.

---

### 3. Listed Formulations
* **Powder for injection:** 
  * 250 mg (as sodium salt) in vial
  * 1 g (as sodium salt) in vial
  *(Often also supplied as 500 mg or 2 g vials depending on the regional formulation and clinical context).*
* **Route:** Intravenous (IV) or Intramuscular (IM).

---

### 4. Key Indications Identified in WHO Guidelines
Ceftriaxone is included for the management of severe or specific systemic bacterial infections, including:
* **Central Nervous System:** Acute bacterial meningitis (empiric and definitive therapy).
* **Sexually Transmitted Infections:** Uncomplicated and complicated gonococcal infections (*Neisseria gonorrhoeae*).
* **Severe Systemic Infections:** Sepsis/septic shock, complicated intra-abdominal infections (often in combination with an antianaerobic agent like metronidazole).
* **Enteric Infections:** Typhoid / enteric fever (when fluoroquinolone resistance is suspected or confirmed).
* **Respiratory & Urinary:** Severe community-acquired pneumonia (hospitalized patients) and complicated pyelonephritis/urinary tract infections.
* **Pediatric Sepsis & Neonates:** Used cautiously in infants, with contraindications in hyperbilirubinemic neonates or when administered concurrently with calcium-containing IV solutions.
sources:
  (none)

[23] web search for 'DailyMed ceftriaxone injection FDA prescribing information label third generation cephalosporin'; grounded search summary:
Below is a structured clinical summary of the **FDA Prescribing Information label** for **Ceftriaxone Injection, USP** (a third-generation cephalosporin) as indexed on **DailyMed**.

---

### **1. Drug Overview & Classification**
* **Drug Name:** Ceftriaxone (as ceftriaxone sodium) for Injection
* **Pharmacologic Class:** Third-generation cephalosporin antibacterial
* **Route:** Intravenous (IV) or Intramuscular (IM)
* **Mechanism of Action:** Bactericidal agent that acts by inhibiting bacterial cell wall synthesis via binding to one or more penicillin-binding proteins (PBPs).

---

### **2. Indications and Usage**
Indicated for the treatment of infections caused by susceptible isolates of designated microorganisms in the following conditions:
* **Lower Respiratory Tract Infections** (e.g., pneumonia caused by *Streptococcus pneumoniae*, *Haemophilus influenzae*, *Klebsiella pneumoniae*)
* **Acute Bacterial Otitis Media** (pediatric single-dose IM regimen)
* **Skin and Skin Structure Infections** (e.g., *Staphylococcus aureus*, *Streptococcus pyogenes*)
* **Urinary Tract Infections (complicated and uncomplicated)**
* **Pelvic Inflammatory Disease (PID)** and **Uncomplicated Gonorrhea** (cervical/urethral and rectal)
* **Bacterial Septicemia**
* **Bone and Joint Infections**
* **Intra-abdominal Infections** (e.g., peritonitis)
* **Bacterial Meningitis** (e.g., *Neisseria meningitidis*, *S. pneumoniae*, *H. influenzae*)
* **Surgical Prophylaxis** (preoperative single dose to reduce the incidence of postoperative infections in contaminated or potentially contaminated procedures)

---

### **3. Dosage and Administration**
* **Adults:** 
  * Usual daily dose: **1 g to 2 g** administered once daily (or in equally divided doses twice daily, every 12 hours) depending on the type and severity of infection.
  * Maximum dose: **4 g per day** (often reserved for severe infections such as meningitis).
* **Pediatric Patients:**
  * **Meningitis:** 100 mg/kg/day (not to exceed 4 g daily) given once daily or divided q12h.
  * **Skin/Soft Tissue, other serious infections:** 50 to 75 mg/kg/day (not to exceed 2 g daily) divided q12h or once daily.
  * **Acute Otitis Media:** Single IM dose of 50 mg/kg (up to 1 g).
* **Renal / Hepatic Impairment:**
  * Generally no dosage adjustment is required for renal or hepatic impairment alone at doses up to 2 g/day.
  * In patients with both severe renal impairment and severe hepatic disease, close clinical monitoring is warranted; dosage should not exceed 2 g/day without monitoring of serum concentrations.
* **Administration & Compatibility Rules:**
  * **Do NOT use diluents containing calcium** (e.g., Ringer’s solution, Hartmann’s solution) to reconstitute ceftriaxone or to dilute it for IV administration.
  * Ceftriaxone and calcium-containing solutions must **not** be administered simultaneously via a Y-site.

---

### **4. Contraindications**
1. **Hypersensitivity:** Known allergy to ceftriaxone, any cephalosporin class antibacterial, or history of severe hypersensitivity (e.g., anaphylaxis) to any β-lactam.
2. **Hyperbilirubinemic Neonates:** Contraindicated in premature neonates up to a postmenstrual age of 41 weeks, and full-term neonates (≤28 days) with hyperbilirubinemia, jaundice, or acidosis (ceftriaxone can displace bilirubin from serum albumin, creating risk of kernicterus).
3. **Neonates Requiring Calcium:** Full-term neonates (≤28 days) if they require (or are expected to require) treatment with calcium-containing IV solutions (including continuous infusions like TPN) due to the risk of fatal precipitation of ceftriaxone-calcium salt in lungs and kidneys.

---

### **5. Warnings and Precautions**
* **Incompatibilities with Calcium-Containing Solutions:** Particulate precipitation can occur. Fatal reactions with ceftriaxone-calcium precipitates in lungs and kidneys have been reported in neonates. In patients >28 days, ceftriaxone and calcium-containing solutions may be administered sequentially if infusion lines are thoroughly flushed with a compatible fluid between infusions.
* **Neurological Adverse Reactions (Encephalopathy/Neurotoxicity):** Encephalopathy, myoclonus, chorea, and seizures have been reported, primarily in patients with renal impairment who received inappropriately high doses or when drug accumulates. Symptoms are usually reversible upon discontinuation.
* **Hypersensitivity / Anaphylactic Reactions:** Serious and occasionally fatal hypersensitivity reactions (anaphylaxis, DRESS, Stevens-Johnson syndrome, TEN) can occur.
* ***Clostridioides difficile*-Associated Diarrhea (CDAD):** Ranging from mild diarrhea to fatal colitis; must be considered in all patients presenting with diarrhea following antibiotic use.
* **Biliary / Gallbladder Pseudolithiasis (Sludge):** Ceftriaxone-calcium precipitates can form in the gallbladder/biliary tract, mimicking cholelithiasis on sonograms. Usually asymptomatic and reversible upon drug discontinuation.
* **Urolithiasis and Renal Impairment:** Reversible ceftriaxone-calcium precipitation in the urinary tract has been reported.
* **Hemolytic Anemia:** Severe immune-mediated hemolytic anemia (including fatal cases) has been observed.

---

### **6. Common Adverse Reactions**
* **Local reactions:** Pain, induration, or tenderness at the IM injection site; phlebitis or thrombophlebitis following IV infusion.
* **Hematologic:** Eosinophilia, thrombocytosis, leukopenia, neutropenia.
* **Gastrointestinal:** Diarrhea, loose stools, nausea, vomiting.
* **Hepatic/Renal:** Elevations in SGOT/AST, SGPT/ALT, BUN, or serum alkaline phosphatase.
* **Dermatologic:** Rash, pruritus.

---

### **7. Use in Specific Populations**
* **Pregnancy:** Ceftriaxone crosses the placenta. Available human data have not established an associated drug-related risk of major birth defects or miscarriage.
* **Lactation:** Present in human milk in low concentrations; exercise caution, but adverse effects on the breastfed infant are generally low.
* **Pediatrics:** Safety and effectiveness have been established for specified indications in pediatric patients (except hyperbilirubinemic neonates and neonates requiring calcium-containing IV fluids).
* **Geriatric Use:** Pharmacokinetics are generally comparable to healthy adults, but age-related renal function decline warrants monitoring when high doses are used.

*(Refer to the specific manufacturer's Package Insert on **DailyMed / U.S. National Library of Medicine** for full product-specific NDC lists, reconstitution volumes, and stability data.)*
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP8Yq7jNIhamX5K41vIxtV7Ffn7vRZeg3vqfWIeeRPIQazQEHcmaiXgCOJsKRntc08E0WYzJVIHm7y9jWofAxqRRJ8ejR3f8j-2dyHwlfbPKR3UF8vZyMBwNyAhHp4x4yWR8_7ZK-ev8MzTZf_OLntm6pjIYFLK0flYzLkN9XDsf1AubTfpUA6h8Agh8oid1-nFLzYP8xmcgzV46PdxhT9qCTileSY>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEewo7zgojDISBE0iwZVfs2cCbNtzTDAb7OMNGtRl6UsprDOLqF5qNmKJyk5DRp5UjjIC_tccJgkF9pPYBJh-HMZkJ3uWozac2s4qCqo1ZwFRvzGllRFBJtMSjDhM3hFqlYqzW0YHtScQws1H8A-fh9W4ypwgihpHRtoX6mVRHU-IOTIvparJNGgXyhrIj4eqY2cx8=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFrW6Cq-qZCi_6jHlV9onbv17jQSUyEStHQjy1RTFLInKtyAWcRsmjm9inz3XdHgrV1O75k9tM45pZzqZyac4xIbBhRF_5xZvBJhQAZ8ptokZ7IPmnPBc25qQJPLV2u3sKjWjsRLPIxJIpLdc0IE_NNAQMvIqsuxkz7fmbwPUpyXyGMULdtKJPBf5iB5p1djOCi0GU=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCNofvfdxECGbm-yHt3bR-_Vg2rt2T97GrlwxYs8ZAqs_mjdFZSCzLwwpNk24YB0GyAXNskX5nYDgbpEEr8fIG-UyMUbJ3cpd0KT5uznuPO752IYuBvho8dk4noILA_EKFnPV9oaONBTQ0Do4P5RoXH6rpyxqZzzQ6YM9uHkX4Y1SaNLgPuiCMRztbJxfJwShihs4=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIM5ewi8fWiapF9z4kdv1qvCTJzlU0OOH3rINUwL-JL4W6UdDgEUCJgF5mWl6YTbUDxtO3s4sCPF1JYzBc20nJrIyh6C2hvmDN8krAmgfzlhSTxBqr2hG98wsTEmdLOpXHRXbBQ1SERAbNM4qJh1HO2kKaShXzBvywHrU7kaVT0vWephqOXA==>

[24] web search for 'StatPearls ceftriaxone NCBI bookshelf third-generation cephalosporin'; grounded search summary:
Based on the clinical monographs from **StatPearls** on the **NCBI Bookshelf** (including reviews on *Third-Generation Cephalosporins* and *Beta-Lactam Antibiotics*), here is a comprehensive clinical summary of **ceftriaxone**:

---

### 1. Classification & Overview
* **Drug Class:** Third-generation cephalosporin (β-lactam antibiotic).
* **Route:** Parenteral only (intravenous [IV] or intramuscular [IM]).
* **Key Pharmacokinetic Features:**
  * **Long Half-Life (~6–9 hours):** Longest half-life among third-generation cephalosporins, allowing once-daily (or twice-daily in severe CNS infections) dosing.
  * **High Protein Binding:** Approximately 85% to 95% bound to plasma albumin.
  * **CNS Penetration:** Excellent penetration across inflamed meninges into the cerebrospinal fluid (CSF).
  * **Dual Elimination:** Excreted both renally (~60%) and through the biliary system (~40%). 
  * **Dose Adjustments:** **No renal dosage adjustment** is required for patients with isolated renal insufficiency (unlike most other cephalosporins), unless both severe renal and hepatic failure coexist.

---

### 2. Mechanism of Action (MOA)
* **Bactericidal:** Ceftriaxone binds to bacterial **penicillin-binding proteins (PBPs)**, specifically transpeptidases, inhibiting the final step of peptidoglycan cell-wall synthesis.
* This weakens the structural integrity of the bacterial cell wall, leading to osmotic instability, activation of bacterial autolysins, and cell lysis.

---

### 3. Spectrum of Activity
* **Gram-Negative Bacilli:** Broad coverage against Enterobacterales (e.g., *Escherichia coli*, *Klebsiella pneumoniae*, *Proteus mirabilis*, *Serratia*) and *Haemophilus influenzae*.
  * *Note:* Unreliable against AmpC β-lactamase producers (SPACE/SPICE organisms) or ESBL-producing strains.
* **Gram-Negative Cocci:** Highly active against *Neisseria meningitidis* and *Neisseria gonorrhoeae*.
* **Gram-Positive Cocci:** Good activity against *Streptococcus pneumoniae* and *Streptococcus pyogenes* (Group A Strep). Poor/variable against methicillin-susceptible *Staphylococcus aureus* (MSSA).
* **Notable Gaps (No Activity):**
  * **Pseudomonas aeruginosa** (requires ceftazidime or cefepime)
  * **Listeria monocytogenes** (requires ampicillin)
  * **Enterococci** (*E. faecalis*, *E. faecium*)
  * **Methicillin-resistant *Staphylococcus aureus* (MRSA)**
  * **Atypical pathogens** (*Mycoplasma*, *Chlamydia*, *Legionella*)

---

### 4. Indications
* **Bacterial Meningitis:** Empiric treatment (combined with vancomycin ± ampicillin for patients >50 years old or immunocompromised).
* **Community-Acquired Pneumonia (CAP):** Hospitalized patients (combined with a macrolide or doxycycline to cover atypicals).
* **Gonococcal Infections:** First-line therapy for uncomplicated and disseminated *N. gonorrhoeae* infections (administered IM).
* **Spontaneous Bacterial Peritonitis (SBP):** Treatment and primary/secondary prophylaxis.
* **Lyme Disease (Borreliosis):** Severe disseminated manifestations (neuroborreliosis, high-grade heart block, Lyme carditis, recurrent arthritis).
* **Infective Endocarditis:** Infections caused by HACEK organisms or highly penicillin-susceptible viridans group streptococci.
* **Pyelonephritis & Complicated UTIs:** Inpatient empirical coverage.
* **Intra-abdominal & Pelvic Infections:** Often combined with metronidazole for anaerobic coverage.

---

### 5. Adverse Effects & High-Yield Safety Warnings
* **Biliary Pseudolithiasis (Sludging):** Due to high biliary elimination, ceftriaxone forms insoluble complexes with calcium in bile, leading to reversible gallbladder sludge/pseudolithiasis that can mimic cholelithiasis.
* **Kernicterus in Neonates:** Ceftriaxone displaces unconjugated bilirubin from albumin-binding sites, significantly increasing free bilirubin levels and raising the risk of kernicterus (bilirubin encephalopathy).
* **Precipitation with Calcium-Containing Solutions:**
  * **Absolute Contraindication in Neonates (≤28 days):** Co-administration with IV calcium products (e.g., Ringer's lactate) causes life-threatening calcium-ceftriaxone crystal precipitation in lungs and kidneys.
  * In patients >28 days, ceftriaxone and calcium-containing solutions may be given sequentially only if the infusion lines are flushed thoroughly between infusions.
* **Immune-Mediated Hemolytic Anemia:** Ceftriaxone-induced autoimmune hemolytic anemia (Coombs-positive) is a rare but potentially severe complication.
* **Gastrointestinal / Other:** *Clostridioides difficile*-associated colitis, injection site pain (often co-administered with 1% lidocaine when given IM), mild transaminase elevation.

---

### 6. Summary Comparison in Class

| Feature | Ceftriaxone | Cefotaxime | Ceftazidime |
| :--- | :--- | :--- | :--- |
| **Generation** | 3rd | 3rd | 3rd |
| **Dosing Frequency** | Every 12–24 hours | Every 6–8 hours | Every 8 hours |
| **Pseudomonas Activity** | No | No | **Yes** |
| **Biliary Sludging Risk** | **High** | Low | Low |
| **Renal Dose Adjustment** | **No** | Yes | Yes |
| **Preferred in Neonates** | **Avoid** (Use Cefotaxime) | **Preferred** over Ceftriaxone | Specific indications only |
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFuHEUx35CC4Va8zuCddEIRw2ulX4bdBRagrJMoFK4GfbPdB5zYT14JqJr5L3LFPNMdq-ImqZg4GgmCdD2AK0XsupXksPrqn0CqXdmr5YbhAx9QIo0mD2wqlq_-f-4LCChCvKydph3QuL0=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT0ZmJ4hTYqjiK-QBe21slDdgXGhZOT7XCLwqoKWsKczbvWO7mD_tqY6P2U2Mabx8iOmk9suFuwCmk932PP8h07oU07TPZqpW38JX8O3FSw2R2WwXr3r2nyc7kXORvVCCLli4hGBglNl4=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFH098i7oNABJ7WpF_JyW05GCklDtSX7WwoXJhozkhZ9-Yh-gU5dE2Wm-VkedM__OEU_XS9RBWdtgB5j3ZdbRsd5_t_H7U0v9y0tGaQxUOzwIvxX0729JYa9mTeMPQiIrwca5V54B23LuA=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFo5SXa6MnLsUh4f6qBEz6U-ksrkSaCOoUbS-HmTz_SC7CZBz61i0marrXfpL6SHQbPyYXJUxAF3Iy5r8X72lgVyjV7zTBknSd8fylSaZk7Uoi4huKfqEi_um91fqle>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAH10UyGp1xWoA02pWQhZp0fVTn_LFjZNlVkjRXuT4_XLECxO3Md2vIGg2cDaIggx5KOd0thNRwoKQqegL645VXTMJie92HupbqG_uGNyERmSdRNYRyT63vOWrevmnGnzAECOMLHNGq18=>
  - merckmanuals.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5qxoiRCoBtw0hi09wWFlG7Fc5f7gmjFs_NCSis_ntx4DhoALX4NQXg5EEVurKVKxaA0T5C-t0L1JoUx_d4ppUaeKr9-q6sRVpJ5cp1fHj1sugE9VxvTtvOhrI57AOIHjiWUucMUJtwwCGAwrWQJzlqrzw5VxB3PPVzt2jFZQ0chtH1qcLOavkVyckMRFXIzCqb4guuFQsHjMdJo2GeLEPB2YbADzRxxupocG8Hw3IhwY=>

[25] web search for 'medlineplus.gov druginfo ceftriaxone injection'; grounded search summary:
Based on the **MedlinePlus (AHFS® Consumer Medication Information)** entry for **Ceftriaxone Injection**, below is an overview of its uses, administration, precautions, and side effects:

---

### **1. What is Ceftriaxone Injection?**
* **Drug Class:** Cephalosporin antibiotic.
* **How it works:** It works by killing bacteria. 
* **Note:** Ceftriaxone does **not** work for viral infections such as colds or the flu. Using antibiotics when they are not needed increases the risk of antibiotic resistance.

---

### **2. Uses (Why It Is Prescribed)**
* **Bacterial Infections:** Ceftriaxone injection is prescribed to treat serious bacterial infections in many different parts of the body, including:
  * Respiratory tract infections (e.g., pneumonia)
  * Blood infections (septicemia)
  * Meningitis (infection of the tissues surrounding the brain and spinal cord)
  * Abdominal infections
  * Skin, bone, and joint infections
  * Urinary tract infections (UTIs)
  * Gonorrhea and pelvic inflammatory disease (PID)
* **Surgical Prophylaxis:** Given before certain surgeries to prevent postoperative infections.
* **Other Uses:** Sometimes used in high-risk patients (e.g., after human/animal bites, close contacts of patients with meningitis, or prevention of infection in certain penicillin-allergic patients
[evidence truncated]
```

</details>

**Answer:**

# Ceftriaxone: Cephalosporin Generation

**Ceftriaxone is a third-generation cephalosporin** (a β-lactam antibiotic).

## Sources & Evidence

| Source type | Finding |
|---|---|
| **Public web sources** (StatPearls/NCBI, MedlinePlus, FDA DailyMed, WHO EML) | Consistently classify ceftriaxone as a **third-generation** cephalosporin. |
| **Internal database** (`drugs` collection) | The drug exists — `generic_name = "Ceftriaxone Sodium for Injection"`, `brand_name = "Rocephin"` (drug_id 6, approval no. H10920012, 1.0 g/vial injection). **However, the database contains no "generation" or "class" field**; its only classification field is `therapeutic_area = "Antibiotic"`. |
| **Internal knowledge base (RAGFlow)** | **No relevant document.** "Ceftriaxone" is not present; the only "cephalosporin" mentions are incidental references inside an *amoxicillin* (AMOXIL) label. |

> Note: The "third-generation" designation comes from **public pharmacology sources only**. The internal database does *not* record a generation/class, so it cannot be cited for this classification.

## Supporting Pharmacology Detail (from public sources)

- **Spectrum:** Strong against gram-negatives (e.g., *E. coli*, *Klebsiella*, *H. influenzae*), and reliable for *N. meningitidis* / *N. gonorrhoeae*. Moderate gram-positive activity (*S. pneumoniae*, *S. pyogenes*). **No** reliable cover for *Pseudomonas*, MRSA, *Enterococcus*, or anaerobes.
- **Typical uses:** Bacterial meningitis (good CSF penetration), community-acquired pneumonia, gonorrhea, pyelonephritis/UTI, sepsis, intra-abdominal infections.
- **Administration:** **Parenteral only** (IV or deep IM); long half-life (~6–8 h) allows once- or twice-daily dosing.

**Public references:** 
- StatPearls — *Third-Generation Cephalosporins*: https://www.ncbi.nlm.nih.gov/books/NBK549881/ 
- StatPearls — *Cephalosporins* (5-generation overview): https://www.ncbi.nlm.nih.gov/books/NBK551517/ 
- MedlinePlus — Ceftriaxone Injection: https://medlineplus.gov/druginfo/meds/a685032.html 
- WHO Model List of Essential Medicines: https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02

**In short: third-generation cephalosporin.** No attached reference files were found in the working directory to analyze; had any been provided, I would have incorporated them.

---

## 23. web-08 (web, easy)

**Question:** Who first synthesised acetylsalicylic acid in a stable form at Bayer, and in what year?

**Gold answer:** Felix Hoffmann, 1897.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] web search for 'Felix Hoffmann first synthesis acetylsalicylic acid Bayer 1897'; grounded search summary:
On **August 10, 1897**, German chemist **Felix Hoffmann**, working at the pharmaceutical laboratory of Friedrich Bayer & Co. in Elberfeld, Germany, successfully synthesized a chemically pure and stable form of **acetylsalicylic acid (ASA)**—the active compound later trademarked and marketed worldwide as **Aspirin**.

---

### 1. The Historical Background & Motivation
* **The Problem with Salicylic Acid:** Salicylates derived from willow bark (*Salix*) and meadowsweet (*Spiraea ulmaria*) had been used for centuries to treat pain and fever. By the late 19th century, synthetic salicylic acid and sodium salicylate were widely prescribed for rheumatism, but they caused severe gastrointestinal irritation, nausea, and had an unpleasant taste.
* **Hoffmann’s Personal Motive:** According to Bayer’s traditional accounts, Hoffmann was motivated by his father, who suffered from severe rheumatoid arthritis and could no longer tolerate the stomach pain caused by sodium salicylate. Hoffmann sought an effective derivative that would be gentler on the digestive tract.

---

### 2. The Chemistry of the Synthesis
Acetylsalicylic acid was produced through an **acetylation** reaction:
$$\text{Salicylic acid} + \text{Acetic anhydride} \xrightarrow{\Delta} \text{Acetylsalicylic acid} + \text{Acetic acid}$$

* Hoffmann reacted the phenolic hydroxyl group ($-OH$) of salicylic acid with acetic anhydride in the presence of heat.
* Masking the reactive phenolic hydroxyl group with an acetyl group ($-OCOCH_3$) created an ester, making the compound significantly less irritating to the gastric mucosa while preserving its anti-inflammatory, analgesic, and antipyretic properties.

---

### 3. Prior Discoveries vs. Hoffmann’s Achievement
Hoffmann was not the first chemist to create acetylsalicylic acid, but he was the first to produce it in a **pure, stable, and medically viable form**:
* **Charles Frédéric Gerhardt (1853):** The French chemist first synthesized acetylsalicylic acid by reacting acetyl chloride with sodium salicylate, but his product was an unstable, impure mixture.
* **Karl Kraut (1869):** The German chemist improved Gerhardt’s work and determined the chemical structure, but the method was not suitable for large-scale pharmaceutical production.
* **Hoffmann’s Contribution:** He developed a reproducible, high-yield process using acetic anhydride that produced stable, pure crystals suitable for clinical use and mass industrial synthesis.

---

### 4. From the Lab to the Market: "Aspirin"
* **Clinical Testing:** Hoffmann’s supervisor in the pharmacology department, **Heinrich Dreser**, initially shelved the compound to focus on diacetylmorphine (heroin, which Hoffmann synthesized just days later). However, subsequent trials confirmed ASA's efficacy and reduced toxicity.
* **The Name:** In 1899, Bayer registered the trademark **Aspirin**:
  * **"A"** stood for *acetyl*.
  * **"spir"** came from *Spiraea ulmaria* (meadowsweet, a natural plant source of salicylic acid).
  * **"-in"** was a conventional suffix for pharmaceutical products at the time.
* Bayer initially sold Aspirin as a powder in 1899 and launched it as a compressed tablet in 1900, revolutionizing modern pain management.

---

### 5. Historical Controversy: Arthur Eichengrün
In 1949, **Arthur Eichengrün**, who was Hoffmann’s superior and head of the chemical division at Bayer in 1897, published a paper claiming that he had directed the project, instructed Hoffmann to synthesize the compound, and pushed it through clinical trials despite Dreser’s initial resistance. 

Eichengrün (who was Jewish and survived the Theresienstadt concentration camp during WWII) argued that his role had been erased from Bayer’s official history during the Nazi era. Medical historians continue to debate the extent of Eichengrün's leadership versus Hoffmann's independent lab work, though most agree Eichengrün played an essential supervisory role in ASA's development.
sources:
  (none)

[3] web search for 'Arthur Eichengrün aspirin credit dispute Felix Hoffmann role'; grounded search summary:
The dispute over who deserves credit for the discovery and development of **Aspirin (acetylsalicylic acid, or ASA)** centers on the rivalry and differing accounts between **Felix Hoffmann** and his supervisor, **Arthur Eichengrün**, at the German pharmaceutical firm Bayer.

---

### 1. The Traditional Narrative (Felix Hoffmann)
For decades, Bayer promoted Felix Hoffmann as the sole discoverer of Aspirin:
* **The Synthesis:** On August 10, 1897, Hoffmann successfully synthesized a pure, stable form of acetylsalicylic acid (ASA had been synthesized earlier in 1853 by French chemist Charles Frédéric Gerhardt, but in an unstable, impure form).
* **The Motivation:** Bayer’s official story, first published during the 1930s, claimed Hoffmann took the initiative independently to relieve his father, who suffered from severe rheumatoid arthritis and could not tolerate sodium salicylate’s stomach-burning side effects.
* **Recognition:** Hoffmann’s name was listed on the lucrative 1900 U.S. patent for Aspirin (a German patent was denied because the compound was deemed unoriginal due to Gerhardt’s prior work).

---

### 2. Arthur Eichengrün’s Counterclaim
Arthur Eichengrün was the head of the chemical division at Bayer and Felix Hoffmann’s direct superior. Eichengrün challenged Hoffmann’s primacy, most notably in a 1949 paper titled *“50 Jahre Aspirin”* (*50 Years of Aspirin*), published in the journal *Die Pharmazie* shortly before his death:
* **Directing the Synthesis:** Eichengrün claimed that Hoffmann did not act on his own initiative. Instead, Eichengrün directed Hoffmann—who was a junior bench chemist—to acetylate salicylic acid as part of a systematic program to produce less toxic derivatives of salicylic acid.
* **Saving Aspirin from Rejection:** Heinrich Dreser, head of Bayer’s pharmacology department, initially rejected ASA, claiming it weakened the heart. Eichengrün claimed that he secretly sent samples of ASA to clinical doctors in Berlin (such as Dr. Felix Goldmann). When the clinical results returned overwhelmingly positive, Dreser was forced to reconsider, eventually patenting the testing and clinical introduction under his own name while denying Eichengrün royalties.
* **Hoffmann’s Role:** According to Eichengrün, Hoffmann merely executed the bench work on explicit instructions, comparing Hoffmann’s contribution to that of a technician following a recipe.

---

### 3. The Racial and Political Dimension
Eichengrün was Jewish; Hoffmann was not. 

* In **1934**, during the Nazi regime, German historian Albrecht Schmidt published a book commemorating Bayer's achievements. It promoted Hoffmann as the sole inventor, attributing the breakthrough to the sentimental story about his father’s arthritis. Eichengrün's role was effectively erased from the public record under Nazi anti-Semitic historiography.
* During World War II, Eichengrün was stripped of his patents and company (Cellon-Werke) and interned in the **Theresienstadt concentration camp**. He survived the Holocaust and spent his final years attempting to reclaim historical credit.

---

### 4. Modern Re-evaluation (Walter Sneader's Research)
In 1999, pharmaceutical historian **Dr. Walter Sneader** of the University of Strathclyde in Glasgow re-examined Bayer’s original laboratory archives:
* **Support for Eichengrün:** Sneader concluded that Eichengrün’s version of events was overwhelmingly supported by archival documents. Laboratory notebooks revealed that Hoffmann was simultaneously working on several derivatives assigned by Eichengrün.
* **No Contemporaneous Mention of Hoffmann's Father:** Sneader found no contemporary 1897 records mentioning Hoffmann’s father; that narrative only emerged publicly in print in 1934 during the Third Reich.
* Sneader argued that Eichengrün conceived the project, supervised the synthesis, and was primarily responsible for pushing the drug through clinical trials despite internal resistance.

---

### 5. Bayer’s Stance and Current Consensus
* **Bayer’s Rebuttal:** Following Sneader’s 1999 paper, Bayer issued a press release defending the traditional narrative. The company maintained that Hoffmann was the true inventor, arguing that Hoffmann's laboratory notebooks recorded the synthesis under his name and that Eichengrün had not formally contested the U.S. patent at the time it was filed.
* **Modern Historical View:** Most modern science historians view Aspirin's development as a collaborative industrial effort rather than a single genius's breakthrough:
  * **Felix Hoffmann** was the chemist who successfully prepared the pure, stable chemical entity at the laboratory bench.
  * **Arthur Eichengrün** was the conceptual director and research manager who conceived the project, directed Hoffmann, and rescued the drug from abandonment.
  * **Heinrich Dreser** conducted the institutional pharmacological trials that established its clinical dosage and safety.

Historians widely agree that Eichengrün’s contributions were marginalized due to corporate politics at Bayer and later erased by Nazi-era anti-Semitism.
sources:
  (none)

[4] web search for 'Bayer corporate history aspirin Felix Hoffmann 1897 official'; grounded search summary:
In Bayer’s **official corporate history**, the discovery of Aspirin is attributed to chemist **Dr. Felix Hoffmann** on **August 10, 1897**. 

---

### 1. The Official Corporate Narrative

* **The Discovery (August 10, 1897):**
  Dr. Felix Hoffmann, a young chemist working in the laboratory of *Farbenfabriken vorm. Friedr. Bayer & Co.* in Wuppertal-Elberfeld, Germany, succeeded in synthesizing **acetylsalicylic acid (ASA)** in a chemically pure and stable form. While acetylsalicylic acid had been synthesized earlier in crude forms by French chemist Charles Frédéric Gerhardt (1853), Hoffmann was the first to develop a stable, reproducible, shelf-stable formulation suitable for medical use.

* **The Origin Story ("The Rheumatic Father"):**
  According to the classic account maintained by Bayer, Hoffmann was motivated by personal empathy. His father suffered from severe rheumatoid arthritis and could no longer tolerate sodium salicylate, the standard painkiller at the time, due to severe stomach irritation and nausea. To create a more tolerable compound, Hoffmann experimented with acetylating salicylic acid using acetic anhydride, creating pure ASA.

* **Testing and Market Launch (1899):**
  * After initial testing overseen by Heinrich Dreser, head of Bayer’s pharmacology laboratory, the drug demonstrated remarkable pain-relieving, anti-inflammatory, and fever-reducing properties with significantly fewer gastric side effects.
  * Bayer registered the trademark **Aspirin** on **March 6, 1899** ("*A*" for acetyl, and "*spirin*" after *Spiraea ulmaria*, meadowsweet, a plant rich in salicin).
  * It was initially distributed as a powder in small 250g glass bottles to pharmacists before being introduced as a standardized tablet in 1900.

---

### 2. The Historical Controversy: Arthur Eichengrün

While Bayer's official records credit Hoffmann, historians and former colleagues have contested the narrative:

* **The 1934 Footnote:** The "father's rheumatism" story first appeared in print in 1934 in a footnote written by Albrecht Schmidt, an IG Farben chemist.
* **Arthur Eichengrün’s Claim (1949):** Dr. Arthur Eichengrün, Hoffmann’s former Jewish supervisor at Bayer, published an article shortly before his death in 1949. Eichengrün claimed that *he* conceived the synthesis project, instructed Hoffmann to carry it out, and personally arranged for secret clinical trials after pharmacology head Heinrich Dreser initially rejected the compound. 
* **The Nazi-Era Erasure:** In 1999, pharmaceutical historian Dr. Walter Sneader published research concluding that Eichengrün's role was deliberately erased during the Nazi regime in the 1930s because of his Jewish heritage, leaving Hoffmann as the sole "Aryan" inventor in German history books.

---

### 3. Bayer’s Stance

* When the controversy resurfaced in 1999, Bayer issued statements upholding its official history:
  * Bayer maintains that **Felix Hoffmann's laboratory logbook dated August 10, 1897**, provides direct, verifiable documentary proof that Hoffmann personally synthesized pure ASA.
  * Bayer also holds the U.S. patent (U.S. Patent No. 644,077, issued in 1900), which formally names **Felix Hoffmann** as the inventor.
  * Bayer acknowledges that late-19th-century industrial pharmaceutical research was collaborative—involving chemists, department heads like Eichengrün, and pharmacologists like Dreser—but officially continues to commemorate Hoffmann as the discoverer of Aspirin.
sources:
  - bayer.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjBOddBIsCfEQ66KOeHk9F7rKJISpMpd_Tcx9Gh6iWePoxP05gjeWFIi3VClZB2boB8lq5lhUvMTlO_GtMuzkGgy1aPCTz6uUbGP7EwjqhQK38fHZcIr5IdeYDWjW-QnGH3duroA==>
  - bayer.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGABxZ976Li933Qu62INf8mQP2V_HhAaRJW8fMKeUwyfPyIqQfXgWVIQGg5Iu0QJwgoNvzBSYSw3lOpdYznfAlWjstfK6AshqczPe3Rsh_vnVJrEc7tf-BaKd641j6JVZ-G5iWbFXJec3n9HCW9Usg7vmPdBkVFDj7VO5fuWV1T97wFLz_cA2rWIza-jpQ6althgmcCqu5ms9xkfOMP-T098g==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHKsjYn6HBD1h1XHSrW2XN7nNJXgZ51gOMzz5801YXTejPsD5o-odRWXbSaigl97i0UxyElaU-oGTF6T6fGQYjbT4l--3b_36x2TuxgKtYNEcqvYoDgx0uFG93qEkhdJueIcu4gjYow>
  - aspirin.sa <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb5TLW4LMSjXvccaJpzY1Yln5ef6PGgS1LCfWvllW3FOWvTX1XEPYipElpsG_gG1KLPxuQPcnroVC3GUc5TJVhf2kaBcsPpYQXjeInhfDGaCmrYjkcDCmVVVQ7ZCrWgYHM0nHitQ==>

[5] web search for 'Charles Frédéric Gerhardt 1853 acetylsalicylic acid acetylated salicylic acid history'; grounded search summary:
In 1853, the French chemist **Charles Frédéric Gerhardt** became the first person to synthesize **acetylsalicylic acid** (ASA)—the active chemical compound that would later become known globally as **Aspirin**. 

Here is the historical context, the chemistry behind his discovery, and how it eventually led to modern aspirin:

---

### 1. The Context: The Quest to Tame Salicylic Acid
* For centuries, plant extracts containing salicylates (from willow bark and meadowsweet) had been used to treat pain, inflammation, and fevers.
* By the 1830s, chemists had isolated **salicin** and converted it into **salicylic acid**. 
* While salicylic acid was an effective analgesic and antipyretic, it had severe drawbacks: it had a foul taste and was notoriously harsh on the stomach, causing severe gastric irritation, nausea, and ulcers.

### 2. Gerhardt’s 1853 Synthesis
In 1853, Gerhardt was conducting research into organic acid anhydrides in Paris. In the course of investigating how different acid chlorides reacted with salts:
* **The Reaction:** Gerhardt treated **sodium salicylate** with **acetyl chloride**.
* **The Product:** The reaction yielded an acetylated salicylic derivative. Gerhardt described it in his 1853 paper (*Recherches sur les acides organiques anhydres*) and called it **“salicylic-acetic anhydride”** (*anhydride acéto-salicylique*).

### 3. Why Gerhardt Did Not Pursue It
Despite creating acetylsalicylic acid, Gerhardt did not market or clinically explore the drug:
* **Impurity and Instability:** His preparation was an impure, crude, and relatively unstable mixture.
* **Academic Focus:** Gerhardt was a theoretical and synthetic chemist primarily interested in the classification of organic compounds and the chemistry of anhydrides, rather than pharmacology.
* **Premature Death:** He moved on to other research, published his magnum opus (*Traité de chimie organique*), and died shortly thereafter in 1856 at the age of 39.

### 4. The Bridge: Von Gilm and Kraut
Gerhardt's compound was not entirely forgotten:
* **1859:** Austrian chemist **Hugo von Gilm** synthesized acetylsalicylic acid by reacting salicylic acid with acetyl chloride, producing a somewhat purer, insoluble solid.
* **1869:** German chemist **Karl (Adolph) Kraut** re-evaluated the experiments of both Gerhardt and von Gilm, refined the purification, and correctly identified its chemical structure as **acetylsalicylic acid**.

### 5. Bayer and the Birth of Aspirin (1897–1899)
By the late 19th century, pure salicylic acid was in widespread medical use, but its gastric side effects remained a major obstacle. 

* **1897:** At the German chemical and pharmaceutical company **Bayer**, chemist **Felix Hoffmann** (working under the direction of pharmaceutical research head **Arthur Eichengrün**) searched the chemical literature for a buffered or acetylated alternative to salicylic acid. 
* Revisiting the chemical path paved by Gerhardt and Kraut, Hoffmann developed a reproducible industrial method to synthesize **chemically pure and shelf-stable acetylsalicylic acid**.
* **1899:** Bayer trademarked the drug as **Aspirin**:
  * **"A"** for *acetyl*.
  * **"spir"** after *Spiraea ulmaria* (meadowsweet, a plant rich in salicylic acid).
  * **"in"** as a standard chemical suffix for medicines at the time.

### Summary
Charles Frédéric Gerhardt is recognized as the **original synthetic discoverer** of acetylsalicylic acid (1853). Although he did not realize its therapeutic potential or produce a pure, stable form, his basic synthesis laid the chemical groundwork that Felix Hoffmann and Bayer capitalized on over 40 years later to create the world's most widely used pain reliever.
sources:
  - facebook.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDSYvmKQToc-IMgnGwlpoUxr1pAhZMWtvfiRVvbG30ALRJrpwrjX51kJwDQvn95fspIoflaED2K35knsRTXTxd3RfLoTDk5uUMoOtl2rt7lQevj8rss4ugDt03zgvJXpUH3KUnNaJIZ4ROqAxysxjeZd8hXF3jgjLZQ6Gnng==>
  - pharmaceutical-journal.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFR2yN7NOi8-IH00uUtZAsJwls82sR9zj1837XM14cnNg5Dd8LmXI5O75tJUzP1Pf4H6g9jCD8PmfcZBN18Xv2zqTeM3KsyifxjAhmGaL5sLGU0Ch7We5LqE0rcdhMUtsp077N9Xwr8GC1vxTxXmO3L7_kHtPhsyErH0vbHTUIVXK_G>
  - grapefrute.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH5SYE2ZyRGJ1HEj-qtAjOaWni44cBBE8rMnsYK_ToDfNsS3BTP3YVpfvAoGDm3aCOZ7bhpLftGnantzE3dZ59kdaYkTwoUzS5keYECTU0ENiCmAlkTkc3Xq2gyRrei4Evg0JSFVNEHrQZUqqQ8vKFAyCBVI5eYxVIeSBTF28yk9tYxh30ARtN6i-fL4f2e0yUaods=>
  - lgcstandards.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMfijt1hXtRsFJBWPA-sSFgeE93_qi4g30tmibKihPJnSDRIB1qjhhaZkIFwds0tPrD4WtVNSiXQq0P6TPKIlPhbhRJKIxbNB916I0WRNRk_Gem46z8PyA-OXgoKiztvGeAtwvVdvBLVGR8Ib4_Vf6b9JTTTRPdGLcdIk4BQLsIg==>
  - wordpress.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJ4PTUd7XHqGAsyM9ZsRVDOp-U7MzRlCEM7uwsWZoaH3XcXnYpAKXuKYCFo0NJINKbu7ycJLGCOv8FNn4E89b-mKZsNp3UJOXq2VDJKssiX0Vw-1RVO9ViZRjuB-5f4cMChxkgVqCMvuSE39YB_7zdKz69UzJKfLODIzsda2kIZSPIFFaHXCBMFg==>
  - dpma.de <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGCCVBKRGjbOYIaDsAxFjlLlNqA3m3CNEk8MTGreK4r95GPNy4X2YIKkg0EJsoUw6QdD7HoZqAjE2W9WMGtCp0IO2KVALTuO4IACWl9GLlWUSg53l-ZCd5ps9f-uaGm7NvsTJciQ7oRxejIVGqorUX5sOK0Y9SK0KkPI4Y5ZFtEUiT9J2OC3iNKWZBLXZybIZJg3pUmLw-QFo=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEEIZafbheJydJHGDIyWtMoVeoic_BavrHclri_gXdUkYik1PTRj8ogfV6OeSTC4utSMTQWlTGzHhuq48jZf2HrHE41aNx5hYeuX8nBrp4J1aWLjgpIL7Rv7et1ukI45U0aD48VAXna49m8DcchJyn_3l0ZbQ-xdQ==>
  - facebook.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDSYvmKQToc-IMgnGwlpoUxr1pAhZMWtvfiRVvbG30ALRJrpwrjX51kJwDQvn95fspIoflaED2K35knsRTXTxd3RfLoTDk5uUMoOtl2rt7lQevj8rss4ugDt03zgvJXpUH3KUnNaJIZ4ROqAxysxjeZd8hXF3jgjLZQ6Gnng==>

[6] web search for 'aspirin history Eichengrün Sneader BMJ 1999 Walter Sneader'; grounded search summary:
In late 1999 (and published in the *British Medical Journal* in December 2000), pharmaceutical historian **Dr. Walter Sneader** of the University of Strathclyde challenged the established history of aspirin’s invention. He argued that **Arthur Eichengrün**, a Jewish chemist and supervisor at Bayer, was the true intellectual driving force behind aspirin, rather than **Felix Hoffmann**, who had long received primary credit.

---

### 1. The Traditional Narrative (The "Hoffmann Myth")
For decades, Bayer attributed the discovery of aspirin to **Felix Hoffmann**. 
* The story claimed that on August 10, 1897, Hoffmann synthesized pure, stable acetylsalicylic acid (ASA) on his own initiative to find a painkiller for his father, who suffered from severe rheumatism and could not tolerate the stomach irritation caused by sodium salicylate.
* According to this version, Hoffmann took the compound to Heinrich Dreser, head of Bayer’s pharmacological testing, who recognized its medical value, leading to its trademarking and launch as **Aspirin** in 1899.

---

### 2. Sneader’s Findings and Reappraisal
While researching drug histories in the late 1990s, Sneader scrutinized Bayer’s archives, laboratory notebooks, and historical publications:

* **Origin of the Father Story:** Sneader discovered that the romantic story of Hoffmann helping his rheumatic father never appeared in any 19th-century document. It first appeared in **1934** in a footnote within a chemical engineering history by Albrecht Schmidt. Sneader noted that 1934 coincided with the Nazi regime’s consolidation of power in Germany, during which Jewish contributions were systematically expunged from German history and science.
* **Eichengrün as Director of the Project:** Archival records and laboratory logs showed that Hoffmann worked directly under Eichengrün, who headed pharmaceutical research at Bayer. Eichengrün had initiated a planned program to synthesize acetylated derivatives of salicylic acid to eliminate gastric toxicity. Hoffmann synthesized the compound under Eichengrün's direct instructions.
* **Rescue from Dreser’s Rejection:** When the compound was first submitted to Heinrich Dreser, Dreser dismissed it, claiming it would cause dangerous cardiac depression. Eichengrün, convinced of the compound’s promise, tested it on himself without harm and then bypassed Dreser. He secretly arranged clinical trials with physicians (including Dr. Felix Goldmann and outside clinicians in Berlin). The clinical reports were overwhelmingly positive, forcing Dreser and Bayer management to reverse their decision and prepare the drug for mass production.

---

### 3. The Erasure of Arthur Eichengrün
* **Financial and Professional Injustice:** Under Bayer’s compensation structure, Dreser received substantial royalties for introducing the drug, while chemists like Eichengrün and Hoffmann received fixed salaries and no drug royalties.
* **Nazi Persecution:** Eichengrün left Bayer in 1908 to successfully found his own chemical manufacturing firm (inventing non-flammable photographic film, *Cellon*). When the Nazis took power, his company was "Aryanized" (seized), and in 1944, at age 76, he was deported to the **Theresienstadt concentration camp**.
* **Eichengrün's Accounts:** 
  * While imprisoned in Theresienstadt, Eichengrün typed an account of his career (now held in Bayer’s archives), detailing his invention of aspirin and how his credit had been stolen.
  * After surviving the Holocaust, he published a paper in 1949 titled *"50 Jahre Aspirin"* (*50 Years of Aspirin*) in *Die Pharmazie*, reiterating that he had directed Hoffmann’s work, overcome Dreser’s obstruction, and spearheaded the clinical testing. He died later that year, and his account was largely ignored for five decades until Sneader revisited it.

---

### 4. Reaction and Legacy
* **Bayer’s Reaction:** Bayer publicly disputed Sneader’s thesis, reiterating their position that company records designate Hoffmann as the inventor and arguing that Eichengrün was merely a supervising administrator whose later claims could not be conclusively corroborated against Hoffmann (who had died in 1946).
* **Modern Consensus:** Most modern medical historians agree with Sneader’s central conclusion: the romanticized "father's rheumatism" story was largely revisionist folklore, and **Arthur Eichengrün played an indispensable, leading role** in both the conceptual synthesis and the clinical adoption of aspirin. Hoffmann was the bench chemist who carried out the reaction, while Eichengrün was the scientist who envisioned the molecule and ensured it reached patients.
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHiuwik-J9OiLUh4qlGU3Qi2BdXYY3ggt40ujcKa8SFQhgxVP8TKuEsq1PY-xdGNfBd1pRDwt8Lb64H1qKAblauxjI1To6xCrx8qV-LyH7RJ7xSkWeoG6wXV7Ykl9YYhvshxWbSNs2y>
  - heraldscotland.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHxVzlyZCaXcVOfq-wO0e8ozC6eP3HgQvgo24iqvrrpnOJJBGtgOAQQfEn13ZJuP9KWDHkaJSxCfiWgwjSSbXYhAMAwMRRGyoskUkYVVEbejMnqHv7G0LmspgFnA3c3cIMPgF3kFa1Dw8p49V_XVJkil2Z2z1Qi-GCKcBh-z0aiyqmEV-wYCdPwVSU80gdPH930pLC89oYc87PpqMceN7n0fv7f-yJjyZ9D1RadOCeP0LBhz-aruphxzeq1psj4ejPsKojl9vM992P77Bo0P-SKz13Y9483pgZfteCuP2CCDQsQUnh4K2RlotHNZG3kq9ODOQ==>
  - pmlive.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2m7K3LfG1cAYDGh0TCNYAQZm7_H9BWwqJ2sUC0jAqzBA-kzker7EyRFeg-SIoA_OCZq6C8QxpM4jGPl2f55kXPnC5h-oOsqbZ-1NK-CmYWZiUiVxyzaYUPS2QjCIglt82tm9rr948Fi5zdSrD_lKT6cbi9F0=>
  - worldneurologyonline.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgcLhNXVlTiQb9B0tyVY_v2A3brW-ldjYgN5H0HNt4LJ90XQJZunutZuWXNmOl3RRBaGKqLJVylds2QjRjUAcSvub0mXCNbINoW7PsjvkOrj46u4Bu8YGe_4arlibxaGCdsckbLmUELIT6HU8ceOpiQP_4AKX9ReQZAWo=>
  - ua-magazine.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEZehdrQPPi_LFz1TsxwmllNvmTg7R9fduvVXinT3F16xSf2TCrZoFJkvUwlvwqg0zznzFwLRcMYHm9sWotQ4VO0HLe3DvqZAE4INLjX-Vns12_IZ2urKhLfNH3b7SMiW-1jDPORmR9KfS5QE8Rv7abYA==>
  - hekint.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQExW2mO_JwCnWSSjvYUhGfL-nfv0JFh6wshsXgQBnkosdyUkzLrxRpb6bL9iCi2lWucibv-PUBIMRgF5infWZZDm1dh0eqwFVXESC7N7MscCwonM1kIvWoQ_CgqncA1GKx0jPcJJ8i89DgOevyYL4U=>
  - dpma.de <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH0yFw1bSxpYc_pKqcaYukj5CbYGkF3NS6YG3R1KmFOGBuZLFmD8jZpRpmN8d6Z-5Nb1QKN7LOxwCRQftkVlfTaP5uSrc12kr6g3PZwZwPtojXPGUDfXHa6hj9bR01gpHyKwxgMcnUR-k2caFGH7h73M8mDW4ItOIz3tC5TtyUV9iNWyWqav-h8E_PvSaDbcM1IHDF5ogEcGfM=>

[7] web search for 'Heinrich Dreser aspirin clinical testing marketing 1899 trademark registration'; grounded search summary:
The commercialization of Aspirin represents one of the foundational milestones of the modern pharmaceutical industry. **Heinrich Dreser**, as the head of the experimental pharmacology laboratory at *Farbenfabriken vorm. Friedr. Bayer & Co.* in Elberfeld, Germany, played a central—and at times controversial—role in its clinical testing, scientific validation, naming, and marketing.

---

### 1. Initial Skepticism and Reversal
In August 1897, Bayer chemist Felix Hoffmann (working in the laboratory directed by Arthur Eichengrün) successfully synthesized a pure, stable form of **acetylsalicylic acid (ASA)**. 

When the compound was submitted to Heinrich Dreser for pharmacological evaluation, Dreser initially rejected it:
* **Fear of Cardiac Toxicity:** Traditional salicylates (such as sodium salicylate) were notorious for depressing heart action and causing severe gastric nausea. Dreser believed ASA would be equally toxic to the heart.
* **Focus on Heroin:** At the time, Dreser was devoting Bayer’s resources to the commercialization of diacetylmorphine, which he branded and marketed heavily as **Heroin** (as a cough suppressant and non-addictive morphine substitute).

It took persistence—historically attributed to Arthur Eichengrün conducting clandestine human self-testing and preliminary trials with local doctors—to force Dreser to reconsider ASA.

---

### 2. Preclinical and Clinical Testing
Once convinced to investigate ASA formally, Dreser led rigorous laboratory and clinical testing:

* **Preclinical / Animal Testing:** 
  * Dreser tested ASA’s cardiac effects on frog hearts and its physiological tolerance in fish and warm-blooded animals. 
  * He discovered that unlike sodium salicylate, ASA did not depress heart muscle contractions.
  * He theorized that ASA passed largely intact through the acidic stomach and was split into free salicylic acid only when it reached the alkaline environment of the small intestine, dramatically reducing gastric irritation.
* **External Clinical Trials (1898–1899):**
  * Dreser arranged extensive human trials with external clinicians to document its efficacy.
  * **Dr. Kurt Witthauer** at the Diakonissenanstalt in Halle evaluated ASA on patients with acute articular rheumatism, reporting remarkable anti-inflammatory and pain-relieving effects without gastrointestinal distress.
  * **Dr. Julius Wohlgemuth** in Berlin evaluated the drug in outpatients and confirmed its safety, antipyretic (fever-reducing) properties, and lack of cardiac side effects.

---

### 3. The 1899 Landmark Paper and the Name "Aspirin"
In early 1899, Dreser introduced the drug to the medical community by publishing a seminal paper in *Pflügers Archiv für die gesammte Physiologie*:
> **"Pharmakologisches über Aspirin (Acetylsalicylsäure)"** (1899)

In this paper, Dreser presented both the laboratory data and clinical trial results, firmly establishing ASA’s therapeutic utility. Notably, Dreser omitted the names of Felix Hoffmann and Arthur Eichengrün, presenting the pharmacological triumph largely as his own.

Around the same time, Bayer coined the proprietary name **Aspirin**:
* **"A-"** stood for the **acetyl** group.
* **"-spir-"** came from ***Spiraea ulmaria*** (meadowsweet), a plant that yielded spiric acid (an older name for salicylic acid).
* **"-in"** was a standard pharmaceutical suffix used during that period.

---

### 4. Trademark Registration (March 6, 1899)
Bayer faced a major intellectual property hurdle in Germany:
* **The Patent Problem:** The Imperial Patent Office (*Kaiserliches Patentamt*) refused to grant Bayer a patent for the chemical compound acetylsalicylic acid. The compound had already been prepared decades earlier by French chemist Charles Frédéric Gerhardt (1853) and later refined by Karl Kraut (1869), establishing "prior art". While Bayer obtained a product patent in the United States in 1900, it could not hold a product patent for ASA in Germany.
* **The Trademark Solution:** Because Bayer could not monopolize the chemical entity in its home country, it pivoted aggressively to brand protection. On **March 6, 1899**, Bayer officially registered **Aspirin** as a trademark with the Imperial Patent Office in Berlin (Registration No. 36433).

---

### 5. Marketing and Commercialization Strategy
Because Bayer relied on trademark power rather than patent exclusivity in Europe, its marketing campaign—overseen commercially by Bayer with Dreser acting as the chief scientific authority—pioneered modern pharmaceutical marketing:

1. **Direct-to-Physician Promotion:** Bayer bypassed lay advertising initially, launching a targeted campaign directed solely at the medical establishment.
2. **Sampling Campaign:** Bayer mailed information packets, scientific literature (including reprints of Dreser's and Witthauer's papers), and free product samples to more than 30,000 physicians, hospitals, and pharmacies across Europe.
3. **Form and Dispensation:** Before Aspirin was pressed into standard tablets (introduced in 1914–1915), Bayer sold it as a fine, dry powder. Pharmacists received it in 250-gram glass jars and weighed out individual 1-gram paper sachets for patients.
4. **Enormous Financial Windfall:** Under his employment agreement, Dreser was entitled to royalties on every product his pharmacological department tested and brought to market. While Hoffmann received a standard salary/modest pension, Dreser's royalties on both Heroin and Aspirin made him exceptionally wealthy before he retired from Bayer in 1914.
sources:
  - dpma.de <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHScQViKC17tFs8gYhmr_N3jscFvdtSdBLuYc2d-e_YTYfOtdodo8j6iKFmPbZfeqsmGqnIDdyTKY1btwlXtNFyxV2hS4gT9VPk3u3ky9e17PvQ9Kmk7FomUHnZEcXa1RL_IOAL1dx7w4e4GC6kLmJZNo1lUNBrF8sEYUr_OLVypFNYie5XOd_ZO-kSGKHH7Aef3mbA_eNvfQ==>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4HanwxwsJjfRm1wVyQ5PjTTIXLSCMBnbjDEKL_9hcQB56wYrrAix0Xg2bl2waQf5aO74RBhMSrR8pUHyh1OXjlaqab_FmqLrifqwLbkH_KANGf36fCxY52Q4YtYmJlersr0p5Yk0=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzWswynoiOc5Fze1SHeL9IUennxtvbXc0V5r2h2uLnimLE4N458JNjRDz0ZsV7wvF_c2zoLHPytYdWaNLa48IabJXQVZmkn0Rl5n3ySr5axGgsHItpN6SKEankFIFvuz6Hyfbp3w==>
  - facebook.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpvi6ShBXfqvcgKWvpDUmD8g1e05iMM4qvx1oDle6K01d3qJ3w2mFOPDY6-NePTlF_G66tZQ5m7_gax0x_NL-nCeLsh09zzaCdFB_BXBlNK7rOC-68ACI_pAkGrbi_Pl7A2O02TBBUECGTvIMYi17qohibECPdMgX0C5cCXsW_HAgr6L0rUqvf4Fognl9maiRjS3-Y1gznmKOHGeD1P9QKiCxbn8XyMvJfzur57uvMDqfXUw==>
  - vo.eu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmyGqGsqccogOhbC1iOFtu5N397lP872W-I9D0bpJ32pKCuSZNRPtJxqsXwtxowxaDCXNWEb5FlayVsxSgL49ZX9mZ7dLU5PeQKVrGUrAlpDuplp3t11ReNSEH4kpQmxedQ27wyJH1HJeFVpXlFnpZBrgQAuhJdvYE>

[8] web search for 'bayer.com aspirin history "Felix Hoffmann" 1897 corporate'; grounded search summary:
In the corporate history maintained by Bayer (*bayer.com* and archival records), the discovery and synthesis of **Aspirin** in **1897** by **Felix Hoffmann** is one of the company's most defining milestones. 

---

### 1. Bayer’s Official Corporate Narrative

* **The Chemist:** Felix Hoffmann (1868–1946) was a German chemist who joined the research laboratories of *Farbenfabriken vorm. Friedr. Bayer & Co.* in Elberfeld (now part of Wuppertal) in 1894, on the recommendation of his professor, Nobel laureate Adolf von Baeyer.
* **The Breakthrough (August 10, 1897):** Working in Bayer’s pharmaceutical laboratory, Hoffmann succeeded in acetylating salicylic acid using acetic anhydride, creating **acetylsalicylic acid (ASA)** in a chemically pure, shelf-stable form. While acetylsalicylic acid had been synthesized earlier in cruder forms (notably by French chemist Charles Frédéric Gerhardt in 1853), Hoffmann was the first to synthesize it in a stable, medically viable form.
* **The Personal Motivation:** Bayer’s historical accounts frequently note that Hoffmann was motivated in part by his father’s suffering from severe rheumatism. The common treatment at the time—sodium salicylate—caused extreme gastrointestinal irritation and nausea, prompting Hoffmann to seek a better-tolerated alternative.
* **Launch and Naming (1899):** Under the oversight of Heinrich Dreser (head of Bayer’s pharmacological laboratory), the drug underwent extensive clinical testing. In **1899**, Bayer registered the trademark **Aspirin®**:
  * **"A"** for acetyl.
  * **"Spir"** from *Spiraea ulmaria* (meadowsweet), a natural plant source of salicylic acid.
  * **"in"** as a standard chemical/pharmaceutical naming suffix.
* **Commercialization:** Initially distributed to pharmacies in 1899 as a powder packaged in glass vials, Aspirin was introduced in standardized 500 mg tablet form in 1900, pioneering modern pre-dosed pharmaceuticals.

---

### 2. Historical Debates and Corporate Defense

While Hoffmann is commemorated in Bayer's corporate history and the National Inventors Hall of Fame as the creator of Aspirin, the discovery became the subject of historical re-evaluation:

* **Arthur Eichengrün’s Claim (1949):** Hoffmann’s superior at Bayer, Arthur Eichengrün (a Jewish chemist), published a paper in 1949 asserting that he was the project leader who conceived the synthesis and directed Hoffmann to carry it out. Eichengrün argued that his contributions were deliberately erased during the Nazi era in the 1930s when corporate and state histories sought an Aryan inventor.
* **Historian Walter Sneader (1999):** Sneader supported Eichengrün's claims, arguing that laboratory notebooks and circumstantial patent evidence pointed to Eichengrün’s direction.
* **Bayer’s Corporate Position:** Bayer reviewed its archives and issued statements reaffirming Felix Hoffmann as the discoverer. Bayer maintains that Hoffmann's August 10, 1897 laboratory notebook entries specifically credit his own chemical synthesis, and that historical documentation does not substantiate Eichengrün's claim to primary authorship of the drug’s creation.
sources:
  - bayer.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG9Nm0YhTPAqh8J2YUE88fiiLxFWGHUKTV7Hosr4A9aKHr0PpAN9cmmCpqeEtjq_6L6fS8crMllpmpFxNJ5fhSUCoy7w3OuvNwsgU0MmnlMapnJBClNeIEXiOgWIdLW0WyMHJpaHumREl2Q5YujorYm3N630isnAtEfCZBw0rW-01Svij_nH67Q70JVmQ9C0aqZbkHDn6lllEOLSRZSNyvoFQ==>
  - bayer.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEPCVaCjBBTFKA23mV1--E8NRRszgd5MJJENTmtmNQqm407Pix9uLoh1vJVafdLN2wsXT7_mJuvdOF3l5BXpx9Oi39mslpfWpDOSravqkoxAP3quW9t_QFCt5IgCalJaErxGFSCrQ==>
  - mit.edu <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEJZ8OF8Z5x_Tk8TQRvLxuSrjuYjMS-hUV4MTan24H3DaLxo6aYu1MuA1R3q54KQVzzI3zVLJ2R4EG9VKrTp1WtqdTwvPcVVFLQ5KRcDItEjvfmHBmc2VR3qBCMfmbIM7zz0oDdAQg=>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGpDSpDI4TgCYCjqVRQhc3lF-jx6qspa7NAVNqx29QWwkRLc-1_VdvUbAY8MwnLk8whUIDUcDvs76RD5a6Vxwf7o9Wde6L-Rt5uGFfOFLml3igOMSQ0XZ7MIk1pDM8mcXpzI19kRj3b>
  - aspirin.sa <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG_dWsboNSyrWoyw5RZOvvLsLRWqtVh37nWmGTiANvO8NkBRpWgp516K85HwID7-XlZY3KdtTMwnk-THzphKBRyRVhLXAgodTYhG2vyV7uzC8Agr5YofyZ1bMenCXxeTkfvtX3WTQ==>
  - facebook.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_WYh2cHM3hn4AuWwBl9Zn5Lk8xfhZiIg3sRbEEkLxt5pbqZ5J8cRHpVR8Ab79cjHunc7p_yNdmupqMgv6dxqDKSXZWr-b5K5nz-DzwkObK_XGPz_W6X_RhGN6msHJhLMjumn7d5--zaFqoETkFJFhGuqfbfm-niky2N2E-tlJ7iqS33w934tzH86LRMgB98Ln5YqEjqZhzYlI-mcbJvu7D8w-Y69PPtubkco2XI-JV0tK7z4=>

[9] web search for 'en.wikipedia.org Aspirin history Felix Hoffmann Eichengrün'; grounded search summary:
In the history of aspirin (acetylsalicylic acid) as documented on Wikipedia, there is a well-known controversy regarding whether credit for its discovery belongs to **Felix Hoffmann** or his superior, **Arthur Eichengrün**.

---

### 1. Background & Synthesis (1897)
* Acetylsalicylic acid (ASA) was originally synthesized in 1853 by French chemist Charles Frédéric Gerhardt, but it was unstable and impure.
* On **August 10, 1897**, working in the pharmaceutical laboratory of Friedrich Bayer & Co. in Elberfeld, Germany, chemist **Felix Hoffmann** successfully synthesized ASA in a pure, stable form. 
* Bayer began marketing the drug under the trade name **Aspirin** in 1899.

---

### 2. The Traditional Narrative (Felix Hoffmann)
* **The "Rheumatic Father" Story:** According to Bayer’s traditional corporate history, Hoffmann synthesized the drug independently to find a pain reliever for his father, who suffered from crippling rheumatoid arthritis and could not tolerate the stomach irritation caused by sodium salicylate.
* **Origin of the Story:** This version first appeared publicly in **1934** in a footnote in a history of chemical engineering written by Albrecht Schmidt, an IG Farben chemist.
* **Patents:** Hoffmann's name appeared on the 1899 U.S. patent for acetylsalicylic acid. Bayer has officially maintained that Hoffmann was the inventor.

---

### 3. Arthur Eichengrün’s Claim
* **Supervisor Role:** Arthur Eichengrün, a Jewish-German chemist and materials scientist, was the head of pharmaceutical research at Bayer and Hoffmann’s direct superior.
* **Directing the Synthesis:** Eichengrün asserted that Hoffmann had acted purely as a bench chemist following his specific instructions to synthesize acetylsalicylic acid, without understanding the overarching research program.
* **Overcoming Resistance:** When Bayer’s pharmacology department head, Heinrich Dreser, rejected ASA as potentially toxic to the heart, Eichengrün claimed that he secretly arranged clinical trials with physicians (and tested it on himself) to prove its safety and effectiveness.
* **Anti-Jewish Revisionism:** Because Eichengrün was Jewish, his contributions were systematically erased or minimized in Germany during the rise of Nazi rule in the 1930s (when the 1934 Hoffmann story was published). Eichengrün survived World War II after being imprisoned in the Theresienstadt concentration camp.
* **1949 Paper:** In 1949, shortly before his death, Eichengrün published a paper in *Pharmazie* titled *"50 Jahre Aspirin"*, laying out his claim as the true originator and director of the project.

---

### 4. Modern Historical Reappraisal
* In **1999**, Walter Sneader, a pharmaceutical historian at the University of Strathclyde, conducted an analysis of laboratory notebooks, internal Bayer documents, and patent records. 
* Sneader concluded that **Eichengrün's account was credible**, showing that Hoffmann was working on a series of salicylic acid derivatives conceived by Eichengrün, and that Aspirin likely would not have reached the market without Eichengrün's intervention.
* **Bayer's Response:** Bayer issued a press release disputing Sneader's conclusions, stating that Hoffmann was credited as the inventor on early patents and maintaining the traditional attribution.

---

### Summary
* **Felix Hoffmann:** Credited with executing the chemical synthesis of stable, pure ASA on August 10, 1897.
* **Arthur Eichengrün:** Credited by many modern historians as the planner, director, and champion of the research who pushed the drug through testing and clinical adoption, but whose credit was suppressed during the Nazi era.
sources:
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUsQGCy95L29o2aNWF2uS9Kz8GUpLiCgQzxMpBU5kqymtpYsiWew8fLAU7wk84PdmEmHgI6vPSYlkZcLpn5mn9DomUtDZLmOLKxITqGkFv5BY3VLxvoi0pMyyv7knykp4GfRub_AceNN_B>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgNM3srBUwY4Jnt7UmSL76jKKA_v3qZst94bhyweKg-rmTa4bH43tPljt4LFa8WIspi7iGRTnR-M8LDb2L3jEiN9ng8t193KlKsiY68jKdORDVbIZSFV9lO9vuJYTHFI8-7w==>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJrojHTygXjPBzahhkXmf3mcZnd061F-AResRhPhURyzYaOFtRM9BlNb7sGHorI3yXdAfLbToWI4VQ4d_Q2eF330SLuH7x3VXapxTCw6jvp2tG5FxCyk0M2dsW>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAj5hcblLQz8nxprVZ1AxcZXmZiOkKpYdZxADAt2rbvzAauTFMhXLlNQ2se9EH-6qsYo7wB3xshxAG7hbpYf51ye2ZngpcJgpYAJtoGsVPETRKo4hx2cpWq26-xUAbZdBnbvGz-TfG>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGAhvn0XkeVXt0RfC34zjq8aIUCCVZqi572tT-oPC93oIRqeKg0ie33TBd78wNiqzVn1Yb7SAgnsN1KeVNKSt07qEDGA6807m9f2YP85Xy6p2wImle6nGQtPOq3oESdU0V4Id-QCSc=>
  - worldneurologyonline.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEq7nBrCiJLx8km7UnYn-aAORE-Yt-GdJDCRhi2fegZS4OkztegNQGDxlE681E8QUPQy4l4DOI_-NMOLeR4JTWWVXLgwfCeoBPc8snebfr3uYjCNyE-6vGVEYn42YPNOzkB3TOhNbuItgSlNEWd-sEEhnn1MQx6MyE_UhU=>

[10] web search for 'Sneader "The discovery of aspirin: a reappraisal" BMJ 2000'; grounded search summary:
**"The discovery of aspirin: a reappraisal"** is a landmark historical paper written by Scottish pharmaceutical historian **Walter Sneader** (University of Strathclyde) and published in the *British Medical Journal* in December 2000 (*BMJ* 2000; 321(7276): 1591–1594). 

The paper directly challenged the long-accepted history regarding who discovered aspirin (acetylsalicylic acid, or ASA) at the German dye and chemical firm **Friedrich Bayer & Co.** in the late 1890s.

---

### 1. The Traditional Narrative
For decades, popular history and Bayer’s corporate history attributed the discovery solely to **Felix Hoffmann**:
* **The "Filial Piety" Story:** Hoffmann was said to have synthesized pure, stable acetylsalicylic acid on August 10, 1897, motivated by a desire to find an effective pain reliever for his rheumatic father, who could not tolerate the stomach irritation caused by sodium salicylate.
* **Origin:** Sneader demonstrated that this story did not appear in any contemporary late-19th-century records. It first surfaced in **1934** as a footnote in a history of chemical engineering written by Albrecht Schmidt.

---

### 2. Sneader’s Reappraisal: The Central Thesis
By examining Bayer’s archival laboratory logs, internal company documents, and historical correspondence, Sneader concluded that:

* **Felix Hoffmann acted under orders:** Hoffmann was a junior chemist following laboratory instructions rather than acting on his own independent initiative.
* **Arthur Eichengrün was the mastermind:** **Dr. Arthur Eichengrün**, the head of pharmaceutical research at Bayer, was the intellectual originator of the project. Eichengrün assigned Hoffmann to synthesize acetylsalicylic acid as part of a systematic program to find less toxic derivatives of salicylic acid.
* **Overcoming internal opposition:** When the head of pharmacology at Bayer, **Heinrich Dreser**, dismissed acetylsalicylic acid—falsely believing it caused cardiac toxicity—Eichengrün circumvented Dreser by covertly organizing clinical trials with physicians (such as Dr. Felix Goldmann and clinician Julius Wohlgemuth). The clinical results were so overwhelming that Bayer was compelled to commercialize the drug in 1899.

---

### 3. Why Was Eichengrün Erased from History?
Sneader addressed why Hoffmann received the credit while Eichengrün’s role was largely erased:

* **Antisemitism in Nazi Germany:** Arthur Eichengrün was Jewish. During the rise of the Third Reich in the 1930s, the Nazi regime systematically expunged Jewish contributions from German history and science. The 1934 account crediting the "Aryan" Felix Hoffmann aligned with Nazi racial ideology.
* **Persecution and Theresienstadt:** Eichengrün was stripped of his company, arrested, and sent to the **Theresienstadt concentration camp** in 1944. While imprisoned there, he wrote a letter detailing his pivotal role in developing aspirin. 
* **Post-War Reassertion:** Eichengrün survived the Holocaust and published an account in the German journal *Die Pharmazie* in 1949 titled *"50 Jahre Aspirin"*, but he died later that same year, leaving the traditional Hoffmann narrative largely intact in popular consciousness until Sneader's research revived the debate.

---

### 4. Impact and Company Response
* **Bayer's Position:** Following the publication of Sneader’s paper, Bayer AG issued a statement contesting Sneader's conclusions. The company maintained that Hoffmann remained the sole inventor named on the U.S. patent and that Eichengrün was only a supervisory figure rather than the principal inventor.
* **Scholarly Consensus:** While some debate remains regarding the exact distribution of credit among Eichengrün, Hoffmann, and Dreser, Sneader’s paper successfully dismantled the simplistic "father's rheumatism" myth and restored Arthur Eichengrün’s central, indispensable role in the development and clinical adoption of aspirin to modern historical scholarship.
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG4qGXGSj5SOUZezzLOc508VtfMRR1xX0V6NyUob-MFHPQS2wzFXjwHdPVcAa1zujaH8XgISREfkeleqAGKP2r9Ob2Q9cO5kM0P9s7IVe0nSv46bAHZWS1A5VInaP5qG_wrlctW7YQo>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmQXGuw5e_Mu6XAYdW1Q7WOmVjl8QTbbNL03eaEFacUPjPdlAdvgMrfs-_sAUBASmEs6-yXHmBvHrYmPBHpkdbPDOEA1yBdvPiBFtbNO_VwZk1Ncs-yHbt5Zw4a-JevA==>
  - pmlive.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh5dOB_avpmC4SdRXJTliqfJpx51u9S-tVLGY5YmEzbiaE3zHzLVbj3mCAgq_PAc7mNYQkwGtKeJWA5T7ruwrZB-d6CS4j6hEW-qNRLvtb3TY0j3RIWX0GtRsC6SLGQN9-NfRnPjPlWQRHMBzdEUHAWKIw3IA=>
  - hekint.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEwy3ZphqNUAhL8Cx_M5518ivsdRFIy13PZng4gQTX_L-6EjUZQunqnPeyb7eLPgZQn-zwG31C7wEeFUKynBLqisQIs3bg8QqV7RZzACwQWVRvAXpbRvqKVLylTrpWSDHmVQj8dl3a8I8i29YiSmgY=>
  - worldneurologyonline.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHg77hQqLE08yS102TTx3bMPHfH7WilPfhAonWCdfOsVnkY2d9SYrPJENk6BmcDIDL6AEDes7PZ7-BxWIyODfMDSob5t7ObYYhxTnDRLgGA3cJDUtikx2yLz2eYpZbJahQYGTH5a3hC9iIMmkoAY_Oqyi6Cb40fHdXjRCI=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHX-FUch7eiNWHDAWYhlYyGiMP77LDxbI2N9m_pY5Y4wrKjjw50OLWkLxJb--wiMHNw6U0kXcJT-M-0UMX2S3zhop8QP2q04vSfQWpyHExTxRo4c5prqP-LADkWwHHe2GjHHLVS6sQ=>

[11] web search for 'Chemistry World aspirin history Hoffmann Gerhardt 1853'; grounded search summary:
The history of aspirin linking **Charles Frédéric Gerhardt (1853)** and **Felix Hoffmann (1897)**—a narrative frequently covered by chemical historians and publications like the Royal Society of Chemistry’s *Chemistry World*—is one of the most famous case studies in drug discovery and industrial chemistry.

---

### 1. The Precursors: Willow Bark and Salicylic Acid
For centuries, extracts from willow bark (*Salix*) and meadowsweet (*Spiraea ulmaria*) were used as folk remedies to treat pain, inflammation, and fevers. In the early 19th century, chemists isolated the active glucoside **salicin** and subsequently prepared **salicylic acid**. 

While salicylic acid and its sodium salt were effective antipyretics and analgesics, they had major drawbacks: an unpleasant taste and severe gastric irritation, which frequently caused nausea, vomiting, and stomach bleeding.

---

### 2. Charles Frédéric Gerhardt (1853): The First Synthesis
In **1853**, French chemist **Charles Frédéric Gerhardt** was investigating the synthesis of acid anhydrides. During his experiments, he reacted acetyl chloride with sodium salicylate. 

* **The result:** Gerhardt successfully produced acetylsalicylic acid (ASA) for the first time.
* **Why it was overlooked:** Gerhardt referred to his product as *salicylic-acetic anhydride*. He did not fully characterize its structure, obtain it in a highly pure or stable state, or test its therapeutic properties. Following his premature death in 1856, his synthesis was largely forgotten in academic literature for over four decades.

---

### 3. Felix Hoffmann and Bayer (1897): Rediscovery and Purity
In the late 19th century, the German dye company **Farbenfabriken vorm. Friedr. Bayer & Co.** expanded into pharmaceuticals. 

* **The Breakthrough (October 1897):** German chemist **Felix Hoffmann**, working in Bayer’s pharmaceutical laboratory under the direction of Arthur Eichengrün and pharmacology head Heinrich Dreser, reviewed previous chemical literature and developed a practical, reproducible method to synthesize pure, stable acetylsalicylic acid using salicylic acid and acetic anhydride.
* **The Legend:** According to Bayer’s official history, Hoffmann was motivated by his father’s debilitating rheumatism; his father could no longer tolerate the severe stomach pain caused by sodium salicylate.
* **The Eichengrün Controversy:** Decades later, Arthur Eichengrün (who was Jewish and had survived the Theresienstadt concentration camp during WWII) published claims that he had directed the project, devised the research plan, and championed the clinical testing of acetylsalicylic acid after Heinrich Dreser initially dismissed it as harmful to the heart. Historians, including Walter Sneader in 1999, supported Eichengrün’s account, suggesting Bayer credited Hoffmann primarily to erase Eichengrün's contribution during the Nazi era.

---

### 4. Patenting and the Name "Aspirin" (1899)
* **Patent Hurdles:** Because Gerhardt (and later Karl Kraut in 1869) had already described acetylsalicylic acid, the German Imperial Patent Office **denied** Bayer a patent on the compound itself, deeming it not entirely novel. Bayer was, however, granted patents in the United States and elsewhere for Hoffmann’s specific manufacturing process and pure form.
* **The Brand Name:** In **1899**, Bayer registered the trademark **Aspirin**:
  * **"A"** for *acetyl*.
  * **"spir"** for *Spiraea ulmaria* (the meadowsweet plant, which yields salicylic acid derivatives).
  * **"in"** as a common commercial pharmaceutical suffix.

---

### Key Historical Takeaway
* **1853:** Gerhardt achieved the chemical synthesis of ASA, but left it crude, unpurified, and untested pharmacologically.
* **1897:** Hoffmann (within the Bayer research group) perfected its synthesis in a pure, shelf-stable form suitable for clinical therapy.
* **Significance:** Aspirin marked one of the foundational milestones of the modern pharmaceutical industry—transitioning medicine from crude natural extracts and irritating simple chemicals to rationally optimized synthetic compounds.
sources:
  - facebook.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDSZ-RDW9qbHi8ipxvRg0xGQkgfgbpW5FFaDPpL2lHBJnY2aCyAwkum91AqiLu-8ZIPFf527nCLmKGGTORp6pXKHiK0cWrLqD9asGGq4zLbXuZyGXr5hzA4CoWhkiNC2O0XciD69Y6CuSmt-WyOAI80p-5MnmVquBGfeULNw==>
  - chemistryworld.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDbF6nGTAg-AYQnmjV8OrTZP2OKKpspJCWwqWWZLh2qSych0g-kZ0BzI7EykVvLjkHNHoDwxJi4YIM2VooEfHNStvOsh5l5MmDlYYBJhyd6J2Q6GfhE0ASaCsiAF8353PUmW6bQFcyipY1ZAZYuKQ-ztIQZpnxuZoTbizdjPPyfwpuPA==>
  - pharmaceutical-journal.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgV38fd7_GYflkZj8FYBWc0FGFaddrdxtkn6G3jzLMd3-GtmYBk8LlnvRVJ0czU1jW6AxHsUnNgrWJd6-HnTY88_zhXGKy_vKH640XfakbfC6ieNNPqw2DjSIf-Ig9FGUrQ0WU79yZfAh6sZtyc0SN-elKDo3aOMYeqAZL9N-RGekv>
  - bris.ac.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQvnZZgjoXLDK70O3vuJEv-sjILYaJ9jolXi24VqOU3Sv2MTAoix7UDcwX3_N7uPuvZoXi3Bp7aaV7RctdarKCAJ24EBu6XpjJ0Cg_ZBYBQOzk2hxan5biyGGP0P6ecQdG8vOiYEuXIwyE_A==>
  - bris.ac.uk <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGT3qpdSF9lojq722Xk7YTCsxri-jrezRTJ5CkQVTVxqIRjzMCiQNLYp_CObvsBNKg6YvBDE933pOxXA7gI0KavefJWKkbZ-wSOIklnwGeNlBRtGqYYN_zK6dPZbpAQkAeFGYv_8MG3a8K>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHqNtdHG88REJM98Wa_P-p7pIS2cGLt3HqZRNwd2tn2_fwNBTQsZIOvYqCFGKvIf0xd4nQvEgNYAFUL2hVCWJPD7BMP0neltm9-A6TCAujTEh50fB878kMNGyasW8nwC_8PsMaq7nBrPofk2XKYkV1YOpUXVRtE_5vSOvE2EDVSprT4SpU3AkIAZbxLqJIKgSH-wKm_og0XfiQ9D-qjEmktNg==>
```

</details>

**Answer:**

## Answer

**Felix Hoffmann**, a chemist at Bayer (Farbenfabriken vorm. Friedr. Bayer & Co., Elberfeld, Germany), is credited with the first synthesis of acetylsalicylic acid (ASA) in a **stable, chemically pure form**, in **1897** (frequently dated to a laboratory notebook entry of **10 August 1897**).

## Supporting detail

| Item | Detail |
|---|---|
| Person | Felix Hoffmann (joined Bayer 1894) |
| Year | 1897 |
| Method | Acetylation of salicylic acid using acetic anhydride |
| Significance | First *stable, pure, medically usable* ASA — the basis of Aspirin |
| Trademark "Aspirin" | Registered **1899** (sources often cite 6 March 1899, German Imperial Patent Office) |
| Market launch | **1899** (powder form) |

## Important context and caveats

- **Not the first-ever synthesis.** Charles Frédéric Gerhardt produced an acetylated salicylic acid in **1853** (acetyl chloride + sodium salicylate), but it was impure and unstable, was never characterised clinically, and Gerhardt died in 1856. Later work is also attributed to Hugo von Gilm (1859) and Karl Kraut (1869). Hoffmann's credit is for the **first stable, pure form**, not the first molecule.
- **Credit dispute.** **Arthur Eichengrün**, Hoffmann's supervisor, claimed in 1949 (in *Die Pharmazie*) that he had conceived and directed the work. Because Eichengrün was Jewish, this contribution was suppressed in print during the Nazi era, and the familiar "Hoffmann synthesised it for his rheumatic father" story first appeared in **1934**. Historian **Walter Sneader** argued in the *British Medical Journal* (2000) that the archival evidence supports Eichengrün's version; **Bayer rejected** this and maintains Hoffmann as the named inventor (U.S. Patent 644,077, 1900). Most modern accounts describe the development as collaborative.
- **Heinrich Dreser**, head of Bayer's pharmacology lab, is reported to have initially rejected ASA before later overseeing testing and publishing on it in 1899. Bayer could not obtain a German product patent (prior art), but secured a U.S. process patent in 1900 naming Hoffmann.

## Source and verification note

I found **no attached reference files** in this session's working directory, so this answer rests on public sources only. The Network Search Agent retrieved results from **bayer.com** (corporate history), **wikipedia.org** (Aspirin / History of aspirin / Felix Hoffmann), **nih.gov**, **dpma.de** (German Patent and Trade Mark Office), **chemistryworld.com**, **pharmaceutical-journal.com**, and **mit.edu**, among others.

**Limitation:** the search tool returned its links as obfuscated redirect URLs rather than canonical page addresses, so I cannot supply verifiable direct links without risking fabrication. If you need exact citations (e.g., the specific Bayer history page or Sneader's BMJ 2000 article, *BMJ* 321:1591–1594), tell me and I'll target those specific sources for canonical URLs.

---

## 24. web-12 (web, easy)

**Question:** In what year did the WHO publish its first Model List of Essential Medicines?

**Gold answer:** 1977.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] web search for 'WHO first Model List of Essential Medicines year published 1977'; grounded search summary:
Yes, that is correct. The World Health Organization (WHO) published its **first Model List of Essential Drugs** (now known as the *WHO Model List of Essential Medicines*) in **1977**.

### Key Facts About the 1977 List:
* **Publication:** It was published in October 1977 as part of the *WHO Technical Report Series, No. 615*, titled *The Selection of Essential Drugs*.
* **Contents:** The initial list contained approximately **208 individual active substances** deemed basic, indispensable, and necessary to meet the health needs of the majority of the population.
* **Significance:** It established the global concept of "essential medicines"—shifting the focus toward safety, efficacy, quality, and cost-effectiveness rather than market-driven proliferation of pharmaceutical products.
* **Legacy:** The list has been updated every two years since its inception and serves as a global standard to help countries prioritize procurement, distribution, and reimbursement policies.
sources:
  (none)

[3] web search for 'WHO Model List of Essential Drugs 1977 World Health Assembly resolution WHA28.66'; grounded search summary:
The relationship between **World Health Assembly Resolution WHA28.66** and the **1977 WHO Model List of Essential Drugs** represents the founding moment of modern global pharmaceutical policy and equitable access to medicines. 

---

### 1. Resolution WHA28.66 (May 1975): The Mandate
During the post-colonial period of the early 1970s, developing nations were spending massive portions of their limited healthcare budgets (often 25–40%) importing thousands of costly, branded, and sometimes ineffective pharmaceutical products. At the same time, rural and impoverished populations lacked access to basic, life-saving medicines.

In response to pressure from these countries, the **Twenty-eighth World Health Assembly (WHA)** adopted **Resolution WHA28.66** in May 1975. 

* **Key Directives of WHA28.66:**
  * It formally requested the WHO Director-General (then Dr. Halfdan Mahler) to develop means to assist Member States by **advising on the selection and procurement, at reasonable cost, of essential drugs of established quality corresponding to their national health needs**.
  * It urged the establishment of national drug policies that prioritized rational use, local production where feasible, and quality control.

---

### 2. The 1977 Model List: The Fulfillment
Guided by the mandate of WHA28.66, the WHO convened the first **Expert Committee on the Selection of Essential Drugs** in Geneva in October 1977. 

The committee published its landmark report as **WHO Technical Report Series No. 615**, titled *The Selection of Essential Drugs*, introducing the first **WHO Model List of Essential Drugs**:
* **Number of Drugs:** It contained roughly **208 to 212 active substances** (such as aspirin, penicillin, ether, and oral rehydration salts) deemed sufficient to handle the vast majority of global health conditions at the time.
* **Core Definition:** Essential drugs were defined as those *“of utmost importance, and are basic, indispensable and necessary for the health needs of the population”*—meaning they should be available at all times, in adequate amounts, and in appropriate dosage forms at an affordable price.
* **Selection Criteria:** Inclusion was strictly based on proven clinical efficacy, safety, public health relevance, and cost-effectiveness (rather than commercial popularity).

---

### 3. Historical Impact and Significance
* **Foundation for Alma-Ata (1978):** The work started by WHA28.66 and the 1977 list became a cornerstone for the 1978 **Declaration of Alma-Ata**, where the *“provision of essential drugs”* was established as one of the eight core pillars of Primary Health Care.
* **Creation of the Action Programme:** Following further resolutions (e.g., WHA31.32 in 1978), WHO established the **Action Programme on Essential Drugs** in 1981 to help countries implement their own national formularies and supply systems.
* **Shift to Generic Prescribing:** The initiative challenged the commercial pharmaceutical market by advocating for procurement under **International Nonproprietary Names (generic names)**, reducing costs and monopolistic pricing worldwide.
* **Enduring Legacy:** What began under WHA28.66 has evolved into the **WHO Model List of Essential Medicines (EML)**, which is revised biennially and serves as an authoritative procurement and reimbursement template for over 150 countries.
sources:
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqyzSoTWE30Q42ixS2FCySEq9_MiZOs0WLLkMpc0Y9eTXz0H1qAg5alF-7Yh1csbFwIEvTyoONwhswi4MueLKWi2iyVvR43hvJs0DafvGhuhJpz_dLVgHOsW6-wy0vb38L0_VvnYao>
  - worldbank.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGitR-t0aJjD-wGjFbGEfARf5NOnujxwskY8qjQu4ynDicxMM3HKajgAlixlbvn2eVjzkrTs-ql6lIxSp3-dGkCBm9zlK2MD5QxIP2McgbCa3Q7_SWqgXH6QTKySx1ljvJathgDxEPOizDJSg9ZSbB3scCdSemGJ8wmX2wifMd1FKgygkSmQmAH_OqN0ZhMp-Ey2NXRdoZmLIaygMPSBBiyoEbbo8ejUBqD>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFd0RsYt8WM4gkl9g3eHwn4d77bAoYBtzxZZet9BubzYSk-W7eYIECDLEKLmUdM2Oa1Eq0UW1MgJiTHbGr0zWRcyl0aRA7CS39T6vg5D3XXfeeJSzzUZUA6AhXD2Hf079C31aD5G3xxqQ==>
  - researchgate.net <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHVDKK_-2pabpJpFP9JBHzpcthIW0EwriTJfxo6QDB0aaGLdIrdOcYCnFFlrpcEw-JTG6qbR6ulm0r7aqhMPSWUntnOVQ9JszjX65Lzo8YYnwA-TSbHuEwuf_bUHuzcRrplGM-4xqt455LbJrVEw5khDZ20eVong5MwVB6CAuo5Ly8gfzaNklYBxFG8zNu6qcf7AXrymu7BdD6F12Wxqa_jrLVfCweWcBEVeTqQeo_6nqU5jH_Uajw4CPNnK8gr7ZVuTZDHh1Cd6t2Abh3u>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEDjGe-m0-lxLgtt3oT3bagaOdP7C2g7KWe4zqRBxZxEyvxsGylDGxj_ksBM_9J6lqid768MtZrjfHiLUas3vlx4b2pQgpcHqkeTeyg936KgFfVlsT2pstVNHH6xKC7uoXd_Z_kEK9jAswkzaUcVLp6Cs-p9W9p_7Ya>

[4] web search for '"Model List of Essential Medicines" WHO history first published 1977 40th anniversary'; grounded search summary:
The **WHO Model List of Essential Medicines (EML)** is a landmark global health tool that identifies the medications considered most effective, safe, and cost-effective to satisfy the priority healthcare needs of a population. 

A summary of its origins in 1977, evolution, and its 40th anniversary milestone in 2017 outlines the history of this public health initiative:

---

### 1. The First List (1977): A "Peaceful Revolution"
* **Origin:** In the 1970s, low- and middle-income countries faced severe disparities in drug availability, wasting scarce resources on non-essential, expensive, or ineffective brand-name drugs while lacking access to basic life-saving treatments.
* **The 1977 Release:** In October 1977, the WHO Expert Committee on the Selection of Essential Drugs convened, publishing Technical Report Series No. 615. 
* **Scope:** The first list contained **208 active substances** (often cited as ~200 items).
* **Impact:** Often referred to in public health as a "peaceful revolution," the list shifted the paradigm by establishing that healthcare systems should prioritize access to a limited, carefully evaluated core group of medicines rather than an unmanageable pharmaceutical market.

---

### 2. Major Evolutions (1980s – 2000s)
* **Biennial Revisions:** The WHO instituted a policy of updating the list every two years to reflect emerging diseases, advancements in pharmacology, and changing epidemiological priorities.
* **Shift to Evidence-Based Medicine (2002):** The selection process transitioned from expert consensus to formal, transparent, evidence-based methods incorporating rigorous comparative efficacy, safety, and cost-effectiveness data.
* **High-Cost & Patented Medicines:** In the early 2000s, the WHO took the historic step of adding antiretrovirals (ARVs) for HIV/AIDS. This established the precedent that patent status or current high price should not preclude a medicine from being deemed "essential," using the list as leverage to lower global drug prices.
* **Pediatric List (2007):** On the 30th anniversary, the WHO launched the first **Model List of Essential Medicines for Children (EMLc)** to address the systemic neglect of child-appropriate formulations and dosages.

---

### 3. The 40th Anniversary (2017)
The year 2017 marked **40 years** of the Essential Medicines List, commemorated by the release of the **20th Model List of Essential Medicines** (and the 6th EMLc):

* **Major Revisions:** The 2017 update included **433 medicines** in the adult list, reflecting four decades of medical innovation.
* **The AWaRe Antibiotic Framework:** One of the most significant changes introduced at the 40-year mark was the **AWaRe** categorization of antibiotics to combat antimicrobial resistance (AMR):
  * **Access:** First- and second-choice antibiotics for common infections that must be widely available, affordable, and quality-assured.
  * **Watch:** Antibiotics with higher resistance potential, recommended as first- or second-choice only for specific, limited indications.
  * **Reserve:** Last-resort antibiotics (e.g., colistin, newer cephalosporins) protected for confirmed multi-drug-resistant infections.
* **Expanded NCD and Specialty Care Coverage:** The 2017 list added breakthrough treatments for non-communicable diseases and viral infections, such as:
  * Direct-acting antivirals (DAAs) for curing **Hepatitis C**.
  * New systemic therapies and targeted therapies for **cancer** (e.g., trastuzumab).
  * New formulations for oral pain and palliative care.

---

### Global Impact
Today, over **150 countries** base their national essential medicine lists, public procurement policies, and reimbursement formularies on the WHO Model List. It remains one of the WHO's most influential instruments for advancing universal health coverage (UHC) and global health equity.
sources:
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5u4qaIHO8bF4QezN19OFFtBtDFzMB3V72MbW09loqG4tWTtzX8Xvfhq4ZIgw-F8gTGxCfvgiGrY9cP-R8RPUoL3-IuJniyEL4OrdLaEda0TNCIEPohPzC9cCK2olkYuQ8RE4=>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnVLkZVYB1GO_mVHyLc_0Xt2vM-JM2-lNYGG-wmtLvOXeytazXlM8f4tS3LMyoxs3-PQniIg1rSLlDjG6Tjpy62NsmYIsp63vFESI5Md5E1m8ovzEn1_Fz_Z7H2lIFtYSLvtrk1a5RYX8zQdRF-EDEqZkprTtKuZQ=>
  - rethinkpriorities.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGymOm-WWiWxhfbH_tgRj1xeOEiw51tOcAKvTn-2YeUtK5dyZ4m8skxk4pjYRGxx5f6VSBEd5y4AM_VUrBT_1-YxhjR-IS_PjALhyINbeILI5azPAAjIbyv0Ln71IyegZ6vA5p00ECITy1o4QFl-U5iA_cnEPiRmGOcmb70y8Q=>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH7iGoQ3BO5Lc7ufKc717eLnMMQs8W3CUtBTyyS5Dknzf6sWIX8-lW1wzSnf-pqX6fxTmR28o65hR2k9ojCXPK5eD2gcZlsR-a2SK-TIYCcRkwMC3t2NIkXBSOymyC4jT8nrXAgrlYu>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKt_at-FEo77sQNfJ5cXyb2jt4bxSEtrxmLmWzRCsv7qeeDbfaXNm9Z9iXmT6g8oVuaG2U9eQmz9Lwwc4ypmS5nS7oYNbVKNaHk1eJjz047nbgONw1I9AWGrNs81wONGvQxC5u6QFGq9GJzm2cFRdiMIb0rYzYieGx>

[5] web search for 'WHO Technical Report Series 615 "The Selection of Essential Drugs" 1977 first list 208 medicines'; grounded search summary:
**WHO Technical Report Series No. 615 (1977)**, titled ***The Selection of Essential Drugs***, is one of the most influential public health documents of the 20th century. It marked the official launch of the **first WHO Model List of Essential Drugs** (now known as the *WHO Model List of Essential Medicines* or EML).

---

### 1. Background and Historical Context
* **Convened:** October 17–21, 1977, in Geneva by the WHO Expert Committee on the Selection of Essential Drugs.
* **The Problem:** In the 1970s, pharmaceutical markets were flooded with tens of thousands of drug products, branded variations, and ineffective fixed-dose combinations. Developing countries in particular were spending large portions of limited healthcare budgets on costly or low-value drugs while basic lifesaving medications remained unavailable to the majority of people.
* **The Revolution:** TRS 615 introduced the principle that **a carefully selected, limited set of safe and effective medicines could satisfy the health needs of the majority of a population**.

---

### 2. The 208 Medicines Figure
* The 1977 model list identified **208 individual active pharmaceutical substances** (frequently cited as roughly 200–212 depending on whether salts, specific formulations, or complementary candidates are isolated).
* These 208 medicines were deemed sufficient to treat the vast majority of global communicable and non-communicable diseases known at the time.
* By contrast, modern editions of the WHO Model List contain well over 500 active substances, reflecting advancements in oncology, antivirals (e.g., HIV/AIDS, Hepatitis C), and chronic disease management.

---

### 3. Core Criteria for Selection Established in TRS 615
The 1977 report laid down strict criteria that continue to define the EML today:

1. **Demonstrated Efficacy and Safety:** Only drugs backed by sound scientific evidence and clinical trials were included.
2. **Public Health Need:** Medicines had to address the most prevalent and severe conditions affecting the general population.
3. **Cost-Effectiveness:** Consideration was given to the total cost of treatment, not merely the unit acquisition cost.
4. **Quality and Shelf Life:** Assured quality, stability under local storage conditions, and availability of generic formulations.
5. **International Nonproprietary Names (INN):** All medicines were listed under their generic INN names rather than commercial brand names to reduce costs and avoid confusion.
6. **Avoidance of Irrational Combinations:** Fixed-dose combination products were largely excluded unless scientifically proven to show a clear clinical advantage over single-ingredient drugs.

---

### 4. Categorization and Structure
The 1977 list grouped the 208 medicines into roughly 20 therapeutic categories, including:
* **Anti-infective agents:** Penicillins, tetracycline, chloroquine, isoniazid, rifampicin.
* **Analgesics, antipyretics, and anti-inflammatories:** Aspirin, paracetamol, morphine, codeine.
* **Cardiovascular drugs:** Digoxin, propranolol, glyceryl trinitrate.
* **Anesthetics:** Halothane, ether, lidocaine.
* **Gastrointestinal drugs, endocrine agents (e.g., insulin), vaccines, and essential vitamins/minerals.**

It also introduced the concept of **core** medicines (first-line, basic health facility level) versus **complementary** medicines (requiring specialized diagnostic or training facilities).

---

### 5. Lasting Legacy
* **Primary Health Care:** TRS 615 provided the pharmaceutical foundation for the landmark **Alma-Ata Declaration (1978)**, which designated the provision of essential drugs as one of the eight core pillars of Primary Health Care.
* **National Policies:** More than 150 countries have since used TRS 615 as a template to establish their own national essential medicines lists (NEMLs), bulk procurement systems, and reimbursement schedules.
* **Biennial Revisions:** The list has been formally updated every two years since 1977, and in 2007, a dedicated *Model List of Essential Medicines for Children (EMLc)* was introduced.
sources:
  - rethinkpriorities.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU2al-jOCPb5PKpEXW1IivazOO4y4sGQ-AzEwrqiCTl_w3UeyU7Reg_PWILXaHVNFdgE8vtyWAvmU_sqnRBEJRy4hfwzZCZuUdl3Sym9-RUEkUBsKFTj2H5_49pNR4MdKMDpHFPphWWC_LlEb0x7_JIVymyIxMBwc4nrfjVZs7>
  - msf.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1pQQw2Qr1VamhlAd46Z0LjqfZE3N31sez8jrmIv0KwfAUZT7VnUV3y8aUms55KxlC3DzzBT_ZjgO0Ssf0CAJaa4umDTyi6QLmXrtztrOGKj8bDOLpf8eUZpaW8ieeRON1S7rW5n-ZteAXhekjSQJ_qBAdzlbwH-ezsRLukUHA_Ctvx6znSi8XEOFN8yf-4Xzcc842Tw==>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcmWhJZNAh14Gvrf4AX8Aj8_AWSnwd0y2KIp0O9A5XE0Zo9FeWmhVzcrXGSOzGluyLXi7PApYldoNXlfM6flI6kH98QG7iKk8WIlUb8bB-S20_vI8ppeHpRriBT2lc2w6jtsZWny8sLgMsYswlHiwgG-DNkBtFVlz4DrmSsHgs8Gwcl23GC78wDo6RK74NwK3YdFTIUwKXf4alVvdNthH7zixg7tDifQ==>
  - rethinkpriorities.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEU2al-jOCPb5PKpEXW1IivazOO4y4sGQ-AzEwrqiCTl_w3UeyU7Reg_PWILXaHVNFdgE8vtyWAvmU_sqnRBEJRy4hfwzZCZuUdl3Sym9-RUEkUBsKFTj2H5_49pNR4MdKMDpHFPphWWC_LlEb0x7_JIVymyIxMBwc4nrfjVZs7>
  - iomc.info <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgUc_UyN4nGXhJU9IZXLddXaez4Uy6fxo_UqX8V0ROi4J401dxJfQaflJd2oaVJTUopg4RjTV7sCWqapUxwt_UBF3hj79SwMEhAEIvtpa3d2HvU1I0hQRTJ3NLmAcRTy119wb_OOE=>

[6] web search for 'who.int essential medicines list eEML history second model list of essential drugs 1979'; grounded search summary:
The **Second Model List of Essential Drugs (1979)** was published following the second meeting of the WHO Expert Committee on the Selection of Essential Drugs. It established the precedent of reviewing and updating the list approximately every two years.

---

### Key Publication Details
* **Report Title:** *The Selection of Essential Drugs: Second Report of the WHO Expert Committee*
* **Publication Series:** WHO Technical Report Series, No. 641 (TRS 641)
* **Meeting Dates:** 2–6 July 1979 (Geneva, Switzerland)
* **Official Release:** 1979 / January 1980
* **ISBN:** 92-4-120641-1
* **Availability:** Accessible via the WHO Institutional Repository for Information Sharing (IRIS) and the official WHO Essential Medicines history portal.

---

### Historical Significance and Context

1. **Follow-Up to the Landmark 1977 List:**
   The first WHO Model List of Essential Drugs was published in 1977 (TRS 615) with roughly 208 active substances. The 1979 edition was the first formal revision, proving that the Model List was intended to be a living, evolving document rather than a one-time declaration.

2. **Refining the "Essential Drug" Concept:**
   The 1979 report reinforced the definition of essential drugs as those indispensable to meet the health needs of the majority of the population. It further refined the criteria for selection:
   * Documented clinical efficacy and safety.
   * Quality, stability, and bioavailability.
   * Total cost and cost-effectiveness relative to alternatives.
   * Suitability for local disease patterns and health system infrastructure.

3. **Core vs. Complementary Classifications:**
   The 1979 revision continued building out standard therapeutic categorizations and clarifying distinctions between:
   * Main list (core medicines suitable for standard healthcare delivery and primary care).
   * Complementary medicines (those requiring specialized diagnostic/training facilities, rare indications, or used when first-line drugs cannot be given).

4. **Integration with Primary Health Care (Alma-Ata):**
   Following the historic 1978 Declaration of Alma-Ata on Primary Health Care (PHC), the 1979 Model List emphasized the provision of essential drugs as one of the fundamental pillars of PHC. The report highlighted the need for national drug policies, generic prescribing (using International Nonproprietary Names, or INNs), rational drug use, and local training for procurement and distribution.

---

### How to Access the 1979 Report
* **WHO IRIS Repository:** Search for **TRS 641** or **"The Selection of Essential Drugs (1979)"** on [iris.who.int](https://iris.who.int) to download the full 44-page meeting report and drug list in PDF format.
* **WHO Electronic Essential Medicines List (eEML):** The historical records and previous committee reports can be tracked through WHO's [eEML platform and Essential Medicines archive](https://www.who.int/groups/expert-committee-on-selection-and-use-of-essential-medicines).
sources:
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEUmyfBFnxABqUnoUNlxuo3H3vfsV8tYQalZPMyn_Kk7uEyVoCsVsMKxZ8-NeR4-PnvFOt9EFK5vZLra72-or86djUIy8Ig9KHR4wmNcnUFdBXUrqRS8D5UJGNon1l5FBUqlzQcFFraJA==>
  - wikipedia.org <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFEpSqb6KxTBGKHR_mqYajPucWYzqBhf54LEu48ZYNwCsPw7j9eGw1HDebSa-LXRrggiT2ywjnio2UcQ4nVDqGmqAGrG0GfRWOuEY8_TVd1YmaxoSnv-dJlKCgMha7iDVQ9X4B436QA4r6erGtQ9dK5WX2P7Gbqf6Kd>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvid3s1j5o-kR9ZWhJWjQs9SVcTT07K43F63RqzYNpysvDcJys1Z6sOdsGsDZIbHOTLc1UaqMl5cQwOo901jojp1cGAwskqSNaxX8HOwEO7IAJNvHFM6ZdK4eN>
  - nih.gov <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh1srER3SP2Y865iVURb5w3C-z2mo0I9GCHBEPWN3JoyR7L4i8FZawX-8okTEwmngxgfqJbOs7Vgk8HbtpA-jpo4h2qpVVYXZHYnUBQGqvcO7qqi7j6aAZA_4m9-EHsw==>
  - alirahealth.com <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHySUJaC2TOFcCK5NsM0mRNMMU9nCX_nWCtuvUkFj_IsksCEGLa3sqF-hfWDKOj7g9ipO4aQstgWG6EZsQdjJ7rYnG3iJpqiWQRVtzBk3d8QTY91H6-Y68sX6WTKRTT7M3CbJhaMpZDxy33sn2AKENlrJl-t6rHgLEmzc4miOdlXA0WnPGT7GE2wVBNn9jYuNN5SDWB5kdZT5o=>
```

</details>

**Answer:**

## WHO's First Model List of Essential Medicines — 1977

**The World Health Organization published its first Model List of Essential Medicines in 1977.**

| Item | Detail |
|---|---|
| **Year of first list** | **1977** |
| **Title at the time** | *The Selection of Essential Drugs* — WHO Technical Report Series No. 615 (TRS 615) |
| **Original list name** | "WHO Model List of Essential Drugs" (renamed "Essential **Medicines**" in later editions) |
| **Prepared by** | WHO Expert Committee on the Selection of Essential Drugs (met 17–21 Oct 1977, Geneva) |
| **Original mandate** | World Health Assembly Resolution WHA28.66 (1975) |
| **Size of first list** | ~208 active substances |
| **Second edition** | 1979 (TRS 641) |

### Context
The list was created to help Member States select and procure drugs of established quality, safety, and efficacy at reasonable cost — selecting medicines by International Nonproprietary Name (INN). The concept became a cornerstone of the 1978 Alma-Ata Declaration on Primary Health Care, and the list has since been revised roughly every two years (2017 marked its 40th anniversary with the 20th edition, listing 433 medicines).

### Sources
Findings come from public web sources retrieved by the network search agent, including **who.int** (WHO essential medicines materials), **wikipedia.org** ("WHO Model List of Essential Medicines"), and **nih.gov** public-health literature. 

⚠️ **Transparency note:** The search tool returned Google grounding *redirect* URLs rather than direct page addresses, so I cannot provide verified deep links. For the primary document, the authoritative record is **WHO Technical Report Series No. 615**, held in the WHO IRIS repository (`iris.who.int`) — this exact page was not independently verified during the search.

*No files in the working directory were found, so no attached reference material was available to cross-check.*

---

## 25. web-20 (web, medium)

**Question:** What is the WHO ATC classification code for metformin?

**Gold answer:** A10BA02.

**Route:** expected ['internet']; delegated {'Network Search Agent': 1}

<details><summary>Evidence retrieved during the run</summary>

```
[2] web search for 'metformin ATC code A10BA02 WHO ATC/DDD Index'; grounded search summary:
Details for **Metformin** according to the **WHO ATC/DDD Index** maintained by the WHO Collaborating Centre for Drug Statistics Methodology:

---

### **ATC Classification**
* **A**: Alimentary tract and metabolism
* **A10**: Drugs used in diabetes
* **A10B**: Blood glucose lowering drugs, excl. insulins
* **A10BA**: Biguanides
* **A10BA02**: **Metformin**

---

### **Defined Daily Dose (DDD)**
* **DDD:** `2 g`
* **Unit of measurement:** `g` (grams)
* **Route of Administration:** `O` (Oral)
* **Note:** The DDD is an internationally standardized statistical measure of drug consumption for comparative research and does not necessarily reflect the recommended clinical dose for an individual patient.
sources:
  - fhi.no <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMDCW6e4DKoyaaRe4ql6x6qwtyodiVSjnJGOoy_4bQX0YvfN9NmUgF10BJRTcUof5T9UKok97rrqpxttusHO1O6yh4WEmqEd6buv1Cz4KSlDAEruw7vFZhqOg=>
  - icdcode.info <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHTqx82b-MXPS3sqYRQdxANjiY7vm1E0fo0m_ITUOMRhrg_v0tYYgYelkxfsOIT3tkBJGjcRSlnHOvzusRn0MHZHZ4kXl-j6ef1irmk4Evtw1ndNBF_U0CIqToM3FBpDdmjC06IJ9-bz7w=>
  - fhi.no <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_oEQPb7a0wR_vlMLdMCBb839XfH5Iid5zrdeGdm-KxU2arHpUBug3QEbelVgwe4RHZHo4WsJVXZOfWSdkWgmZVx4tahXl2QqUrszu_ISl5xMCq6Hfqx1Iyy6gOCRyirZE3_VoF5aa>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpoSVxCNdY4vWKgndWXtuCPjmVFrzRjzTkP_CLy0bEtuOm5PCub4UknOmoLMyZF1PpUB43uRL4OkCiNv6b_350rBnD5cTPJLmWFTt47WhxZX3vA_lwBufs-ya7PaVbfHwvb-JBbkOexPd8YdDiTfqbFIwUnaN2wF_0qhew_XCtOWFw_g==>

[3] web search for 'WHO ATC/DDD Index 2024 A10BA02 metformin hierarchy names'; grounded search summary:
In the **WHO ATC/DDD Index (2024)**, the full 5-level hierarchical breakdown for **A10BA02** (metformin) is as follows:

| Level | ATC Code | Level Type | Hierarchy Name |
| :--- | :--- | :--- | :--- |
| **Level 1** | **A** | Anatomical main group | **Alimentary tract and metabolism** |
| **Level 2** | **A10** | Therapeutic subgroup | **Drugs used in diabetes** |
| **Level 3** | **A10B** | Pharmacological subgroup | **Blood glucose lowering drugs, excl. insulins** |
| **Level 4** | **A10BA** | Chemical subgroup | **Biguanides** |
| **Level 5** | **A10BA02** | Chemical substance | **metformin** |
sources:
  - fhi.no <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG72OQb-z42ZBr1XB0H1PwI55Sg4xQtsAIByOF7adyKHkI1cPiUpYtrsDeeyQdX_cD5L5JVkohnujLILiunERyO2YlLbGPFd3VXxXAVyd_56y5v_g2AYoPFVWQn8tmnDkXDulXMXo_4rB0=>
  - fhi.no <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLs67UbbgLc20aAZJDerM0xfTGUlAYX4x6Xilp40V2UHGa0-MBTNP3y0WP_mALPXWyAnVkD_IfsrxQ9vWBgNZrRweHYg7zdtqi7NKk_yiwYfS1jdRJnl3H9sDDCUTIjnS62-KZXvRamnDEdpcY_dqMbuMVAi3EARh817NYIjziXKow0Wlmsf1IqzuB5tow9rVDDaI9-ufOeeZV-GU9WWAkQaE=>

[4] web search for 'atcddd.fhi.no ATC/DDD Index metformin A10BA02 DDD 2 g oral'; grounded search summary:
Based on the **WHO Collaborating Centre for Drug Statistics Methodology** (accessible via [atcddd.fhi.no](https://atcddd.fhi.no/atc_ddd_index/)), here is the official ATC/DDD entry for metformin:

---

### **ATC Classification & DDD Details**

| Parameter | Details |
| :--- | :--- |
| **ATC Code** | **A10BA02** |
| **INN / Name** | **Metformin** |
| **Defined Daily Dose (DDD)** | **2 g** |
| **Unit of Measurement** | Grams (g) |
| **Administration Route** | **Oral** (`O`) |

---

### **ATC Hierarchy Breakdown**

* **A** — Alimentary tract and metabolism  
  * **A10** — Drugs used in diabetes  
    * **A10B** — Blood glucose lowering drugs, excl. insulins  
      * **A10BA** — Biguanides  
        * **A10BA02** — Metformin  

---

### **Key Note on DDD**
* The **Defined Daily Dose (DDD)** is a statistical unit of measurement defined as the assumed average maintenance dose per day for a drug used for its main indication in adults.
* It is intended for drug utilization research and **does not necessarily reflect the recommended or prescribed daily dose** for an individual patient.
sources:
  (none)

[5] web search for '"ATC/DDD Index" 2025 version publication who.int atcddd metformin'; grounded search summary:
According to the official **ATC/DDD Index** published and maintained by the **WHO Collaborating Centre for Drug Statistics Methodology** (NIPH, Oslo, Norway):

---

### **1. Metformin (Single Substance Entry)**

* **ATC Code:** `A10BA02`
* **ATC Classification Hierarchy:**
  * **A:** Alimentary tract and metabolism
  * **A10:** Drugs used in diabetes
  * **A10B:** Blood glucose lowering drugs, excl. insulins
  * **A10BA:** Biguanides
  * **A10BA02:** Metformin

#### **Defined Daily Dose (DDD):**
* **DDD:** `2`
* **Unit:** `g` (grams)
* **Route of Administration (Adm.R):** `O` (Oral)
* **Notes:** None

---

### **2. Common Fixed Combinations with Metformin**

Under **A10BD** (*Combinations of oral blood glucose lowering drugs*), metformin is listed in multiple combination codes:

* **A10BD02:** Metformin and glibenclamide
* **A10BD03:** Metformin and rosiglitazone
* **A10BD05:** Metformin and pioglitazone
* **A10BD07:** Metformin and sitagliptin
* **A10BD08:** Metformin and vildagliptin
* **A10BD10:** Metformin and saxagliptin
* **A10BD11:** Metformin and linagliptin
* **A10BD13:** Metformin and alogliptin
* **A10BD14:** Metformin and repaglinide
* **A10BD15:** Metformin and dapagliflozin
* **A10BD16:** Metformin and canagliflozin
* **A10BD18:** Metformin and gemigliptin
* **A10BD20:** Metformin and empagliflozin
* **A10BD22:** Metformin and evogliptin
* **A10BD23:** Metformin and ertugliflozin
* **A10BD25:** Metformin, saxagliptin and dapagliflozin
* **A10BD26:** Metformin and lobeglitazone
* **A10BD34:** Metformin and enavogliflozin

*(Note: In the ATC/DDD methodology, fixed-combination products in `A10BD` are generally assigned DDDs based on average daily dosing count rather than weight).*

---

### **Publication Details**
* **Source:** [WHO Collaborating Centre for Drug Statistics Methodology](https://www.whocc.no/atc_ddd_index/) (affiliated with the Norwegian Institute of Public Health and the World Health Organization).
* **Revision:** The ATC/DDD Index is updated annually each January.
sources:
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFjLtqgvHgfmbKNqHemuqTr7EDRMtez2saA9_XBX6oSScJikAaA7gTMT3vSvNkThgqAdkUwcec5U3mv8tcYCftp969y_ncx2WQflG3HC4_86mV6rsl9DpnjBQuHuOUq7eQfk7l9EWncdo0KlA==>
  - fhi.no <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLcvhBbcj-dgOwMhctqBZhpWWm-1RFTzlfIsgYEobTvD1ANZ6S_RNue4my8H03aQfMSkrC1i5NVPRp9bbw9X7uJ7OYzUT7tNNmAR_2ukn0t5oBL-_UUvx2-hgyabk2GcPGw1Ca-d0A>
  - fhi.no <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOkN4ISBen833za_uDnIBnWXPn34mnkni3U19cDjZsPWRscnbHzgWQYQaI7TT_3QmuhZBkJHDQbOfHDY_fLLrzRlTzgvkFdClp3uEl7ULxa05HjGp8Icabai9XRNJoQ0UjVMzQVSPo>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQ4pX1NZQGc_zN_UOHwF6NfqoqTfnX__c-6-lZfTuu__D35DDSBLkeVIydNbx7w6LO3xxX0lF6zzdnmJzC6yhPhSaKUsZNEfluUOZJKCsgB8qNQ4MWWl-ywTkkTjetnTHj5ELvx8Hgw9n1qXGF5MHjlsR0hhU-vGHxKUwhYN8Yqz8akw==>
  - who.int <https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHt5a6h9NEvLMVCtY7sJGF4ajAhR_mMuZwM2C0GhuVgVT2yzhNR_CyNDDvq-9Q8PJgRwPf5hnsYzmE1U0t-byhXPeZirzbkJzRNZJZ7ge4tfXIHCJwj2iiX3N5Ps_4-vnafBfCh94XyLgvqcluLJjFrdrjnevT1BclpisooFe2Z7ctENw==>
```

</details>

**Answer:**

## WHO ATC Classification for Metformin

**Full ATC code: `A10BA02`**

The ATC (Anatomical Therapeutic Chemical) system has five levels. Metformin's full classification:

| Level | Code | Meaning |
|---|---|---|
| 1 — Anatomical main group | **A** | Alimentary tract and metabolism |
| 2 — Therapeutic subgroup | **A10** | Drugs used in diabetes |
| 3 — Pharmacological subgroup | **A10B** | Blood glucose lowering drugs, excl. insulins |
| 4 — Chemical subgroup | **A10BA** | Biguanides |
| 5 — Chemical substance | **A10BA02** | Metformin |

**Additional details**
- **Defined Daily Dose (DDD):** 2 g, oral route (O). Note: the DDD is a statistical unit for drug-utilisation research, not a recommended individual dose.
- Metformin also appears in fixed-dose combination codes under **A10BD** (combinations of oral blood glucose lowering drugs), e.g. metformin + glibenclamide (A10BD02), metformin + sitagliptin (A10BD07), metformin + dapagliflozin (A10BD15), metformin + empagliflozin (A10BD20).

**Source**
- WHO Collaborating Centre for Drug Statistics Methodology (Norwegian Institute of Public Health, Oslo), *ATC/DDD Index* — https://atcddd.fhi.no/atc_ddd_index/ (mirror: https://www.whocc.no/atc_ddd_index/)

**Notes and caveats**
- No reference files were present in the working directory, so this answer is based solely on public sources.
- The search returned redirect/tracking URLs and did not let me independently confirm the exact current *ATC/DDD Index* edition year from a primary page. The Index is revised annually each January (one result referenced the 2024 edition). For a formal citation, please open the official Index page above and cite the current edition year.

---
