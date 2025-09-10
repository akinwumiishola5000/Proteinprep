# ProteinPrep — Fast protein preparation for docking (CLI + GUI)

ProteinPrep is a small, user-friendly tool that fetches PDB structures, cleans them (removes water/heteroatoms), optionally retains only selected chains, adds hydrogens using OpenBabel, and converts to PDBQT for AutoDock Vina. It supports both a command-line interface (CLI) and a graphical user interface (GUI). 🧪        

---

## Features

-   **Download PDB** by ID from the RCSB database with built-in retries.
-   **Clean PDB**: Remove water molecules and heteroatoms.
-   **Select Chains**: Keep only specified chains (e.g., `--keep-chains A,C`).
-   **Keep Ligands**: Optionally preserve specific heteroatoms/ligands.
-   **Add hydrogen**: Add hydrogens (`--auto-add-h`).
-   **Convert**: Generate PDBQT files for docking (`--auto-pdbqt`).
-   **Batch Mode**: Process multiple PDB IDs from a file (`--batch-file`).
-   **Simple GUI**: An intuitive graphical interface for all features.
-   **Logging**: Generates a `proteinprep_log.json` file with a full report of the operations performed.

---

## Installation
Make sure to copy/download `proteinprep.py` and `proteinprep_gui.py` into your working directory

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
3.  **Install Requests used for HTTP requests to download PDB files**:
    ```bash
    pip install requests
    ```
4. **Install Typer, for CLI command parsing and options**:
    ```bash
    pip install typer[all]
    ```
5.  **Install OpenBabel separately**:

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
    python3 -m pip install --upgrade --no-cache-dir --extra-index-url https://pysimplegui.net/pysimplegui/ PySimpleGUI
    ```
3.  **Use python3 instead of python if on Linux or macOS:**:
    ```bash
    python3 -m pip uninstall PySimpleGUI
    python3 -m pip install --force-reinstall --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
     ```
---

## Usage

You can run the tool via the command line or the graphical interface.

### CLI (Command Line Interface)

Open your terminal in the project directory to run the following commands.

**1. Basic Processing**
Single PDB (download, clean, add hydrogens, convert to PDBQT), using the protein `8fv4` as an example:
```bash
python3 proteinprep.py 8fv4 --auto-add-h --auto-pdbqt
