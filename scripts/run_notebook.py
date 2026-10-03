"""Execute the whole notebook with the Python environment running this script."""
import argparse
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Do not save notebook outputs (CSV/PNG exports still run).")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / "TK1_Nomor1.ipynb"
    nb = nbformat.read(path, as_version=4)
    nbformat.validate(nb)
    km = KernelManager(kernel_name="python3")
    km.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
    client = NotebookClient(nb, km=km, timeout=180, resources={"metadata": {"path": str(root)}})
    client.execute(cleanup_kc=True)
    nbformat.validate(nb)
    if not args.check:
        nbformat.write(nb, path)
    print(f"Notebook OK: {sum(c.cell_type == 'code' for c in nb.cells)} code cells executed.")
    print("Notebook outputs " + ("not saved." if args.check else "saved."))
    print(f"Experiment artifacts: {root / 'output' / 'no1'}")


if __name__ == "__main__":
    main()
