#!/bin/env python


"""
Generates info YAML for use with preprocessing pipeline.
Requires:
- Metadata CSV file with the following fields:
    run: run folder name
    lib_type: library type
    donor: donor ID
    hash: hash ID
"""


# ==============================
# MODULES
# ==============================
import os
import yaml
import docopt
import pandas as pd
from id import sample_id, lib_id


# ==============================
# COMMAND LINE OPTIONS
# ==============================
# Define options
DOC = """
Generate info YAML for use with preprocessing pipeline

Usage:
  generate_info_yaml.py --md=<md> --outdir=<outdir> [options]

Arguments:
  -m --md=<md>              Metadata CSV file (required)
  -o --outdir=<outdir>      Output directory (required)

Options:
  -h --help                 Show this screen
"""


# ==============================
# FUNCTIONS
# ==============================
def _main(opt: dict) -> None:
    # Read input CSV and check fields are valid
    md = pd.read_csv(opt["--md"], header=0)
    assert set(md.columns).issuperset(
        {"run", "lib_type", "donor", "hash"}
    ), "Invalid metadata CSV file."

    # Add unique library ID and unique sample ID
    md = md.assign(
        lib_id=lambda x: lib_id(x.lib_type.tolist(), x.run.tolist()),
        sample_id=lambda x: sample_id(x.donor.tolist(), x.hash.tolist()),
    )

    # Generate info YAML
    generate_info_yaml(
        df=md[["sample_id", "lib_id", "lib_type", "run"]],
        filename=os.path.join(opt["--outdir"], "info.yaml"),
    )


def generate_info_yaml(df: pd.DataFrame, filename: str | None = None) -> dict:
    """
    Generate info YAML.

    Arguments:
        ``df``: DataFrame containing run metadata.\n
        ``filename``: Output file path or ``None``.

    Returns:
        Writes formatted YAML string to ``filename`` (if provided) and returns dictionary containing YAML data.
    """
    out = {
        sample_id: libs.loc[sample_id].to_dict("index")
        for sample_id, libs in df.set_index(["sample_id", "lib_id"]).groupby(
            "sample_id"
        )
    }

    if filename is not None:
        with open(file=filename, mode="w", encoding="UTF-8") as file:
            yaml.dump(data=out, stream=file)

    return out


# ==============================
# SCRIPT
# ==============================
if __name__ == "__main__":
    _main(opt=docopt.docopt(DOC))
