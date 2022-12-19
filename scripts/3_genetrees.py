import sys
import os
import re
import sge_scriptgen
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "-a",
    "--aln",
    action="store",
    required=True,
    help=
    "Path to directory containing all the trimmed, filtered marker alignments."
)
parser.add_argument(
    "--suffix",
    action="store",
    required=False,
    default="[.]aa.trim$",
    help=
    "Regular expression pattern matching the suffix of protein FASTA files. Default: ([.]aa.trim$"
)
parser.add_argument("--jobs",
                    action="store",
                    required=False,
                    default=10,
                    help="Number of batch jobs scripts to split work into.")
args = parser.parse_args()

NJOBS = int(args.jobs)
ALN_PATH = os.path.abspath(args.aln)
SUFFIX = args.suffix

todo = [
    f"{os.path.join(ALN_PATH,x)}" for x in os.listdir(ALN_PATH)
    if re.search(SUFFIX, x).group(0) is not None
]
todo = np.array(todo)
todo_spl = np.array_split(todo, NJOBS)

jobname = "FaTr"

for idx, chunk in enumerate(todo_spl):
    sg = sge_scriptgen.SgeScriptGenerator(jobname=f"{jobname}_{idx}",
                                          threads=1,
                                          memory="2G")
    for line in chunk:
        outbase = os.path.basename(line)
        sg.add_command(
            f"fasttree -gamma < {line} > {re.sub(SUFFIX,'.aa.tre', outbase)}")

    sg.write()
