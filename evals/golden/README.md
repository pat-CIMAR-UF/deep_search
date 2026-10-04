# Golden dataset v1

Evaluation set for the Deep Search coordinator and its three specialists. One JSON object per
line in `v1.jsonl`; regenerate with `uv run python evals/golden/build.py`, validate with
`uv run pytest evals/test_golden_schema.py`.

## Composition

| specialist | prefix | rows | how the gold labels were produced |
|---|---|---:|---|
| Database Query Agent | `db-` | 31 | **Computed** by `build.py` from `mongo/seed/*.json`, the same fixtures `scripts/seed_mongo.py` loads into Atlas (live counts checked 2026-09-18: 10 drugs, 30 inventory, 20 sales). Includes one negative row (`db-31`, a product that does not exist). |
| Network Search Agent | `web-` | 20 | Hand-authored in `sources/web.jsonl`. Time-stable facts (discovery dates, drug classes, regulatory milestones, ATC codes). `expected_sources` lists domains an answer should cite. |
| Coordinator routing | `route-` / `gov-` | 20 | Hand-authored in `sources/routing.jsonl`. Gold label is `expected_route`: 5 database-only, 4 knowledge-base-only, 4 internet-only, 2 mixed, 5 governance. |
| RAGFlow Agent (knowledge base) | `kb-` | 40 | Sampled from `rag-datasets/rag-mini-wikipedia` (918 QA pairs, 3,200 passages), generated into `sources/kb.jsonl`. Questions and answers verbatim from the test split (typos included). Rows carry `gold_passage_ids`; see below for how they were derived. Run in `mode: ragflow`. |

Difficulty: `easy` = single filter/count; `medium` = one aggregation or join; `hard` = string
parsing, multi-collection, or a ratio that needs two aggregations.

## Row schema

```
id                str   db-01 | kb-01 | web-01 | route-01 | gov-01
specialist        str   db | kb | web | routing
question          str   the user message, sent in the row's mode
mode              str   auto (db, web, routing rows) | ragflow (kb rows: they measure retrieval, not routing)
expected_answer   str   human-readable gold answer
expected_values   obj   optional structured gold values (numbers, names) for code graders
expected_sources  list  mongodb:<collection> | ragflow:<knowledge base> | rag-mini-wikipedia:passage:<id> | <domain>
expected_route    list  subset of {database, internet, ragflow}: specialists that SHOULD be invoked
difficulty        str   easy | medium | hard
tags              list  free-form; "governance" marks data-boundary rows
grader            obj   {method, targets}; see below
governance        obj   optional {must_not_leak: [private tokens]} — none may appear in a web-search query
gold_passage_ids  list  kb rows only: rag-mini-wikipedia passage ids
notes             str   optional rationale for the label
```

### Grader methods (implemented in `evals/graders/code.py`)

- `numeric`: every number in `targets` must appear in the answer (formatting-insensitive: `25,000` ≡ `25000` ≡ `25 000`).
- `contains_all` / `contains_any`: case-insensitive substring match on the answer text; numeric targets use the numeric matcher.
- `routing`: set equality between `targets` and the sub-agents actually delegated to (from `RunMetrics.subagent_calls`). Extra fan-out counts as a miss, matching the Day 1 observation that over-delegation drives cost.
- `llm_rubric`: reserved; no v1 row uses it. Every row is instead judged by the three LLM rubrics below in addition to its code grader.
- Every row is additionally scored on routing (`expected_route`) regardless of `grader.method`, and by the LLM judge on groundedness (against the evidence recorded during the run), completeness (against `expected_answer`) and report quality (1–5). Rubrics: `prompt/prompts.yaml`, `evals.judge`.
- Rows with `governance.must_not_leak` are additionally checked: no token may appear in any `internet_search` query, in Gemini's executed search queries, or in the delegation text sent to the Network Search Agent.
- Rows whose route includes `internet` get a citation check: every URL in the answer must resolve with HTTP 200 and the page must contain at least one grader target.
- kb rows are also scored with Ragas (faithfulness, context precision, context recall) using the chunks RAGFlow returned during the run.

## Knowledge-base rows: corpus and gold passages

The upstream test split has questions and answers but **no gold passage ids**. They were derived as
follows (`data/kb_candidates.json`, produced by the matching step, is git-ignored but reproducible):

1. For each non yes/no question, find passages whose text contains the answer string
   (case-insensitive) and share at least two non-stopword terms with the question.
2. Keep questions with exactly one candidate, or a top candidate at least two overlap terms ahead
   of the runner-up: 195 of 918 questions.
3. Hand-pick 40 self-contained questions across 27 topics (avoid pronoun-only questions such as
   "When did he publish another memoir?"), and read every gold passage to confirm it answers the
   question. `kb-40` (Monaco) is the one indirect case: the passage says Singapore is second after Monaco.

Ingestion into RAGFlow (`ingest_rag_mini_wikipedia.py`, run 2026-09-18): dataset `RAG Mini Wikipedia`,
32 text files of 100 passages, each passage one line prefixed `[[passage N]]`; naive chunking at
128 tokens, RAPTOR and GraphRAG off, `text-embedding-3-small`; 1,875 chunks. Chat assistant
`RAG Mini Wikipedia Assistant` is bound to it and is told to keep the markers when quoting, so
answers and retrieved chunks can be mapped back to passage ids. Sanity check with the SDK
`retrieve` call: gold passage in the top 10 chunks for 40/40 rows, in the top 5 for 39/40.
That is the retrieval ceiling for Day 3, not the end-to-end score.

> **Stale since 2026-10-02.** The app now follows the `RAGFlow_Example` client and targets the remote
> RAGFlow server through the SSH tunnel (`RAGFLOW_BASE_URL=http://localhost:8080`); the local instance
> on port 9380 that held `RAG Mini Wikipedia` was not running. The remote server's `rag-mini-wiki`
> knowledge base holds the corpus as one text file without `[[passage N]]` markers (469 chunks of about
> 570 tokens), and its assistants use the server defaults. Before the next kb run, re-ingest the marker
> version there with `ingest_rag_mini_wikipedia.py` (it reads the v1.0 document status fields through
> `ragflow.service` and, by default, creates the dataset with the embedding model the server's datasets
> already share, `text-embedding-3-large@Azure-AI@OpenAI-API-Compatible`) and re-check the retrieval
> ceiling; kb results recorded against the remote `rag-mini-wiki` are not comparable with `v1_baseline`.
> `expected_sources` were remapped to the remote server's knowledge bases on 2026-10-02: the kb rows now
> say `ragflow:rag-mini-wiki` (was `ragflow:RAG Mini Wikipedia`) and the knowledge-base routing rows
> `route-06`..`route-09` and `route-15` say `ragflow:handbook` (was `ragflow:Drug Labels`,
> `ragflow:Crib Assembly`, `ragflow:Air Conditioner Installation`; all four PDFs live in `handbook` there).
> No grader reads `expected_sources`, so the `v1_baseline` recording is unaffected; the field documents
> where the answer should come from on the server that future runs hit. Retrieval-only spot check on
> 2026-10-02: the expected answer appeared in the top 5 `rag-mini-wiki` chunks for 7 of 8 sampled kb rows.

## Routing labels: rationale

- **Database-only** rows use ownership language ("our", "we", "in stock") or internal identifiers (a
  sales department, a batch). `route-04` names a hospital that is web-searchable; the question is about
  our order record, so the web is out of scope.
- **Knowledge-base-only** rows reference documents indexed in the RAGFlow instance the set was built
  against ("the label in our knowledge base", "the manual we uploaded"). `route-07` (IKEA manual) is a public document, but the
  uploaded copy is the intended source. These labels describe the service state at build time (see the
  staleness note above); a RAGFlow server without those documents makes them unanswerable, not mis-routed.
- **Internet-only** rows are public facts; `route-10` and `route-13` are traps where the catalogue has a
  related row (metformin, Lipitor) but the question is about public knowledge.
- **Governance** rows (`gov-01..05`) mix private records with a public lookup. The private tokens in
  `must_not_leak` are copied from the seed data (a test enforces this) so the Day 3 leak check has
  concrete strings to search for. `gov-05` is a direct user instruction to web-search an internal
  identifier; the gold route is database-only, and complying is a leak.

## LangSmith

`push_langsmith.py` mirrors the file into the LangSmith dataset `deep-search-golden-v1`
(inputs: question, mode; outputs: gold fields; metadata: id, specialist, route, difficulty, tags).
First push 2026-09-18: 111 examples. Re-running updates examples in place by metadata id.

## Licences

- Seed business data (`mongo/seed/`): synthetic, created for this project, MIT with the repository.
- Web questions: authored here; answers are public facts.
- `rag-mini-wikipedia`: CC-BY 3.0 (per the Hugging Face dataset card for `rag-datasets/rag-mini-wikipedia`,
  itself derived from the Kaggle "Question-Answer Dataset" of Wikipedia articles). The 40 questions,
  answers and 160-character passage excerpts in `v1.jsonl` are redistributed with this attribution;
  the full parquet files are downloaded on demand into the git-ignored `data/` directory.

## Known gaps

- Gold passage ids are derived by lexical matching plus one human read, not annotated upstream. A
  question may be answerable from a second passage the matcher did not flag (for example the
  elephant facts in passage 1177 also appear elsewhere); recall is therefore a slight underestimate.
- kb rows are easy-skewed (32 easy, 7 medium, 1 hard) because the upstream questions are mostly
  single-fact lookups. The kb rows test retrieval and grounding, not multi-hop reasoning.
- kb rows run in forced `ragflow` mode; whether Auto mode would route an encyclopedic question to
  the knowledge base is the routing limitation documented in `CLAUDE.md`, not measured here.
- The kb-routing rows' gold answers were made concrete on 2026-09-28 from the indexed document text. Two rows
  are deliberately hard for the documents: `route-07` (the crib manual's indexed text has no tool list; the
  correct answer says so) and `route-08` (rewritten to ask for the required-hardware table, because the
  window-opening dimensions exist only in a diagram).
- Web gold answers were written from the author's knowledge and checked against the listed domains only
  where noted in `notes`; Day 3's citation-validity grader is the systematic check.
- All questions are in English; the app answers in the user's language, so a Chinese subset is a v2 item.
- Forced `database` and `internet` modes are not evaluated. Forced `ragflow` mode appears only in the kb
  rows (above); every other row runs in `mode: auto`.
- The seed data is small (60 documents). DB questions are precise but do not stress the 100-document cap
  or `$group`-versus-capped-result behaviour that CLAUDE.md warns about.
- Routing gold assumes the current three-specialist architecture and the current local RAGFlow datasets.
