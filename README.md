# Test-Guarded LLM-Assisted Reengineering of Legacy PHP Monoliths

Repository ini berisi artifact eksperimen untuk studi:

```text
Test-Guarded LLM-Assisted Reengineering of Legacy PHP-Based Monolithic Web Applications Using Static-Analysis Evidence
```

Eksperimen ini mengevaluasi apakah patch reengineering dari LLM menjadi lebih stabil ketika prompt diberi **candidate-level static-analysis evidence** dan hasilnya dicek melalui beberapa **gate**.

## Ringkasan Eksperimen

Subject pilot:

| Subject | Versi | Runtime target |
|---|---|---|
| DokuWiki | `release-2018-04-22b` | PHP 5.6 |
| Kanboard | `v1.2.13` | PHP 7.2 |

Status eksperimen saat ini:

| Metric | Nilai |
|---|---:|
| Initial candidates | 633 |
| Locked eligible candidates | 51 |
| T1 prompts executed | 21 |
| T3 prompts executed | 19 |
| Generated LLM patches | 40 |
| Applied and syntax-pass patches | 35 |

Scope pelaporan:

```text
two-subject executed-subset pilot
```

Artinya, hasil treatment T1/T3 dilaporkan berdasarkan subset prompt yang berhasil dieksekusi, bukan evaluasi penuh terhadap semua 51 eligible candidates.

## Struktur Repository

| Path | Isi |
|---|---|
| `datasets.pilot.yml` | konfigurasi subject pilot |
| `datasets.rio-audit.yml` | konfigurasi subject pool dari jalur Rio et al. |
| `tools/` | script pipeline eksperimen |
| `subjects/` | source code subject PHP |
| `docker/` | konfigurasi runtime Docker |
| `results/` | hasil kandidat, evidence, syntax, oracle, dan summary |
| `runs/` | prompt, response, patch, dan status per candidate/treatment |
| `workspaces/` | workspace sementara untuk patch gate |
| `paper/` | tabel dan material pendukung paper |
| `.local/` | file lokal, backup, source PDF, dan scratch yang tidak menjadi artifact utama |

## Dokumentasi Utama

| Dokumen | Fungsi |
|---|---|
| `PROJECT_EXPERIMENT_MAP.md` | peta struktur proyek, alur data, dan traceability artifact |
| `EXPERIMENT_RUNBOOK.md` | cara menjalankan eksperimen dan script pipeline |
| `CANDIDATE_EXTRACTION_METHOD.md` | metode teknis ekstraksi kandidat |
| `FULL_STUDY_WORKFLOW.md` | perbedaan pilot saat ini dan versi full study |
| `results/README.md` | penjelasan folder hasil eksperimen |
| `runs/README.md` | penjelasan folder prompt/patch/status |

## Alur Data

```text
datasets.pilot.yml
  -> audit subject
  -> extract candidates
  -> build evidence JSON
  -> syntax gate
  -> oracle coverage
  -> eligible candidates
  -> create treatment runs
  -> run LLM treatment
  -> summarize treatment outputs
  -> patch gate
  -> paper tables
```

Artifact utama:

| Artifact | Isi |
|---|---|
| `results/summary/eligible_candidates_current.csv` | kandidat yang masuk treatment |
| `results/summary/treatment_outputs_summary.csv` | status eksekusi treatment |
| `results/summary/treatment_patch_gate_results.csv` | hasil patch gate |
| `paper/tables/*.csv` | tabel siap masuk paper |

## Cara Menjalankan Eksperimen

Panduan lengkap ada di:

```text
EXPERIMENT_RUNBOOK.md
```

Untuk melanjutkan eksperimen aktif tanpa menghapus patch yang sudah ada, gunakan jalur **Safe Resume** di runbook.

Untuk reproduksi penuh dari awal, gunakan jalur **Full Rebuild** di runbook.

## Prasyarat

- Windows PowerShell
- Docker Desktop
- Python 3
- akses OpenAI API untuk treatment LLM
- environment variable `OPENAI_API_KEY` saat menjalankan `tools/run_openai_treatment.py`

Contoh cek API key:

```powershell
$env:OPENAI_API_KEY
```

Jangan menyimpan API key di file repository.

## Klaim yang Didukung

Klaim yang didukung artifact saat ini:

- dataset kandidat nyata berhasil dibangun dari DokuWiki dan Kanboard
- candidate-level evidence tersedia untuk kandidat awal
- target-runtime syntax gate dijalankan dengan Docker
- eligible candidates dikunci melalui oracle coverage
- T1 dan T3 menghasilkan patch pada executed subset
- T3 menunjukkan patch stability yang lebih baik daripada T1 pada executed subset

Klaim yang belum didukung penuh:

- semantic preservation penuh
- route-level regression safety penuh
- rendered-output equivalence
- full accepted-and-improving transformation untuk semua 51 eligible candidates
- generalisasi ke semua aplikasi PHP monolitik

## Replication Repository

Repository ini berfungsi sebagai replication package untuk eksperimen.

URL:

```text
https://github.com/ediprin/Test-Guarded-LLM-Assisted-Reengineering-of-Legacy-PHP-Based-Monolithic.git
```

Jika artifact dipakai untuk paper, sebaiknya gunakan tag/release tertentu, misalnya:

```text
v1.0-paper
```

Tag ini membuat artifact yang dirujuk di paper tidak berubah setelah paper dikirim.
