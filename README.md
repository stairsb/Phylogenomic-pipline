# Phylogenomic-pipline
This pipeline uses orthologous sequences from whole genome data and outputs individual gene and species trees.

## Table of contents

## Obtaining the data
Most of the raw reads were obtained using illumina sequencing data downloaded from the NCBI SRA database. Reads in this analysis that were not downloaded from a database were prepped by the Uehling lab at OSU and sequenced by the UO sequencing core using illumina. The reference genome used was obtained from the NCBI SRA database https://www.ncbi.nlm.nih.gov/Traces/wgs/SMRR01?display=contigs&page=1.

Go to the busco database (Documentation: https://busco.ezlab.org/) and download hmm files that are the most closely related to your species. Run these commands to make a combines hmm file. You will need to download hmmpress https://manpages.ubuntu.com/manpages/bionic/man1/hmmpress.1.html.
```
cd /path/to/mucorales_obd10
cat hmm/*.hmm > mucorales_odb10.combined.hmm
hmmpress mucorales_odb10.combined.hmm
```

## Assembly
The whole genome data for this analysis was in the form of short raw reads that were sequenced using illumina sequencing. `Spades` is a great tool for assembling NGS short reads into contigs (SPAdes documentation: https://cab.spbu.ru/software/spades/). The isolate option needs to be included if you are NOT starting with single-cell data.
```
spades.py --isolate -1 read1.fq  -2 read2.fq -t 5 -m 40 -o output_directory
```
Each contig file will need to be clipped to get rid of extra data that isn't needed, this will speed up our over all computational time and be less memmory taxing. A word of advice, contigs that are smaller than 1000 nucleotides will most likely not represent a protein. The following script will provide information that gives us an idea of well the reads were assembled into contigs, this can be useful when deciding a cutoff for how short of contigs we will include.
```
perl assemblathon_stats.pl Insertfastacontainingcontigs.fasta
```
Now to remove contigs that are smaller than we want
```
perl remove_small_contigs.pl 200 intertfastacontainingcontigs.fasta > clipped.fasta
```
It is advised to rerun the assemblathon_stats.pl to make sure we clipped the contigs appropriately 

## Annotation

`Funannotate` (Documentation: https://funannotate.readthedocs.io/en/latest/) will be used to annotate proteins from the contig files. Before predicting the proteins the contig files have to get run through assembly prep. `Funannotate` should be set up in a `conda environment` because there are a lot of dependcies. I also ran into issues with running this program in shells other than bash. If running as a submittable job, make sure that the job script path is updated to the conda environment pathing.
```
Conda activate /local/cluster/funannotate
```
First we want to remove repeative contigs that are not "uniq"
```
funannotate clean -i SRR8845243_clipped.fasta -o cleaned.fasta
```
Second we need to sort our contigs by length and `Augustus` which is a program within `funannotate` has issues with long contigs/scaffold names so we will add the `-b` option to have names that are less than 16 characters.
```
funannotate sort -i cleaned.fasta -o sorted.fasta -b contigs
```
Finally, we will soft mask repeats. You can switch this step out for a program of your choosing such as `Repeatmasker`. This step may seem redudant after running `funannotate clean` but is required.
```
funannotate mask -i sorted.fasta -o norepeat.fasta
```
Finally annotate! We need to give the program information that will help it to predict proteins. I used the busco_db (Documentation: https://busco.ezlab.org/) but other information could be included to help predict proteins. There are a lot of alternative methods found in the `funannotate` manual for protein prediction if your organism isn't well supported by the busco database.
```
funannotate predict -i norepeat.fasta -o . -s \"Rhizopus microsporus\" --busco_db /mucorales_odb10/ --cpus 2
```
## Formating files
Make sure fasta files have a unique locus tag for each (locustag|contigname)
Use this add tag: 
```
sed -i 's/>/>1239|/g' filename
```

Check if each file has a unique tag. Number should be same as number of files:
```
cat *.fasta | grep \> | cut -d '|' -f1 | sort | uniq | wc -l
```
If there is a weird error the temporary dir may not have enough space so add a dir option to `sort`

## Creating gene and species trees
This step may seem redudant but here we will use the busco database again to make our predicted proteins to homologs via `hmmsearch` http://eddylab.org/software/hmmer/Userguide.pdf.
```
python3 1_hmmsearch.py -h
```
Reads and parses domtbl from `hmmsearch` and uses an input E-value cutoff to remove sequences that have low hmm matching profile
```
domtbl2unaln -h
	Use --best 
For cutoff option use “mucorales” when working with Rhizopus.
The proteins option uses a index (.fai) file that includes of protein files that will be used in the tree.
cat /path/to/pep/*.faa > pep_combined.fasta
samtools faidx pep_combined.fasta
```
Produces a full alignment by aligning every sequence to a seed concensus using `hmmalign` and `trimAl`
```
python3 2_hmmalign.py -h
```
Finally we will generate individual genes alignments for all taxon that had the gene and use 'fasttree' to create maximum likelihood gene phylogenetic reconstructions. Make sure to run output script in folder with fasta files
```
python3 3_genetrees.py -h
```
In the 2_hmmalign.py step `.trim` files were created with individual gene alignments for each gene that was included in the analysis. To perform a single phylogenetic reconstruction of all taxon and single copy othologs the individual gene alignments will need to be concatinated together. `SCGID` can be used to do this and is found here https://github.com/amsesk/SCGid. 

This program is managed in a conda environmnet and to activate the environment run.
```
source SCGid/scgidenv/bin/activate
```
Now we can concatinate!
```
concatenate_msa.py -a /path/to/trim/files/directory -o output_file_name -s .aa.trim
```
The last step is to finally perform the phylogenetic reconstruction using iqtree2.
```
iqtree2 --seqtype AA -m JTT -s concat.fasta -T 20
```
## Ploting to output
If you have experience in R I would highly recommend plotting your data via this software.




