# Simple Nextflow workflow for Comet identification

Identifies mzML using Comet, returns PSMs in TSV format, calculates the FDR and filters them.


## Requirements
* [Comet](https://github.com/UWPR/Comet/releases)
* [Nextflow](https://www.nextflow.io/)
* Conda | Micromamba (see install section for more info)

## Install
```
conda env create -f environment.yml
conda activate comet_ident
```

Hint: Will only install Python 3 and Pandas from the requirements file for now. If those dependencies are installed on your system anyway, you may skip this.

## Usage
1. Prepare your mzMLs e.g. by converting RAW-files etc, and put them in a folder
2. Prepare the comet settings
    * `comet -p` will create a well documented default parameter file `comet.params.new`
    * Adjust them to your needs
    * The workflow only need Comet's txt-output, and makes sure it is active. Everything else can be disabled.
3. Run the workflow
    ```
    nextflow run comet_ident.nf <ARGUMENTS>
    ```
    

| Argument | Description |
| --- | --- |
| --comet-bin | Path to comet binary |
| --comet-params | Path to comet parameter file |
| --fasta | Path to target/decoy FASTA |
| --mzml-dir | Path to mzML dir |
| --results-dir | Path to results dir |
| --fdr-threshold | Threshold for FDR |
