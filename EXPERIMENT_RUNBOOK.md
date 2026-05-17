# Experiment Runbook

Dokumen ini menjelaskan cara menjalankan eksperimen dari root repo.

Gunakan PowerShell dan masuk dulu ke folder proyek:

```powershell
cd C:\Users\acer\Herd\test-guarded
```

## Gambaran Singkat

Eksperimen ini mencoba menjawab pertanyaan:

```text
Kalau AI diminta merapikan kode PHP lama, apakah hasilnya lebih stabil kalau AI diberi bukti analisis kode?
```

Alur sederhananya:

```text
aplikasi PHP lama
  -> ambil kandidat kode
  -> buat bukti analisis
  -> pilih kandidat yang bisa diuji
  -> buat prompt AI
  -> AI membuat tambalan
  -> pasang tambalan di workspace salinan
  -> cek apakah tambalan bisa dipasang
  -> cek sintaks PHP di Docker
  -> hitung perubahan LOC/kompleksitas
  -> buat tabel hasil untuk paper
```

Istilah penting:

| Istilah | Arti mudah |
|---|---|
| subject | aplikasi yang diuji, yaitu DokuWiki dan Kanboard |
| kandidat | bagian kode yang mau dirapikan |
| evidence | bukti analisis untuk kandidat, misalnya file, baris, jenis masalah, constraint |
| treatment | jenis perlakuan eksperimen |
| tambalan | patch/perubahan kode dari AI |
| gate | pos pemeriksaan sebelum tambalan dianggap layak |

Treatment yang dipakai:

| Treatment | Maksud |
|---|---|
| `T1-llm-only` | AI diberi kode dan instruksi umum |
| `T2-rule-static-only` | baseline aturan mekanis, sekarang `not_applicable` |
| `T3-evidence-llm` | AI diberi kode, evidence, constraint, dan allowed transformation |

## Jalur Aman: Melanjutkan Eksperimen Saat Ini

Gunakan jalur ini kalau tidak mau menghilangkan hasil yang sudah ada.

Saat ini hasil utama sudah ada:

| Metric | Nilai |
|---|---:|
| Active subjects | 2 |
| Initial candidates | 633 |
| Locked eligible candidates | 51 |
| T1 prompts executed | 21 |
| T3 prompts executed | 19 |
| Generated LLM patches | 40 |
| Applied and syntax-pass patches | 35 |

Yang belum selesai hanya 3 prompt Kanboard:

- `kanboard-C0120` T3
- `kanboard-C0121` T1
- `kanboard-C0121` T3

### 1. Hidupkan Docker

Maksud tahap ini:

Docker dipakai untuk menjalankan PHP versi lama sesuai subject. DokuWiki butuh PHP 5.6, Kanboard memakai PHP 7.2. Jangan pakai PHP host modern sebagai bukti utama.

Command:

```powershell
Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe" -WindowStyle Hidden
docker info
```

Kalau `docker info` gagal, jangan lanjut ke patch gate.

### 2. Jalankan Container Aplikasi

Maksud tahap ini:

Aplikasi harus hidup supaya karakterisasi dan gate runtime bisa dijalankan.

Command:

```powershell
docker compose -f docker/subjects/dokuwiki/docker-compose.yml up -d --build
docker compose -f docker/subjects/kanboard/docker-compose.yml up -d --build
```

URL subject:

| Subject | URL |
|---|---|
| DokuWiki | `http://localhost:8102/doku.php` |
| Kanboard | `http://localhost:8107/` |

### 3. Backup Hasil Sebelum Resume

Maksud tahap ini:

Supaya hasil test, patch, dan tabel yang sudah ada tidak hilang kalau ada script yang menulis ulang output.

Command:

```powershell
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = ".local/backups/experiment-$ts"
New-Item -ItemType Directory -Force -Path $backup | Out-Null
Copy-Item -Recurse -Force results/summary "$backup/results-summary"
Copy-Item -Recurse -Force paper/tables "$backup/paper-tables"
Copy-Item -Recurse -Force runs "$backup/runs"
```

### 4. Jalankan Sisa Prompt AI

Maksud tahap ini:

Mengirim prompt kandidat yang masih pending ke OpenAI API. Opsi `--skip-existing` wajib dipakai supaya patch yang sudah ada tidak dibuat ulang.

Pastikan API key sudah ada di environment:

```powershell
$env:OPENAI_API_KEY
```

Kalau kosong, set dulu di PowerShell. Jangan simpan key di file repo.

Command:

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

Hasil yang dibuat:

```text
runs/kanboard/<candidate_id>/<treatment>/response.txt
runs/kanboard/<candidate_id>/<treatment>/patch.diff
runs/kanboard/<candidate_id>/<treatment>/status.json
```

### 5. Ringkas Hasil Treatment

Maksud tahap ini:

Membaca semua folder `runs/` dan membuat ringkasan: mana yang sudah model executed, mana yang pending, mana yang menghasilkan patch.

Command:

```powershell
python tools/summarize_treatment_outputs.py
```

Output:

```text
results/summary/treatment_outputs_summary.csv
```

### 6. Jalankan Patch Gate

Maksud tahap ini:

Setiap patch dipasang ke salinan file di `workspaces/patch_gate/`, bukan ke source asli. Setelah itu script mengecek:

- patch bisa dipasang atau gagal
- file PHP yang berubah lolos `php -l` di Docker
- LOC sebelum/sesudah
- complexity proxy sebelum/sesudah
- label outcome

Command:

```powershell
python tools/evaluate_generated_patch_gates.py
```

Output:

```text
results/summary/treatment_patch_gate_results.csv
workspaces/patch_gate/
```

Catatan aman:

Script ini menulis ulang `workspaces/patch_gate/` dan `results/summary/treatment_patch_gate_results.csv`, tetapi tidak menghapus patch asli di `runs/`.

### 7. Buat Tabel Paper

Maksud tahap ini:

Mengubah hasil CSV eksperimen menjadi tabel ringkas yang bisa dimasukkan ke paper.

Command:

```powershell
python tools/build_paper_tables.py
```

Output:

```text
paper/tables/
```

Tabel utama:

| Tabel | Isi |
|---|---|
| `paper/tables/table_0_dataset_totals.csv` | ringkasan dataset |
| `paper/tables/table_7_treatment_execution.csv` | jumlah prompt/treatment yang jalan |
| `paper/tables/table_8_patch_gate_results.csv` | hasil patch gate |

## Jalur Reproduksi Penuh Dari Awal

Gunakan bagian ini hanya kalau ingin membangun ulang eksperimen dari awal. Jalur ini bisa menulis ulang output lama.

Sebelum mulai, lakukan backup seperti di bagian resume.

### 1. Audit Subject

Maksud tahap ini:

Membaca `datasets.pilot.yml`, memastikan subject tersedia, dan membuat ringkasan subject yang dipakai.

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

### 2. Ekstrak Kandidat dan Evidence

Maksud tahap ini:

Mencari bagian kode yang berpotensi dirapikan. Misalnya long method, mixed PHP/HTML, SQL/data access, session logic, dan form handling.

DokuWiki:

```powershell
python tools/extract_candidates.py `
  --project dokuwiki `
  --subject-dir subjects/dokuwiki `
  --out-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --evidence-dir results/subjects/dokuwiki/evidence
```

Kanboard:

```powershell
python tools/extract_candidates.py `
  --project kanboard `
  --subject-dir subjects/kanboard `
  --out-csv results/subjects/kanboard/candidates/candidates.csv `
  --evidence-dir results/subjects/kanboard/evidence
```

Output:

```text
results/subjects/dokuwiki/candidates/candidates.csv
results/subjects/dokuwiki/evidence/*.json
results/subjects/kanboard/candidates/candidates.csv
results/subjects/kanboard/evidence/*.json
```

### 3. Cek Sintaks Runtime Target

Maksud tahap ini:

Memastikan file kandidat valid di versi PHP yang sesuai, bukan hanya valid di PHP host.

DokuWiki:

```powershell
python tools/generic_container_syntax_gate.py `
  --project dokuwiki `
  --subject-dir subjects/dokuwiki `
  --candidate-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --image php:5.6-cli `
  --out results/subjects/dokuwiki/syntax/syntax_php56_generic.csv
```

Kanboard:

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
results/subjects/dokuwiki/syntax/syntax_php56_generic.csv
results/subjects/kanboard/syntax/syntax_php72_generic.csv
```

### 4. Buat Oracle Coverage

Maksud tahap ini:

Menghubungkan kandidat ke patokan uji/rute yang stabil. Kandidat yang tidak bisa dikaitkan ke rute stabil tidak dipakai sebagai eligible treatment candidate.

DokuWiki:

```powershell
python tools/build_oracle_coverage.py `
  --project dokuwiki `
  --candidate-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --routes-json results/subjects/dokuwiki/oracle/routes.json `
  --out results/subjects/dokuwiki/oracle/coverage.csv
```

Kanboard:

```powershell
python tools/build_oracle_coverage.py `
  --project kanboard `
  --candidate-csv results/subjects/kanboard/candidates/candidates.csv `
  --routes-json results/subjects/kanboard/oracle/routes.json `
  --out results/subjects/kanboard/oracle/coverage.csv
```

Output:

```text
results/subjects/dokuwiki/oracle/coverage.csv
results/subjects/kanboard/oracle/coverage.csv
```

### 5. Kunci Eligible Candidates

Maksud tahap ini:

Menggabungkan kandidat yang sudah punya oracle stabil menjadi dataset treatment.

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

### 6. Buat Paket Treatment

Maksud tahap ini:

Membuat folder per kandidat di `runs/`. Di dalamnya ada prompt T1, keputusan T2, prompt T3, evidence, dan potongan kode.

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

Peringatan:

Script ini menulis ulang `status.json` T1/T3 menjadi `pending_model_execution`. Jangan jalankan ini kalau hanya ingin resume hasil yang sudah ada.

### 7. Jalankan LLM Treatment

Maksud tahap ini:

Mengirim prompt T1 dan T3 ke OpenAI API untuk membuat tambalan.

Command:

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
runs/<project>/<candidate_id>/T1-llm-only/patch.diff
runs/<project>/<candidate_id>/T3-evidence-llm/patch.diff
```

### 8. Ringkas Treatment, Jalankan Gate, Buat Tabel

Maksud tahap ini:

Mengubah patch yang sudah dibuat menjadi angka hasil paper.

Command:

```powershell
python tools/summarize_treatment_outputs.py
python tools/evaluate_generated_patch_gates.py
python tools/build_paper_tables.py
```

Output:

```text
results/summary/treatment_outputs_summary.csv
results/summary/treatment_patch_gate_results.csv
paper/tables/
```

## Script Yang Menulis Ulang Artifact

Gunakan tabel ini untuk tahu mana script yang aman untuk resume dan mana yang harus hati-hati.

| Script | Artifact yang ditulis ulang | Catatan |
|---|---|---|
| `audit_runner.py` | `results/summary/audit_matrix.csv` | aman jika memang ingin audit ulang |
| `extract_candidates.py` | candidates CSV dan evidence JSON | hati-hati, bisa mengubah dataset kandidat |
| `generic_container_syntax_gate.py` | syntax CSV | aman jika Docker hidup |
| `build_oracle_coverage.py` | oracle coverage CSV | hati-hati jika route config berubah |
| `build_eligible_set.py` | `eligible_candidates_current.csv` | hati-hati, mengubah kandidat treatment |
| `create_treatment_runs.py` | `runs/` prompt/status dan `treatment_readiness.csv` | jangan untuk resume |
| `run_openai_treatment.py` | response, patch, status per treatment | aman jika pakai `--skip-existing` |
| `summarize_treatment_outputs.py` | `treatment_outputs_summary.csv` | aman setelah treatment |
| `evaluate_generated_patch_gates.py` | `workspaces/patch_gate/` dan `treatment_patch_gate_results.csv` | aman setelah backup |
| `build_paper_tables.py` | `paper/tables/*.csv` | aman setelah summary/gate benar |

## Artifact Utama

| Artifact | Isi |
|---|---|
| `results/summary/audit_matrix.csv` | ringkasan subject |
| `results/subjects/<project>/candidates/candidates.csv` | daftar kandidat |
| `results/subjects/<project>/evidence/*.json` | bukti analisis kandidat |
| `results/subjects/<project>/syntax/*.csv` | hasil cek sintaks runtime target |
| `results/subjects/<project>/oracle/coverage.csv` | mapping kandidat ke oracle/rute |
| `results/summary/eligible_candidates_current.csv` | kandidat yang terkunci untuk treatment |
| `runs/<project>/<candidate_id>/` | prompt, response, patch, dan status |
| `results/summary/treatment_outputs_summary.csv` | ringkasan eksekusi treatment |
| `results/summary/treatment_patch_gate_results.csv` | hasil patch gate |
| `paper/tables/*.csv` | tabel siap masuk paper |

## Cara Membaca Hasil Untuk Paper

Paper saat ini harus disebut sebagai:

```text
two-subject executed-subset pilot
```

Artinya:

- subject ada dua: DokuWiki dan Kanboard
- eligible candidates ada 51
- treatment yang selesai baru subset yang berhasil dieksekusi sebelum rate limit
- hasil T1 vs T3 tidak boleh diklaim sebagai evaluasi penuh semua kandidat

Angka terakhir yang dipakai:

| Metric | Nilai |
|---|---:|
| Active subjects | 2 |
| Initial candidates | 633 |
| Locked eligible candidates | 51 |
| T1 prompts executed | 21 |
| T3 prompts executed | 19 |
| Generated LLM patches | 40 |
| Applied and syntax-pass patches | 35 |

Kalimat aman untuk paper:

```text
The treatment comparison is based on the executed subset, not a completed evaluation over all 51 eligible candidates.
```
