##########################################################################################
# Snakemake rule for BarCounter
# Author: Redwan Farooq
# Requires functions from resources/scripts/rule.py
# Requires outputs from resources/rules/bcl2fastq.smk
##########################################################################################

# Define rule
rule barcounter:
	input: lambda wildcards: get_count_inputs(wildcards, input_type = config["input_type"], lib_types={"ADT", "HTO"}, info=info)
	output: os.path.abspath("stamps/barcounter/{sample}.stamp")
	log: os.path.abspath("logs/barcounter/{sample}.log")
	threads: 1
	params:
		R1_fastqs = lambda wildcards: get_count_fastqs(wildcards, lib_types={"ADT", "HTO"}, read="R1", info=info, output_dir=config["output_dir"]),
		R2_fastqs = lambda wildcards: get_count_fastqs(wildcards, lib_types={"ADT", "HTO"}, read="R2", info=info, output_dir=config["output_dir"]),
		tags = os.path.abspath(os.path.join(config.get("metadata_dir", "metadata"), config["tags"])),
		whitelist = config["gex_barcode_whitelist"],
		output_path = os.path.join(config["output_dir"], "barcounter") # DO NOT CHANGE - downstream rules will search for mapping statistics in this directory
	envmodules: "barcounter"
	message: "Making ADT and HTO count matrix for {wildcards.sample}"
	shell:
		"""
		( \
		mkdir -p stamps/barcounter && \
		mkdir -p {params.output_path}/{wildcards.sample} && \
		barcounter \
			-w {params.whitelist} \
			-t {params.tags} \
			-1 {params.R1_fastqs} \
			-2 {params.R2_fastqs} \
			-o {params.output_path}/{wildcards.sample} && \
		touch {output} \
		) > {log} 2>&1
		"""
		

# Set rule targets
barcounter = [f"stamps/barcounter/{sample}.stamp" for sample in samples]