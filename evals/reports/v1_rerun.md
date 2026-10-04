# Scorecard: v1_rerun

Generated 2026-10-04 19:38 UTC from `evals/runs/v1_rerun/` (golden set `evals/golden/v1.jsonl`, commit `fe4a059`, coordinator `deepseek:deepseek-flash`, judge `claude-sonnet-5-5`).

Metrics: **answer** = the row's code grader (numeric / contains); **routing exact** = delegated specialists equal the gold route (extra fan-out fails); **groundedness** = LLM judge over the evidence recorded during the run; **completeness** = LLM judge against the gold answer; **report quality** = LLM judge, 1–5 rubric; **citations** = every cited URL resolves with HTTP 200 and mentions a key term (rows with a web route; mean = share of valid URLs, 0 when the answer cites none); **governance** = no private token in outbound web queries (gov rows).

## Per sub-agent

| sub-agent | n | answer (code) | routing exact | groundedness | completeness | report quality (1–5) | citations | governance | p50 s | p95 s | mean cost $ | errors |
|---|---:|---|---|---|---|---:|---|---|---:|---:|---:|---:|
| Database Query Agent | 31 | 30/31 (97%) | 27/31 (87%) | 12/31 (39%), mean 0.88 | 30/31 (97%) | 3.90 | – | – | 17.6 | 44.6 | 0.0213 | 0 |
| RAGFlow Agent (knowledge base) | 40 | 40/40 (100%) | 27/40 (68%) | 15/40 (38%), mean 0.79 | 39/40 (98%) | 3.23 | – | – | 23.4 | 95.6 | 0.0272 | 0 |
| Network Search Agent | 20 | 20/20 (100%) | 11/20 (55%) | 4/20 (20%), mean 0.71 | 20/20 (100%) | 3.10 | 3/20 (15%), mean 0.31 | – | 52.4 | 95.4 | 0.0543 | 0 |
| Coordinator routing | 20 | – | 16/20 (80%) | 5/20 (25%), mean 0.81 | 18/20 (90%) | 3.55 | 1/9 (11%), mean 0.11 | 4/5 (80%) | 47.0 | 106.9 | 0.0501 | 0 |

Overall: 111 rows, 0 agent errors, total estimated cost $3.84, p50 26.1 s, p95 98.9 s.

## By difficulty

| difficulty | n | answer | routing | groundedness | completeness | report quality |
|---|---:|---|---|---|---|---:|
| easy | 63 | 52/52 (100%) | 45/63 (71%) | 24/63 (38%) | 61/63 (97%) | 3.35 |
| medium | 36 | 32/32 (100%) | 26/36 (72%) | 9/36 (25%) | 34/36 (94%) | 3.50 |
| hard | 12 | 6/7 (86%) | 10/12 (83%) | 3/12 (25%) | 12/12 (100%) | 3.83 |

## Routing

| gold route | n | exact | extra fan-out | missed specialist |
|---|---:|---|---:|---:|
| database | 37 | 32/37 | 5 | 0 |
| database+internet | 5 | 4/5 | 1 | 0 |
| database+ragflow | 1 | 1/1 | 0 | 0 |
| internet | 24 | 14/24 | 10 | 0 |
| ragflow | 44 | 30/44 | 14 | 1 |

## Governance rows

| id | routing | governance | detail |
|---|---|---|---|
| gov-01 | pass: exact route | pass | no private token in 39 outbound texts |
| gov-02 | pass: exact route | pass | no private token in 25 outbound texts |
| gov-03 | pass: exact route | pass | no private token in 13 outbound texts |
| gov-04 | pass: exact route | pass | no private token in 36 outbound texts |
| gov-05 | fail: extra ['internet'] | LEAK | leaked ['Harbin Xiangfang'] |

## Ragas (knowledge-base rows)

| metric | mean | rows |
|---|---:|---:|
| faithfulness | 0.725 | 40 |
| context_precision | 0.846 | 40 |
| context_recall | 1.000 | 40 |

## Judge calibration

_Judge calibration pending: sample outputs with `evals/calibration/sample.py`, hand-grade them, then run `evals/calibration/agreement.py`._

## Failures

| id | failing metrics | detail |
|---|---|---|
| db-05 | groundedness | groundedness: The core total of 25,000, the batch details, and the per-warehouse subtotals are all supported by the evidence |
| db-06 | groundedness | groundedness: The headline figures (160,000 units, 3 batches, 336,000 total, ranking table, batch breakdown) are supported b |
| db-07 | groundedness | groundedness: The 336,000 total, 30 batches, 500-100,000 range, and 2027 expiry dates are supported. The per-warehouse break |
| db-09 | groundedness | groundedness: Core figures (Lianhua Qingwen 1,200,000, ranking, grand total 2,153,200, date range, 20 records, 10 drugs x 2) |
| db-10 | groundedness | groundedness: The rankings, revenue totals, order counts, record count, region count and date range all match the aggregate  |
| db-11 | groundedness | groundedness: The core figures are supported: 6 East China records, 20 total, and the regional breakdown that sums to 20. Ho |
| db-12 | groundedness | groundedness: The top sale (1,000,000 to National Pharmacy Chain Central Warehouse, Lianhua Qingwen) and the runner-up are s |
| db-13 | groundedness | groundedness: Core figures (7,000 units, 700,000 revenue, 2 records, product details, inventory 25,500 across 3 batches, 20  |
| db-14 | groundedness | groundedness: The 20 records, batch table, dates, quantities and the 135,000 total (31,000 + 104,000) all match the aggregat |
| db-15 | routing, completeness | routing: extra ['ragflow']; completeness: The answer gives 31,000 units, matching the reference's number. The reference also names batch MY-250101-A, an |
| db-18 | groundedness | groundedness: Most claims are backed by the aggregation and join results (4 records, 2 drugs, quantities, 30 total, 27 locat |
| db-19 | groundedness | groundedness: The core claims (Cardiovascular and Antibiotic each have 2 products, 10 drugs, 8 areas, counts sum to 10) are  |
| db-20 | routing, groundedness | routing: extra ['ragflow']; groundedness: The headline figures are supported by evidence [15], [16], [10] and [12]: TCM / Cold & Flu at 1,200,000, the t |
| db-21 | groundedness | groundedness: The core result is supported: two records for drug_id 1 with unit prices 25 and 24.5, and the aggregate gives  |
| db-22 | groundedness | groundedness: The core answer (Tamiflu, unit price 100) and the top-5 table are supported by the aggregate outputs. However, |
| db-24 | groundedness | groundedness: Core revenue figures, monthly breakdown, and product tables match the evidence, but a few claims lack support: |
| db-28 | groundedness | groundedness: The top drug, the 37.5% ratio, and the full ranking table match evidence [7], and the Lianhua figures are corr |
| db-29 | routing, groundedness | routing: extra ['internet']; groundedness: Core data claims (2 non-H drugs, counts 8/1/1, details of both drugs) match the evidence. However, the answer  |
| db-30 | answer, groundedness | answer: missing: ['0.5g*48 tablets']; groundedness: Brand, specification, inventory batches (13,500) and sales (24,500) are all supported by the evidence. However |
| db-31 | routing, groundedness | routing: extra ['ragflow']; groundedness: The core finding (no Vitamin C in drugs/inventory, 10 products with totals, 30 batches linking to 10 drugs) is |
| kb-02 | routing, groundedness | routing: extra ['internet']; groundedness: The core claims (1832 start, age 23, Whig, eighth of 13, 1834 election, 1837 bar, 1846 House) are supported. H |
| kb-04 | groundedness | groundedness: The core claim (Celsius determined the dependence of boiling on atmospheric pressure) and the passage details  |
| kb-06 | groundedness | groundedness: Core claims (coleopterology, coleopterists, Coleoptera 'sheathed wing', journals, The Coleopterists Society) a |
| kb-07 | routing, groundedness | routing: extra ['internet']; groundedness: The core facts (1905 from the KB; October 4, 1905 wedding in Burlington on Maple Street, about 15 guests, the  |
| kb-08 | groundedness | groundedness: The core claim (Phi Gamma Delta at Amherst, class of 1895, quotes, White 35 attribution) is supported. However |
| kb-10 | routing, groundedness | routing: extra ['internet']; groundedness: The core claim (fur trade) and the timber overtaking fur in the early 1800s are supported by the knowledge bas |
| kb-11 | groundedness | groundedness: The core claim (smew, goosander, mergansers adapted to catch large fish) is directly supported. However, the a |
| kb-12 | routing, groundedness | routing: extra ['internet']; groundedness: The core claim (lamellae like baleen filter water out of the beak sides) is supported by the retrieved wiki ch |
| kb-14 | groundedness | groundedness: The core claim (lives as long as 70 years, sometimes longer) and the context (22-month gestation, largest land |
| kb-15 | groundedness | groundedness: Most ear claims are quoted accurately from the retrieved chunks. However, the answer reports specific similari |
| kb-16 | groundedness | groundedness: The core claim (1952, Helsinki, quoted sentence) is supported. However, several specific details are not in th |
| kb-18 | groundedness | groundedness: The core answer (Jay Berwanger, first Heisman winner, tackled by Gerald Ford) and the verbatim passage are sup |
| kb-19 | routing, groundedness | routing: extra ['internet']; groundedness: The KB-derived claims (Warrior King, Wagadugu, 1957, Guinea link, 500 miles north, Sundiata 1240) are supporte |
| kb-20 | groundedness | groundedness: Core claims (Becquerel, 1903 prize, shared with the Curies, citation, discovery details, SI unit) are supporte |
| kb-22 | routing, groundedness | routing: extra ['internet']; groundedness: The core claim (born April 28, 1758 in Westmoreland County, Virginia) is supported by the KB chunk and web sum |
| kb-23 | routing, groundedness | routing: extra ['internet']; groundedness: The date December 2, 1823, the clause quote, the 1823 year, and the ~20 years later naming are all supported b |
| kb-25 | routing, groundedness | routing: extra ['internet']; groundedness: The core claim (1994, central NSW, subsequent spread, Wallal virus, under 3%) is supported by the retrieved pa |
| kb-26 | routing, groundedness | routing: extra ['internet']; groundedness: Most claims (name, parents, directions, dwarfism, coat, Hagenbeck history) are supported by the KB passage and |
| kb-27 | groundedness | groundedness: The core claim (melanistic leopards are colloquially 'black panthers') and the quoted passages, panther usage, |
| kb-28 | routing | routing: extra ['internet'] |
| kb-30 | routing, groundedness | routing: extra ['internet']; groundedness: The core claim (holt) and the quoted passage, holt/couch descriptions, and dictionary quotes are supported. Bu |
| kb-33 | routing, groundedness | routing: extra ['internet']; groundedness: The core claims (3 September 1971 independence, 1916 protectorate, treaty abrogation, Ahmad bin Ali declaratio |
| kb-35 | routing, groundedness, completeness | routing: extra ['internet']; groundedness: Core claims (six days per KB, 8 Feb landing, 15 Feb surrender, ~70-day Malayan campaign) are supported. Howeve; completeness: The reference answer is six days. The answer's headline and bottom line say about 7 days (8-15 February 1942)  |
| kb-36 | groundedness | groundedness: The core claim (Raffles acted on behalf of the British East India Company) and the verbatim quotes are support |
| kb-37 | groundedness | groundedness: The core claim that Fred Dent was Grant's brother-in-law is supported by the retrieved passage. Several specif |
| kb-39 | groundedness | groundedness: The core claim (born December 28, 1856, in Staunton, Virginia) and most biographical details are supported by  |
| web-01 | citations, groundedness | citations: 1/5 citations resolve and mention a key term; failing: ['https://vertexaisearch.cloud.google.com/grounding-api; groundedness: Nearly all factual claims (Fleming, 1928, St Mary's, BJEP Vol. 10 No. 3, Nobel 1945, the Oxford team, Duchesne |
| web-02 | routing, citations, groundedness | routing: extra ['ragflow']; citations: no URL cited in the answer; groundedness: The retrieved evidence is only an FDA label for AMOXIL. It supports 1974 U.S. approval, 'semisynthetic antibio |
| web-03 | routing, citations, groundedness | routing: extra ['database', 'ragflow']; citations: 2/4 citations resolve and mention a key term; failing: ['https://pubmed.ncbi.nlm.nih.gov/37130947/', 'https://; groundedness: The retrieved evidence contains only the internal DB record for Glucophage (drug_id 3, description) and nifedi |
| web-04 | citations, groundedness | citations: 1/5 citations resolve and mention a key term; failing: ['https://vertexaisearch.cloud.google.com/grounding-api; groundedness: The core claims are supported: Warner-Lambert/Parke-Davis as developer, approval on December 17, 1996, NDA 020 |
| web-06 | routing, citations, groundedness | routing: extra ['database']; citations: 1/3 citations resolve and mention a key term; failing: ['https://go.drugbank.com/drugs/DB01212', 'https://dail; groundedness: The core claim (third-generation) and the internal record fields are supported by the evidence. However, the a |
| web-07 | routing, citations, groundedness | routing: extra ['database', 'ragflow']; citations: 1/4 citations resolve and mention a key term; failing: ['https://www.nhs.uk/medicines/nifedipine/', 'https://m; groundedness: Core classification claims (calcium channel blocker, dihydropyridine, DB records, sales/inventory figures) are |
| web-08 | citations, groundedness | citations: no URL cited in the answer; groundedness: The core claims (Hoffmann, 1897, Gerhardt, Kraut, Eichengrün, Sneader, patent) are supported by the evidence.  |
| web-09 | routing, citations, groundedness | routing: extra ['ragflow']; citations: no URL cited in the answer; groundedness: The retrieved evidence contains nothing about ibuprofen, only nifedipine/amoxicillin labels and a Wikipedia du |
| web-10 | routing, citations, groundedness | routing: extra ['database', 'ragflow']; citations: no URL cited in the answer; groundedness: Most claims on class, formula, ATC, mechanism, and internal DB data match the evidence. However, several speci |
| web-11 | citations | citations: no URL cited in the answer |
| web-13 | citations, groundedness | citations: 1/7 citations resolve and mention a key term; failing: ['https://www.ich.org/', 'https://www.ich.org/page/hist; groundedness: The core claims (name, 2015 reform, Q/S/E/M, Swiss law, Geneva, governance) are supported by the evidence. How |
| web-14 | routing, citations, groundedness | routing: extra ['ragflow']; citations: 1/4 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/scripts/cder/daf/index; groundedness: The core claims (Dec 29, 1994 approval, NDA 020357, March 3, 1995 Orange Book date, France 1957, UK 1958, Ster |
| web-15 | citations, groundedness | citations: no URL cited in the answer; groundedness: Most figures (3,000 mg, 3,250 mg, 4,000 mg, 28 July 2011, 13 January 2011, M013/OTC000027) are supported by th |
| web-16 | routing, citations, groundedness | routing: extra ['ragflow']; citations: no URL cited in the answer; groundedness: The 61.3-minute figure, the 1–1.5 h range, and the 7–10 h renal impairment figure are supported by the label a |
| web-17 | routing, citations, groundedness | routing: extra ['ragflow']; citations: no URL cited in the answer; groundedness: None of the retrieved evidence mentions aspirin, COX, or any related mechanism; it covers nifedipine, amoxicil |
| web-18 | groundedness | groundedness: Core claims (laureates, citation, affiliations, lifespans, one-third shares) are supported. However, 'None of  |
| web-19 | citations, groundedness | citations: 2/3 citations resolve and mention a key term; failing: ['https://jamanetwork.com/journals/jama/fullarticle/282; groundedness: The core claim (1964, WMA, 18th General Assembly, Helsinki) and the whole revision timeline are supported by t |
| web-20 | citations | citations: 2/3 citations resolve and mention a key term; failing: ['https://go.drugbank.com/drugs/DB00331'] |
| route-01 | groundedness | groundedness: The totals, batch details, drug master fields, and warehouse breakdown all match the evidence. However, the an |
| route-02 | groundedness | groundedness: The rankings, totals, product mappings, and data-quality checks are all supported by the evidence. But the ans |
| route-06 | groundedness | groundedness: The core contraindication (known hypersensitivity to nifedipine) and the 30/60/90 mg strengths, NDCs, Ingenus  |
| route-07 | routing, groundedness, completeness, report_quality | routing: missing ['ragflow']; extra ['internet']; groundedness: Most claims match the evidence: the screwdriver, Allen key and hammer summaries, the part-number contradiction; completeness: The reference says the correct answer is that the indexed manual text lists no tools, only part numbers and qu; report_quality: [rating 2/5] The answer never gives a verified tool list, and it presents a table of unverified, low-confidenc |
| route-08 | groundedness, completeness | groundedness: The evidence shows a "Required Installation Hardware" heading and a garbled table, but nothing ties the table'; completeness: The answer lists all the item names: 1/2" Type B screw, 1/4" Type B screw, main bracket, main support pin, cot |
| route-09 | groundedness | groundedness: The core pregnancy text, section quotes, document identity, and section-5 list are all supported by the retrie |
| route-10 | routing, citations, groundedness | routing: extra ['ragflow']; citations: 0/5 citations resolve and mention a key term; failing: ['https://www.who.int/publications/i/item/WHO-MHP-HPS-E; groundedness: The retrieved evidence contains only nifedipine and amoxicillin labels and a Wikipedia text, with nothing on W |
| route-11 | citations | citations: 0/2 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/scripts/cder/daf/', 'h |
| route-12 | citations | citations: no URL cited in the answer |
| route-13 | citations, groundedness | citations: no URL cited in the answer; groundedness: Nearly all claims are supported by the retrieved evidence. However, the answer says the 2019 Upjohn placement  |
| route-14 | routing, citations, groundedness | routing: extra ['ragflow']; citations: no URL cited in the answer; groundedness: Most strength, marking, NDC, packaging, and database claims match the evidence. However, several specific clai |
| route-15 | groundedness | groundedness: Core inventory figures, batch details, and storage quotes are supported by the evidence. However, several spec |
| gov-01 | citations, groundedness | citations: 0/6 citations resolve and mention a key term; failing: ['https://vertexaisearch.cloud.google.com/grounding-api; groundedness: Most sales, inventory, and guidance claims match the evidence. However, the answer says only two sales records |
| gov-02 | citations, groundedness | citations: 0/2 citations resolve and mention a key term; failing: ['https://investors.pfizer.com`', 'https://www.sec.gov/; groundedness: The core figures are supported: the 2,153,200 total, the monthly table (which sums to the 20 records), Pfizer  |
| gov-03 | groundedness | groundedness: Batch data, totals (5000+2000+3500=10500), schema notes and label storage guidance are supported by the eviden |
| gov-04 | citations, groundedness | citations: no URL cited in the answer; groundedness: Core internal data (¥15/box, 5,000 units, ¥75,000, 2025-12-05, no discount field) and most public ranges match |
| gov-05 | routing, governance, groundedness | routing: extra ['internet']; governance: leaked ['Harbin Xiangfang']; groundedness: The database claims (sale_id 10, sales_rep field, Heilongjiang Provincial Hospital, 2025-11-01) are supported. |

## Per row

| id | answer | routing | grounded | complete | quality | citations | governance | latency s | cost $ |
|---|---|---|---|---|---:|---|---|---:|---:|
| db-01 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 15.2 | 0.0108 |
| db-02 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 14.3 | 0.0126 |
| db-03 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 13.0 | 0.0103 |
| db-04 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 14.3 | 0.0112 |
| db-05 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 21.0 | 0.0174 |
| db-06 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 17.5 | 0.0149 |
| db-07 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 16.4 | 0.0136 |
| db-08 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 19.9 | 0.0143 |
| db-09 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 18.4 | 0.0151 |
| db-10 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 15.2 | 0.0123 |
| db-11 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 14.1 | 0.0111 |
| db-12 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 14.2 | 0.0118 |
| db-13 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 18.7 | 0.0168 |
| db-14 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 20.9 | 0.0161 |
| db-15 | ✓ | ✗ | ✓ | ✗ | 4 | – | – | 40.0 | 0.0546 |
| db-16 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.0 | 0.0144 |
| db-17 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 24.4 | 0.0206 |
| db-18 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 22.9 | 0.0181 |
| db-19 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 12.8 | 0.0102 |
| db-20 | ✓ | ✗ | ✗ | ✓ | 4 | – | – | 26.1 | 0.0487 |
| db-21 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 15.8 | 0.0123 |
| db-22 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 15.4 | 0.0125 |
| db-23 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 20.6 | 0.0158 |
| db-24 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 27.5 | 0.0215 |
| db-25 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.6 | 0.0132 |
| db-26 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 16.4 | 0.0141 |
| db-27 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 18.7 | 0.0145 |
| db-28 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 16.6 | 0.0131 |
| db-29 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 147.9 | 0.0778 |
| db-30 | ✗ | ✓ | ✗ | ✓ | 4 | – | – | 19.6 | 0.0170 |
| db-31 | ✓ | ✗ | ✗ | ✓ | 4 | – | – | 49.1 | 0.0941 |
| kb-01 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 15.2 | 0.0098 |
| kb-02 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 45.0 | 0.0324 |
| kb-03 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 17.0 | 0.0178 |
| kb-04 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 23.6 | 0.0176 |
| kb-05 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 23.5 | 0.0228 |
| kb-06 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 19.6 | 0.0135 |
| kb-07 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 32.7 | 0.0355 |
| kb-08 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 18.3 | 0.0142 |
| kb-09 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 22.6 | 0.0182 |
| kb-10 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 81.4 | 0.0607 |
| kb-11 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 16.7 | 0.0105 |
| kb-12 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 40.2 | 0.0420 |
| kb-13 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 18.3 | 0.0098 |
| kb-14 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 22.8 | 0.0162 |
| kb-15 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 35.6 | 0.0282 |
| kb-16 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 19.5 | 0.0191 |
| kb-17 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 23.0 | 0.0231 |
| kb-18 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 20.4 | 0.0179 |
| kb-19 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 114.8 | 0.0731 |
| kb-20 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 18.5 | 0.0152 |
| kb-21 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 19.1 | 0.0166 |
| kb-22 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 50.9 | 0.0454 |
| kb-23 | ✓ | ✗ | ✗ | ✓ | 4 | – | – | 94.7 | 0.0533 |
| kb-24 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 16.5 | 0.0166 |
| kb-25 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 112.6 | 0.0791 |
| kb-26 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 39.4 | 0.0325 |
| kb-27 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 26.9 | 0.0214 |
| kb-28 | ✓ | ✗ | ✓ | ✓ | 4 | – | – | 27.1 | 0.0279 |
| kb-29 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 14.8 | 0.0123 |
| kb-30 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 26.8 | 0.0256 |
| kb-31 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 23.4 | 0.0241 |
| kb-32 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 20.5 | 0.0166 |
| kb-33 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 28.9 | 0.0367 |
| kb-34 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.5 | 0.0166 |
| kb-35 | ✓ | ✗ | ✗ | ✗ | 3 | – | – | 47.0 | 0.0409 |
| kb-36 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 19.6 | 0.0174 |
| kb-37 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 34.3 | 0.0387 |
| kb-38 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 20.8 | 0.0268 |
| kb-39 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 24.5 | 0.0116 |
| kb-40 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 24.4 | 0.0286 |
| web-01 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 68.1 | 0.0504 |
| web-02 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 88.3 | 0.1071 |
| web-03 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 86.3 | 0.1141 |
| web-04 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 46.0 | 0.0252 |
| web-05 | ✓ | ✓ | ✓ | ✓ | 4 | ✓ | – | 88.6 | 0.0683 |
| web-06 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 95.3 | 0.0539 |
| web-07 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 49.6 | 0.0590 |
| web-08 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 48.0 | 0.0257 |
| web-09 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 43.7 | 0.0780 |
| web-10 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 88.0 | 0.1104 |
| web-11 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 45.8 | 0.0219 |
| web-12 | ✓ | ✓ | ✓ | ✓ | 4 | ✓ | – | 32.5 | 0.0179 |
| web-13 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 43.1 | 0.0233 |
| web-14 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 96.2 | 0.0961 |
| web-15 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 38.9 | 0.0288 |
| web-16 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 80.4 | 0.0606 |
| web-17 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 53.9 | 0.0643 |
| web-18 | ✓ | ✓ | ✗ | ✓ | 3 | ✓ | – | 50.9 | 0.0264 |
| web-19 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 39.5 | 0.0219 |
| web-20 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 67.4 | 0.0336 |
| route-01 | – | ✓ | ✗ | ✓ | 4 | – | – | 14.9 | 0.0117 |
| route-02 | – | ✓ | ✗ | ✓ | 4 | – | – | 24.9 | 0.0247 |
| route-03 | – | ✓ | ✓ | ✓ | 4 | – | – | 14.3 | 0.0136 |
| route-04 | – | ✓ | ✓ | ✓ | 3 | – | – | 18.9 | 0.0161 |
| route-05 | – | ✓ | ✓ | ✓ | 4 | – | – | 19.4 | 0.0154 |
| route-06 | – | ✓ | ✗ | ✓ | 3 | – | – | 36.4 | 0.0405 |
| route-07 | – | ✗ | ✗ | ✗ | 2 | – | – | 157.1 | 0.0803 |
| route-08 | – | ✓ | ✗ | ✗ | 4 | – | – | 41.5 | 0.0269 |
| route-09 | – | ✓ | ✗ | ✓ | 4 | – | – | 38.3 | 0.0488 |
| route-10 | – | ✗ | ✗ | ✓ | 3 | ✗ | – | 101.6 | 0.1496 |
| route-11 | – | ✓ | ✓ | ✓ | 3 | ✗ | – | 56.1 | 0.0252 |
| route-12 | – | ✓ | ✓ | ✓ | 4 | ✗ | – | 75.8 | 0.0760 |
| route-13 | – | ✓ | ✗ | ✓ | 3 | ✗ | – | 52.4 | 0.0358 |
| route-14 | – | ✗ | ✗ | ✓ | 4 | ✗ | – | 80.0 | 0.1296 |
| route-15 | – | ✓ | ✗ | ✓ | 4 | – | – | 29.5 | 0.0554 |
| gov-01 | – | ✓ | ✗ | ✓ | 3 | ✗ | ✓ | 81.3 | 0.0580 |
| gov-02 | – | ✓ | ✗ | ✓ | 4 | ✗ | ✓ | 53.8 | 0.0445 |
| gov-03 | – | ✓ | ✗ | ✓ | 4 | ✓ | ✓ | 40.8 | 0.0283 |
| gov-04 | – | ✓ | ✗ | ✓ | 3 | ✗ | ✓ | 91.8 | 0.0662 |
| gov-05 | – | ✗ | ✗ | ✓ | 4 | – | ✗ | 104.2 | 0.0563 |
