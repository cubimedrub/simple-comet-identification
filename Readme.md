# Simple Nextflow workflow for Comet identification

Identifies mzML using Comet, returns PSMs in TSV format, calculates the FDR and filters them.


## Requirements
* [Nextflow](https://www.nextflow.io/)
* Conda | Micromamba (see install section for more info, only needed for native install)
* Docker (only needed if you want to use the Docker images)

## Install

### Native
```
curl -L -o ./bin/comet https://github.com/UWPR/Comet/releases/download/v2023.01.2/comet.linux.exe
chmod +x ./bin/comet
conda env create -f environment.yml
conda activate comet_ident
```

### Docker
1. `docker build -t cubimed/comet-ident-conda:latest -f docker/conda/Dockerfile .`
    * Bundles some Python dependencies for FDR-script
2. `docker build -t cubimed/comet-ident-comet:latest -f docker/comet/Dockerfile .`
    * Makes Comet search engine available

## Usage
1. Prepare your mzMLs e.g. by converting RAW-files etc, and put them in a folder
2. Prepare the comet settings
    * Native
        * `bin/comet -p` will create a well documented default parameter file `comet.params.new`
        * Adjust them to your needs
        * The workflow only need Comet's txt-output, and makes sure it is active. Everything else can be disabled.
    * Docker
        `docker run --rm -it cubimed/comet-ident-comet:latest bash -c "comet -p && cat comet.params.new" > comet.params`
3. Run the workflow
    * Nativ
        ```
        nextflow run comet_ident.nf <ARGUMENTS>
        ```
    * Docker
        ```
        nextflow run -profile docker comet_ident.nf <ARGUMENTS>
        ```
        On Apple Silicon (M1, M2, ...) add `env DOCKER_DEFAULT_PLATFORM=linux/amd64` before `nextflow` to prevent the Docker engine from throwing a warning on about miss matching Container and Host architecture which stops Nextflow execution.


| Argument | Description |
| --- | --- |
| --comet-bin | Path to comet binary |
| --comet-params | Path to comet parameter file |
| --fasta | Path to target/decoy FASTA |
| --mzml-dir | Path to mzML dir |
| --results-dir | Path to results dir |
| --fdr-threshold | Threshold for FDR |
| --keep-decoys | If not 0, decoys will be removed from filtered PSMs, default 0 |
