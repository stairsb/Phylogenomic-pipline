import sys
import os
import numpy as np
import re
import argparse
import sge_scriptgen

parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--proteins",
    action="store",
    required=True,
    help="Path to directory containing protein FASTA files for marker search.")
parser.add_argument("-m",
                    "--markers",
                    action="store",
                    required=True,
                    help="Path to combined hmm marker file.")
parser.add_argument(
    "--suffix",
    action="store",
    required=False,
    default="([.]fa$|[.]fasta$|[.]faa$)",
    help=
    "Regular expression pattern matching the suffix of protein FASTA files. Default: ([.]fa$|[.]fasta$|[.]faa$)"
)
parser.add_argument("--jobs",
                    action="store",
                    required=False,
                    default=10,
                    help="Number of batch jobs scripts to split work into.")
args = parser.parse_args()

NJOBS = int(args.jobs)
PEP_PATH = args.proteins
MARKERS_PATH = args.markers
SUFFIX_PATTERN = re.compile(args.suffix)

todo = [
    os.path.join(PEP_PATH, x) for x in os.listdir(PEP_PATH)
    if re.search(SUFFIX_PATTERN, x) is not None
]
todo = np.array(todo)
todo_spl = np.array_split(todo, NJOBS)

jobname = "HmSe"

for idx, chunk in enumerate(todo_spl):
    sg = sge_scriptgen.SgeScriptGenerator(jobname=f"{jobname}_{idx}",
                                          threads=1,
                                          memory="2G",
                                          queue="selway,bpp@selway,bpp")
    for line in chunk:
        outline = os.path.basename(line)
        sg.add_command(
            f"hmmsearch --cpu 1 -E 1e-5 --domtblout {re.sub(SUFFIX_PATTERN, '.odb10.domtbl', outline)} {MARKERS_PATH} {line} > {outline+'.hmmsearch.log'}"
        )

    sg.write()
