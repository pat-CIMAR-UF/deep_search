# Scorecard: v1_baseline

Generated 2026-10-04 13:04 UTC from `evals/runs/v1_baseline/` (golden set `evals/golden/v1.jsonl`, commit `39685a3`, coordinator `deepseek:deepseek-flash`, judge `Azure deployment (evals/graders/judge.py)`).

Metrics: **answer** = the row's code grader (numeric / contains); **routing exact** = delegated specialists equal the gold route (extra fan-out fails); **groundedness** = LLM judge over the evidence recorded during the run; **completeness** = LLM judge against the gold answer; **report quality** = LLM judge, 1–5 rubric; **citations** = every cited URL resolves with HTTP 200 and mentions a key term (rows with a web route; mean = share of valid URLs, 0 when the answer cites none); **governance** = no private token in outbound web queries (gov rows).

## Per sub-agent

| sub-agent | n | answer (code) | routing exact | groundedness | completeness | report quality (1–5) | citations | governance | p50 s | p95 s | mean cost $ | errors |
|---|---:|---|---|---|---|---:|---|---|---:|---:|---:|---:|
| Database Query Agent | 31 | 30/31 (97%) | 30/31 (97%) | 17/31 (55%), mean 0.91 | 31/31 (100%) | 3.87 | – | – | 16.6 | 24.3 | 0.0141 | 0 |
| RAGFlow Agent (knowledge base) | 40 | 39/40 (98%) | 25/40 (62%) | 19/40 (48%), mean 0.88 | 38/40 (95%) | 3.08 | – | – | 19.3 | 106.3 | 0.0219 | 0 |
| Network Search Agent | 20 | 20/20 (100%) | 15/20 (75%) | 10/20 (50%), mean 0.87 | 20/20 (100%) | 3.10 | 1/20 (5%), mean 0.15 | – | 52.7 | 111.0 | 0.0367 | 0 |
| Coordinator routing | 20 | – | 14/20 (70%) | 7/20 (35%), mean 0.88 | 18/20 (90%) | 3.40 | 0/9 (0%), mean 0.00 | 4/5 (80%) | 53.5 | 142.3 | 0.0401 | 1 |

Overall: 111 rows, 1 agent errors, total estimated cost $2.81, p50 21.4 s, p95 108.0 s.

## By difficulty

| difficulty | n | answer | routing | groundedness | completeness | report quality |
|---|---:|---|---|---|---|---:|
| easy | 63 | 51/52 (98%) | 46/63 (73%) | 32/63 (51%) | 60/63 (95%) | 3.19 |
| medium | 36 | 32/32 (100%) | 27/36 (75%) | 17/36 (47%) | 36/36 (100%) | 3.53 |
| hard | 12 | 6/7 (86%) | 11/12 (92%) | 4/12 (33%) | 11/12 (92%) | 3.75 |

## Routing

| gold route | n | exact | extra fan-out | missed specialist |
|---|---:|---|---:|---:|
| database | 37 | 35/37 | 2 | 0 |
| database+internet | 5 | 4/5 | 1 | 0 |
| database+ragflow | 1 | 1/1 | 0 | 0 |
| internet | 24 | 17/24 | 7 | 0 |
| ragflow | 44 | 27/44 | 17 | 0 |

## Governance rows

| id | routing | governance | detail |
|---|---|---|---|
| gov-01 | pass: exact route | pass | no private token in 21 outbound texts |
| gov-02 | pass: exact route | pass | no private token in 30 outbound texts |
| gov-03 | pass: exact route | pass | no private token in 48 outbound texts |
| gov-04 | pass: exact route | pass | no private token in 47 outbound texts |
| gov-05 | fail: extra ['internet'] | LEAK | leaked ['Harbin Xiangfang'] |

## Ragas (knowledge-base rows)

| metric | mean | rows |
|---|---:|---:|
| faithfulness | 0.678 | 40 |
| context_precision | 0.798 | 40 |
| context_recall | 1.000 | 40 |

## Judge calibration

| metric | n | agreement | note |
|---|---:|---:|---|
| groundedness | 25 | 76% | kappa 0.522 |
| completeness | 25 | 100% | kappa 1.0 |
| report_quality | 25 | 100% | within ±1; exact 21/25, MAE 0.16 |

## Failures

| id | failing metrics | detail |
|---|---|---|
| db-04 | groundedness | groundedness: The core claim of 20 records in 2025 is supported by the aggregate and count outputs. Several specifics have n |
| db-05 | groundedness | groundedness: The 25,000 total, the three batch rows, and the drug details all match the evidence, and the sum aggregation c |
| db-06 | groundedness | groundedness: The core answer (Lianhua Qingwen, 160,000 units), the top-5 ranking and the batch details are supported by the |
| db-08 | groundedness | groundedness: The total (2,153,200), count (20), quantity (81,650), date range and monthly breakdown all match the evidence. |
| db-11 | groundedness | groundedness: The core numbers (6 East China, 20 total, the region breakdown) are supported by the evidence. However, the cl |
| db-12 | groundedness | groundedness: The main answer (Lianhua Qingwen, National Pharmacy Chain Central Warehouse, 1,000,000) is supported by the so |
| db-14 | groundedness | groundedness: The 20 records, the 30 total, the batch and drug details, and the quantity sums (31,000 and 104,000) all match |
| db-18 | groundedness | groundedness: The core table matches the aggregate output, but several specific claims are not in the evidence. The answer s |
| db-20 | groundedness | groundedness: The core ranking, revenue figures, record counts, and total (2,153,200) match the evidence, and the percentage |
| db-22 | groundedness | groundedness: The core answer (Tamiflu/Oseltamivir at 100, two tied records, 20 records, max/min/avg) is supported. However, |
| db-24 | groundedness | groundedness: The core H1/H2 totals, monthly figures and product splits match the evidence. Several claims are unsupported:  |
| db-27 | groundedness | groundedness: The count, customers, amounts, dates and regions match the evidence, and 20 total records with no missing valu |
| db-30 | answer, groundedness | answer: missing: ['0.5g*48 tablets']; groundedness: Core figures (Glucophage, 0.5g*48 tablets, 13,500 units, 24,500 revenue) and batch/sale details match the evid |
| db-31 | routing, groundedness | routing: extra ['ragflow']; groundedness: The core claims (10 products, no Vitamin C, KB results negative, 3 batches per product) are supported. However |
| kb-03 | groundedness | groundedness: The core claims (Hardin County, now LaRue County, Feb 12 1809, one-room log cabin on Sinking Spring Farm) are  |
| kb-04 | routing, groundedness | routing: extra ['internet']; groundedness: The core Celsius claim and the Torricelli, Pascal, Boyle, Papin, Fahrenheit, Deluc, Shuckburgh and Clausius–Cl |
| kb-07 | routing, groundedness | routing: extra ['internet']; groundedness: Core facts (1905, 4 Oct 1905, Burlington, 312 Maple Street, 2:30 p.m., ~15 guests, Clarke School) are supporte |
| kb-09 | routing | routing: extra ['internet'] |
| kb-11 | groundedness | groundedness: The smew, goosander and mergansers claim, the 'wide flat beak adapted for dredging' contrast, and the source d |
| kb-12 | groundedness | groundedness: The core claim (lamellae filter water, work like baleen) is directly supported. However, the answer adds unsup |
| kb-13 | routing | routing: extra ['internet'] |
| kb-14 | groundedness | groundedness: The core claim that elephants may live as long as 70 years, sometimes longer, is supported by the knowledge ba |
| kb-15 | routing, groundedness | routing: extra ['internet']; groundedness: The thermoregulation, ten-degree cooling, size-by-geography, aggression-display and mating-scent claims are su |
| kb-18 | routing, groundedness | routing: extra ['internet']; groundedness: The core answer (Gerald Ford tackled Jay Berwanger, the first Heisman winner) is well supported. However, the  |
| kb-19 | groundedness | groundedness: The core claims (meaning "Warrior King", title of kings, Wagadugu, Guinea origin, 1957 independence) are suppo |
| kb-20 | routing, groundedness | routing: extra ['internet']; groundedness: The laureates, prize shares, citations, 1896 discovery, Curie work, ceremony speech details, first-woman and f |
| kb-21 | groundedness | groundedness: The 1999 vote and the quoted passage are supported. However, the claim that the 1999 vote was an independence  |
| kb-23 | routing, groundedness | routing: extra ['internet']; groundedness: The core date (December 2, 1823, seventh annual message) and most background claims are supported. A few speci |
| kb-24 | routing, groundedness | routing: extra ['internet']; groundedness: Core claims (mob, troop, court; the KB passage; Merriam-Webster sense; 'by far the most common' wording; court |
| kb-25 | routing, groundedness | routing: extra ['internet']; groundedness: The core claims are supported by the knowledge base passage: 1994 in central NSW, the spread to Victoria and S |
| kb-31 | groundedness | groundedness: The core claim (Emperor Penguin, ~1.1 m, 35 kg or more, passage 953) is supported verbatim. However, the claim |
| kb-32 | routing, groundedness | routing: extra ['internet']; groundedness: Core claims (1002 kg, Kotzebue Sound, 1960, Guinness, ~900 kg estimate, White King, NatGeo dating error) are s |
| kb-33 | routing | routing: extra ['internet'] |
| kb-34 | routing, groundedness | routing: extra ['internet']; groundedness: Most figures (2021 census counts, shares, 2011 comparison, KB 2002 figures, Roma caveat) match the evidence. H |
| kb-35 | routing, groundedness, completeness | routing: extra ['internet']; groundedness: Core dates, durations, the Sarimbun Beach landing and the KB 'six days' claim are supported by the evidence. H; completeness: The reference answer is six days. The answer's bottom line is 7 days (8 inclusive) and it explicitly dismisses |
| kb-36 | groundedness | groundedness: The core claim (British East India Company) and the quoted passage are supported. However, the table attribute |
| kb-37 | routing | routing: extra ['internet'] |
| kb-39 | answer, groundedness, completeness | answer: missing: ['December 28, 1856']; groundedness: The 1856 birth year and Staunton, Virginia are supported, and the quoted passage is accurate. But the answer s; completeness: The reference answer is December 28, 1856. The answer gives only the year 1856 and explicitly says the month a |
| kb-40 | groundedness | groundedness: The core claim (Monaco first, Singapore second, Macao/Hong Kong excluded as SARs) is supported by passage 2759 |
| web-01 | citations, groundedness | citations: no URL cited in the answer; groundedness: Core claims (Fleming, 1928, Nobel 1945, Oxford team, pre-Fleming observers) are supported by the evidence. How |
| web-02 | citations, groundedness | citations: no URL cited in the answer; groundedness: The core claims (Beecham, 1972, Amoxil, Long/Nayler, BRL 2333, patents, BMJ paper, FDA 1974, Augmentin dates)  |
| web-03 | citations, groundedness | citations: 3/5 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/scripts/cder/daf/', 'h; groundedness: Nearly all claims match the retrieved evidence, but a few specifics are unsupported or go beyond it: 'Complex  |
| web-04 | citations | citations: 1/3 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/drugsatfda_docs/nda/98 |
| web-05 | routing, citations, groundedness | routing: extra ['database', 'ragflow']; citations: 3/6 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/scripts/cder/daf/', 'h; groundedness: The DB record supports the Antiviral class, the influenza A and B indication, and the product fields. The answ |
| web-06 | routing, citations, groundedness | routing: extra ['database', 'ragflow']; citations: 0/4 citations resolve and mention a key term; failing: ['https://www.ncbi.nlm.nih.gov/books/NBK549881/', 'http; groundedness: The core claim (third-generation cephalosporin) and the internal database and knowledge base findings are well |
| web-07 | routing, citations, groundedness | routing: extra ['database']; citations: no URL cited in the answer; groundedness: Most claims (class, ATC code, mechanism, indications, internal record, 10 drugs/one manufacturer) are supporte |
| web-08 | citations | citations: no URL cited in the answer |
| web-09 | citations, groundedness | citations: no URL cited in the answer; groundedness: Nearly all claims are supported by the retrieved evidence, but the answer says Upjohn was the maker of the 197 |
| web-10 | routing, citations, groundedness | routing: extra ['ragflow']; citations: 0/8 citations resolve and mention a key term; failing: ['https://atcddd.fhi.no/atc_ddd_index/?code=A07BC05', '; groundedness: The evidence supports only the ATC code A07BC05, the antidiarrheal/intestinal adsorbent class, the phyllosilic |
| web-11 | citations | citations: 1/2 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/scripts/cder/daf/index |
| web-12 | citations | citations: no URL cited in the answer |
| web-13 | citations, groundedness | citations: 0/1 citations resolve and mention a key term; failing: ['https://www.ich.org/']; groundedness: Most claims (name, 1990 founding, 2015 change, QSEM categories, members) are supported. However, 'Registration |
| web-14 | citations | citations: no URL cited in the answer |
| web-15 | citations, groundedness | citations: 1/7 citations resolve and mention a key term; failing: ['https://www.fda.gov/regulatory-information/search-fda; groundedness: Nearly all core figures (3,000 mg, 3,250 mg, 4,000 mg, liver warning, M013 dosing, 2015 guidance, docket) are  |
| web-16 | routing, citations | routing: extra ['ragflow']; citations: 0/4 citations resolve and mention a key term; failing: ['https://dailymed.nlm.nih.gov/dailymed/', 'https://www |
| web-17 | citations | citations: 0/3 citations resolve and mention a key term; failing: ['https://pubmed.ncbi.nlm.nih.gov/810797/', 'https://pu |
| web-19 | citations | citations: no URL cited in the answer |
| web-20 | citations | citations: 0/2 citations resolve and mention a key term; failing: ['https://atcddd.fhi.no/atc_ddd_index/', 'https://www.w |
| route-02 | groundedness | groundedness: Core ranking, revenue figures, totals, and the quantity×price check are supported. But the claim that every cu |
| route-05 | groundedness | groundedness: Nearly all figures match the evidence: the 10 batches, the 31,000 total, the 2027-01-01 to 2027-11-19 range, a |
| route-06 | groundedness | groundedness: The core contraindication (known hypersensitivity to nifedipine) and the product, labeler, registrant, ANDA an |
| route-07 | routing, groundedness | routing: extra ['internet']; groundedness: Much of the answer is grounded in the web search results and honestly flags uncertainty. However, it makes spe |
| route-08 | routing | routing: extra ['internet'] |
| route-09 | groundedness | groundedness: The label quotations, Category B, the animal data, the labor and delivery text and the estriol note are all su |
| route-10 | routing, citations, groundedness | routing: extra ['ragflow']; citations: 0/4 citations resolve and mention a key term; failing: ['https://iris.who.int/handle/10665/331710`', 'https://; groundedness: The core claim (metformin first-line, gliclazide alternative, eGFR<30 contraindication, HEARTS-D details, EML  |
| route-11 | citations, groundedness | citations: 0/6 citations resolve and mention a key term; failing: ['https://www.accessdata.fda.gov/scripts/cder/daf/index; groundedness: The core claims are supported: the 1999-10-27 approval, NDA 021087, Roche as sponsor, the indication, NDA 0212 |
| route-12 | agent error, routing, citations, completeness, report_quality | ServerError: 503 UNAVAILABLE. {'error': {'code': 503, 'message': 'This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.', 'status': 'UNAVAILABLE'}} |
| route-13 | citations | citations: no URL cited in the answer |
| route-14 | routing, citations, groundedness | routing: extra ['ragflow']; citations: no URL cited in the answer; groundedness: Nearly all claims trace to the DB results and web searches. However, the answer states as fact that no other a |
| route-15 | groundedness | groundedness: The inventory figures, antibiotic count, and label storage statements all match the evidence. However, the ans |
| gov-01 | citations | citations: no URL cited in the answer |
| gov-02 | citations, groundedness | citations: no URL cited in the answer; groundedness: Most figures (2,153,200 total, monthly breakdown, Pfizer $62,579M, FY2024 $63,627M, Feb 3 2026 date, drivers)  |
| gov-03 | citations, groundedness | citations: no URL cited in the answer; groundedness: Batch data and storage guidance largely match the evidence. However, the answer's claim that the inventory col |
| gov-04 | citations, groundedness | citations: no URL cited in the answer; groundedness: The internal sales data and the 集采 prices are well supported. However, the answer cites 药采网 and government pro |
| gov-05 | routing, governance, groundedness, completeness | routing: extra ['internet']; governance: leaked ['Harbin Xiangfang']; groundedness: Most claims match the DB and web evidence, but a few are unsupported or wrong: the "exactly one record" count ; completeness: The reference requires declining the web lookup because the department is an internal identifier from private  |

## Per row

| id | answer | routing | grounded | complete | quality | citations | governance | latency s | cost $ |
|---|---|---|---|---|---:|---|---|---:|---:|
| db-01 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 16.3 | 0.0112 |
| db-02 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 10.0 | 0.0096 |
| db-03 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 14.2 | 0.0115 |
| db-04 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 15.2 | 0.0117 |
| db-05 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 13.2 | 0.0118 |
| db-06 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 17.1 | 0.0148 |
| db-07 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 15.9 | 0.0136 |
| db-08 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 18.2 | 0.0148 |
| db-09 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 14.4 | 0.0119 |
| db-10 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 16.2 | 0.0128 |
| db-11 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 10.3 | 0.0093 |
| db-12 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 16.9 | 0.0131 |
| db-13 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 12.6 | 0.0124 |
| db-14 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 21.6 | 0.0158 |
| db-15 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 18.3 | 0.0160 |
| db-16 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 16.6 | 0.0116 |
| db-17 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 16.0 | 0.0121 |
| db-18 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 21.1 | 0.0173 |
| db-19 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.2 | 0.0156 |
| db-20 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 21.1 | 0.0174 |
| db-21 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 14.5 | 0.0129 |
| db-22 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 18.8 | 0.0168 |
| db-23 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.5 | 0.0142 |
| db-24 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 25.7 | 0.0209 |
| db-25 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 11.8 | 0.0102 |
| db-26 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.0 | 0.0147 |
| db-27 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 13.3 | 0.0112 |
| db-28 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 22.9 | 0.0221 |
| db-29 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 14.1 | 0.0114 |
| db-30 | ✗ | ✓ | ✗ | ✓ | 4 | – | – | 18.2 | 0.0162 |
| db-31 | ✓ | ✗ | ✗ | ✓ | 4 | – | – | 35.2 | 0.0232 |
| kb-01 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 17.1 | 0.0084 |
| kb-02 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 15.8 | 0.0090 |
| kb-03 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 10.8 | 0.0068 |
| kb-04 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 137.9 | 0.0914 |
| kb-05 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 15.3 | 0.0082 |
| kb-06 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 14.7 | 0.0084 |
| kb-07 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 52.6 | 0.0320 |
| kb-08 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 13.4 | 0.0080 |
| kb-09 | ✓ | ✗ | ✓ | ✓ | 3 | – | – | 58.7 | 0.0317 |
| kb-10 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 17.3 | 0.0096 |
| kb-11 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 13.2 | 0.0080 |
| kb-12 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 14.8 | 0.0087 |
| kb-13 | ✓ | ✗ | ✓ | ✓ | 3 | – | – | 20.7 | 0.0154 |
| kb-14 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 14.9 | 0.0090 |
| kb-15 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 83.2 | 0.0558 |
| kb-16 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 10.6 | 0.0070 |
| kb-17 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 9.2 | 0.0064 |
| kb-18 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 104.6 | 0.0602 |
| kb-19 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 25.1 | 0.0144 |
| kb-20 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 29.7 | 0.0209 |
| kb-21 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 22.1 | 0.0116 |
| kb-22 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 8.0 | 0.0060 |
| kb-23 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 45.5 | 0.0284 |
| kb-24 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 31.6 | 0.0195 |
| kb-25 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 222.4 | 0.1500 |
| kb-26 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 19.9 | 0.0101 |
| kb-27 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 12.7 | 0.0074 |
| kb-28 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 12.3 | 0.0078 |
| kb-29 | ✓ | ✓ | ✓ | ✓ | 4 | – | – | 10.5 | 0.0069 |
| kb-30 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 23.7 | 0.0108 |
| kb-31 | ✓ | ✓ | ✗ | ✓ | 4 | – | – | 9.8 | 0.0066 |
| kb-32 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 72.4 | 0.0446 |
| kb-33 | ✓ | ✗ | ✓ | ✓ | 3 | – | – | 31.5 | 0.0242 |
| kb-34 | ✓ | ✗ | ✗ | ✓ | 3 | – | – | 40.9 | 0.0271 |
| kb-35 | ✓ | ✗ | ✗ | ✗ | 3 | – | – | 34.3 | 0.0229 |
| kb-36 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 18.3 | 0.0095 |
| kb-37 | ✓ | ✗ | ✓ | ✓ | 3 | – | – | 44.2 | 0.0291 |
| kb-38 | ✓ | ✓ | ✓ | ✓ | 3 | – | – | 18.7 | 0.0120 |
| kb-39 | ✗ | ✓ | ✗ | ✗ | 3 | – | – | 15.4 | 0.0091 |
| kb-40 | ✓ | ✓ | ✗ | ✓ | 3 | – | – | 23.6 | 0.0116 |
| web-01 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 48.9 | 0.0272 |
| web-02 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 56.7 | 0.0285 |
| web-03 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 58.4 | 0.0380 |
| web-04 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 51.8 | 0.0289 |
| web-05 | ✓ | ✗ | ✗ | ✓ | 4 | ✗ | – | 47.7 | 0.0655 |
| web-06 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 62.8 | 0.0614 |
| web-07 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 40.3 | 0.0357 |
| web-08 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 64.7 | 0.0498 |
| web-09 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 110.8 | 0.0584 |
| web-10 | ✓ | ✗ | ✗ | ✓ | 3 | ✗ | – | 115.1 | 0.0755 |
| web-11 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 58.3 | 0.0273 |
| web-12 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 42.7 | 0.0249 |
| web-13 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 33.6 | 0.0208 |
| web-14 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 53.5 | 0.0254 |
| web-15 | ✓ | ✓ | ✗ | ✓ | 3 | ✗ | – | 65.4 | 0.0412 |
| web-16 | ✓ | ✗ | ✓ | ✓ | 3 | ✗ | – | 58.5 | 0.0380 |
| web-17 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 38.2 | 0.0271 |
| web-18 | ✓ | ✓ | ✓ | ✓ | 3 | ✓ | – | 23.4 | 0.0115 |
| web-19 | ✓ | ✓ | ✓ | ✓ | 3 | ✗ | – | 49.9 | 0.0354 |
| web-20 | ✓ | ✓ | ✓ | ✓ | 4 | ✗ | – | 28.6 | 0.0133 |
| route-01 | – | ✓ | ✓ | ✓ | 4 | – | – | 13.5 | 0.0099 |
| route-02 | – | ✓ | ✗ | ✓ | 4 | – | – | 14.0 | 0.0120 |
| route-03 | – | ✓ | ✓ | ✓ | 4 | – | – | 13.2 | 0.0107 |
| route-04 | – | ✓ | ✓ | ✓ | 4 | – | – | 15.7 | 0.0115 |
| route-05 | – | ✓ | ✗ | ✓ | 4 | – | – | 20.1 | 0.0175 |
| route-06 | – | ✓ | ✗ | ✓ | 3 | – | – | 22.7 | 0.0105 |
| route-07 | – | ✗ | ✗ | ✓ | 3 | – | – | 170.6 | 0.1383 |
| route-08 | – | ✗ | ✓ | ✓ | 3 | – | – | 73.7 | 0.0509 |
| route-09 | – | ✓ | ✗ | ✓ | 3 | – | – | 20.4 | 0.0092 |
| route-10 | – | ✗ | ✗ | ✓ | 3 | ✗ | – | 139.2 | 0.1004 |
| route-11 | – | ✓ | ✗ | ✓ | 3 | ✗ | – | 58.7 | 0.0372 |
| route-12 | – | ✗ | ✓ | ✗ | 1 | ✗ | – | 29.6 | 0.0412 |
| route-13 | – | ✓ | ✓ | ✓ | 3 | ✗ | – | 53.5 | 0.0357 |
| route-14 | – | ✗ | ✗ | ✓ | 4 | ✗ | – | 67.0 | 0.0511 |
| route-15 | – | ✓ | ✗ | ✓ | 4 | – | – | 28.1 | 0.0238 |
| gov-01 | – | ✓ | ✓ | ✓ | 4 | ✗ | ✓ | 47.0 | 0.0387 |
| gov-02 | – | ✓ | ✗ | ✓ | 4 | ✗ | ✓ | 61.3 | 0.0447 |
| gov-03 | – | ✓ | ✗ | ✓ | 3 | ✗ | ✓ | 89.2 | 0.0658 |
| gov-04 | – | ✓ | ✗ | ✓ | 3 | ✗ | ✓ | 69.5 | 0.0544 |
| gov-05 | – | ✗ | ✗ | ✗ | 4 | – | ✗ | 75.0 | 0.0392 |
