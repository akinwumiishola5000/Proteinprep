# ProteinPrep — Fast protein preparation for docking (CLI + GUI)

ProteinPrep is a small, user-friendly tool to fetch PDB structures, clean them (remove water/heteroatoms), optionally keep only selected chains, protonate (add hydrogens) using OpenBabel, and convert to PDBQT for AutoDock Vina. It supports both a command-line interface (CLI) and a graphical user interface (GUI). 🧪



---

## Features

-   **Download PDB** by ID from the RCSB database with built-in retries.
-   **Clean PDB**: Remove water molecules and heteroatoms.
-   **Select Chains**: Keep only specified chains (e.g., `--keep-chains A,C`).
-   **Keep Ligands**: Optionally preserve specific heteroatoms/ligands.
-   **Protonate**: Add hydrogens using OpenBabel (`--auto-protonate`).
-   **Convert**: Generate PDBQT files for docking (`--auto-pdbqt`).
-   **Batch Mode**: Process multiple PDB IDs from a file (`--batch-file`).
-   **Simple GUI**: An intuitive graphical interface for all features.
-   **Logging**: Generates a `proteinprep_log.json` file with a full report of the operations performed.

---

## Installation
Make sure to copy/download proteinprep.py and proteinprep_gui.py in your working directory

You can install the necessary dependencies using either Conda (recommended for simplicity) or Pip.

### Recommended: Conda

This is the easiest method as it handles the installation of OpenBabel and Python packages within an isolated environment.

1.  **Create and activate a new conda environment**:
    ```bash
    conda create -n proteinprep python=3.10 -y
    conda activate proteinprep
    ```

2.  **Install OpenBabel and Python packages**:
    ```bash
    conda install -c conda-forge openbabel -y
    pip install -r requirements.txt
    ```

### Alternative: Pip + System OpenBabel

1.  **Create a virtual environment** (optional but highly recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install OpenBabel separately**:

    * **Linux (Ubuntu/Debian)**:
        ```bash
        sudo apt-get update
        sudo apt-get install -y openbabel
        ```
    * **macOS (Homebrew)**:
        ```bash
        brew install open-babel
        ```
    * **Windows**:
        The recommended way is to use `conda`. Alternatively, download the official installer from the [OpenBabel website](https://open-babel.readthedocs.io/en/latest/Installation/install.html).

### PySimpleGUI Notes

Recent versions of PySimpleGUI require installation from a private server. If you encounter an error message about this after running `pip install -r requirements.txt`, follow these steps to fix it:

1.  **Uninstall the current version and clear the cache**:
    ```bash
    python3 -m pip uninstall PySimpleGUI -y
    python3 -m pip cache purge
    ```

2.  **Install PySimpleGUI from the correct source**:
    ```bash
    python3 -m pip install --upgrade --no-cache-dir --extra-index-url [https://pysimplegui.net/pysimplegui/](https://pysimplegui.net/pysimplegui/) PySimpleGUI
    ```

---

## Usage

You can run the tool via the command line or the graphical interface.

### CLI (Command Line Interface)

Open your terminal in the project directory to run the following commands.

**1. Basic Processing**
Download PDB `1a4w`, clean it, add hydrogens, and convert it to PDBQT.
```bash
python3 proteinprep.py 1a4w --auto-protonate --auto-pdbqt
```
