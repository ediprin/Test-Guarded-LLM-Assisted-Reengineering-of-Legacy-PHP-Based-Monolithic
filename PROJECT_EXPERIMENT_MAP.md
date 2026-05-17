# Project Experiment Map

Dokumen ini mendeskripsikan struktur proyek, alur data, prosedur eksperimen, artifact yang dihasilkan, dan batas klaim penelitian. Tujuannya adalah menyediakan dokumentasi reproduksi agar eksperimen dapat diuji ulang, diaudit, dan ditelusuri dari source code sampai tabel hasil.

## 1. Tujuan Eksperimen

Eksperimen ini mengevaluasi workflow:

```text
Test-Guarded LLM-Assisted Reengineering of Legacy PHP-Based Monolithic Web Applications Using Static-Analysis Evidence
```

Pertanyaan penelitian operasional:

```text
Apakah prompt LLM yang diperkaya candidate-level static-analysis evidence menghasilkan patch reengineering yang lebih stabil dibanding prompt LLM-only pada aplikasi PHP monolitik lama?
```

Unit analisis adalah **candidate-level code region**, bukan seluruh repository. Setiap kandidat memiliki:

- lokasi file dan rentang baris
- jenis kandidat
- evidence statis
- constraint yang harus dipertahankan
- treatment prompt
- patch yang dihasilkan
- hasil gate

## 2. Batas Eksperimen Saat Ini

Eksperimen saat ini adalah:

```text
two-subject executed-subset pilot
```

Subject:

| Subject | Versi | Runtime target |
|---|---|---|
| DokuWiki | `release-2018-04-22b` | PHP 5.6 |
| Kanboard | `v1.2.13` | PHP 7.2 |

Ringkasan hasil aktif:

| Metric | Nilai |
|---|---:|
| Initial candidates | 633 |
| Locked eligible candidates | 51 |
| T1 prompts executed | 21 |
| T3 prompts executed | 19 |
| Generated LLM patches | 40 |
| Applied and syntax-pass patches | 35 |

Interpretasi yang sah:

```text
Hasil treatment merupakan executed-subset pilot, bukan evaluasi penuh terhadap semua 51 eligible candidates.
```

## 3. Struktur Root Proyek

```text
test-guarded/
  datasets.pilot.yml
  datasets.rio-audit.yml
  tools/
  subjects/
  docker/
  results/
  runs/
  workspaces/
  paper/
  .local/
  EXPERIMENT_RUNBOOK.md
  FULL_STUDY_WORKFLOW.md
  CANDIDATE_EXTRACTION_METHOD.md
  PROJECT_EXPERIMENT_MAP.md
```

| Path | Peran dalam eksperimen |
|---|---|
| `datasets.pilot.yml` | konfigurasi subject pilot yang dipakai untuk treatment |
| `datasets.rio-audit.yml` | konfigurasi subject pool yang lebih luas dari jalur Rio et al. |
| `tools/` | script pipeline eksperimen |
| `subjects/` | checkout source code subject PHP |
| `docker/` | runtime container untuk subject |
| `results/` | hasil terstruktur: candidate, evidence, syntax, oracle, summary |
| `runs/` | prompt, response, patch, dan status per candidate/treatment |
| `workspaces/` | workspace sementara untuk memasang patch dan menjalankan gate |
| `paper/` | tabel dan material paper |
| `.local/` | artifact lokal, backup, source PDF, dan scratch yang tidak menjadi hasil utama |

## 4. Alur Data End-to-End

```text
datasets.pilot.yml
  -> tools/audit_runner.py
  -> results/summary/audit_matrix.csv

subjects/<project>/
  -> tools/extract_candidates.py
  -> results/subjects/<project>/candidates/candidates.csv
  -> results/subjects/<project>/evidence/*.json

candidates.csv
  -> tools/generic_container_syntax_gate.py
  -> results/subjects/<project>/syntax/*.csv

candidates.csv + oracle/routes.json
  -> tools/build_oracle_coverage.py
  -> results/subjects/<project>/oracle/coverage.csv

oracle/coverage.csv
  -> tools/build_eligible_set.py
  -> results/summary/eligible_candidates_current.csv

eligible_candidates_current.csv
  -> tools/create_treatment_runs.py
  -> runs/<project>/<candidate_id>/

runs/<project>/<candidate_id>/<treatment>/prompt.md
  -> tools/run_openai_treatment.py
  -> response.txt
  -> patch.diff
  -> status.json

runs/*/patch.diff
  -> tools/summarize_treatment_outputs.py
  -> results/summary/treatment_outputs_summary.csv

runs/*/patch.diff + subjects/<project>/
  -> tools/evaluate_generated_patch_gates.py
  -> workspaces/patch_gate/
  -> results/summary/treatment_patch_gate_results.csv

results/summary/*.csv
  -> tools/build_paper_tables.py
  -> paper/tables/*.csv
```

Traceability principle:

```text
Setiap angka yang dilaporkan harus dapat dilacak ke subject, candidate CSV, evidence JSON, prompt, response, patch, workspace gate, dan summary CSV.
```

## 5. Subject Configuration

Subject pilot didefinisikan di:

```text
datasets.pilot.yml
```

Source code:

```text
subjects/dokuwiki/
subjects/kanboard/
```

Runtime container:

```text
docker/subjects/dokuwiki/
docker/subjects/kanboard/
```

Runtime URLs:

```text
DokuWiki: http://localhost:8102/doku.php
Kanboard: http://localhost:8107/
```

## 6. Pipeline Stages

### 6.1 Subject Audit

Script:

```text
tools/audit_runner.py
```

Fungsi:

- membaca konfigurasi subject
- memastikan repository/tag/commit tersedia
- mencatat metadata subject
- menghasilkan audit matrix

Command:

```powershell
python tools/audit_runner.py `
  --config datasets.pilot.yml `
  --subjects-dir subjects `
  --out results/summary/audit_matrix.csv `
  --clone `
  --count-candidates
```

Output:

```text
results/summary/audit_matrix.csv
```

### 6.2 Candidate and Evidence Extraction

Script:

```text
tools/extract_candidates.py
```

Fungsi:

- memindai file PHP subject
- membentuk function-level dan file-level candidate regions
- menghitung complexity proxy
- mendeteksi request parameter, session key, SQL/data access, DOM selector, dan form
- memberi label `candidate_type`
- menulis candidate CSV dan evidence JSON

Command DokuWiki:

```powershell
python tools/extract_candidates.py `
  --project dokuwiki `
  --subject-dir subjects/dokuwiki `
  --out-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --evidence-dir results/subjects/dokuwiki/evidence
```

Command Kanboard:

```powershell
python tools/extract_candidates.py `
  --project kanboard `
  --subject-dir subjects/kanboard `
  --out-csv results/subjects/kanboard/candidates/candidates.csv `
  --evidence-dir results/subjects/kanboard/evidence
```

Output:

```text
results/subjects/<project>/candidates/candidates.csv
results/subjects/<project>/evidence/*.json
```

Candidate counts:

| Subject | Initial candidates |
|---|---:|
| DokuWiki | 385 |
| Kanboard | 248 |
| Total | 633 |

Metode ekstraksi kandidat dijelaskan secara rinci di:

```text
CANDIDATE_EXTRACTION_METHOD.md
```

### 6.3 Evidence JSON

Evidence JSON menyimpan informasi kandidat yang dipakai pada treatment T3.

Contoh:

```text
results/subjects/dokuwiki/evidence/dokuwiki-C0001.json
```

Field utama:

| Field | Deskripsi |
|---|---|
| `candidate_id` | ID kandidat |
| `subject_id` | subject asal |
| `file` | file sumber |
| `lines` | rentang baris |
| `candidate_type` | jenis kandidat |
| `issues` | issue dan metric proxy |
| `dependencies` | request/session/database dependency |
| `web_contracts` | DOM selector dan form |
| `protected_constraints` | elemen yang harus dipertahankan |
| `allowed_transformations` | transformasi yang diizinkan |
| `test_support` | status oracle/test awal |

### 6.4 Target-Runtime Syntax Gate

Script:

```text
tools/generic_container_syntax_gate.py
```

Fungsi:

- menjalankan `php -l` pada file kandidat
- memakai Docker image runtime target
- menghindari validasi dengan PHP host yang versinya berbeda

Command DokuWiki:

```powershell
python tools/generic_container_syntax_gate.py `
  --project dokuwiki `
  --subject-dir subjects/dokuwiki `
  --candidate-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --image php:5.6-cli `
  --out results/subjects/dokuwiki/syntax/syntax_php56_generic.csv
```

Command Kanboard:

```powershell
python tools/generic_container_syntax_gate.py `
  --project kanboard `
  --subject-dir subjects/kanboard `
  --candidate-csv results/subjects/kanboard/candidates/candidates.csv `
  --image php:7.2-cli `
  --out results/subjects/kanboard/syntax/syntax_php72_generic.csv
```

Output:

```text
results/subjects/<project>/syntax/*.csv
```

### 6.5 Oracle Coverage

Script:

```text
tools/build_oracle_coverage.py
```

Fungsi:

- menghubungkan kandidat ke route/oracle yang stabil
- memisahkan kandidat eligible dari kandidat yang masih pending atau perlu review

Route configuration:

```text
results/subjects/dokuwiki/oracle/routes.json
results/subjects/kanboard/oracle/routes.json
```

Command DokuWiki:

```powershell
python tools/build_oracle_coverage.py `
  --project dokuwiki `
  --candidate-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --routes-json results/subjects/dokuwiki/oracle/routes.json `
  --out results/subjects/dokuwiki/oracle/coverage.csv
```

Command Kanboard:

```powershell
python tools/build_oracle_coverage.py `
  --project kanboard `
  --candidate-csv results/subjects/kanboard/candidates/candidates.csv `
  --routes-json results/subjects/kanboard/oracle/routes.json `
  --out results/subjects/kanboard/oracle/coverage.csv
```

Output:

```text
results/subjects/<project>/oracle/coverage.csv
```

### 6.6 Eligible Candidate Set

Script:

```text
tools/build_eligible_set.py
```

Fungsi:

- menggabungkan kandidat yang memiliki oracle stabil
- menghasilkan candidate set untuk treatment

Command:

```powershell
python tools/build_eligible_set.py `
  --subjects dokuwiki kanboard `
  --out results/summary/eligible_candidates_current.csv
```

Output:

```text
results/summary/eligible_candidates_current.csv
```

Eligible counts:

| Subject | Eligible candidates |
|---|---:|
| DokuWiki | 43 |
| Kanboard | 8 |
| Total | 51 |

### 6.7 Treatment Package Creation

Script:

```text
tools/create_treatment_runs.py
```

Fungsi:

- membuat folder run per candidate
- menyalin metadata kandidat
- menyalin evidence
- mengekstrak code region
- membuat prompt T1
- membuat prompt T3
- membuat decision T2

Command:

```powershell
python tools/create_treatment_runs.py `
  --eligible-csv results/summary/eligible_candidates_current.csv `
  --subjects-dir subjects `
  --out-dir runs `
  --summary-out results/summary/treatment_readiness.csv
```

Output:

```text
runs/<project>/<candidate_id>/
results/summary/treatment_readiness.csv
```

Run folder layout:

```text
runs/<project>/<candidate_id>/
  candidate.json
  evidence.json
  code_region.php
  T1-llm-only/
    prompt.md
    response.txt
    patch.diff
    status.json
  T2-rule-static-only/
    decision.json
    patch.diff
  T3-evidence-llm/
    prompt.md
    response.txt
    patch.diff
    status.json
```

Resume warning:

```text
create_treatment_runs.py menulis ulang status T1/T3 menjadi pending_model_execution. Script ini tidak digunakan untuk resume treatment yang sudah berjalan.
```

### 6.8 LLM Treatment Execution

Script:

```text
tools/run_openai_treatment.py
```

Fungsi:

- membaca `prompt.md`
- mengirim prompt ke OpenAI Responses API
- menyimpan response
- mengekstrak patch
- menyimpan status eksekusi

Resume command:

```powershell
python tools/run_openai_treatment.py `
  --candidate-id kanboard-C0120 `
  --candidate-id kanboard-C0121 `
  --treatment T1-llm-only `
  --treatment T3-evidence-llm `
  --skip-existing `
  --timeout 240 `
  --sleep-seconds 1 `
  --max-prompt-chars 28000
```

Full treatment command:

```powershell
python tools/run_openai_treatment.py `
  --all-eligible `
  --treatment T1-llm-only `
  --treatment T3-evidence-llm `
  --skip-existing `
  --timeout 240 `
  --sleep-seconds 1 `
  --max-prompt-chars 28000
```

Output:

```text
runs/<project>/<candidate_id>/<treatment>/response.txt
runs/<project>/<candidate_id>/<treatment>/patch.diff
runs/<project>/<candidate_id>/<treatment>/status.json
```

Execution counts:

| Treatment | Executed | Generated patches |
|---|---:|---:|
| T1 | 21 | 21 |
| T3 | 19 | 19 |
| Total | 40 | 40 |

### 6.9 Treatment Output Summary

Script:

```text
tools/summarize_treatment_outputs.py
```

Fungsi:

- membaca folder `runs/`
- mencatat status treatment
- mencatat apakah patch tersedia
- mencatat format patch dan ukuran patch

Command:

```powershell
python tools/summarize_treatment_outputs.py
```

Output:

```text
results/summary/treatment_outputs_summary.csv
```

### 6.10 Patch Gate Evaluation

Script:

```text
tools/evaluate_generated_patch_gates.py
```

Fungsi:

- membuat sparse workspace di `workspaces/patch_gate/`
- menyalin file target dari `subjects/`
- menerapkan patch dari `runs/`
- menjalankan `php -l` di Docker
- menghitung LOC delta
- menghitung complexity delta
- memberi label gate outcome

Command:

```powershell
python tools/evaluate_generated_patch_gates.py
```

Output:

```text
results/summary/treatment_patch_gate_results.csv
workspaces/patch_gate/
```

Gate result counts:

| Treatment | Generated | Applied | Syntax pass | Apply failed |
|---|---:|---:|---:|---:|
| T1 | 21 | 17 | 17 | 4 |
| T3 | 19 | 18 | 18 | 1 |
| Total | 40 | 35 | 35 | 5 |

### 6.11 Paper Table Generation

Script:

```text
tools/build_paper_tables.py
```

Fungsi:

- membaca summary CSV
- membuat tabel ringkas untuk paper

Command:

```powershell
python tools/build_paper_tables.py
```

Output:

```text
paper/tables/
```

Tabel utama:

| File | Isi |
|---|---|
| `table_0_dataset_totals.csv` | ringkasan dataset |
| `table_7_treatment_execution.csv` | ringkasan eksekusi treatment |
| `table_8_patch_gate_results.csv` | ringkasan patch gate |

## 7. Reproduction Protocol

### 7.1 Safe Resume

Digunakan untuk melanjutkan eksperimen aktif tanpa menghapus patch yang sudah ada.

```powershell
python tools/run_openai_treatment.py `
  --candidate-id kanboard-C0120 `
  --candidate-id kanboard-C0121 `
  --treatment T1-llm-only `
  --treatment T3-evidence-llm `
  --skip-existing `
  --timeout 240 `
  --sleep-seconds 1 `
  --max-prompt-chars 28000

python tools/summarize_treatment_outputs.py
python tools/evaluate_generated_patch_gates.py
python tools/build_paper_tables.py
```

### 7.2 Full Rebuild

Digunakan untuk membangun ulang artifact dari awal.

```powershell
python tools/audit_runner.py --config datasets.pilot.yml --subjects-dir subjects --out results/summary/audit_matrix.csv --clone --count-candidates

python tools/extract_candidates.py --project dokuwiki --subject-dir subjects/dokuwiki --out-csv results/subjects/dokuwiki/candidates/candidates.csv --evidence-dir results/subjects/dokuwiki/evidence
python tools/extract_candidates.py --project kanboard --subject-dir subjects/kanboard --out-csv results/subjects/kanboard/candidates/candidates.csv --evidence-dir results/subjects/kanboard/evidence

python tools/generic_container_syntax_gate.py --project dokuwiki --subject-dir subjects/dokuwiki --candidate-csv results/subjects/dokuwiki/candidates/candidates.csv --image php:5.6-cli --out results/subjects/dokuwiki/syntax/syntax_php56_generic.csv
python tools/generic_container_syntax_gate.py --project kanboard --subject-dir subjects/kanboard --candidate-csv results/subjects/kanboard/candidates/candidates.csv --image php:7.2-cli --out results/subjects/kanboard/syntax/syntax_php72_generic.csv

python tools/build_oracle_coverage.py --project dokuwiki --candidate-csv results/subjects/dokuwiki/candidates/candidates.csv --routes-json results/subjects/dokuwiki/oracle/routes.json --out results/subjects/dokuwiki/oracle/coverage.csv
python tools/build_oracle_coverage.py --project kanboard --candidate-csv results/subjects/kanboard/candidates/candidates.csv --routes-json results/subjects/kanboard/oracle/routes.json --out results/subjects/kanboard/oracle/coverage.csv

python tools/build_eligible_set.py --subjects dokuwiki kanboard --out results/summary/eligible_candidates_current.csv
python tools/create_treatment_runs.py --eligible-csv results/summary/eligible_candidates_current.csv --subjects-dir subjects --out-dir runs --summary-out results/summary/treatment_readiness.csv
python tools/run_openai_treatment.py --all-eligible --treatment T1-llm-only --treatment T3-evidence-llm --skip-existing --timeout 240 --sleep-seconds 1 --max-prompt-chars 28000
python tools/summarize_treatment_outputs.py
python tools/evaluate_generated_patch_gates.py
python tools/build_paper_tables.py
```

## 8. Overwrite Behavior

| Script | Artifact yang ditulis ulang | Risiko |
|---|---|---|
| `audit_runner.py` | `results/summary/audit_matrix.csv` | rendah |
| `extract_candidates.py` | candidate CSV dan evidence JSON | dapat mengubah dataset kandidat |
| `generic_container_syntax_gate.py` | syntax CSV | rendah jika Docker aktif |
| `build_oracle_coverage.py` | oracle coverage CSV | dapat mengubah eligibility |
| `build_eligible_set.py` | `eligible_candidates_current.csv` | dapat mengubah treatment set |
| `create_treatment_runs.py` | `runs/` prompt/status dan `treatment_readiness.csv` | tinggi untuk resume |
| `run_openai_treatment.py` | response, patch, status | aman untuk resume jika `--skip-existing` dipakai |
| `summarize_treatment_outputs.py` | `treatment_outputs_summary.csv` | rendah |
| `evaluate_generated_patch_gates.py` | `workspaces/patch_gate/` dan `treatment_patch_gate_results.csv` | menulis ulang gate summary |
| `build_paper_tables.py` | `paper/tables/*.csv` | menulis ulang tabel paper |

## 9. Claim Boundary

Klaim yang didukung artifact saat ini:

- dataset kandidat nyata berhasil dibangun dari DokuWiki dan Kanboard
- candidate-level evidence tersedia untuk setiap kandidat awal
- target-runtime syntax gate berhasil dijalankan
- eligible candidates dikunci melalui oracle coverage
- T1 dan T3 menghasilkan patch pada executed subset
- patch gate awal menunjukkan T3 lebih stabil daripada T1 pada executed subset

Klaim yang belum didukung penuh:

- semantic preservation penuh
- route-level regression safety penuh
- rendered-output equivalence
- full accepted-and-improving transformation untuk seluruh 51 eligible candidates
- generalisasi ke semua aplikasi PHP monolitik

## 10. Non-Black-Box Traceability

Eksperimen tidak bergantung pada output yang tidak terlacak. Artifact berikut menyimpan jejak setiap tahap:

| Tahap | Artifact |
|---|---|
| subject selection | `datasets.pilot.yml` |
| source code | `subjects/<project>/` |
| candidate extraction | `results/subjects/<project>/candidates/candidates.csv` |
| evidence | `results/subjects/<project>/evidence/*.json` |
| syntax gate | `results/subjects/<project>/syntax/*.csv` |
| oracle mapping | `results/subjects/<project>/oracle/coverage.csv` |
| eligible set | `results/summary/eligible_candidates_current.csv` |
| prompt | `runs/<project>/<candidate_id>/<treatment>/prompt.md` |
| LLM response | `runs/<project>/<candidate_id>/<treatment>/response.txt` |
| patch | `runs/<project>/<candidate_id>/<treatment>/patch.diff` |
| treatment status | `runs/<project>/<candidate_id>/<treatment>/status.json` |
| patch gate | `results/summary/treatment_patch_gate_results.csv` |
| paper tables | `paper/tables/*.csv` |

Dengan struktur ini, setiap hasil dapat diuji ulang dari konfigurasi subject sampai tabel paper.
