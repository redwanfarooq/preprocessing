"""
Functions for use in Snakemake rule definitions.
"""

import os
import glob
import xml.etree.ElementTree as ET


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
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``info``: dictionary of sample/library info.\n
        ``run_dir``: raw sequencing runs directory.

    Returns:
        Path to run folder.
    """
    libs = parse_info(info)["libs"]
    return os.path.join(run_dir, libs[wildcards.lib]["run"])


def get_lib_type(wildcards, info: dict) -> str:
    """
    Get library type.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``info``: dictionary of sample/library info.

    Returns:
        Library type.
    """
    libs = parse_info(info)["libs"]
    return libs[wildcards.lib]["lib_type"]


def get_bases_mask_flag(
    wildcards, bases_mask: dict | None, info: dict, run_dir: str
) -> str:
    """
    Get bases mask flag for bcl2fastq.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``bases_mask``: dictionary of bases mask strings with library types as keys.\n
        ``info``: dictionary of sample/library info.\n
        ``run_dir``: raw sequencing runs directory.

    Returns:
        String containing bases mask flag to be inserted into shell command.
    """
    libs = parse_info(info)["libs"]
    n_reads = sum(
        1
        for _ in ET.parse(
            os.path.join(run_dir, libs[wildcards.lib]["run"], "RunInfo.xml")
        )
        .getroot()
        .iter("Read")
    )
    mask = (
        bases_mask.get(libs[wildcards.lib]["lib_type"], None).split(",")
        if bases_mask is not None
        else None
    )
    if mask is not None:
        if len(mask) == 4 and n_reads == 3:
            mask.pop(2)
    return f"--use-bases-mask={','.join(mask)}" if mask is not None else ""


def get_read_trim_flags(wildcards, read_trim: dict | None, info: dict) -> str:
    """
    Get read trimming flags for seqtk trimfq.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``read_trim``: dictionary of read trimming options with library types as keys.\n
        ``info``: dictionary of sample/library info.\n

    Returns:
        Dictionary of read trimming flags to be inserted into shell command.
    """
    libs = parse_info(info)["libs"]
    read_trim = (
        read_trim.get(libs[wildcards.lib]["lib_type"], {})
        if read_trim is not None
        else {}
    )
    flags = {f"R{x}": "-L 150" for x in range(1, 4)}
    for read in read_trim.keys():
        flags[read] = [f"-{k} {v}" for k, v in read_trim[read].items()].join(" ")
    return flags


def get_count_inputs(
    wildcards, input_type: str, lib_types: set[str], info: dict
) -> list[str]:
    """
    Get path to bcl2fastq or trimfastq stamp files for specific library type(s).

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``input_type``: string specifying input type ('bcl' or 'fastq').\n
        ``lib_types``: set of library types (use * to match any library type).\n
        ``info``: dictionary of sample/library info.

    Returns:
        List of paths to bcl2fastq or trimfastq stamp files, depending on input type.
    """
    match input_type.lower():
        case "bcl":
            rule = "bcl2fastq"
        case "fastq":
            rule = "trimfastq"
        case _:
            raise ValueError(f"Invalid input type: {input_type}")
    libs = parse_info(info)["libs"]
    inputs = [
        f"stamps/{rule}/{lib}.stamp"
        for lib in info[wildcards.sample].keys()
        if any(x in {libs[lib]["lib_type"], "*"} for x in lib_types)
    ]
    return [os.path.abspath(path) for path in inputs]


def get_count_fastqs(
    wildcards, lib_types: set[str], read: str, info: dict, output_dir: str
) -> str:
    """
    Get input FASTQ string for barcounter/CITE-seq-Count.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``lib_types``: set of library types (use * to match any library type).\n
        ``read``: string specifying read number ('R1' or 'R2').\n
        ``info``: dictionary of sample/library info.\n
        ``output_dir``: pipeline output directory.

    Returns:
        Comma-separated string of paths to input FASTQs.
    """
    libs = parse_info(info)["libs"]
    fastqs = [
        fastq
        for lib in info[wildcards.sample].keys()
        if any(x in {libs[lib]["lib_type"], "*"} for x in lib_types)
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


def get_fastqc_inputs(wildcards, input_type: str) -> str:
    """
    Get path to bcl2fastq or trimfastq stamp file.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``input_type``: string specifying input type ('bcl' or 'fastq').\n

    Returns:
        Path to bcl2fastq or trimfastq stamp file, depending on input type.
    """
    match input_type.lower():
        case "bcl":
            path = "stamps/bcl2fastq/{lib}.stamp"
        case "fastq":
            path = "stamps/trimfastq/{lib}.stamp"
        case _:
            raise ValueError(f"Invalid input type: {input_type}")
    return os.path.abspath(path.format(lib=wildcards.lib))


def get_fastqc_fastqs(wildcards, info: dict, output_dir: str) -> str:
    """
    Get input FASTQ string for fastqc.

    Arguments:
        ``wildcards``: Snakemake ``wildcards`` object.\n
        ``info``: dictionary of sample/library info.\n
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
