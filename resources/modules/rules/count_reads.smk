##########################################################################################
# Snakemake rule for count_reads
# Author: Redwan Farooq
# Requires outputs from resources/rules/fastqc.smk
##########################################################################################

scripts_dir = config.get("scripts_dir", "resources/scripts")

# Define rule
rule count_reads:
	input: os.path.abspath("stamps/multiqc/multiqc.stamp")
	output: os.path.abspath("stamps/count_reads/count_reads.stamp")
	log: os.path.abspath("logs/count_reads/count_reads.log")
	threads: 1
	params:
		script_path = scripts_dir if os.path.isabs(scripts_dir) else os.path.join(workflow.basedir, scripts_dir),
		multiqc_dir = os.path.join(config["output_dir"], "qc/multiqc"),
		output_path = os.path.join(config["output_dir"], "qc/count_reads")
	# conda: "quarto"
	envmodules: "python-cbrg"
	message: "Calculating total read counts per sample/library"
	script: "{params.script_path}/count_reads.py"


# Set rule targets
count_reads = ["stamps/count_reads/count_reads.stamp"]