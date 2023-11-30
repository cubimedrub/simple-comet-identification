#! /usr/bin/env python
# std imports
import argparse
from pathlib import Path
from typing import List

# 3rd party imports
import pandas as pd

COMET_RESULT_CELL_SEPARATOR: str = "\t"
COMET_SKIP_HEADER_ROWS: int = 1

def get_cli() -> argparse.ArgumentParser:
    """Create the command line interface for the fdr_filtering script."""
    parser = argparse.ArgumentParser(
        description="Filter a csv file by FDR and log2FC"
    )
    parser.add_argument(
        "comet_psms",
        type=str,
        help="File to Comet PSMs (TSV or TXT)"
    )
    parser.add_argument(
        "--fdr",
        type=float,
        default=0.05,
        help="The FDR cutoff to filter by, default is 0.05"
    )
    parser.add_argument(
        "--decoy-prefix",
        type=str,
        default="DECOY_",
        help="Decoy prefix to filter by, default is DECOY_"
    )
    return parser


def read_comet_psms(comet_psms_file_path: Path) -> pd.DataFrame:
    """
    Read columns from list

    Parameters
    ----------
    comet_psms_file_path : Path
        Path to the comet PSMs file (TSV or TXT)

    Returns
    -------
    pd.DataFrame
        The PSMs as a dataframe
    """
    return pd.read_csv(
        comet_psms_file_path,
        sep = COMET_RESULT_CELL_SEPARATOR,
        header = COMET_SKIP_HEADER_ROWS
    )

def mark_decoys(psms: pd.DataFrame, decoy_prefix: str) -> pd.DataFrame:
    """
    Marks decoys in the PSMs dataframe by adding a column "is_decoy" with 1 for decoys and 0 for targets

    Parameters
    ----------
    psms : pd.DataFrame
        PSMs
    decoy_prefix : str
        Prefix for decoy

    Returns
    -------
    pd.DataFrame
        PSMs
    """
    protein_col_index = psms.columns.get_loc("protein")
    psms["is_decoy"] = psms.apply(lambda row: 0 if any([not prot.startswith(decoy_prefix) for prot in row[protein_col_index].split(",")]) else 1, axis=1)
    return psms

def calc_fdr(psms: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the FDR for the PSMs

    Parameters
    ----------
    psms : pd.DataFrame
        PSMs

    Returns
    -------
    pd.DataFrame
        PSMs with FDR column

    Raises
    ------
    ValueError
        If `is_decoy` column is not present in PSMs
    """
    if "is_decoy" not in psms.columns:
        raise ValueError("PSMs must be marked as decoys before calculating FDR")
    psms["fpn"] = psms["is_decoy"].cumsum()
    psms["fdr"] = psms["fpn"] / (psms.index.values + 1)
    psms.drop(columns=["fpn"], inplace=True)

    return psms


def remove_decoys(psms: pd.DataFrame) -> pd.DataFrame:
    """
    Removes decoys from the PSMs and removed the `is_decoy` column

    Parameters
    ----------
    psms : pd.DataFrame
        PSMs

    Returns
    -------
    pd.DataFrame
        PSMs without decoys

    Raises
    ------
    ValueError
        If `is_decoy` column is not present in PSMs
    """
    if "is_decoy" not in psms.columns:
        raise ValueError("PSMs must be marked as decoys before calculating FDR")
    psms = psms[psms["is_decoy"] == 0]
    psms.drop(columns=["is_decoy"], inplace=True)
    return psms

def filter_by_fdr(psms: pd.DataFrame, fdr_threshold: float) -> pd.DataFrame:
    """
    Filters PSMs by FDR

    Parameters
    ----------
    psms : pd.DataFrame
        PSMs
    fdr_threshold : float
        FDR threshold to filter by
    Returns
    -------
    pd.DataFrame
        Filtered PSMs
    """

    return psms[psms["fdr"] <= fdr_threshold]


def overwrite(comet_tsv_path: Path, psms: pd.DataFrame):
    """
    Overwrites the comet tsv file with the new PSMs,
    keeping the revision line on top. 

    Parameters
    ----------
    comet_tsv_path : Path
        _description_
    psms : pd.DataFrame
        _description_
    """
    content_before_header: List[str] = []
    with comet_tsv_path.open("r") as psm_file:
        # Read comment/revision lines
        for _ in range(COMET_SKIP_HEADER_ROWS):
            content_before_header.append(next(psm_file))

    with comet_tsv_path.open("w") as psm_file:
        # Write comment/revision lines
        for line in content_before_header:
            psm_file.write(line)
        # Write the rest
        psms.to_csv(
            psm_file,
            sep=COMET_RESULT_CELL_SEPARATOR,
            index=False,
        )

def main():
    cli = get_cli()
    args = cli.parse_args()

    psms = read_comet_psms(Path(args.comet_psms))
    psms.sort_values("xcorr", ascending=False, inplace=True, ignore_index=True)
    psms = mark_decoys(psms, args.decoy_prefix)
    psms = calc_fdr(psms)
    psms = filter_by_fdr(psms, args.fdr)
    psms = remove_decoys(psms)
    overwrite(Path(args.comet_psms), psms)


if __name__ == "__main__":
    main()