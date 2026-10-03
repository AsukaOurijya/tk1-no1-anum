"""Export a readable technical summary from the notebook's experiment CSVs.

Numerical solver implementations remain in TK1_Nomor1.ipynb.
"""
import csv
import json
from pathlib import Path


def write_analysis_report(output_dir, report_path):
    output_dir, report_path = Path(output_dir), Path(report_path)

    def read(name):
        with (output_dir / name).open(encoding="utf-8", newline="") as stream:
            return list(csv.DictReader(stream))

    performance = read("kinerja.csv")
    condition = read("kondisi.csv")
    accuracy = read("galat.csv")
    interpretation = read("interpretasi.csv")
    flux = read("verifikasi_arus.csv")
    metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
    by_method = {(int(row["N"]), row["method"]): row for row in performance}
    sizes = [int(row["N"]) for row in condition]
    perf_lines = []
    for n in sizes:
        dense, banded = by_method[n, "dense"], by_method[n, "banded"]
        perf_lines.append(
            f"| {n} | {float(dense['seconds'])*1000:.3f} | {float(banded['seconds'])*1000:.3f} | "
            f"{float(dense['peak_total_bytes'])/1024:.2f} | {float(banded['peak_total_bytes'])/1024:.2f} |"
        )
    accuracy_by_n = {int(row["N"]): row for row in accuracy if row["method"] == "banded"}
    accuracy_lines = []
    for row in condition:
        n = int(row["N"])
        a = accuracy_by_n[n]
        accuracy_lines.append(
            f"| {n} | {float(row['kappa_inf']):.6e} | {float(a['stationary_residual_inf']):.3e} | "
            f"{float(a['normalization_error']):.3e} | {float(a['backward_error']):.3e} | "
            f"{float(a['dense_banded_difference_inf']):.3e} |"
        )
    stop_lines = [
        f"| {row['N']} | {row['numerical_max_stop']} | {float(row['max_pi_percent']):.6f}% | "
        f"{float(row['min_pi']):.10f} | {float(row['max_to_uniform_ratio']):.6f} |"
        for row in interpretation
    ]
    flux_lines = [
        f"| {row['N']} | {float(row['difference_to_balanced_flux_reference_inf']):.3e} |"
        for row in flux
    ]
    dense, banded = by_method[512, "dense"], by_method[512, "banded"]
    speedup = float(dense["seconds"]) / float(banded["seconds"])
    memory_ratio = float(dense["peak_total_bytes"]) / float(banded["peak_total_bytes"])
    perturbation = metadata["perturbation_N256"]
    text = r"""# Analisis Perpindahan Penumpang Antarhalte

## Rangkuman

Pekerjaan awal pada i-v sudah benar secara numerik untuk data yang tersedia.
Penurunan matematis ii dan petunjuk eksekusi belum lengkap; keduanya diperbaiki.
Seluruh tugas i-ix kini ada di `TK1_Nomor1.ipynb`, dengan output yang telah
dieksekusi ulang. Solver banded dengan partial pivoting direkomendasikan untuk
koridor besar dengan bandwidth tetap. Kasus N=256 perlu perhatian terhadap
sensitivitas data, karena κ∞(B) mencapai sekitar 1,07×10⁹.

## 1. Ruang lingkup dan audit repo

Sumber tugas adalah `TK_1_Anum_Gasal_26_27.pdf`, No. 1, halaman 3-5;
No. 2 tidak dianalisis. `Petunjuk_Penulisan_Dokumen_Project_Anum.pdf`
menjadi acuan struktur laporan teknis. Dokumen ini adalah isi teknis No. 1;
identitas kelompok, tanda tangan, dan format PDF pengumpulan diisi terpisah
oleh anggota kelompok.

| Butir | Hasil pemeriksaan pekerjaan awal | Penyelesaian sekarang |
| --- | --- | --- |
| i | Dimensi, nonnegativitas, stochastic, SCC, dan kelas tertutup benar | Seluruh ukuran diuji ulang |
| ii | A, B, b dan normalisasi benar; penurunan belum ditulis | Derivasi dan syarat B nonsingular dilengkapi |
| iii | Bandwidth p=1, q=2 dan rumus slot benar | Dibedakan dari tridiagonal dan ruang fill-in |
| iv | Dense PB=LU dan compact pivoting/fill benar pada controlled test | Ditambah 120 uji acak dengan solusi acuan |
| v | Benchmark memisahkan waktu, tracing, dan persiapan input dengan benar | Dieksekusi ulang; tabel/grafik diekspor |
| vi | Placeholder | Kompleksitas operasi/memori dan hubungannya dengan waktu diisi |
| vii | Belum tersedia | κ∞, residual, normalisasi, backward error, dan sensitivitas dihitung |
| viii | Belum tersedia | Plot enam ukuran dan halte maksimum dijelaskan |
| ix | Belum tersedia | Rekomendasi berdasarkan bukti waktu/memori/galat diisi |

README awal memakai nama `soal1.ipynb` yang tidak ada serta jalur interpreter
Unix pada lingkungan Windows. README dan pengaturan interpreter VS Code
sekarang menggunakan nama/jalur yang benar. Dua file solver di `src/` masih
placeholder kosong dari repo awal; algoritma yang dijalankan berada di notebook.
`src/utils.py` hanya menghasilkan ringkasan ini dari hasil CSV.

PDF menyebut kode A untuk kelompok ganjil dan B untuk kelompok genap.
CSV repo tidak mencantumkan kode; analisis ini berlaku untuk data yang ada,
dan asal kode kelompok perlu dicocokkan dengan SCeLE.

## 2. Validasi data — i)

Untuk N ∈ {16,32,64,128,256,512}, semua T berdimensi N×N, berhingga,
dan tidak memiliki entri negatif. Galat jumlah baris maksimum ≤2,22×10⁻¹⁶,
jauh di bawah toleransi 10⁻¹⁰. Data asli tidak dinormalisasi ulang atau dipotong.

Graf memiliki sisi i→j untuk setiap Tᵢⱼ>0, tanpa threshold yang menghapus
peluang kecil. Algoritma SCC Kosaraju menemukan satu SCC pada setiap ukuran:
rantai irreducible, dengan satu kelas tertutup dan distribusi stasioner tunggal.
Self-loop positif membuktikan aperiodisitas, sehingga distribusi dari setiap
kondisi awal menuju distribusi stasioner. Aperiodisitas adalah syarat konvergensi,
bukan syarat ketunggalan. Untuk rantai berhingga, ketunggalan setara dengan satu
kelas komunikasi tertutup; irreducible merupakan syarat cukup.

## 3. Formulasi dan penanganan singularitas — ii)

Dengan π sebagai vektor kolom, hukum probabilitas total memberikan

$$\pi_j^{(k+1)}=\sum_i T_{ij}\pi_i^{(k)},\qquad
\pi^{(k+1)}=T^T\pi^{(k)}.$$

Pada steady state, Tᵀπ=π dan Aπ=0, dengan A=I−Tᵀ. Karena T1=1,
1ᵀA=0; A mempunyai nullspace kiri bukan nol sehingga singular.
Jumlah semua baris A nol, jadi baris pertama sama dengan negatif jumlah
baris lainnya. Baris pertama dapat diganti tanpa kehilangan arah stasioner.

Untuk dataset irreducible, rank(A)=N−1 dan nullspace(A)=span{π}, dengan
π₁>0. Ganti baris pertama menjadi e₁ᵀ dan b=e₁. Jika Bx=0, maka Ax=0
dan x₁=0, sehingga x=cπ dan c=0. B nonsingular. Solusi Bz=b menetapkan
z₁=1, yakni z=π/π₁; jumlah z umumnya bukan satu, jadi perlu normalisasi
π=z/(1ᵀz). Contoh dua halte T=[[0,75;0,25],[0,5;0,5]] menghasilkan
z=(1;1/2) dan π=(2/3;1/3).

Ketunggalan pada rantai reducible saja belum cukup untuk penetapan ini bila
halte 1 transient dan π₁=0. Seluruh dataset di sini memenuhi syarat irreducible.
Identitas stochastic data float64 berlaku hingga pembulatan, sehingga residual
stasioner tetap diperiksa setelah normalisasi.

## 4. Struktur dan penyimpanan — iii)

Deteksi semua entri bukan nol memberikan p=1, q=2 untuk seluruh B.
Transposisi menukar bandwidth T, sedangkan mengganti baris pertama hanya
menghapus entri lama dan mempertahankan diagonal; tidak memperlebar band.
Matriks ini bukan tridiagonal klasik yang mempunyai p=q=1.

Dense menyimpan N² slot. Slot di dalam band berjumlah
N(p+q+1)−p(p+1)/2−q(q+1)/2=4N−4; format padded memakai 4N.
Slot geometris mencakup nol di dalam band. Pada N=512 dan float64, koefisien
dense membutuhkan 2.097.152 byte, band tanpa padding 16.352 byte.
Solver menyimpan 5N slot karena menambah diagonal fill-in, terpisah dari rhs,
solusi, input, dan salinan kerja.

## 5. Algoritma dan verifikasi — iv)

**Kode 5.1. Langkah dense LU dengan partial pivoting.**

```text
U = salinan B; L = I; P = I
untuk setiap kolom k:
    pilih |U[r,k]| maksimum pada baris k..N
    tukar baris U, P, serta kolom L yang sudah terisi
    eliminasi semua baris di bawah pivot; simpan multiplier di L
selesaikan Ly = Pb, kemudian Uz = y
normalisasi z untuk mendapatkan pi
```

Penukaran koefisien L yang sudah terisi diperlukan agar PB=LU tetap benar.
Pivot dengan nilai absolut ≤10⁻¹⁰ ditolak; ini ambang absolut konfigurabel,
bukan estimasi condition number.

**Kode 5.2. Langkah solver compact Thomas-style.**

```text
simpan lower1, diagonal, upper1, upper2, upper3_fill=0, dan rhs
untuk setiap kolom k:
    bandingkan pivot diagonal dengan lower1 pada baris k+1
    bila perlu tukar kedua baris sekaligus rhs
    pertahankan fill diagonal atas ketiga
    eliminasi hanya baris k+1 menggunakan seluruh upper yang aktif
substitusi mundur dengan tiga upper, kemudian normalisasi
```

Karena p=1, semua baris di bawah k+1 mempunyai nol pada kolom pivot;
pivot lokal tersebut setara dengan partial pivoting penuh. Pertukaran dapat
memperlebar U dari q=2 menjadi p+q=3. Solver menyalin vektor saja, tidak
memiliki matriks kerja dense ataupun matriks permutasi eksplisit.

Controlled test menguji dua swap pada dense, swap dan upper fill bukan nol
pada compact, batas N=1/2, input tidak valid, dan input yang tidak berubah.
Untuk N=16, galat faktorisasi infinity sekitar 1,39×10⁻¹⁷ dan residual
SPL sekitar 2,78×10⁻¹⁷. Kedua solver diuji pada 120 matriks band acak
dengan seed 20261003 dan b=Bz★; galat maksimum terhadap z★ adalah
**{random_error}**, dengan **{swaps}** swap compact. Semua pengujian lolos.

## 6. Eksperimen kinerja — v)

Tabel 6.1 mencatat median tiga pengulangan sesudah satu pemanasan.
Waktu mencakup solver, validasi input, salinan kerja, dan normalisasi;
pembacaan CSV, pembuatan sistem, ekstraksi band, dan diagnostik tidak dihitung.
Memori diukur terpisah: input koefisien/rhs + peak alokasi tambahan tracemalloc.
Ukuran ini bukan RSS atau memori seluruh notebook. Angka berikut merupakan
eksekusi lokal, dapat berubah pada run berikutnya.

**Tabel 6.1. Waktu solver dan memori terukur.**

| N | Dense ms | Banded ms | Dense KiB | Banded KiB |
| --- | ---: | ---: | ---: | ---: |
{performance_table}

![Grafik kinerja](output/no1/kinerja.png)

**Gambar 6.1.** Waktu dan memori solver pada enam ukuran, menggunakan sumbu
logaritmik. Banded lebih cepat dan lebih hemat memori pada seluruh ukuran.

## 7. Kompleksitas — vi)

Dense memperbarui N−k−1 baris sepanjang N−k pada langkah k. Sekitar
2∑(N−k−1)(N−k)=2(N³−N)/3 operasi perkalian/pengurangan, ditambah
pembagian O(N²). Faktorisasi Θ(N³); pencarian pivot, substitusi dan Pb
eksplisit O(N²). B, P, L, U mempunyai memori Θ(N²).

Untuk banded umum, pivot memeriksa p+1 kandidat dan memperlebar upper band
sampai p+q. Eliminasi memakai O(N[1+p+p(p+q+1)]) operasi, lazim diringkas
O(Np(p+q)) untuk p≥1. Substitusi O(N(p+q+1)); memori faktor/band/rhs/pivot
O(N(2p+q+1)). Implementasi khusus p=1,q=2 mempunyai waktu/memori Θ(N).

Penggandaan N memberi FLOPs dense mendekati 8× dan memori 4×; banded
dengan lebar tetap mendekati 2×. Waktu Python pada rentang uji tidak harus
8×: loop baris dense berjumlah Θ(N²), dan operasi vektor menggunakan
NumPy. Overhead, cache, serta timer menjelaskan waktu yang mendekati 4×
tanpa mengubah kompleksitas teoretis.

Notebook masih memuat T,A,B dense dan membaca CSV dense; tahap ini memakai
waktu/memori O(N²). Keuntungan linear berlaku pada solver compact, bukan
keseluruhan pipeline yang sekarang. Penghitungan κ∞ melalui N solve compact
memakai O(N²) waktu dan O(N) ruang tambahan, di luar benchmark bagian 6.

## 8. Kondisi dan galat — vii)

Norma konsisten: ||v||∞=max|vᵢ| dan ||M||∞=maxᵢ∑ⱼ|Mᵢⱼ|.
κ∞(B)=||B||∞||B⁻¹||∞ dihitung tanpa inverse/faktorisasi pustaka:
selesaikan Bx⁽ʲ⁾=eⱼ, akumulasikan ∑ⱼ|xᵢ⁽ʲ⁾|, lalu ambil maksimum baris.
Ini norma inverse lengkap yang dihitung dalam float64. Inverse dense tidak
disimpan. Contoh analitik dua halte menghasilkan κ∞=2,5; matriks identitas 1.

Ukur r∞=||Tᵀπ−π||∞, e_norm=|∑π−1|, δπ=||π_dense−π_banded||∞,
dan η=||Bz−b||∞/(||B||∞||z||∞+||b||∞). Tabel 8.1 sama untuk kedua
solver pada run ini; rincian masing-masing solver dan residual sebelum
normalisasi tersedia di `output/no1/galat.csv`.

**Tabel 8.1. Kondisi B dan akurasi distribusi.**

| N | κ∞(B) | r∞ | e_norm | η | δπ |
| --- | ---: | ---: | ---: | ---: | ---: |
{accuracy_table}

![Grafik kondisi dan galat](output/no1/kondisi_galat.png)

**Gambar 8.1.** Kondisi melonjak pada N=256 meskipun residual stasioner kecil.
Transisi lintas potongan 128|129 adalah 128→129 ≈1,18948×10⁻⁷,
129→127=2×10⁻⁸, 129→128=8×10⁻⁸, dan 130→128=2×10⁻⁸.
Dua bagian koridor nyaris menjadi kelas tertutup, menyebabkan sensitivitas tinggi.
κ∞ tidak ditentukan hanya oleh ukuran N.

Residual kecil menunjukkan persamaan dipenuhi dengan baik, tetapi tidak
menjamin galat maju kecil. Untuk z, batas residual-only dalam aritmetika
eksak ialah ||z_hat−z||∞/||z||∞ ≤ κ∞||Bz_hat−b||∞/||b||∞;
batas dapat longgar dan bukan batas langsung untuk π setelah normalisasi.
Kesamaan dua solver bukan bukti independen karena keduanya menjalankan
operasi efektif yang sama pada band dan dapat berbagi galat pembulatan.
Residual absolut menurun juga karena komponen π mengecil sekitar 1/N;
ini tidak otomatis berarti akurasi relatif membaik. CSV galat turut memuat
r∞/||π||∞ untuk perbandingan skala distribusi.

Sebagai pemeriksaan independen, keseimbangan arus lintas batas i|i+1 memberikan

$$\pi_iT_{i,i+1}=\pi_{i+1}(T_{i+1,i}+T_{i+1,i-1})
+\pi_{i+2}T_{i+2,i}.$$

Dengan bobot halte terakhir satu dan suku di luar rentang nol, bobot dihitung
mundur memakai Decimal 60 digit, lalu dinormalisasi. Acuan ini menggunakan
off-diagonal float64 asli dan diagonal implisit 1−jumlah off-diagonal.
Karena jumlah baris CSV hanya tepat hingga pembulatan, matriks acuan berbeda
sekitar 10⁻¹⁶ pada diagonal dari data asli. Data asli tidak diubah. Selisih
acuan bukan galat maju tersertifikasi terhadap B asli.

**Tabel 8.2. Selisih infinity distribusi banded dan acuan arus 60 digit.**

| N | Selisih terhadap acuan arus |
| --- | ---: |
{flux_table}

Selisih yang lebih besar pada N=256 konsisten dengan sensitivitas terhadap
pembulatan data. Demonstrasi perubahan relatif 10⁻⁶ pada peluang 128→129,
dikompensasi di diagonal agar jumlah baris tetap, menghasilkan perubahan
relatif B **{perturb_B}** dan perubahan relatif π **{perturb_pi}**.
Condition number memberi batas kasus terburuk, bukan amplifikasi yang selalu
dicapai. Partial pivoting menekan multiplier |m|≤1 dan menghindari pivot nol,
tetapi tidak menghilangkan conditioning input. Residual absolut kolom inverse
dapat besar karena nilai inverse besar; backward error kolom terskala tetap kecil.

## 9. Interpretasi halte — viii)

**Tabel 9.1. Halte dengan proporsi maksimum (nomor halte dimulai dari 1).**

| N | Halte maksimum | Proporsi maksimum | Proporsi minimum | Maksimum / (1/N) |
| --- | ---: | ---: | ---: | ---: |
{stop_table}

![Distribusi stasioner](output/no1/distribusi_stasioner.png)

**Gambar 9.1.** Distribusi kedua solver berimpit pada seluruh ukuran.
Distribusi mempunyai dua daerah puncak dan daerah proporsi rendah di bagian
kanan koridor. Maksimum sekitar 1,24-1,25 kali rata-rata 1/N, minimum sekitar
setengah rata-rata. Pemeriksaan nilai dalam jarak relatif 10⁻¹⁰ dari maksimum
menghasilkan satu halte maksimum pada setiap dataset; puncak lain yang terlihat
hampir sama pada grafik tidak persis sama secara numerik.

Prioritas armada/petugas dapat memakai πᵢ sebagai indikator beban relatif.
Untuk total penumpang M, perkiraan steady state adalah Mπᵢ. Kapasitas halte
dan jumlah penumpang aktual diperlukan untuk menyimpulkan risiko penuh absolut.
Bottleneck N=256 juga mengindikasikan perpindahan massa antarkedua bagian
berpotensi lambat; waktu konvergensi belum diukur di sini.

## 10. Rekomendasi — ix)

Gunakan **solver banded dengan partial pivoting** untuk koridor besar dengan
struktur p=1,q=2. Waktu dan memori solver linear, dibanding dense kubik dan
kuadratik, dengan residual/normalisasi sebanding pada data ini. Pada N=512,
banded terukur **{speedup:.2f}× lebih cepat**, dengan rasio memori dense/banded
**{memory_ratio:.2f}×**. Angka ini adalah benchmark lokal sesuai definisi di bagian 6.
Dense LU tetap berguna sebagai pembanding ukuran kecil dan untuk band yang lebar
atau di luar kapasitas solver compact sekarang.

Pertahankan diagonal atas kedua dan upper fill ketiga; jangan menghapus peluang
kecil atau memakai Thomas klasik langsung. Untuk bandwidth lain, diperlukan
solver banded umum dengan ruang fill p+q atau fallback dense buatan sendiri.
Untuk mendapat memori linear pada pipeline lengkap, input dan validasi graf harus
menggunakan format band langsung, tanpa membentuk T,A,B dense.

Periksa nonnegativitas, normalisasi, residual, dan backward error setiap solve.
Pada data sensitif, verifikasi akurasi peluang serta uji perturbasi; gunakan
presisi lebih tinggi atau iterative refinement bila target akurasi memerlukannya.
Refinement tidak mengatasi ketidakpastian data. Diagnostik inverse lengkap O(N²)
sebaiknya tidak dilakukan pada setiap solve produksi berskala besar; estimator
norma inverse dan faktor yang dipakai ulang merupakan pengembangan berikutnya.

## 11. Reproduksi dan keluaran

Jalankan dari direktori repo:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.txt
.venv/Scripts/python.exe scripts/run_notebook.py
```

Skrip menggunakan interpreter aktif, menjalankan semua sel dan assert, lalu
menyimpan output notebook. `--check` mempertahankan berkas notebook, tetapi
tetap memperbarui CSV, PNG, dan ringkasan ini. Alternatif: pilih kernel `.venv`
di VS Code lalu Run All. README berisi petunjuk lengkap.

CSV di `output/no1/`: kinerja, kompleksitas, kondisi, galat, interpretasi,
verifikasi_arus, dan distribusi per halte. `metadata.json` mencatat versi
Python/NumPy/Matplotlib, platform, toleransi, protokol, seed, dan hash data.
Lingkungan yang diuji: Python {python_version}, NumPy {numpy_version},
Matplotlib {matplotlib_version}. Tidak ada solver atau faktorisasi pustaka utama.

## Referensi

1. Tim Dosen dan Asisten Dosen Analisis Numerik, *TK 1: Sistem Persamaan Linear
   dan Least Square Problem*, Semester Gasal 2026/2027, soal No. 1, halaman 3-5.
2. *Petunjuk Penulisan Dokumen Project Anum*, dokumen yang disertakan dalam repo.
3. Seluruh hasil numerik/tabel/grafik di atas dihitung dari keenam CSV repo oleh
   notebook; metode pengukuran dan implementasi tersedia untuk diperiksa ulang.
"""
    # Replace only named tokens; retain literal mathematical braces.
    values = {
        "random_error": f"{metadata['random_test_max_error']:.3e}",
        "swaps": metadata["random_test_pivot_swaps"],
        "performance_table": "\n".join(perf_lines),
        "accuracy_table": "\n".join(accuracy_lines),
        "flux_table": "\n".join(flux_lines),
        "stop_table": "\n".join(stop_lines),
        "perturb_B": f"{perturbation['relative_B_change']:.3e}",
        "perturb_pi": f"{perturbation['relative_pi_change']:.3e}",
        "speedup:.2f": f"{speedup:.2f}",
        "memory_ratio:.2f": f"{memory_ratio:.2f}",
        "python_version": metadata["python"].split()[0],
        "numpy_version": metadata["numpy"],
        "matplotlib_version": metadata["matplotlib"],
    }
    for key, value in values.items():
        text = text.replace("{" + key + "}", str(value))
    report_path.write_text(text, encoding="utf-8")
