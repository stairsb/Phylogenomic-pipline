# Phylogenomic-pipline
This pipeline uses orthologous sequences from whole genome data and outputs individual gene trees and a specie tree

Steps for Phylogenomic pipeline

When starting with raw reads they need to be annotated into protein fasta files. The first step is to get the contigs which spades can be used to do

spades.py --isolate -1 read1.fq  -2 read2.fq -t 5 -m 40 -o output_directory

Each contig file will need to be clipped. Contigs that are smaller than 1000 nucleotides will most likely not represent a protein. The first script provides information on the contig files and the second is used to remove contigs.
perl scripts/assemblathon_stats.pl Insertfastacontainingcontigs.fasta
perl scripts/remove_small_contigs.pl 200 intertfastacontainingcontigs.fasta > clipped.fasta
perl scripts/assemblathon_stats.pl insertclippedcontigs.fasta

Funannotate will be used to annotate proteins from the contig files. Before predicting the proteins the contig files have to get run through assembly prep. Funannotate is located in it’s conda environment on the cluster. Make sure to be in bash when running the commands.

Conda activate /local/cluster/funannotate
If running a job make sure that the pathing in the job lscript is updated to the conda environment

funannotate clean -i SRR8845243_clipped.fasta -o cleaned.fasta
funannotate sort -i cleaned.fasta -o sorted.fasta -b contigs
funannotate mask -i sorted.fasta -o norepeat.fasta

Finally annotate!
Make sure to add the cpus option
I used the busco_db but other information could be included to help predict proteins

funannotate predict -i norepeat.fasta -o . -s \"Rhizopus microsporus\" --busco_db ~/rhizopus_phylogenomics/data/mucorales_odb10/ --cpus 2



Make sure fasta files have a unique locus tag for each (locustag|contigname)
Use this add tag: sed -i 's/>/>1239|/g' filename
Check if each file has a unique tag. Number should be same as number of files:
cat *.fasta | grep \> | cut -d '|' -f1 | sort | uniq | wc -l
If there is a weird error the temporary dir may not have enough space so add a dir option to sort

Make sure to go to the busco database and download hmm files that are the most closely related to your species. Make a combines hmm file
cd /path/to/mucorales_obd10
cat hmm/*.hmm > mucorales_odb10.combined.hmm
hmmpress mucorales_odb10.combined.hmm

python3 /nfs4/BPP/Uehling_Lab/Uehling_Lab_Wiki/Biological_Computing/Phylogenomics/scripts/1_hmmsearch.py -h

/nfs4/BPP/Uehling_Lab/Uehling_Lab_Wiki/Biological_Computing/Phylogenomics/bin/domtbl2unaln -h
	Use --best 
For cutoff option use “mucorales”
The proteins option uses a index (.fai) file that includes of protein files that will be used in the tree.
cat /path/to/pep/*.faa > pep_combined.fasta
samtools faidx pep_combined.fasta

python3 /nfs4/BPP/Uehling_Lab/Uehling_Lab_Wiki/Biological_Computing/Phylogenomics/scripts/2_hmmalign.py -h
Make sure to run output script in folder with fasta files
python3 /nfs4/BPP/Uehling_Lab/Uehling_Lab_Wiki/Biological_Computing/Phylogenomics/scripts/3_genetrees.py -h
