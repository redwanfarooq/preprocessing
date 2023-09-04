##########################################################################################
# Snakemake rule for STARsolo
# Author: Redwan Farooq
# Requires functions from resources/scripts/rule.py
# Requires outputs from resources/rules/bcl2fastq.smk
##########################################################################################


# Define rule
rule starsolo:
	input: lambda wildcards: get_count_inputs(wildcards, lib_types={"GEX"}, info=info)
	output: os.path.abspath("stamps/starsolo/{sample}.stamp")
	log: os.path.abspath("logs/starsolo/{sample}.log")
	threads: 1
	params: 
		R1_fastqs = lambda wildcards: get_count_fastqs(wildcards, lib_types={"GEX"}, read="R1", info=info, output_dir=config["output_dir"]),
		R2_fastqs = lambda wildcards: get_count_fastqs(wildcards, lib_types={"GEX"}, read="R2", info=info, output_dir=config["output_dir"]),
		reference = config["starsolo_reference"],
		whitelist = config["barcode_whitelist"],
		custom_flags = config.get("starsolo_args", ""),
		output_path = os.path.join(config["output_dir"], "starsolo")
	conda: "starsolo"
	envmodules:
		"STAR/2.7.8a",
		"samtools/1.17"
	message: "Making GEX count matrix for {wildcards.sample}"
	shell:
		"""
		( \
		mkdir -p stamps/starsolo && \
		mkdir -p {params.output_path}/{wildcards.sample} && \
		STAR \
			--readFilesIn {params.R2_fastqs} {params.R1_fastqs} \
			--genomeDir {params.reference} \
			--soloCBwhitelist <(zcat {params.whitelist}) \
			--outFileNamePrefix {params.output_path}/{wildcards.sample}/ \
			{params.custom_flags} \
			--runThreadN {threads} && \
		find {params.output_path}/{wildcards.sample} -type f -name '*.bam' -exec samtools index -@ {threads} {{}} + && \
		find {params.output_path}/{wildcards.sample}/Solo.out -type f -exec gzip {{}} + && \
		touch {output} \
		) > {log} 2>&1
		"""


# Set rule targets
starsolo = [f"stamps/starsolo/{sample}.stamp" for sample in samples]