#!/usr/bin/env bash
# Filtre le callset SV public (1000 Genomes phase 3, GRCh37) sur le panel de
# gènes cardiomyopathie/arythmie. Outils exécutés en conteneur (Docker),
# mêmes images que honeybee-gwas-pipeline pour la cohérence.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA="$ROOT/data"
RESULTS="$ROOT/results"
mkdir -p "$RESULTS"

BCFTOOLS_IMG="quay.io/biocontainers/bcftools:1.19--h8b25389_1"
BEDTOOLS_IMG="quay.io/biocontainers/bedtools:2.31.1--hf5e1c6e_2"

echo "== Statistiques du callset brut =="
docker run --rm -v "$DATA:/data" "$BCFTOOLS_IMG" \
  bcftools stats /data/raw/sv_calls.vcf.gz | grep "^SN"

echo "== Filtrage sur le panel de gènes (bedtools intersect) =="
docker run --rm -v "$DATA:/data" -v "$RESULTS:/results" "$BEDTOOLS_IMG" \
  bash -c "bedtools intersect -a /data/raw/sv_calls.vcf.gz -b /data/gene_panel.bed -header > /results/sv_panel_filtered.vcf"

n=$(grep -vc "^#" "$RESULTS/sv_panel_filtered.vcf")
echo "SV chevauchant le panel : $n"
