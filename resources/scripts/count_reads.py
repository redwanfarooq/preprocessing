"""
Get read counts per library type/sample from MultiQC summary for FASTQC.

Run from Snakemake rule with the following params:
- multiqc_dir: Path to MultiQC output directory
- output_path: Path to output directory
"""

import os
import sys
import pandas as pd


with open(file=snakemake.log[0], mode="w", encoding="UTF-8") as log:
    sys.stdout = sys.stderr = log

    os.makedirs(snakemake.params["output_path"], exist_ok=True)
    if os.path.isfile(
        os.path.join(snakemake.params["multiqc_dir"], "multiqc_data/multiqc_fastqc.txt")
    ):
        os.system(
            f"cp {os.path.join(snakemake.params['multiqc_dir'], 'multiqc_data/multiqc_fastqc.txt')} {os.path.join(snakemake.params['output_path'])}"
        )
    elif os.path.isfile(
        os.path.join(snakemake.params["multiqc_dir"], "multiqc_data.zip")
    ):
        os.system(
            f"unzip -p {os.path.join(snakemake.params['multiqc_dir'], 'multiqc_data.zip')} multiqc_fastqc.txt > {os.path.join(snakemake.params['output_path'], 'multiqc_fastqc.txt')}"
        )
    else:
        raise FileNotFoundError

    df = pd.read_table(
        os.path.join(snakemake.params["output_path"], "multiqc_fastqc.txt"),
        delimiter="\t",
    ).rename(
        columns={
            "Sample": "directory",
            "Filename": "filename",
            "Total Sequences": "read_count",
        }
    )
    df = (
        df[["directory", "filename", "read_count"]][df.filename.str.contains("_R1_")]
        .assign(
            lib_type=lambda x: [y.split("-")[0] for y in x.directory],
            sample=lambda x: [y.split("_")[0] for y in x.filename],
            read_count=lambda x: [int(y) for y in x.read_count],
        )
        .groupby(["lib_type", "sample"])
        .agg({"read_count": "sum"})
        .reset_index()
        .pivot(index="sample", columns="lib_type", values="read_count")
    )
    df.to_csv(
        os.path.join(snakemake.params["output_path"], "read_counts.tsv"),
        sep="\t",
        header=True,
        index=True,
    )

    os.system(
        f"rm {os.path.join(snakemake.params['output_path'], 'multiqc_fastqc.txt')}"
    )

    os.makedirs(os.path.dirname(snakemake.output[0]), exist_ok=True)
    os.system(f"touch {snakemake.output[0]}")
