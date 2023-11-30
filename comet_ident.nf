nextflow.enable.dsl = 2

// required arguments
params.cometBin = ""
params.cometParams = ""
params.fasta = ""
params.mzmlDir = ""
params.resultsDir = ""
params.fdrThreshold = 0.05

// Makes sure the txt output is active
process adjust_comet_params {
    input:
    path comet_param_file

    output:
    path "*.params.adjusted"

    """
    # adjust comet params
}

process search {
    maxForks 1

    input:
    path comet_param_file
    path fasta_file
    path mzml

    output:
    path "*.tsv"
    """

    ${params.cometBin} -P${comet_param_file} -D${fasta_file} ${mzml}

    for file in *.txt; do
        mv -- "\$file" "\$(basename \$file .txt).psms.tsv"
    done
    """
}


process filter {
    publishDir "${params.resultsDir}/psms", mode: 'copy'

    input: 
    path "*"

    output:
    path "*.tsv", includeInputs: true
    
    """
    psm_file=(*.tsv)
    fdr_filter.py \${psm_file} --fdr ${params.fdrThreshold}
    """
}


workflow() {
    mzmls = Channel.fromPath(params.mzmlDir + "/*.{mzML,mzml}")
    comet_param_file = Channel.fromPath(params.cometParams)
    fasta_file = Channel.fromPath(params.fasta)

    psms_files = search(comet_param_file, fasta_file, mzmls)
    filter(psms_files)
}