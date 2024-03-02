# Description
Snakemake pipeline for preprocessing sequencing data
- Modularised workflow can be modified and/or extended for different library preparation protocols
- Add as a submodule in a bioinformatics project GitHub repository
```
git submodule add https://github.com/redwanfarooq/preprocessing preprocessing
```
- Update submodule to the latest version
```
git submodule update --remote
```

# Required software
1. Global environment
    - [Snakemake >=v7.31](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html)
    - [docopt >=v0.6](https://github.com/docopt/docopt)
    - [pandas >=v2.0](https://pandas.pydata.org/docs/getting_started/install.html)
2. Specific modules
    - [bcl2fastq >=v2.20](https://sapac.support.illumina.com/sequencing/sequencing_software/bcl2fastq-conversion-software.html)
    - [Cell Ranger >=v7.1](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/installation)
    - [Cell Ranger ARC >=v2.0](https://support.10xgenomics.com/single-cell-multiome-atac-gex/software/pipelines/latest/installation)
    - [STAR >=v2.7.11a](https://github.com/alexdobin/STAR)
    - [samtools >=v1.17](http://www.htslib.org)
    - [chromap >=v0.2.5](https://github.com/haowenz/chromap)
    - [htslib >=v1.18](http://www.htslib.org)
    - [MACS2 >=v2.2.9](https://github.com/macs3-project/MACS/wiki/Install-macs2)
    - [BarCounter](https://github.com/AllenInstitute/BarCounter-release)
    - [FastQC >=v0.11](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
    - [MultiQC >=v1.14](https://multiqc.info/docs/getting_started/installation/)
    - [quarto >=v1.4](https://quarto.org/docs/get-started/)
    - [panel >=v1.3.8](https://panel.holoviz.org/getting_started/installation.html)
    - [R >=v4.3](https://cran.r-project.org)
        * [Signac v1.10.0](https://CRAN.R-project.org/package=Signac)

# Setup
1. Install software for global environment (requires Anaconda or Miniconda - see [installation instructions](https://conda.io/projects/conda/en/stable/user-guide/install/index.html))
    - Download [environment YAML](/resources/envs/snakemake.yaml)
    - Create new conda environment from YAML
    ```
    conda env create -f snakemake.yaml
    ```
2. Install software for specific module(s)
    - Manually install required software from source and check that executables are available in **PATH** (using `which`) *and/or*
    - Create new conda environments with required software from YAML (as above - download [environment YAMLs](/resources/envs)) *and/or*
    - Check that required software is available to load as environment modules (using `module avail`)
3. Set up pipeline configuration file **config/config.yaml** (see comments in file for detailed instructions)
4. Set up profile configuration file **profile/config.yaml** (see comments in file for detailed instructions)

# Run
1. Activate global environment
```
conda activate snakemake
```
2. Execute **run.py** in root directory

# Input
Pipeline requires the following input files/folders:

## General

**REQUIRED:**

1. Illumina sequencing run folder(s)
- Folders should be named according to default convention for the system e.g. **YYYYMMDD_InstrumentID_RunNumber_FlowCellID**
2. Runs summary table in CSV format with the following required fields (with headers):
- **run**: run folder name
- **lib_type**: library type
- **donor**: donor ID
- **pool**: pool ID
- **sample_index**: *either* index name *or* i7 index sequence
- **lane**: *either* lane number *or* * (for all lanes)

**OPTIONAL:**

3. Index kit CSV files with the following required fields (with headers) - must be provided if any index names are used in **sample_index** field of runs summary table:
- **index_name**: index set name (e.g. SI-TT-A1); must be first field
- **\***: 1 or more fields specifying index sequences in the following order:
    - *Dual index kits*: i7 sequence, i5 sequence (forward strand), i5 sequence (reverse complement)
    - *Single index kits*: i7 sequence (additional fields if more than 1 sequence per index set)

## Module-specific

### gex_fb: 10X feature barcoding (GEX + FB) protocol

**REQUIRED:**

1. Reference files:
- Cell Ranger genome reference package
2. Feature reference in CSV format - see [specifications](https://support.10xgenomics.com/single-cell-gene-expression/software/pipelines/latest/using/feature-bc-analysis#feature-ref)

### gex_atac: 10X multiome (GEX + ATAC) protocol

**REQUIRED:**

1. Reference files:
- STAR genome reference package
- chromap genome reference and index
- Cell barcode whitelist (GEX)
- Cell barcode whitelist (ATAC)

### cite_seq: CITE-seq protocol (TotalSeq-A antibodies)

**REQUIRED:**

1. Reference files:
- STAR genome reference package
- Cell barcode whitelist (GEX)
2. Antibody tag list in CSV format with the following required fields (without headers):
- Tag sequence (length 15nt)
- Tag name

### tea_seq: TEA-seq protocol (TotalSeq-A antibodies)

**REQUIRED:**

1. Reference files:
- STAR genome reference package
- chromap genome reference and index
- Cell barcode whitelist (GEX)
- Cell barcode whitelist (ATAC)
2. Antibody tag list in CSV format with the following required fields (without headers):
- Tag sequence (length 15nt)
- Tag name

# Output
Output directory will be created in specified location with subfolders containing the output of each software tool specified in the module.

# Modules

## Available modules
- gex_fb
- gex_atac
- cite_seq
- tea_seq

## Adding new module
1. Add entry to module rule specifications file **config/modules.yaml** with module name and list of rule names
2. Add additional rule definition files in **modules/rules** folder (if needed)
- Rule definition file **must** also assign a list of pipeline target files generated by the rule to a variable with the same name as the rule
- Rule definition file **must** have the same file name as the rule with the file extension **.smk**
3. Execute **run.py** in root directory with `--update` flag (needs to be repeated if there are any further changes to the module rule specification in **config/modules.yaml**)