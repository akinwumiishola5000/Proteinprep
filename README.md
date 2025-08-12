# Proteinprep
Protein preparation CLI + GUI for docking.
# ProteinPrep — Fast protein preparation for docking (CLI + GUI)

ProteinPrep is a small, user-friendly tool to fetch PDB structures, clean them (remove water/heteroatoms), optionally keep only selected chains, protonate (add hydrogens) using OpenBabel, and convert to PDBQT (for AutoDock Vina). It supports both a command-line interface (CLI) and a graphical user interface (GUI) via PySimpleGUI.

---

## Features

- Download PDB by ID (from RCSB) with retries
- Clean PDB: remove water molecules, remove heteroatoms (optionally keep specific ligands)
- Keep only specified chains (e.g., `--keep-chains A,C`)
- Auto-protonate using OpenBabel CLI (`--auto-protonate`)
- Convert to PDBQT using OpenBabel CLI (`--auto-pdbqt`)
- Batch mode via `--batch-file`
- Simple GUI wrapper for non-coders (`proteinprep_gui.py`)
- JSON log with full run report (`proteinprep_log.json`)

---

## Quick start — Overview

1. Download this repository (Upload to GitHub or clone).
2. Install dependencies (see installation below).
3. Run CLI:
   ```bash
   python3 proteinprep.py 1a4w --auto-protonate --auto-pdbqt --keep-chains A,C
   python3 proteinprep.py <protein ID> --auto-protonate --auto-pdbqt --keep-chains <Chain>
**4.** **Installation**
Choose one of these approaches.

**Recommended**: Conda (cross-platform, easiest for OpenBabel)
**Create & activate a conda environment**:
conda create -n proteinprep python=3.10 -y
conda activate proteinprep
**Install OpenBabel + Python packages:**
conda install -c conda-forge openbabel -y
pip install -r requirements.txt
**Simple pip (Linux / Windows)**
Create a virtualenv (optional but recommended) and activate it.
Install Python packages:
python -m pip install -r requirements.txt
**Install OpenBabel:**
  **Linux (Ubuntu/Debian):**
  sudo apt-get update
  sudo apt-get install -y openbabel
  **macOS (Homebrew)**
  brew install open-babel
  **Windows**
  Use conda: conda install -c conda-forge openbabel
  OR download the Windows installer from the OpenBabel website
**PySimpleGUI notes (Windows/Mac/Linux):** 
If PySimpleGUI instructs you to use its private PyPI, re-run:
python -m pip uninstall PySimpleGUI
python -m pip cache purge
python -m pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
But usually pip install -r requirements.txt works.
**If you get a message about PySimpleGUI moving to a private PyPI server, which means** 
The latest PySimpleGUI version is now hosted on a private PyPI repo, so you must install it from there.
Here’s what to do to fix this:
  **1.	Uninstall any existing PySimpleGUI:**
  python3 -m pip uninstall PySimpleGUI
  python3 -m pip cache purge
  **2.	Install PySimpleGUI from the private server**
  python3 -m pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
  **3. After that, try rerunning your script:** 
  python3 proteinprep_gui.py

**5. Usage 
CLI (Command Line Interface)**
  **1. Single PDB** (download, clean, protonate, convert), using the protein "8fv4" as an example:
    python3 proteinprep.py 8fv4 --auto-protonate --auto-pdbqt
  
  **2. Keep only chains A and B of protein "8fv4":** 
    python3 proteinprep.py 8fv4 --keep-chains A,B --auto-pdbqt
    **To keep more than two chains, use**
    python3 proteinprep.py 8fv4 --keep-chains A,B,C --auto-pdbqt
 
  **3. Use a local PDB file:**
    python3 proteinprep.py ./8fv4.pdb --auto-protonate
**Usage GUI (Graphical User Interface)**
  Run: python3 proteinprep_gui.py
  1. Enter a PDB ID or choose a local PDB file.
  2. (Optional) Choose a batch file.
  3. Toggle checkboxes for removing waters/heteroatoms, auto-protonate, auto-pdbqt.
  4. Optionally enter A or A,B for chains to keep.

Click Run and watch the log window.
