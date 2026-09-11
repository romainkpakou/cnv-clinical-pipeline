#!/usr/bin/env python3
"""
Annotation fonctionnelle des variants structuraux filtrés via l'API REST
Ensembl VEP (GRCh37), utilisée à la place d'AnnotSV local pour ce dépôt :
AnnotSV nécessite une base d'annotation de plusieurs Go (installation locale
ou conteneur lourd), disproportionnée pour 14 variants et pour la portabilité
du dépôt. VEP est l'outil de référence standard en génomique clinique et
fournit ici gene symbol, conséquence et impact (SO terms) par simple appel
API, sans base à installer.
"""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VCF_IN = ROOT / "results" / "sv_panel_filtered.vcf"
OUT = ROOT / "results" / "sv_panel_annotated.tsv"

VEP_BASE = "https://grch37.rest.ensembl.org/vep/human/region"

# Correspondance SVTYPE du VCF -> type d'allèle structurel accepté par VEP
SVTYPE_TO_VEP = {
    "DEL": "DEL",
    "DEL_ALU": "DEL",
    "DUP": "DUP",
    "CNV": "CNV",
    "INV": "INV",
    "ALU": "INS",
    "LINE1": "INS",
    "SVA": "INS",
}


def parse_info(info_field):
    d = {}
    for kv in info_field.split(";"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            d[k] = v
        else:
            d[kv] = True
    return d


def query_vep(chrom, start, end, allele):
    url = f"{VEP_BASE}/{chrom}:{start}-{end}/{allele}?content-type=application/json"
    with urllib.request.urlopen(url, timeout=20) as resp:
        return json.loads(resp.read())


def main():
    rows = []
    with open(VCF_IN) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            chrom, pos, vid, ref, alt, qual, filt, info = line.rstrip("\n").split("\t")[:8]
            info_d = parse_info(info)
            svtype_raw = info_d.get("SVTYPE", "")
            allele = SVTYPE_TO_VEP.get(svtype_raw)
            if allele is None:
                print(f"! type non géré, ignoré : {vid} (SVTYPE={svtype_raw})", file=sys.stderr)
                continue

            start = int(pos)
            end = int(info_d.get("END", pos))
            if end < start:
                end = start

            try:
                vep_result = query_vep(chrom, start, end, allele)
            except Exception as e:
                print(f"! échec VEP pour {vid}: {e}", file=sys.stderr)
                continue
            time.sleep(0.2)  # courtoisie envers l'API publique

            genes, consequences, impacts = set(), set(), set()
            for entry in vep_result:
                for tc in entry.get("transcript_consequences", []):
                    if tc.get("gene_symbol"):
                        genes.add(tc["gene_symbol"])
                    consequences.update(tc.get("consequence_terms", []))
                    impacts.add(tc.get("impact", ""))

            impact_rank = {"HIGH": 3, "MODERATE": 2, "LOW": 1, "MODIFIER": 0, "": -1}
            top_impact = max(impacts, key=lambda i: impact_rank.get(i, -1)) if impacts else "NA"

            rows.append({
                "id": vid,
                "chrom": chrom,
                "start": start,
                "end": end,
                "svtype": svtype_raw,
                "size_bp": end - start,
                "af_global": info_d.get("AF", "NA"),
                "genes": ";".join(sorted(genes)) or "NA",
                "consequences": ";".join(sorted(consequences)) or "NA",
                "top_impact": top_impact,
            })

    rows.sort(key=lambda r: (-{"HIGH": 3, "MODERATE": 2, "LOW": 1, "MODIFIER": 0, "NA": -1}.get(r["top_impact"], -1),
                              float(r["af_global"]) if r["af_global"] not in ("NA", ".") else 1.0))

    with open(OUT, "w") as out:
        header = ["id", "chrom", "start", "end", "svtype", "size_bp", "af_global", "genes", "consequences", "top_impact"]
        out.write("\t".join(header) + "\n")
        for r in rows:
            out.write("\t".join(str(r[h]) for h in header) + "\n")

    print(f"{len(rows)} variants annotés -> {OUT}")


if __name__ == "__main__":
    main()
