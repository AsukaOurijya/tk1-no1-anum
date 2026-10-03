# TK 1 Analisis Numerik — Nomor 1

Analisis perpindahan penumpang antarhalte untuk tugas **i–ix**, berdasarkan
`TK_1_Anum_Gasal_26_27.pdf` halaman 3–5. Soal No. 2 tidak dikerjakan di repo ini.

## Isi repo

- `TK1_Nomor1.ipynb`: formulasi, implementasi solver, pengujian, eksperimen,
  analisis kondisi/galat, interpretasi halte, dan rekomendasi. Output sudah dijalankan.
- `ANALISIS_NO1.md`: ringkasan teknis lengkap dan hasil audit pekerjaan awal;
  diperbarui otomatis oleh sel ekspor terakhir.
- `data/T_<N>.csv`: enam matriks transisi asli, untuk N = 16, 32, 64, 128, 256, 512.
- `output/no1/`: tabel CSV, distribusi per halte, grafik PNG, dan metadata eksperimen.
- `scripts/run_notebook.py`: menjalankan semua sel dengan interpreter yang dipakai
  memanggil skrip, tanpa perlu registrasi kernel global.
- `src/utils.py`: penulisan ringkasan teknis dari hasil eksperimen.
  `src/dense_lu.py` dan `src/banded_solver.py` masih placeholder kosong dari repo awal;
  **implementasi solver yang dipakai berada di notebook**, bukan kedua file tersebut.

## Instalasi — Windows PowerShell

Jalankan dari direktori repo. Gunakan Python 3.12 dan `uv`:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
```

Jika `uv` tidak tersedia, gunakan Python 3.12 yang sudah terpasang:

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Menjalankan seluruh analisis

```powershell
.venv/Scripts/python.exe scripts/run_notebook.py
```

Skrip memvalidasi format notebook, mengeksekusi seluruh sel dari awal,
menyimpan output ke notebook, serta memperbarui `output/no1/` dan `ANALISIS_NO1.md`.
Keberhasilan ditandai `Notebook OK`; kegagalan assert atau sel membuat proses gagal.
Data CSV asli tidak diubah.

Untuk memverifikasi tanpa menyimpan ulang output notebook:

```powershell
.venv/Scripts/python.exe scripts/run_notebook.py --check
```

Opsi `--check` tetap menjalankan sel ekspor, sehingga tabel, grafik, dan ringkasan
teknis diperbarui; hanya berkas `.ipynb` yang tidak ditulis ulang.

Di VS Code, buka **`TK1_Nomor1.ipynb`**, pilih interpreter
`.venv/Scripts/python.exe` melalui **Select Kernel**, lalu **Run All**.
Jika ingin kernel bernama, registrasi ini opsional:

```powershell
.venv/Scripts/python.exe -m ipykernel install --user --name tk01 --display-name "Python (tk01)"
```

Linux/macOS: gunakan `.venv/bin/python` menggantikan `.venv/Scripts/python.exe`.
Jangan menjalankan sel eksperimen sebelum sel definisi solver dan pembacaan data.

## Metode dan hasil utama

Kedua algoritma penyelesaian SPL diimplementasikan sendiri: dense LU dengan
partial pivoting dan eliminasi banded Thomas-style dengan partial pivoting.
Tidak digunakan `np.linalg.solve`, `inv`, `cond`, SVD, atau faktorisasi pustaka.
Condition number infinity dihitung melalui solusi untuk seluruh ruas kanan basis
menggunakan solver buatan sendiri; inverse dense tidak dibentuk.

Semua data irreducible, mempunyai self-loop, dan lolos validasi stochastic hingga
pembulatan float64. Matriks B memiliki **p=1, q=2**, sehingga solver compact menyimpan
diagonal atas kedua dan diagonal atas ketiga untuk fill-in. Thomas tridiagonal
klasik tidak cukup. Kapasitas solver ini khusus p≤1, q≤2; bandwidth lain ditolak.

Audit menjalankan controlled test, 120 matriks band acak dengan solusi yang
ditentukan terlebih dahulu, dan acuan stasioner independen berbasis keseimbangan
arus dengan aritmetika Decimal 60 digit. Norma galat dan condition number konsisten
memakai norma infinity. Kasus **N=256** memiliki bottleneck lintas halte 128–129
dan κ∞(B) ≈ 1,07×10⁹; residual kecil tetap harus dibaca bersama conditioning.

Rekomendasi akhir adalah solver banded untuk koridor besar dengan bandwidth tetap:
waktu/memori solver O(N), dibanding dense O(N³)/O(N²). Notebook masih membaca
CSV dan membentuk matriks dense untuk validasi/perbandingan, jadi seluruh pipeline
belum memiliki penggunaan memori linear.

## Protokol eksperimen

- Waktu: sekali pemanasan, median 3 pengulangan solver + normalisasi, tanpa tracing.
  Validasi input dan salinan kerja solver ikut dihitung; baca CSV, konstruksi sistem,
  ekstraksi band, penghitungan kondisi, dan pengujian hasil tidak ikut dihitung.
- Memori: byte koefisien/rhs input + peak alokasi tambahan `tracemalloc` pada
  pemanggilan terpisah; bukan RSS proses atau seluruh notebook.
- `output/no1/metadata.json` mencatat versi runtime/pustaka, hash data, toleransi,
  seed uji, dan rincian metode pengukuran. Waktu lokal dapat berubah pada run lain.
- Persyaratan utama dipin pada versi yang berhasil diuji. Tidak ada SciPy atau
  pustaka solver tambahan.

PDF soal menyebut kode data A/B berdasarkan nomor kelompok. CSV repo tidak
mencantumkan kode tersebut; cocokkan sumber data dengan kelompok di SCeLE.
Notebook/ringkasan ini merupakan bahan teknis No. 1. PDF pengumpulan akhir mengikuti
`Petunjuk_Penulisan_Dokumen_Project_Anum.pdf`, dengan identitas dan pernyataan
integritas yang diisi anggota kelompok.
