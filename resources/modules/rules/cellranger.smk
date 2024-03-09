##########################################################################################
# Snakemake rule for Cell Ranger
# Author: Redwan Farooq
# Requires functions from resources/scripts/rule.py
# Requires outputs from resources/rules/bcl2fastq.smk
##########################################################################################

# Define rule
rule cellranger:
	input: lambda wildcards: get_count_inputs(wildcards, lib_types={"*"}, info=info)
	output: os.path.abspath("stamps/cellranger/{sample}.stamp")
	log: os.path.abspath("logs/cellranger/{sample}.log")
	threads: 1
	params: 
		librarysheet_path = os.path.abspath(os.path.join(config.get("metadata_dir", "metadata"), "cellranger")),
		features = os.path.abspath(os.path.join(config.get("metadata_dir", "metadata"), config["features"])),
		reference = config["cellranger_reference"],
		custom_flags = config.get("cellranger_args", ""),
		output_path = os.path.join(config["output_dir"], "cellranger")
	envmodules: "cellranger/7.1.0"
	message: "Making GEX and FB count matrix for {wildcards.sample}"
	shell:
		"""
		( \
		mkdir -p stamps/cellranger && \
		mkdir -p {params.output_path} && \
		cd {params.output_path} && \
		cellranger count \
			--id={wildcards.sample} \
			--libraries={params.librarysheet_path}/{wildcards.sample}.csv \
			--feature-ref={params.features} \
			--transcriptome={params.reference} \
			{params.custom_flags} \
			--localcores={threads} && \
		touch {output} \
		) > {log} 2>&1
		"""


# Set rule targets
cellranger = [f"stamps/cellranger/{sample}.stamp" for sample in samples]