#!/bin/env -S Rscript --vanilla


# ==============================
# PACKAGES
# ==============================
suppressPackageStartupMessages({
  library(docopt)
  library(future)
  library(dplyr)
  library(Signac)
  library(GenomicRanges)
  library(Matrix)
})


# ==============================
# COMMAND LINE OPTIONS
# ==============================
# Define options
DOC <- "
Generate peak count matrix

Usage:
  count_peaks.R --fragments=<fragments> --peaks=<peaks> [--threads=<threads>] [options]

Arguments:
  -f --fragments=<fragments>  Path to fragments TSV file (required)
  -p --peaks=<peaks>          Path to peaks BED file (required)
  -t --threads=<threads>      Number of threads [default: 1]

Options:
  -h --help                   Show this screen
"

# Parse options
opt <- docopt(DOC)
outdir <- file.path(dirname(opt[["--fragments"]]), "raw_feature_bc_matrix")
plan(multicore, workers = as.integer(opt[["--threads"]]))



# ==============================
# SCRIPT
# ==============================
message("Loading fragments...")
fragments <- CreateFragmentObject(opt[["--fragments"]])

message("Loading peaks...")
features <- read.table(
  file = opt[["--peaks"]],
  header = FALSE,
  sep = "\t"
) %>%
  select(1:3) %>%
  transmute(
    chr = V1,
    start = V2,
    stop = V3,
    id = sprintf("%s:%d-%d", chr, start, stop),
    symbol = sprintf("%s:%d-%d", chr, start, stop),
    type = "Peaks"
  ) %>%
  select(id, symbol, type, chr, start, stop)
peaks <- makeGRangesFromDataFrame(features)

message("Counting fragments in peaks per cell...")
peaks.mat <- FeatureMatrix(fragments, peaks)

if (!dir.exists(outdir)) dir.create(outdir, recursive = TRUE)

message("Saving features.tsv...")
write.table(
  features,
  file = file.path(outdir, "features.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  col.names = FALSE
)

message("Saving barcodes.tsv...")
write.table(
  data.frame(barcodes = colnames(peaks.mat)),
  file = file.path(outdir, "barcodes.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  col.names = FALSE
)

message("Saving matrix.mtx...")
writeMM(
  peaks.mat,
  file = file.path(outdir, "matrix.mtx")
) %>% invisible()

message("Done.")
