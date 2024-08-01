##########################################################################################
# Snakemake module
# Author: Redwan Farooq
# Module name: gex_atac_cellranger_arc
##########################################################################################


# --------------------------------------------------
# SETUP
# Load modules
import os
import yaml
from resources.scripts.rule import *

# Load and parse sample/library info from YAML file
with open(file=os.path.join(config.get("metadata_dir", "metadata"), "info.yaml"), mode="r", encoding="UTF-8") as file:
    info = yaml.load(stream=file, Loader=yaml.SafeLoader)
for key, value in parse_info(info).items():
    globals()[key] = value

# Set module rules list
module_rules = ['bcl2fastq', 'trimfastq', 'fastqc', 'multiqc', 'count_reads', 'cellranger_arc']

# Import rules
include: 'rules/bcl2fastq.smk'
include: 'rules/trimfastq.smk'
include: 'rules/fastqc.smk'
include: 'rules/multiqc.smk'
include: 'rules/count_reads.smk'
include: 'rules/cellranger_arc.smk'

# Set targets list
targets = [x for rule in [bcl2fastq, trimfastq, fastqc, multiqc, count_reads, cellranger_arc] for x in rule]
# --------------------------------------------------


# --------------------------------------------------
# RULES
rule all:
	input: [os.path.abspath(x) for x in targets]
# --------------------------------------------------