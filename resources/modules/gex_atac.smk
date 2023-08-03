##########################################################################################
# Snakemake module for preprocessing sequencing data
# Author: Redwan Farooq
# Module name: gex_atac
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

# Import rules
include: 'rules/bcl2fastq.smk'
include: 'rules/fastqc.smk'
include: 'rules/multiqc.smk'
include: 'rules/cellranger_arc.smk'

# Set targets
targets = [x for rule in (bcl2fastq, fastqc, multiqc, cellranger_arc) for x in rule]
# --------------------------------------------------


# --------------------------------------------------
# RULES
rule all:
	input: [os.path.abspath(x) for x in targets]
# --------------------------------------------------