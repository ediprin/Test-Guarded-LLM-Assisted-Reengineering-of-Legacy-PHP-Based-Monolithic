# Candidate Extraction Method

Dokumen ini menjelaskan bagaimana kandidat reengineering didapatkan oleh script:

```text
tools/extract_candidates.py
```

Tujuannya adalah membuat proses ekstraksi kandidat tidak menjadi kotak hitam. Kandidat tidak dipilih manual satu-satu, tetapi dicari dari source code PHP dengan aturan statis yang eksplisit.

## 1. Definisi Kandidat

Kandidat adalah bagian kode lokal yang layak dipertimbangkan untuk dirapikan.

Dalam eksperimen ini, kandidat bisa berupa:

- satu file PHP yang kompleks
- satu fungsi PHP yang panjang
- region kode yang mencampur PHP dan HTML
- region yang menangani request/form
- region yang memakai session
- region yang mengandung akses SQL/data

Kandidat bukan berarti patch pasti aman. Kandidat hanya berarti:

```text
bagian kode ini punya tanda-tanda maintainability issue dan layak masuk tahap screening berikutnya.
```

## 2. Input dan Output

Input:

```text
subjects/<project>/
```

Contoh:

```text
subjects/dokuwiki/
subjects/kanboard/
```

Output:

```text
results/subjects/<project>/candidates/candidates.csv
results/subjects/<project>/evidence/<candidate_id>.json
```

Command:

```powershell
python tools/extract_candidates.py `
  --project dokuwiki `
  --subject-dir subjects/dokuwiki `
  --out-csv results/subjects/dokuwiki/candidates/candidates.csv `
  --evidence-dir results/subjects/dokuwiki/evidence
```

```powershell
python tools/extract_candidates.py `
  --project kanboard `
  --subject-dir subjects/kanboard `
  --out-csv results/subjects/kanboard/candidates/candidates.csv `
  --evidence-dir results/subjects/kanboard/evidence
```

## 3. File yang Dibaca

Script hanya membaca file dengan ekstensi berikut:

```text
.php
.phtml
.inc
.module
```

Folder berikut dilewati:

```text
.git
vendor
node_modules
tests
test
_test
_cs
cache
tmp
```

Alasannya:

- `vendor` dan `node_modules` adalah dependency eksternal
- `tests` bukan target reengineering aplikasi
- `cache` dan `tmp` bukan source utama
- `.git` bukan kode aplikasi

## 4. Cara Script Membentuk Region Kode

Script mencari dua jenis region:

1. function-level region
2. file-level region

### 4.1 Function-Level Region

Script mencari pola:

```php
function namaFungsi(...)
```

Setiap fungsi dianggap sebagai satu region dari:

```text
awal function
sampai sebelum function berikutnya
```

Function masuk kandidat kalau memenuhi salah satu:

```text
jumlah baris >= 40
atau
complexity proxy >= 8
```

Artinya, fungsi yang panjang atau punya banyak percabangan/perulangan akan masuk sebagai kandidat.

### 4.2 File-Level Region

Script juga bisa menganggap satu file penuh sebagai kandidat.

Syarat awal:

```text
jumlah baris file >= 20
```

Lalu file harus memiliki minimal 2 dari 5 sinyal berikut:

```text
campur PHP/HTML
ada SQL/data access
ada $_SESSION
ada $_GET/$_POST/$_REQUEST
complexity proxy >= 12
```

Jika syarat ini terpenuhi, region yang dibuat adalah:

```text
baris 1 sampai baris terakhir file
```

Contoh:

```text
dokuwiki-C0001
file: doku.php
lines: 1-125
candidate_type: long_method_or_region
```

## 5. Complexity Proxy

Script tidak menjalankan PHPMD penuh pada tahap ini. Untuk ekstraksi awal, script memakai complexity proxy sederhana.

Complexity proxy dihitung dari jumlah token:

```text
if
elseif
for
foreach
while
case
catch
&&
||
?
```

Rumus:

```text
complexity_proxy = 1 + jumlah token percabangan/perulangan
```

Contoh:

```text
complexity_proxy = 22
```

Artinya region tersebut memiliki banyak titik keputusan menurut proxy sederhana ini.

Catatan:

```text
Complexity proxy bukan pengganti penuh cyclomatic complexity dari static-analysis tool. Proxy ini dipakai untuk candidate mining awal.
```

## 6. Sinyal Web yang Dicari

Script mencari pola web-facing behavior supaya prompt AI tahu bagian mana yang harus dijaga.

### 6.1 Request Parameters

Pola yang dicari:

```php
$_GET['name']
$_POST['name']
$_REQUEST['name']
```

Disimpan sebagai:

```text
request_parameters
```

Contoh:

```text
do
idx
submit
```

### 6.2 Session Keys

Pola yang dicari:

```php
$_SESSION['key']
```

Disimpan sebagai:

```text
session_keys
```

### 6.3 SQL/Data Access

Script menganggap region punya akses data kalau menemukan pola seperti:

```text
PDO
mysqli_
mysql_
pg_query
db_query
DB::
executeQuery
```

Atau string SQL:

```sql
SELECT ... FROM
INSERT INTO
UPDATE
DELETE FROM
```

Jika memungkinkan, nama tabel diambil dari pola:

```sql
FROM table
JOIN table
UPDATE table
INTO table
```

Disimpan sebagai:

```text
database_tables
```

### 6.4 DOM Selectors

Script mencari HTML id dan class:

```html
id="..."
class="..."
```

Disimpan sebagai:

```text
dom_selectors
```

Contoh:

```text
#login
.form-control
.btn
```

### 6.5 Forms

Script mencari:

```html
<form name="...">
<form action="...">
```

Disimpan sebagai:

```text
forms
```

## 7. Penentuan Candidate Type

Setelah region ditemukan, script menentukan jenis kandidat dengan urutan aturan berikut:

| Kondisi | Candidate type | Dominant issue |
|---|---|---|
| campur PHP/HTML dan ada SQL | `mixed_php_html_sql` | SQL in Presentation Logic |
| campur PHP/HTML dan ada request parameter | `form_handling` | Request Handling Mixed With Rendering |
| campur PHP/HTML | `mixed_php_html` | Mixed PHP/HTML |
| ada session | `session_dependent_logic` | Session-Dependent Logic |
| ada SQL/data access | `sql_data_access` | SQL/Data Access Region |
| baris >= 100 atau complexity >= 10 | `long_method_or_region` | Long or Complex Region |
| selain itu | `local_region` | Maintainability Candidate |

`local_region` tidak disimpan sebagai kandidat akhir karena sinyalnya terlalu lemah.

## 8. Allowed Transformations

Setiap candidate type diberi daftar transformasi yang boleh dilakukan.

| Candidate type | Allowed transformations |
|---|---|
| `long_method_or_region` | `Extract Method` |
| `mixed_php_html` | `Separate PHP Logic from Markup`, `Extract View Helper` |
| `form_handling` | `Extract Validation Helper`, `Extract Method`, `Extract View Helper` |
| `session_dependent_logic` | `Extract Guard`, `Extract Method` |
| `sql_data_access` | `Light Data-Access Isolation`, `Extract Method` |
| `mixed_php_html_sql` | `Light Data-Access Isolation`, `Extract Method`, `Extract View Helper` |

Allowed transformations dipakai untuk membatasi AI. AI tidak diberi izin melakukan rewrite besar, migrasi framework, migrasi database, atau microservice extraction.

## 9. Isi CSV Kandidat

Setiap kandidat ditulis ke:

```text
results/subjects/<project>/candidates/candidates.csv
```

Kolom:

| Kolom | Isi |
|---|---|
| `candidate_id` | ID unik kandidat |
| `project` | nama subject |
| `file` | file sumber |
| `start_line` | baris awal region |
| `end_line` | baris akhir region |
| `candidate_type` | jenis kandidat |
| `dominant_issue` | masalah utama |
| `complexity_proxy` | proxy kompleksitas |
| `request_parameters` | parameter GET/POST/REQUEST |
| `session_keys` | key session |
| `database_tables` | tabel database yang terdeteksi |
| `dom_selectors` | id/class HTML yang perlu dijaga |
| `forms` | form name/action |
| `allowed_transformations` | transformasi yang boleh |
| `oracle_status` | status oracle awal, default `pending` |

Contoh:

```text
candidate_id: dokuwiki-C0001
project: dokuwiki
file: doku.php
start_line: 1
end_line: 125
candidate_type: long_method_or_region
dominant_issue: Long or Complex Region
complexity_proxy: 22
request_parameters: do;idx
allowed_transformations: Extract Method
oracle_status: pending
```

## 10. Isi Evidence JSON

Setiap kandidat juga punya evidence JSON:

```text
results/subjects/<project>/evidence/<candidate_id>.json
```

Isi utamanya:

```json
{
  "candidate_id": "dokuwiki-C0001",
  "subject_id": "dokuwiki",
  "file": "doku.php",
  "lines": [1, 125],
  "candidate_type": "long_method_or_region",
  "issues": [
    {
      "type": "Long or Complex Region",
      "evidence": "Detected by pre-treatment heuristic extractor; join with PHPMD/PHPStan logs for final static evidence."
    },
    {
      "type": "Complexity Proxy",
      "metric": "branch_keyword_count_plus_one",
      "value": 22
    }
  ],
  "dependencies": {
    "request_parameters": ["do", "idx"],
    "session_keys": [],
    "database_tables": []
  },
  "protected_constraints": {
    "must_preserve_request_parameters": ["do", "idx"],
    "must_preserve_session_keys": [],
    "must_preserve_database_tables": [],
    "must_preserve_dom_selectors": [],
    "must_preserve_forms": []
  },
  "allowed_transformations": ["Extract Method"],
  "test_support": {
    "oracle_status": "pending"
  }
}
```

Evidence JSON ini dipakai dalam prompt T3.

## 11. Kenapa Tidak Semua Kandidat Dipakai?

Hasil ekstraksi kandidat masih mentah.

Alur setelah ekstraksi:

```text
candidates.csv
  -> syntax gate
  -> oracle coverage
  -> eligible_candidates_current.csv
  -> treatment
```

Kandidat hanya masuk treatment kalau:

1. file kandidat lolos syntax gate di runtime target
2. kandidat bisa dikaitkan ke patokan uji/rute yang stabil
3. kandidat masuk `eligible_candidates_current.csv`

Hasil saat ini:

| Subject | Kandidat awal | Eligible |
|---|---:|---:|
| DokuWiki | 385 | 43 |
| Kanboard | 248 | 8 |
| Total | 633 | 51 |

## 12. Batasan Metode Ekstraksi

Metode ini punya batasan:

1. Berbasis heuristic, bukan parser PHP penuh.
2. Tidak membuktikan bug atau semantic problem.
3. Complexity proxy bukan pengganti PHPMD/PHPStan.
4. Deteksi SQL, session, form, dan DOM berbasis pola teks.
5. Kandidat yang ditemukan masih harus disaring lewat syntax gate dan oracle coverage.

Klaim yang aman:

```text
Script ini menghasilkan candidate-level static evidence untuk tahap awal reengineering.
```

Klaim yang tidak boleh dibuat:

```text
Script ini membuktikan bahwa kandidat pasti salah, pasti bau kode, atau pasti aman ditransformasi.
```

## 13. Ringkasan Teknis

Secara teknis, prosesnya adalah:

```text
scan file PHP
  -> buang folder vendor/test/cache/tmp
  -> deteksi function region dan file-level region
  -> hitung complexity proxy
  -> deteksi PHP/HTML, SQL, request, session, DOM, form
  -> klasifikasi candidate_type
  -> tentukan allowed_transformations
  -> tulis candidates.csv
  -> tulis evidence JSON
```

Dengan dokumentasi ini, proses kandidat tidak lagi menjadi kotak hitam. Semua aturan ekstraksi, threshold, field output, dan batasan metode ditulis eksplisit.
