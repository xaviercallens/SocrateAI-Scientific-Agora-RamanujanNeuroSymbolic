# Final Release Package Manifest (Campaign v2 / Wave 4 / v3.3 Elenchus Canon)

## Verified Campaign v2, Wave 4 & Elenchus Canon Metrics
- **Manuscript pages processed:** `839 / 839` (`0` extraction errors)
- **Total structured identities (`namagiri.db`):** `2458` (`Tier A: 70`, `Tier B: 10`, `Tier C: 2378`)
- **Unique Lean 4 zero-axiom Dedekind eta-quotients:** `54`
- **Finite-order verified Ramanujan `LHS = RHS` identities:** `5` (order $q^{15}$ in Lean 4, $q^{29}$ in Python; 4 upgraded to universal $\forall n$ / $\forall\text{len}$ and 1 Sturm-conditional in `AllNAndPropositionsVerified.lean`)
- **Total live Lean 4.33.1 kernel theorems:** `591` (`CampaignV2Verified.lean`: `275`, `AllNAndPropositionsVerified.lean`: `63`, `RamanujanElenchusCanon.lean`: `253`, `mathesis-gate` footprints $\subseteq \{\texttt{propext}\}$)
- **OCR-corrupted equations refuted automatically:** `14`

## Packaged Deliverables & SHA-256 Checksums

| File | Size (bytes) | SHA-256 | Description |
|---|---:|---|---|
| `RAMA_Compendium_EN.pdf` | 325133 | `d22b86b3157adaafec278ed96f82971a827edcb56b30514ddb37c2a5a982c44c` | English Campaign v2 Compendium (15 pages) |
| `RAMA_Compendium_EN.tex` | 16646 | `7efe01f6cc387a74eb1048d3a3f1193eabb086d566001933aa681aa7ca6f46ad` | English Compendium LaTeX source |
| `RAMA_Compendium_FR.pdf` | 326093 | `df1f702234ffe2db5b63037abf75ef13f7e74287eb90aaed19772a94b15ad3e6` | French Campaign v2 Compendium (16 pages, 100% localized) |
| `RAMA_Compendium_FR.tex` | 17104 | `f6c8de9627d859df2b1ed8c7ff93d21ca9708aaee1399e292583f44040883012` | French Compendium LaTeX source |
| `v3_paper_main.pdf` | 637072 | `ad83e20d99bf9fb87a818637f9bed397145caafeb759731fd42ecfdde2ec864b` | Research Paper v3.2 with R1-R5 Audit, Campaign v2 & Wave 4 Addendum (14 pages) |
| `CampaignV2Verified.lean` | 50481 | `64b4177ceb15fecd6fc4baebe9854fde21950e1c46670e827765a3ac4d080c80` | Standalone zero-custom-axiom Lean 4.33.1 kernel module (275 theorems) |
| `AllNAndPropositionsVerified.lean` | 130926 | `626e6c86b3235e4ed73616bc141259d476e97d9bfcefbede474a2a7923a455c4` | Standalone zero-custom-axiom Lean 4.33.1 all-n & proposition module (63 theorems) |
| `campaign_v2_report.json` | 56871 | `953e9a39ae04ca590a56dfd04176025b5247b75c671685ebfbf2cb4fa6722ba9` | Machine-readable Campaign v2 exact verification certificate |
| `llm_lean_validation_report.json` | 17276 | `3606daae0b0550fb3d209385acfc93abd1804cf41497a18b10826ddf3f457414` | T2 adversarial validation & audit certificate |
| `oeis_batch.txt` | 31189 | `da33fee8dae5b6d2b49b20edcc073e0b253529524ce08fda71881225173fcfe3` | Exact 30-term OEIS sequence catalog (54 unique sequences, 1:1 Lean synced) |
| `arxiv_metadata.txt` | 2949 | `75bfb9b4796978c2727e19661f03c52f7b037ddc5a91d7be15f4a850e4090a9b` | Updated arXiv v3.2 submission metadata |
| `RamanujanElenchusCanon.lean` | 153374 | `124155079b379158095ff15515cce7c617d25195c65eb10c0221414de7ccee4a` | Standalone zero-custom-axiom Lean 4.33.1 Elenchus Canon module (253 theorems incl. 20 negative controls) |
| `RAMANUJAN_LEAN4_ELENCHUS_ROADMAP.md` | 122237 | `58dcc002fbe02b3a1e6be16f08484463051c8d2b7a7f6f91b2c268986bb6ddd2` | Full 10-Domain / 12-Milestone Lean 4 Formalization Roadmap & Elenchus Blueprint (44 arXiv papers + Lost Notebook I-IV) |
| `ramanujan_elenchus_audit_ledger.json` | 15328 | `35bab44f5dff023c156f555f15d24fe242d65f3f416fd902e5da58867c2d80e3` | Independent Blind Elenchus Auditor Owner's Epistemic Ledger (APPROVED) |
