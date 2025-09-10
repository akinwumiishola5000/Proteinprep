#!/usr/bin/env python3
"""
proteinprep.py

CLI tool to:
 - fetch PDB by ID (with retries)
 - clean protein: remove waters, remove heteroatoms (optionally keep named ligands)
 - optionally keep only specified chains (A,B,...)
 - optionally add hydrogens using OpenBabel CLI (note: this only *adds hydrogens*, it does not perform
   full chemical protonation state prediction — OpenBabel's -h adds hydrogens based on the input)
 - optionally convert to PDBQT using OpenBabel CLI
 - produce a JSON log file with a short report

Usage examples:
  python3 proteinprep.py 1a4w --auto-add-h --auto-pdbqt
  python3 proteinprep.py 1a4w --keep-chains A,C --auto-pdbqt
  python3 proteinprep.py ./my.pdb --out-dir ./out --auto-add-h

Author: Ishola Abeeb Akinwumi
"""
import os
import sys
import time
import json
import shutil
import subprocess
import platform
from typing import List, Optional

import requests
import typer

app = typer.Typer(add_completion=False)

# -------------------- Utilities --------------------
def which(program: str) -> Optional[str]:
    return shutil.which(program)

def obabel_available() -> bool:
    return which("obabel") is not None or which("babel") is not None

def try_install_openbabel() -> bool:
    """
    Try to install OpenBabel via conda (preferred) or pip (openbabel-wheel).
    Returns True if installation appears successful.
    NOTE: automatic installs may require user privileges and are not guaranteed.
    """
    print("[INSTALL] Attempting to install OpenBabel (conda -> pip fallback)...")
    # Try conda
    if which("conda"):
        try:
            subprocess.check_call(["conda", "install", "-c", "conda-forge", "openbabel", "-y"])
            return obabel_available()
        except Exception as e:
            print("[WARN] Conda install failed:", e)
    # Try pip
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openbabel-wheel"])
        return obabel_available()
    except Exception as e:
        print("[WARN] pip install openbabel-wheel failed:", e)
    return False

# -------------------- Download PDB --------------------
def download_pdb(pdb_id: str, out_path: str, retries: int = 3, timeout: int = 10):
    url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            with open(out_path, "wb") as fh:
                fh.write(resp.content)
            return
        except requests.RequestException as e:
            last_err = e
            print(f"[DOWNLOAD] Attempt {attempt}/{retries} failed: {e}")
            time.sleep(2)
    raise RuntimeError(f"Failed to download {pdb_id} after {retries} attempts: {last_err}")

# -------------------- Clean PDB --------------------
def clean_pdb(input_pdb: str,
              output_pdb: str,
              remove_waters: bool = True,
              remove_hetero: bool = True,
              keep_chains: Optional[List[str]] = None,
              keep_ligands: Optional[List[str]] = None) -> dict:
    """
    Simplistic-but-robust text-based PDB cleaner:
      - keeps ATOM/HETATM/TER/END records
      - can filter by chain IDs (keep_chains)
      - can remove water residues (HOH)
      - can remove HETATM unless in keep_ligands
    Returns a dict summary.
    """
    keep_chains = [c.strip().upper() for c in (keep_chains or [])] if keep_chains else None
    keep_ligands = [k.strip().upper() for k in (keep_ligands or [])] if keep_ligands else []
    removed = {"waters": 0, "hetero_residues": 0, "skipped_chains": 0}

    wrote_any = False
    with open(input_pdb, "r") as fin, open(output_pdb, "w") as fout:
        for line in fin:
            if line.startswith(("ATOM  ", "HETATM", "TER", "END")):
                rec = line[0:6].strip()
                # chain id usually column 22 (index 21)
                chain_id = line[21:22].strip() if len(line) >= 22 else ""
                if keep_chains and chain_id and chain_id.upper() not in keep_chains:
                    removed["skipped_chains"] += 1
                    continue
                # residue name at columns 18-20 (index 17:20)
                resname = line[17:20].strip().upper() if len(line) >= 20 else ""
                # waters
                if remove_waters and resname in ("HOH", "H2O", "WAT"):
                    removed["waters"] += 1
                    continue
                # heteroatoms
                if remove_hetero and rec == "HETATM" and resname not in keep_ligands:
                    removed["hetero_residues"] += 1
                    continue
                fout.write(line)
                wrote_any = True
            # skip other lines (HEADER, REMARKS). This keeps output minimal and suitable for docking.
    if not wrote_any:
        raise RuntimeError("No ATOM/HETATM records written — check input or filters.")
    return removed

# -------------------- OpenBabel helpers --------------------
def add_hydrogens_with_obabel(input_file: str, output_file: str) -> dict:
    exe = which("obabel") or which("babel")
    if not exe:
        raise RuntimeError("OpenBabel CLI not found (obabel).")
    # -h adds hydrogens; this is not a full protonation state predictor
    cmd = [exe, input_file, "-O", output_file, "-h"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return {"cmd": " ".join(cmd), "rc": proc.returncode, "output": proc.stdout}

def convert_to_pdbqt_with_obabel(input_file: str, output_file: str) -> dict:
    exe = which("obabel") or which("babel")
    if not exe:
        raise RuntimeError("OpenBabel CLI not found (obabel).")
    cmd = [exe, input_file, "-O", output_file]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return {"cmd": " ".join(cmd), "rc": proc.returncode, "output": proc.stdout}

# -------------------- Main workflow --------------------
@app.command()
def main(
    pdb: str = typer.Argument(..., help="PDB ID (4 chars) or local PDB path"),
    out_dir: str = typer.Option(".", help="Output directory"),
    remove_waters: bool = typer.Option(True, help="Remove water molecules"),
    remove_hetero: bool = typer.Option(True, help="Remove heteroatoms (HETATM)"),
    keep_chains: Optional[str] = typer.Option(None, help="Comma-separated chain IDs to keep, e.g. 'A,C'"),
    keep_ligands: Optional[str] = typer.Option(None, help="Comma-separated 3-letter ligand names to keep, e.g. NAD,HEM"),
    auto_add_h: bool = typer.Option(False, "--auto-add-h", "--auto-add-hydrogens", help="Automatically add hydrogens using OpenBabel (note: adds hydrogens, not full protonation state prediction)"),
    auto_pdbqt: bool = typer.Option(False, help="Automatically convert to PDBQT using OpenBabel"),
    batch_file: Optional[str] = typer.Option(None, help="Optional: path to a newline-separated file of PDB IDs or paths"),
):
    os.makedirs(out_dir, exist_ok=True)
    targets = []

    if batch_file:
        if not os.path.exists(batch_file):
            typer.echo(f"[ERROR] Batch file not found: {batch_file}")
            raise typer.Exit(code=1)
        with open(batch_file, "r") as f:
            targets = [ln.strip() for ln in f if ln.strip()]
    else:
        targets = [pdb]

    keep_chain_list = [c.strip().upper() for c in keep_chains.split(",")] if keep_chains else None
    keep_lig_list = [k.strip().upper() for k in keep_ligands.split(",")] if keep_ligands else None

    reports = []
    obabel_ready = obabel_available()
    if (auto_add_h or auto_pdbqt) and not obabel_ready:
        typer.echo("[WARN] OpenBabel CLI not found. Will try automatic install (may fail).")
        if try_install_openbabel():
            obabel_ready = obabel_available()
            typer.echo("[OK] OpenBabel appears installed.")
        else:
            typer.echo("[WARN] OpenBabel not installed. Hydrogen addition / PDBQT will be skipped.")

    for t in targets:
        try:
            if os.path.exists(t):
                fetched = t
                pdb_label = os.path.splitext(os.path.basename(t))[0]
            else:
                if len(t) == 4 and t.isalnum():
                    pdb_label = t.upper()
                else:
                    raise typer.Exit(f"Invalid PDB identifier or file path: {t}")
                fetched = os.path.join(out_dir, f"{pdb_label}.pdb")
                typer.echo(f"[FETCH] Downloading {pdb_label} ...")
                download_pdb(pdb_label, fetched)

            cleaned = os.path.join(out_dir, f"{pdb_label}_clean.pdb")
            report = {"input": t, "fetched": fetched, "cleaned": cleaned}
            removed = clean_pdb(fetched, cleaned, remove_waters, remove_hetero, keep_chain_list, keep_lig_list)
            report["removed"] = removed

            processed = cleaned

            if auto_add_h:
                if obabel_ready:
                    added_h = os.path.join(out_dir, f"{pdb_label}_added_h.pdb")
                    typer.echo(f"[OBABEL] Adding hydrogens to {processed} -> {added_h}")
                    obres = add_hydrogens_with_obabel(processed, added_h)
                    # record under a clear key indicating hydrogen addition (not 'protonation')
                    report["add_hydrogens"] = obres
                    if obres["rc"] == 0:
                        processed = added_h
                    else:
                        typer.echo("[WARN] OpenBabel returned non-zero exit during hydrogen addition.")
                else:
                    report["add_hydrogens_skipped"] = "OpenBabel not available"

            if auto_pdbqt:
                if obabel_ready:
                    pdbqt = os.path.join(out_dir, f"{pdb_label}.pdbqt")
                    typer.echo(f"[OBABEL] Converting {processed} -> {pdbqt}")
                    obres = convert_to_pdbqt_with_obabel(processed, pdbqt)
                    report["pdbqt"] = obres
                else:
                    report["pdbqt_skipped"] = "OpenBabel not available"

            reports.append(report)
            typer.echo(f"[DONE] {pdb_label}")
        except Exception as e:
            typer.echo(f"[ERROR] processing {t}: {e}")
            reports.append({"input": t, "error": str(e)})

    # write log
    logf = os.path.join(out_dir, "proteinprep_log.json")
    with open(logf, "w") as fh:
        json.dump(reports, fh, indent=2)
    typer.echo(f"[FINISHED] Reports: {logf}")

if __name__ == "__main__":
    app()
