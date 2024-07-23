##########################################################################################
# Snakemake rule for BarCounter
# Author: Redwan Farooq
# Requires functions from resources/scripts/rule.py
# Requires outputs from resources/rules/bcl2fastq.smk
##########################################################################################

# Define rules
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

rule barcode_translate:
	input: os.path.abspath("stamps/barcounter/{sample}.stamp")
	output: os.path.abspath("stamps/barcode_translate/{sample}.stamp")
	log: os.path.abspath("logs/barcode_translate/{sample}.log")
	threads: 1
	params:
		barcounter_csv = os.path.join(config["output_dir"], "barcounter", "{sample}", "{sample}_Tag_Counts.csv"),
		reference = config.get("barcode_translate", None)
	message: "Translating ADT and HTO barcodes for {wildcards.sample}"
	run:
		import csv
		import shutil
		from tempfile import NamedTemporaryFile
		from loguru import logger
		logger.remove(0)
		logfile = logger.add(sink=log[0], level="INFO", mode="w")

		with logger.catch(reraise=True):
			shell("mkdir -p stamps/barcode_translate")
			
			lookup = {}
			logger.info("Loading reference file: {}", params.reference)
			with open(params.reference, "r", newline="") as infile:
				reader = csv.reader(infile, delimiter="\t")
				for row in reader:
					lookup[row[0]] = row[1]

			tempfile = NamedTemporaryFile(newline="")
			logger.info("Loading barcounter CSV file: {}", params.barcounter_csv)
			with open(params.barcounter_csv, "r", newline="") as infile, tempfile:
				reader = csv.reader(csvfile, delimiter=",")
				writer = csv.writer(tempfile, delimiter=",")
				header = next(reader)
				writer.writerow(header)
				for row in reader:
					row[0] = lookup[row[0]]
					writer.writerow(row)
			shutil.move(tempfile.name, params.barcounter_csv)
			tempfile.close()
			logger.success("Barcode translation complete")

			shell("touch {output}")

		logger.remove(logfile)

# Set rule targets
barcounter = [f"stamps/barcounter/{sample}.stamp" for sample in samples]
if config["barcode_translate"]:
	barcounter.extend([f"stamps/barcode_translate/{sample}.stamp" for sample in samples])