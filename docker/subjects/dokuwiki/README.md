# Pemulihan Runtime DokuWiki

Folder ini berisi konfigurasi Docker untuk menjalankan DokuWiki pada runtime yang sesuai dengan versi subject penelitian.

## Metadata Subject

| Item | Nilai |
|---|---|
| Repository | `https://github.com/dokuwiki/dokuwiki.git` |
| Tag Rio | `release-2018-04-22b` |
| Commit | `4e34491f07933bfb7e59e6cab0c029799dd381ab` |
| Kebutuhan PHP | `>=5.6` |
| Database | tidak diperlukan |

## Menjalankan Container

Jalankan dari root repo:

```powershell
docker compose -f docker/subjects/dokuwiki/docker-compose.yml up --build -d
```

URL runtime:

```text
http://localhost:8102/doku.php
```

## Smoke Check

Gunakan command ini untuk memastikan halaman utama bisa diakses:

```powershell
Invoke-WebRequest http://localhost:8102/doku.php -UseBasicParsing
```

Jika berhasil, DokuWiki sudah hidup di container.

## Test Bawaan

Audit menemukan command PHPUnit berikut:

```powershell
docker compose -f docker/subjects/dokuwiki/docker-compose.yml exec dokuwiki php _test/phpunit.phar -c _test/phpunit.xml --exclude-group slow,internet
```

Catatan:

```text
PHPUnit PHAR tidak ikut disediakan dalam skeleton runtime ini.
```

Jika test bawaan ingin dipakai sebagai oracle tambahan, tambahkan PHPUnit PHAR yang kompatibel dengan PHP 5.6 ke folder `_test/`, lalu simpan log test sebagai artifact eksperimen.

Untuk eksperimen pilot saat ini, oracle utama berasal dari characterization/oracle mapping yang tersimpan di:

```text
results/subjects/dokuwiki/characterization/
results/subjects/dokuwiki/oracle/
```
