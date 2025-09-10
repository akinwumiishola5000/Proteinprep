#!/usr/bin/env python3
"""
proteinprep_gui.py

Simple PySimpleGUI wrapper that calls the CLI script (proteinprep.py) in a subprocess
and streams stdout/stderr into the GUI.

Note: Keep this file in the same folder as proteinprep.py
"""
import os
import sys
import subprocess
import threading
import PySimpleGUI as sg

def run_cmd_in_thread(args, window):
    """Run command and stream output lines back to GUI via events."""
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in proc.stdout:
        window.write_event_value("-OUT-", line.rstrip("\n"))
    proc.wait()
    window.write_event_value("-DONE-", proc.returncode)

def build_args(pdb, outdir, remove_waters, remove_hetero, keep_chains, auto_add_h, auto_pdbqt, batch_file):
    args = [sys.executable, os.path.join(os.path.dirname(__file__), "proteinprep.py")]
    if batch_file:
        args.extend(["--batch-file", batch_file])
    args.append(pdb)
    if outdir:
        args.extend(["--out-dir", outdir])
    if remove_waters is not None:
        if remove_waters:
            args.append("--remove-waters")
        else:
            args.append("--no-remove-waters")
    if remove_hetero is not None:
        if remove_hetero:
            args.append("--remove-hetero")
        else:
            args.append("--no-remove-hetero")
    if keep_chains:
        args.extend(["--keep-chains", keep_chains])
    if auto_add_h:
        args.append("--auto-add-h")
    if auto_pdbqt:
        args.append("--auto-pdbqt")
    return args

def main():
    sg.theme("LightGreen")
    layout = [
        [sg.Text("ProteinPrep — GUI", font=("Helvetica", 16))],
        [sg.Text("PDB ID or local PDB file:"), sg.Input(key="-PDB-"), sg.FileBrowse(file_types=(("PDB Files","*.pdb"),), target="-PDB-")],
        [sg.Text("Or batch file (one ID/path per line):"), sg.Input(key="-BATCH-"), sg.FileBrowse(file_types=(("Text Files","*.txt"),), target="-BATCH-")],
        [sg.Checkbox("Remove waters", default=True, key="-WATERS-"), sg.Checkbox("Remove heteroatoms", default=True, key="-HETERO-")],
        [sg.Text("Keep chains (comma separated):"), sg.Input(key="-CHAINS-", size=(20,1))],
        [sg.Checkbox("Auto add hydrogens (requires OpenBabel)", key="-ADDH-"), sg.Checkbox("Auto convert to pdbqt (OpenBabel)", key="-PDBQT-")],
        [sg.Text("Output folder:"), sg.Input(default_text=".", key="-OUT-"), sg.FolderBrowse(target="-OUT-")],
        [sg.Button("Run"), sg.Button("Exit")],
        [sg.Multiline(size=(100,20), key="-LOG-", autoscroll=True, disabled=True)]
    ]
    window = sg.Window("ProteinPrep GUI", layout, finalize=True)

    thread = None
    while True:
        event, values = window.read(timeout=100)
        if event in (sg.WIN_CLOSED, "Exit"):
            break
        if event == "Run":
            pdb = values["-PDB-"].strip()
            batch = values["-BATCH-"].strip()
            if not pdb and not batch:
                sg.popup_error("Please enter a PDB ID or select a batch file.")
                continue
            outdir = values["-OUT-"].strip() or "."
            args = build_args(
                pdb if pdb else batch,
                outdir,
                values["-WATERS-"],
                values["-HETERO-"],
                values["-CHAINS-"].strip(),
                values["-ADDH-"],
                values["-PDBQT-"],
                batch if batch else None
            )
            window["-LOG-"].update("")
            window["Run"].update(disabled=True)
            thread = threading.Thread(target=run_cmd_in_thread, args=(args, window), daemon=True)
            thread.start()
        elif event == "-OUT-":
            window["-LOG-"].print(values[event])
        elif event == "-DONE-":
            rc = values[event]
            window["-LOG-"].print(f"\n[Process finished with return code {rc}]")
            window["Run"].update(disabled=False)
        # catch streamed lines
        if event == "-OUT-":
            window["-LOG-"].print(values[event])

    window.close()

if __name__ == "__main__":
    main()
