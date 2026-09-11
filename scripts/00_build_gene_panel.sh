#!/usr/bin/env bash
# Construit le BED du panel de gènes cardiomyopathie/arythmie en GRCh37,
# via l'API REST Ensembl (assembly GRCh37) -- pas de coordonnées codées en dur
# non vérifiées.
set -euo pipefail

GENES=(TTN MYH7 LMNA DSP PKP2 RBM20 DES)
OUT="$(dirname "$0")/../data/gene_panel.bed"

: > "$OUT"
for gene in "${GENES[@]}"; do
  json=$(curl -s "https://grch37.rest.ensembl.org/lookup/symbol/homo_sapiens/${gene}?content-type=application/json")
  chrom=$(echo "$json" | python3 -c "import sys,json; print(json.load(sys.stdin)['seq_region_name'])")
  start=$(echo "$json" | python3 -c "import sys,json; print(json.load(sys.stdin)['start'])")
  end=$(echo "$json"   | python3 -c "import sys,json; print(json.load(sys.stdin)['end'])")
  # BED est 0-based demi-ouvert : start Ensembl (1-based) - 1
  echo -e "${chrom}\t$((start - 1))\t${end}\t${gene}" >> "$OUT"
done

sort -k1,1 -k2,2n "$OUT" -o "$OUT"
echo "Panel écrit dans $OUT ($(wc -l < "$OUT") gènes)"
