#!/bin/env python


"""
Runs preprocessing pipeline.
"""


# ==============================
# MODULES
# ==============================
import os
import yaml
import docopt
from loguru import logger


# ==============================
# COMMAND LINE OPTIONS
# ==============================
# Define options
DOC = """
Run preprocessing pipeline

Usage:
  run.py [options]

Options:
  -h --help                 Show this screen
  -u --update               Update module scripts using rule specifications in 'config/modules.yaml' (will not run pipeline)
"""


# ==============================
# FUNCTIONS
# ==============================
@logger.catch(reraise=True)
def _main(opt: dict) -> None:
    # Get and execute shell command
    if not opt["--update"]:
        logger.info("Starting pipeline using module {}", MODULE)
    cmd = _get_cmd(update=opt["--update"])
    os.system(" && ".join(cmd))


def _cmd(*args):
    cmd = [" ".join(args)]
    return cmd


def _get_index_kit_flags(dual: list[str] | None, single: list[str] | None) -> str:
    dual_flag = f"--dual={','.join(dual)}" if dual is not None else ""
    single_flag = f"--single={','.join(single)}" if single is not None else ""
    return f"{dual_flag} {single_flag}"


def _get_reverse_complement_flag(reverse_complement: bool) -> str:
    return "--reversecomplement" if reverse_complement else ""


def _get_cmd(update: bool = False) -> list[str]:
    if update:
        cmd = _cmd(
            f"{SCRIPTS_DIR}/generate_modules.py",
            "--modules=config/modules.yaml",
            "--template=resources/templates/module.template",
            "--outdir=resources/modules",
        )
    else:
        cmd = _cmd(
            f"{SCRIPTS_DIR}/generate_wrapper.py",
            f"--module={MODULE}",
            "--template=resources/templates/wrapper.template",
        )
        if "bcl2fastq" in RULES:
            cmd += _cmd(
                f"mkdir -p {os.path.join(METADATA_DIR, 'bcl2fastq')} &&",
                f"{SCRIPTS_DIR}/generate_bcl2fastq_csv.py",
                f"--md={RUNS_CSV}",
                f"--outdir={os.path.join(METADATA_DIR, 'bcl2fastq')}",
                _get_index_kit_flags(
                    dual=DUAL,
                    single=SINGLE,
                ),
                _get_reverse_complement_flag(reverse_complement=REVERSE_COMPLEMENT),
            )
        if "cellranger_arc" in RULES:
            cmd += _cmd(
                f"mkdir -p {os.path.join(METADATA_DIR, 'cellranger_arc')} &&",
                f"{SCRIPTS_DIR}/generate_cellranger_arc_csv.py",
                f"--md={RUNS_CSV}",
                f"--fastqdir={os.path.join(OUTPUT_DIR, 'fastqs')}",
                f"--outdir={os.path.join(METADATA_DIR, 'cellranger_arc')}",
            )
        if "cellranger" in RULES:
            cmd += _cmd(
                f"mkdir -p {os.path.join(METADATA_DIR, 'cellranger')} &&",
                f"{SCRIPTS_DIR}/generate_cellranger_csv.py",
                f"--md={RUNS_CSV}",
                f"--fastqdir={os.path.join(OUTPUT_DIR, 'fastqs')}",
                f"--outdir={os.path.join(METADATA_DIR, 'cellranger')}",
            )
        cmd += _cmd(
            f"{SCRIPTS_DIR}/generate_info_yaml.py",
            f"--md={RUNS_CSV}",
            f"--outdir={METADATA_DIR}",
        )
        cmd += _cmd("snakemake --profile=profile")
    return cmd


# ==============================
# SCRIPT
# ==============================
with open(file="config/config.yaml", mode="r", encoding="UTF-8") as file:
    config = yaml.load(stream=file, Loader=yaml.SafeLoader)
    SCRIPTS_DIR = config.get("scripts_dir", "resources/scripts")
    METADATA_DIR = config.get("metadata_dir", "metadata")
    DUAL = config.get("dual_index_kits", None)
    SINGLE = config.get("single_index_kits", None)
    REVERSE_COMPLEMENT = config.get("reverse_complement", False)
    try:
        RUNS_CSV = os.path.join(METADATA_DIR, config["runs"])
        OUTPUT_DIR = config["output_dir"]
        MODULE = config["module"]
    except KeyError as err:
        logger.exception("{} not specified in {}", err, file.name)
        raise KeyError from err


with open(file="config/modules.yaml", mode="r", encoding="UTF-8") as file:
    try:
        RULES = yaml.load(stream=file, Loader=yaml.SafeLoader)[MODULE]
    except KeyError as err:
        logger.exception("Module {} not specified in {}", err, file.name)
        raise KeyError from err

if __name__ == "__main__":
    _main(opt=docopt.docopt(DOC))
