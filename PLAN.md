# Plan — Détection et priorisation de CNV dans des gènes cardiaques (cohorte publique)

## Contexte

Ce projet reprend, sur données publiques, la méthodologie d'une analyse initialement menée
sur une cohorte clinique de 284 patients atteints de prolapsus valvulaire mitral (variant
calling Delly/Smoove, annotation AnnotSV). **Les données patient originales ne sont ni
publiées ni publiables** (secret médical, RGPD) — ce dépôt démontre la même chaîne
méthodologique sur une cohorte de référence en libre accès, et le README le précise
explicitement pour rester transparent sur cette substitution.

## Objectif scientifique

Identifier, annoter et prioriser des variants structuraux (CNV) dans un panel de gènes
associés aux cardiomyopathies et aux arythmies, à partir d'un jeu de variants structuraux
public.

## Données

| Source | Description | Accès |
|---|---|---|
| 1000 Genomes Project — Phase 3 SV | Callset de variants structuraux, population générale | `http://ftp.1000genomes.org/vol1/ftp/phase3/integrated_sv_map/` |
| gnomAD-SV v2.1 | Callset SV complémentaire, plus large | `https://gnomad.broadinstitute.org/downloads#v2-structural-variants` |

**Panel de gènes ciblés** (cardiomyopathies/arythmies, cohérent avec ClinGen) :
`TTN`, `MYH7`, `LMNA`, `DSP`, `PKP2`, `RBM20`, `DES`.

## Méthodologie

1. Récupération du callset SV public (VCF déjà calling — pas de calling de novo nécessaire)
2. Génération d'un BED du panel de gènes ciblés (coordonnées GRCh38 via Ensembl/UCSC)
3. Filtrage des CNV chevauchant le panel (`bedtools intersect`)
4. Annotation fonctionnelle avec **AnnotSV**
5. Priorisation (fréquence populationnelle, type de SV — délétion/duplication, chevauchement exonique)
6. Rapport de synthèse reproductible (R Markdown) : tableau des CNV priorisés + visualisation
   (`karyoploteR` ou snapshots IGV batch)

## Stack technique

`R / Bioconductor` · `bcftools` · `AnnotSV` · `bedtools` · VCF publics (1000G, gnomAD-SV)

## Structure de dépôt prévue

```
cnv-clinical-pipeline/
├── README.md                # inclut la mention explicite de la substitution de données
├── data/
│   └── gene_panel.bed       # panel de gènes ciblés, pas de VCF patient
├── scripts/
│   ├── 01_filter_region.sh
│   ├── 02_annotate_annotsv.sh
│   └── 03_report.Rmd
├── results/
└── LICENSE
```

## Livrables

- Pipeline reproductible de bout en bout, exécutable par un tiers sans accès aux données originales
- Rapport HTML/PDF des CNV priorisés dans le panel de gènes
- README expliquant la démarche et la raison du remplacement de la cohorte clinique

## Limites (à mentionner explicitement dans le rapport final)

La cohorte 1000 Genomes est une population générale, pas une cohorte de patients
cardiopathes : les CNV identifiés sont des **variants de population**, pas des variants
pathogènes confirmés cliniquement. Le projet démontre la méthode, pas un diagnostic.

## Écart au plan initial : AnnotSV → API VEP

L'étape 4 prévoyait AnnotSV pour l'annotation fonctionnelle. AnnotSV nécessite une base
d'annotation locale de plusieurs Go (téléchargement Docker ou `INSTALL_annotations.pl`),
disproportionné pour 14 variants filtrés et pour la portabilité du dépôt (un utilisateur
tiers n'aurait pas à télécharger plusieurs Go pour reproduire l'analyse). L'annotation
utilise donc l'**API REST Ensembl VEP** (GRCh37), qui fournit les mêmes catégories
d'information (gene symbol, conséquences, impact Sequence Ontology) sans base à installer.
Décision documentée ici et dans le README pour rester transparent sur l'écart au plan
d'origine.

## Statut

- [x] Choix du callset : 1000 Genomes Phase 3 seul (gnomAD-SV jugé non nécessaire, le
      callset 1000G suffisant pour la démonstration méthodologique)
- [x] Récupération des données (callset SV + panel de 7 gènes via API Ensembl GRCh37)
- [x] Implémentation du pipeline (filtrage bedtools → annotation VEP → priorisation)
- [x] Rapport final (`results/report.html`)
- [ ] Publication sur GitHub (dépôt public `cnv-clinical-pipeline`)
