"""
Functions for use in Snakemake rule definitions.
"""

import os
import glob


def parse_info(info: dict) -> dict:
    """
    Parse dictionary of sample/library info.

    Arguments:
        ``info``: dictionary of sample/library info.

    Returns:
        Dictionary of parsed sample/library info.
    """
    samples = list(info.keys())

    libs = {}
    for sample in samples:
        libs.update(info[sample])

    return {"samples": samples, "libs": libs}


def get_run_path(wildcards, info: dict, run_dir: str) -> str:
    """
    Get path to run folder.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.
        ``info``: dictionary of sample/library info.
        ``run_dir``: raw sequencing runs directory.

    Returns:
        Path to run folder.
    """
    libs = parse_info(info)["libs"]
    return os.path.join(run_dir, libs[wildcards.lib]["run"])


def get_bases_mask_flag(wildcards, bases_mask: dict | None, info: dict) -> str:
    """
    Get bases mask flag for bcl2fastq.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.
        ``bases_mask``: dictionary of bases mask strings with library types as keys.
        ``info``: dictionary of sample/library info.

    Returns:
        String containing bases mask flag to be inserted into shell command.
    """
    libs = parse_info(info)["libs"]
    mask = (
        bases_mask.get(libs[wildcards.lib]["lib_type"], None)
        if bases_mask is not None
        else None
    )
    return f"--use-bases-mask={mask}" if mask is not None else ""


def get_count_inputs(wildcards, lib_types: set[str], info: dict) -> list[str]:
    """
    Get path to bcl2fastq stamp files.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.
        ``lib_types``: set of library types.
        ``info``: dictionary of sample/library info.

    Returns:
        List of paths to bcl2fastq stamp files.
    """
    libs = parse_info(info)["libs"]
    inputs = [
        f"stamps/bcl2fastq/{lib}.stamp"
        for lib in info[wildcards.sample].keys()
        if any(libs[lib]["lib_type"] == x for x in lib_types)
    ]
    return [os.path.abspath(path) for path in inputs]


def get_count_fastqs(
    wildcards, lib_types: set[str], read: str, info: dict, output_dir: str
) -> str:
    """
    Get input FASTQ string for barcounter/CITE-seq-Count.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.
        ``lib_types``: set of library types.
        ``read``: string specifying read number ('R1' or 'R2').
        ``info``: dictionary of sample/library info.
        ``output_dir``: pipeline output directory.

    Returns:
        Comma-separated string of paths to input FASTQs.
    """
    libs = parse_info(info)["libs"]
    fastqs = [
        fastq
        for lib in info[wildcards.sample].keys()
        if any(libs[lib]["lib_type"] == x for x in lib_types)
        for fastq in glob.glob(
            os.path.join(
                output_dir,
                f"fastqs/{lib}/**/{wildcards.sample}_*_{read}_001.fastq.gz",
            ),
            recursive=True,
        )
    ]
    fastqs.sort()
    return ",".join(fastqs)


def get_fastqc_fastqs(wildcards, info: dict, output_dir: str) -> str:
    """
    Get input FASTQ string for fastqc.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.
        ``info``: dictionary of sample/library info.
        ``output_dir``: pipeline output directory.

    Returns:
        Whitespace-separated string of paths to input FASTQs.
    """
    fastqs = [
        fastq
        for sample in info.keys()
        if wildcards.lib in info[sample].keys()
        for fastq in glob.glob(
            os.path.join(
                output_dir,
                f"fastqs/{wildcards.lib}/**/{sample}_*.fastq.gz",
            ),
            recursive=True,
        )
    ]
    fastqs.sort()
    return " ".join(fastqs)
