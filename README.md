# Genomics-Toolbox
A set of python scripts useful when analyzing and/or fixing a draft genome assembly and annotation.  Type each script followed by '-h' for more details for now (will add details in this document later).

- `genomic_regions_collapse_overlaps.py` collapses overlapping genomic regions in tab-delimited tables with chromosome IDs, start, and end positions.

- `genomic_regions_extract_intergenic.py` extract 5' and 3' sequences for all gene models, given a set of genome (`*.genome.fa`) and gene model (`*.gtf`) files. Also create LASTZ commands for comparigng intergenic regions of ortholog pairs. 

- `genomic_regions_mark_overlaps.py` marks overlaps between two tab-delimited list of genomic regions.

- `parse_gtf_2table.py` prints a table summary of a gtf file, including the start, end, length, and number of exons for both mRNA and CDS, one transcript per line; it has options to extract subset of transcripts from a .gtf, collapse overlapping transcripts and keep the one with the longest ORF, simply cluster overlapping transcripts to identify locus, etc.; part of the CLfinder-OrthNet pipeline.    

- `remove_regions_in_gff.py` removes genomic regions from a gff file and adjust coordinates of all features in the gff automatically; useful when cleaning up a genome assembly of haplotigs/duplicated artifacts, etc.

- `rename_gtf_transcripts.py` renames transcript_id, gene_id, and gene_name fields of a .gtf file, using the transcript_id field as the anchor. 

