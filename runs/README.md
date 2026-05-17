# Struktur Folder `runs`

Folder ini menyimpan paket treatment per kandidat. Isi folder ini adalah jejak eksperimen LLM: prompt, response, patch, status, evidence, dan potongan kode.

Struktur:

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

## Arti File

| File | Isi |
|---|---|
| `candidate.json` | metadata kandidat yang diambil dari eligible set |
| `evidence.json` | bukti analisis statis untuk kandidat |
| `code_region.php` | potongan kode yang diberikan ke prompt |
| `prompt.md` | instruksi yang dikirim ke AI |
| `response.txt` | jawaban mentah dari AI |
| `patch.diff` | patch/tambalan yang diekstrak dari jawaban AI |
| `status.json` | status eksekusi treatment |
| `decision.json` | keputusan T2 rule/static-only |

## Treatment

| Treatment | Isi |
|---|---|
| `T1-llm-only` | prompt berisi kode dan instruksi umum |
| `T2-rule-static-only` | baseline aturan mekanis; saat ini `not_applicable` untuk kandidat terkunci |
| `T3-evidence-llm` | prompt berisi kode, evidence JSON, constraint, dan allowed transformation |

## Status Saat Ini

Eksperimen saat ini sudah menghasilkan patch untuk executed subset:

| Treatment | Executed | Generated patches |
|---|---:|---:|
| T1 | 21 | 21 |
| T3 | 19 | 19 |
| Total | 40 | 40 |

Sebagian prompt masih pending karena API rate limit. Oleh karena itu, hasil paper harus disebut sebagai executed-subset pilot, bukan evaluasi penuh semua kandidat.

## Catatan Aman

Jangan menjalankan ulang `tools/create_treatment_runs.py` hanya untuk resume, karena script itu bisa menulis ulang `status.json` menjadi `pending_model_execution`.

Untuk melanjutkan eksperimen yang sudah ada, gunakan:

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

Opsi `--skip-existing` menjaga patch yang sudah ada agar tidak dibuat ulang.
