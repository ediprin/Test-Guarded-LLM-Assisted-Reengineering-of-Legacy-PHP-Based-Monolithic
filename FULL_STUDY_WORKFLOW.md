# Full Study Workflow

Dokumen ini menjelaskan perbedaan antara eksperimen pilot saat ini dan versi penuh dari studi test-guarded LLM-assisted reengineering.

Istilah yang digunakan:

- **tambalan** = perubahan kode yang dibuat AI
- **pos pemeriksaan** = tahap pengecekan sebelum perubahan diterima
- **kandidat** = bagian kode yang mau dirapikan
- **patokan uji** = halaman/rute yang dipakai untuk mengecek perilaku aplikasi

Kalau dibuat versi penuh, alur kerja tidak berhenti di "kode berhasil ditambal dan tidak error sintaks". Versi penuh harus sampai membuktikan bahwa aplikasi tetap berjalan benar setelah kode dirapikan.

Versi paper saat ini masih pilot, karena pos pemeriksaan yang selesai baru:

- pembuatan tambalan
- pemasangan tambalan
- cek sintaks PHP
- perbandingan sederhana jumlah baris dan kompleksitas

Pos pemeriksaan yang belum selesai penuh:

- regresi rute
- perbandingan tampilan
- pemeriksaan batasan perilaku
- cakupan pengujian

## Alur Penuh Ideal

```text
Aplikasi PHP lama
        |
        v
Pulihkan aplikasi di lingkungan lama
        |
        v
Catat perilaku awal aplikasi
        |
        v
Cari bagian kode yang perlu dirapikan
        |
        v
Buat bukti analisis untuk tiap bagian kode
        |
        v
Pilih hanya kandidat yang bisa diuji
        |
        v
Buat instruksi ke AI
        |
        v
AI membuat tambalan kode
        |
        v
Pasang tambalan di salinan aplikasi
        |
        v
Cek sintaks PHP
        |
        v
Cek aturan yang tidak boleh berubah
        |
        v
Jalankan halaman/rute yang terkait
        |
        v
Bandingkan tampilan sebelum dan sesudah
        |
        v
Jalankan pengujian tambahan
        |
        v
Ukur kualitas kode
        |
        v
Tentukan diterima / ditolak / perlu diperiksa manual
```

## Tahap Demi Tahap

| Tahap | Maksud sederhana | Hasil yang diharapkan |
|---|---|---|
| 1. Pilih aplikasi lama | Tentukan aplikasi PHP lama yang mau diteliti, misalnya DokuWiki dan Kanboard | Daftar aplikasi uji |
| 2. Pulihkan aplikasi | Jalankan aplikasi di versi PHP yang sesuai, misalnya PHP 5.6 atau PHP 7.2 | Aplikasi bisa hidup di container |
| 3. Catat kondisi awal | Simpan perilaku awal aplikasi sebelum diubah | Halaman login, home, dashboard, feed, CSS, JavaScript, dan lain-lain berjalan normal |
| 4. Cari kandidat | Temukan bagian kode yang panjang, rumit, campur PHP/HTML, akses database, form, atau session | Daftar kandidat kode |
| 5. Buat bukti analisis | Untuk setiap kandidat, catat file, baris kode, jenis masalah, session, database, form, URL, dan batasan penting | Berkas bukti per kandidat |
| 6. Pilih kandidat yang bisa diuji | Kandidat hanya boleh lanjut kalau perilakunya bisa dicek lewat halaman/rute tertentu | Kandidat layak diuji |
| 7. Buat instruksi AI | Buat instruksi ke AI agar merapikan kode tanpa mengubah URL, parameter, session, database, atau tampilan penting | Instruksi siap dikirim |
| 8. AI membuat tambalan | AI menghasilkan perubahan kode | Tambalan kode |
| 9. Pasang tambalan | Tambalan dipasang ke salinan aplikasi, bukan langsung ke aplikasi asli | Tambalan berhasil/gagal dipasang |
| 10. Cek sintaks | Pastikan kode PHP tidak rusak secara penulisan | Tidak ada error PHP |
| 11. Cek batasan | Pastikan URL, parameter, session key, nama tabel, field form, dan elemen tampilan penting tidak berubah | Batasan tetap aman |
| 12. Jalankan rute terkait | Jalankan halaman yang berhubungan dengan kandidat kode | Halaman tetap bisa dibuka |
| 13. Bandingkan tampilan | Bandingkan hasil HTML sebelum dan sesudah perubahan | Tampilan tidak berubah secara berbahaya |
| 14. Jalankan pengujian tambahan | Jalankan test, skenario klik, login, submit form, atau pengecekan API | Perilaku aplikasi tetap sama |
| 15. Ukur kualitas kode | Lihat apakah kode lebih sederhana, tidak makin panjang, tidak makin kompleks | Kualitas membaik atau minimal tidak memburuk |
| 16. Putuskan hasil | Tentukan tambalan diterima, ditolak, atau perlu dicek manual | Keputusan akhir |

## Pilot Saat Ini vs Versi Penuh

Versi pilot sekarang:

```text
Kandidat
  -> bukti analisis
  -> instruksi AI
  -> tambalan
  -> pasang
  -> cek sintaks
  -> ukur sederhana
```

Versi penuh:

```text
Kandidat
  -> bukti analisis
  -> instruksi AI
  -> tambalan
  -> pasang
  -> cek sintaks
  -> cek batasan
  -> jalankan halaman/rute
  -> bandingkan tampilan
  -> jalankan pengujian perilaku
  -> ukur kualitas kode
  -> keputusan akhir
```

## Contoh Kandidat Login

Misalnya ada kandidat kode di halaman login. AI membuat tambalan untuk merapikan kode login.

Pada versi pilot, pemeriksaan baru menjawab:

1. Apakah tambalan bisa dipasang?
2. Apakah PHP masih valid?
3. Apakah jumlah baris atau kompleksitas tidak makin buruk?

Pada versi penuh, pemeriksaan harus dilanjutkan:

1. Apakah halaman login masih terbuka?
2. Apakah form login masih punya nama field yang sama?
3. Apakah session login tetap dibuat dengan nama yang sama?
4. Apakah login berhasil dengan akun benar?
5. Apakah login gagal dengan akun salah?
6. Apakah tampilan HTML tidak berubah secara berbahaya?
7. Apakah tidak ada error di log?
8. Apakah kode memang lebih mudah dipelihara?

Baru setelah itu tambalan bisa dikatakan diterima:

```text
Perubahan kode ini diterima karena tidak hanya lolos sintaks, tetapi juga perilaku aplikasinya tetap aman.
```

## Empat Lapis Keamanan

| Lapis | Pertanyaan utama |
|---|---|
| Lapis 1: kode | Apakah tambalan bisa dipasang dan PHP tidak error? |
| Lapis 2: batasan | Apakah URL, session, request, database, form, dan tampilan penting tidak berubah? |
| Lapis 3: perilaku | Apakah halaman dan fitur masih berjalan sama seperti sebelum diubah? |
| Lapis 4: kualitas | Apakah kode benar-benar lebih rapi, lebih kecil, atau lebih mudah dipelihara? |

## Kesimpulan

Versi pilot menjawab:

```text
Apakah alur ini bisa berjalan dan apakah AI dengan bukti analisis menghasilkan tambalan yang lebih stabil?
```

Versi penuh menjawab:

```text
Apakah tambalan dari AI benar-benar aman diterima karena aplikasi tetap berperilaku sama dan kualitas kode membaik?
```

Jadi, kalau paper dilanjutkan dari pilot ke full study, bagian yang perlu ditambah terutama adalah uji perilaku aplikasi setelah tambalan dipasang, bukan hanya cek sintaks kode.
