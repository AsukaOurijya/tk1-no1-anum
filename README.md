# Environment notebook

Jalankan dari direktori proyek ini (memerlukan `uv`):

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m ipykernel install --user --name tk01 --display-name "Python (tk01)"
```

Di VS Code, buka `soal1.ipynb`, klik **Select Kernel**, lalu pilih
**Python (tk01)** atau interpreter `.venv/bin/python`. Jalankan **Run All**.
Sel pertama memeriksa import, membaca data, dan menampilkan grafik.

Untuk memeriksa notebook dari terminal tanpa mengubah hasil yang tersimpan:

```bash
.venv/bin/python -c 'import nbformat; from nbclient import NotebookClient; nb = nbformat.read("soal1.ipynb", as_version=4); nbformat.validate(nb); NotebookClient(nb, timeout=60, kernel_name="tk01").execute(); print("Notebook OK")'
```

NumPy digunakan untuk data dan Matplotlib untuk grafik; algoritma solver
tugas tetap perlu diimplementasikan sendiri sesuai petunjuk tugas.
