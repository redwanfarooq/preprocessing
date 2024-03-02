##########################################################################################
# Snakemake rule for mapping QC
# Author: Redwan Farooq
# Requires functions from resources/scripts/rule.py
# Requires outputs from resources/rules/starsolo.smk
# Requires outputs from resources/rules/barcounter.smk
# Requires outputs from resources/rules/chromap.smk
# Requires outputs from resources/rules/macs2.smk
##########################################################################################


scripts_dir = config.get("scripts_dir", "resources/scripts")

# Define rule
rule mapping_qc:
	input: expand("stamps/{rule}/{sample}.stamp", rule=[x for x in rules if x in {"starsolo", "barcounter", "chromap", "macs2"}], sample=samples.keys())
	output: os.path.abspath("stamps/mapping_qc/mapping_qc.stamp")
	log: os.path.abspath("logs/mapping_qc/mapping_qc.log")
	threads: 1
	params:
		script_path = scripts_dir if os.path.isabs(scripts_dir) else os.path.join(workflow.basedir, scripts_dir),
		output_dir = config["output_dir"],
		samples = ",".join(samples.keys()),
		custom_flags = config.get("mapping_qc_args", ""),
		output_path = os.path.join(config["output_dir"], "qc/mapping_qc")
	conda: "quarto"
	envmodules: "python-cbrg"
	message: "Generating mapping QC report"
	shell:
		"""
		( \
		mkdir -p stamps/mapping_qc && \
		mkdir -p {params.output_path} && \
		quarto render \
			{params.script_path}/mapping_qc.qmd \
			--output-dir {params.output_path} \
			-P output_dir:{params.output_dir} \
			-P samples:{params.samples} && \
		touch {output} \
		) > {log} 2>&1
		"""


# Set rule targets
mapping_qc = ["stamps/mapping_qc/mapping_qc.stamp"]