# Struktur Folder `results`

Folder ini menyimpan hasil eksperimen yang sudah diproses. Isi folder ini bukan source code aplikasi, tetapi artifact hasil audit, kandidat, evidence, syntax gate, oracle, dan ringkasan treatment.

Struktur utama:

```text
results/
  summary/
    audit_matrix.csv
    candidate_summary_all.csv
    syntax_summary_target.csv
    screening_summary_all.csv
    eligible_candidates_current.csv
    treatment_outputs_summary.csv
    treatment_patch_gate_results.csv
    artifact_manifest.csv
  subjects/
    <project>/
      audit/
      candidates/
      evidence/
      syntax/
      screening/
      characterization/
      oracle/
      notes/
  legacy_flat/
```

## Arti Folder Per Subject

| Folder | Isi |
|---|---|
| `audit/` | hasil audit subject, misalnya repo, tag, runtime, dan status awal |
| `candidates/` | daftar kandidat hasil ekstraksi statis |
| `evidence/` | satu file JSON evidence untuk setiap kandidat |
| `syntax/` | hasil cek sintaks PHP di runtime target |
| `screening/` | label screening sebelum treatment |
| `characterization/` | hasil pengecekan HTTP/runtime baseline |
| `oracle/` | mapping kandidat ke route/oracle yang stabil |
| `notes/` | catatan pemulihan environment atau ekstraksi |

## Subject Aktif

| Subject | Peran |
|---|---|
| DokuWiki | subject aktif untuk candidate extraction, oracle mapping, treatment, dan patch gate |
| Kanboard | subject aktif untuk candidate extraction, oracle mapping, treatment parsial, dan patch gate parsial |

Runtime artifact:

| Subject | Artifact |
|---|---|
| DokuWiki | `results/subjects/dokuwiki/characterization/`, `results/subjects/dokuwiki/oracle/` |
| Kanboard | `results/subjects/kanboard/characterization/`, `results/subjects/kanboard/oracle/` |

## Scope Pelaporan Saat Ini

Eksperimen saat ini dilaporkan sebagai:

```text
two-subject executed-subset pilot
```

Artinya:

- DokuWiki dan Kanboard sama-sama masuk dataset pilot.
- Total kandidat awal adalah 633.
- Total kandidat eligible adalah 51.
- Treatment LLM yang sudah selesai baru subset yang berhasil dieksekusi sebelum API rate limit.
- Perbandingan T1 dan T3 tidak boleh diklaim sebagai evaluasi penuh untuk semua 51 kandidat.

Angka aktif:

| Metric | Nilai |
|---|---:|
| Initial candidates | 633 |
| Locked eligible candidates | 51 |
| T1 prompts executed | 21 |
| T3 prompts executed | 19 |
| Generated LLM patches | 40 |
| Applied and syntax-pass patches | 35 |

## File Summary Penting

| File | Fungsi |
|---|---|
| `results/summary/audit_matrix.csv` | ringkasan audit subject |
| `results/summary/eligible_candidates_current.csv` | kandidat yang terkunci untuk treatment |
| `results/summary/treatment_outputs_summary.csv` | status eksekusi T1/T2/T3 |
| `results/summary/treatment_patch_gate_results.csv` | hasil apply patch, syntax gate, LOC delta, complexity delta, dan outcome |
| `results/summary/artifact_manifest.csv` | manifest artifact hasil eksperimen |

## Catatan Tentang `legacy_flat`

Folder `results/legacy_flat/` berisi artifact lama dari struktur awal yang belum dirapikan. Artifact baru sebaiknya ditulis ke:

```text
results/subjects/<project>/...
results/summary/...
```
