# Revue de Littérature Détaillée & Cartographie Épistémique — Projet RAMA / DualScale ($K3 \times T^2$)

> **Note de conformité arXiv :** Ce corpus bibliographique a été constitué via le skill officiel `literature-search-arxiv` (API arXiv, respect strict de la limite de fréquence). Veuillez consulter les conditions d'utilisation de l'API arXiv ([https://info.arxiv.org/help/api/index.html](https://info.arxiv.org/help/api/index.html)) ainsi que la licence propre à chaque prépublication sur sa page arXiv avant toute redistribution. Notice enregistrée dans `.licenses/literature_search_arxiv_LICENSE.txt`.

---

## 1. Architecture du Corpus et Base Vectorielle ChromaDB

Pour ancrer l'ensemble des propositions mathématiques, physiques et formelles du dépôt `SocrateAI-Scientific-RajMathRecovery` dans la littérature scientifique de référence, **24 articles fondateurs et récents (1998–2026)** ont été sélectionnés, téléchargés en texte intégral (PDF) dans `docs/literature/papers/`, vérifiés par `pypdf`, référencés dans `dualscale/refs/bib/dualscale.bib` et indexés dans une base vectorielle persistante **ChromaDB** (`data/chromadb/`).

| Indicateur ChromaDB | Valeur vérifiée |
|---|---|
| Répertoire persistant | `data/chromadb/` (distance cosinus HNSW, embeddings locaux ONNX MiniLM) |
| Collection littérature (`ramanujan_literature_v1`) | **24 articles arXiv**, **1 163 pages PDF extraites**, **2 829 segments indexés** (résumés + pages découpées 1 200 car. / recouvrement 200) |
| Collection artefacts du dépôt (`rama_repo_artifacts`) | **37 segments** (`dualscale.bib`, sections article v3.1, certificat `campaign_v2_report.json`, puis cette revue) |
| Manifeste structuré | `docs/literature/corpus_manifest.json` |
| Outil CLI d'interrogation RAG | `.venv/bin/python src/literature/chroma_kb.py query "<requête>" --n 5 --pillar <pilier>` |

Les 24 articles couvrent **cinq piliers thématiques** correspondant exactement aux modules Lean 4 et aux conjectures du programme DualScale :

1. **Pilier 1 (`pillar1_mock_eta`, 8 articles, 287 pages) :** Fonctions thêta moqueuses de Ramanujan, formes de Maass harmoniques, quotients $\eta$ de Dedekind, sommes de Rademacher et bornes de Sturm.
2. **Pilier 2 (`pillar2_bps_moonshine`, 5 articles, 407 pages) :** Trous noirs quantiques BPS, traversée de murs (*wall crossing*), genre elliptique de $K3$, *Mathieu Moonshine* ($M_{24}$) et *Umbral Moonshine*.
3. **Pilier 3 (`pillar3_picard_fuchs`, 3 articles, 177 pages) :** Équations de Picard–Fuchs, uniformisation modulaire des cartes miroirs, familles $K3$/Calabi–Yau et opérateur $\operatorname{Sym}^2(L_2)$.
4. **Pilier 4 (`pillar4_fluid_spectral`, 4 articles, 202 pages) :** Correspondance Fluide/Gravité (AdS/CFT), explosion en temps fini de Navier–Stokes 3D moyenné, et graphes de Ramanujan (borne d'Alon–Boppana).
5. **Pilier 5 (`pillar5_lean_neurosymbolic`, 4 articles, 90 pages) :** Démonstration automatique et agentique en Lean 4 assistée par LLM et RAG.

---

## 2. Pilier 1 — Fonctions Thêta Moqueuses, Formes de Maass Harmoniques & Quotients $\eta$

### 2.1. État de l'art mathématique

1. **Complétion de Zwegers (2002 / arXiv:0807.4834) :** Dans sa thèse fondatrice (*Mock Theta Functions*, 94 pages), Sander Zwegers résout le mystère posé par Ramanujan dans sa dernière lettre à Hardy (1920) et le *Lost Notebook* (Narosa 1988). Il exprime les fonctions thêta moqueuses via des sommes d'Appell–Lerch, des séries thêta indéfinies de signature $(r-1, 1)$ et des formes de Jacobi méromorphes, et démontre que l'ajout d'une intégrale de période non holomorphe (l'**ombre** — *shadow* — associée à une série thêta unaire de poids $3/2$) transforme chaque fonction thêta moqueuse en une **forme de Maass harmonique réelle-analytique de poids $1/2$** annulée par le laplacien hyperbolique $\Delta_{1/2}$.
2. **Quotients $\eta$ de Dedekind, modularité et bases d'espaces modulaires :**
   - **Ono (2004, Thm 1.64) :** Établit les conditions nécessaires et suffisantes sur les exposants $\{r_d\}_{d \mid N}$ pour que $f(\tau) = \prod_{d \mid N} \eta(d\tau)^{r_d}$ appartienne à $M_k(\Gamma_0(N), \chi)$ : poids entier $k = \frac{1}{2}\sum r_d \in \mathbb{Z}$, $\sum d r_d \equiv 0 \pmod{24}$ et $\sum (N/d) r_d \equiv 0 \pmod{24}$ (plus positivité des ordres d'annulation aux pointes pour l'holomorphie).
   - **Rouse & Webb (2015, arXiv:1311.1460) :** Déterminent pour quels niveaux $N$ l'anneau gradué des formes modulaires holomorphes sur $\Gamma_0(N)$ est engendré par des quotients $\eta$, et prouvent que toute forme modulaire holomorphe ne s'annulant pas sur $\mathbb{H}$ à coefficients de Fourier entiers est un multiple entier d'un quotient $\eta$.
   - **Acres & Broadhurst (2018, arXiv:1810.07478) :** Relient directement **quotients $\eta$ et sommes de Rademacher** (y compris pour les intégrales de Feynman *sunrise* à 2, 3, 4 et 6 boucles sur $\Gamma_0(6)$). Ils montrent comment les transformations d'Atkin–Lehner permutent les pointes (*cusps*) pour optimiser la convergence, et étendent les formules de Rademacher aux niveaux de genre $0$ ($N \in \{1,\dots,10,12,13,16,18,25\}$) puis aux genres $1$ à $13$ malgré les obstructions elliptiques.
   - **Ryan, Scherr, Sirolli & Treneer (2019, arXiv:1911.05799) :** Fournissent un algorithme explicite (basé sur la **borne de Sturm**) pour certifier les congruences arithmétiques des coefficients de Fourier de quotients $\eta$.
   - **Bhattacharya (2026, arXiv:2610.10576) :** Démontre qu'un quotient $\eta$ cuspidal irréductible de niveau $N$ est uniquement déterminé par ses ordres d'annulation en seulement $O((\log_2 N)^{r-1})$ pointes (et uniquement à $\infty$ pour les formes propres de Fricke de niveau puissance de premier), et établit la divisibilité du $k$-ième niveau de Mersmann par $2^{2k}$.
3. **Combinatoire, invariants topologiques et unicité résurgente des fonctions thêta moqueuses :**
   - **Malmendier & Ono (2012, arXiv:0808.1442) :** Prouvent la conjecture de Moore–Witten sur les invariants de Donaldson $SO(3)$ de $\mathbb{CP}^2$ en combinant l'intégrale du plan-$u$ avec une fonction thêta moqueuse de Ramanujan pour obtenir une forme modulaire de poids $1/2$.
   - **Ballantine, Burson, Folsom, Hsu, Negrini & Wen (2022, arXiv:2202.03329) :** Établissent des identités de partitions de type Beck associées aux fonctions thêta moqueuses d'ordre 3 ($\omega(q), \nu(q), \phi(q)$) par méthodes analytiques et bijectives.
   - **Costin, Dunne & Saraeb (2026, arXiv:2604.20034) :** Développent une approche **résurgente** (transformées de Laplace des intégrales de Mordell–Appell et rotation sur la ligne de Stokes) prouvant l'unicité du prolongement canonique des fonctions thêta moqueuses d'ordres 3 et 5 au-delà de leur frontière naturelle $|q|=1$.

### 2.2. Positionnement critique par rapport au dépôt RAMA

- **Ce qui est solidement aligné (Niveau A / B) :** Les 54 quotients $\eta$ de la Campagne v2 vérifiés dans `CampaignV2Verified.lean` (dont 25 satisfaisant Ono Thm 1.64 sur $\Gamma_0(N)$) et les 10 correspondances exactes de fonctions thêta moqueuses d'ordres 3, 5, 6 et de Rogers–Ramanujan $G(q)$ suivent fidèlement le cadre Zwegers / Ono / Andrews–Berndt. Le calcul multi-pointes $c_{\text{eff}}(c) = -\frac{1}{c^2}\sum_d \frac{\gcd(d,c)^2}{d} r_d$ s'accorde avec la géométrie des pointes d'Acres–Broadhurst (2018) et Bhattacharya (2026).
- **Écart comblé par notre nouveau workflow Lean 4 :** Les preuves initiales des 5 identités `LHS = RHS` de la Campagne v2 étaient limitées à l'ordre fini $q^{15}$. En nous appuyant sur la structure algébrique des séries thêta de Ramanujan et sur la borne de Sturm (Ryan et al. 2019), nous élevons 4 identités à des **preuves universelles $\forall n \in \mathbb{N}$** dans le noyau Lean 4 et la 5e (`eq_0722eebfe8`) à une preuve conditionnelle $\forall n$ au-delà de la borne de Sturm exacte $B(\Gamma_0(12), k=1) = 2 < 15$.

---

## 3. Pilier 2 — Trous Noirs BPS, $K3 \times T^2$ et Moonshine ($M_{24}$ / Umbral)

### 3.1. État de l'art mathématique et physique

1. **Dabholkar, Murthy & Zagier (2012, arXiv:1208.4074 — 153 pages) :** Référence centrale reliant directement les fonctions thêta moqueuses de Ramanujan à la gravité quantique. Pour les trous noirs $1/4$-BPS en théorie des cordes $\mathcal{N}=4$ (compactification $K3 \times T^2$), la forme de Jacobi méromorphe comptant les dégénérescences microscopiques se décompose canoniquement en :
   $$\psi_m(\tau, z) = \psi_m^{\text{F}}(\tau, z) + \psi_m^{\text{P}}(\tau, z)$$
   où la partie finie $\psi_m^{\text{F}}$ est une **forme mock-Jacobi** dont les coefficients comptent les trous noirs quantiques **mono-centrés**, et la partie polaire $\psi_m^{\text{P}}$ est une **somme d'Appell–Lerch** capturant les états liés **multi-centrés** qui apparaissent ou disparaissent lors des traversées de murs (*wall crossing*). La complétion non holomorphe restaure la modularité attendue par $\text{AdS}_3/\text{CFT}_2$, tandis que son anomalie holomorphe reflète la non-compacité du continuum microscopique.
2. **Eguchi, Ooguri & Tachikawa (2010/2011, arXiv:1004.0956) & Gannon (2012/2016, arXiv:1211.5531) :** EOT observent que la décomposition du genre elliptique de $K3$ en caractères du groupe superconforme $\mathcal{N}=4$ fait apparaître les dimensions des représentations irréductibles du groupe sporadique de Mathieu $M_{24}$ ($45, 231, 770, 2277,\dots$). Terry Gannon démontre rigoureusement la conjecture EOT en prouvant que toutes les fonctions de classe associées aux séries de McKay–Thompson tordues sont de véritables caractères de $M_{24}$ (avec parité des multiplicités et interprétation cohomologique).
3. **Cheng, Duncan & Harvey (2012/2014, arXiv:1204.2779 — *Umbral Moonshine*, 124 pages) :** Généralisent *Mathieu Moonshine* à une famille de groupes finis paramétrés par les diviseurs de $12$ (et plus généralement les réseaux de Niemeier), où **plusieurs fonctions thêta moqueuses originales de Ramanujan apparaissent explicitement comme séries de McKay–Thompson** liées aux formes mock-Jacobi extrémales de Dabholkar–Murthy–Zagier.
4. **Gukov, Pei, Putrov & Vafa (2017/2020, arXiv:1701.06567) :** Relient les spectres BPS de théories 3D $\mathcal{N}=2$ sur des 3-variétés $M_3$ (demi-indices sur $D^2 \times S^1$) aux invariants quantiques de Witten–Reshetikhin–Turaev (WRT) et aux fonctions fausses thêta / formes quantiques modulaires.

### 3.2. Positionnement critique par rapport au dépôt RAMA

- **Correction essentielle confirmée par DMZ (2012) :** L'entropie asymptotique de Bekenstein–Hawking–Cardy $S(n) \sim 2\pi\sqrt{c_{\text{eff}}\, n / 6}$ n'a de sens unitaire que pour $c_{\text{eff}} > 0$ et des dégénérescences de signe cohérent (ou un indice BPS protégé dont on connaît le signe $(-1)^F$). L'ancienne convention inversée $+\sum r_d/d$ (corrigée en $-\sum r_d/d$ dans tout le dépôt et dans l'erratum de `04b_bps_state_counting.tex`) aurait attribué un $c_{\text{eff}} > 0$ à des formes cuspidales alternées comme $\Delta(\tau) = \eta(\tau)^{24}$ ($c_{\text{eff}}(0) = -24$).
- **Frontière physique stricte :** Conformément à DMZ (2012), le comptage BPS s'applique aux trous noirs **extrémaux supersymétriques** dans $K3 \times T^2$ ($\mathcal{N}=4$), et non aux trous noirs astrophysiques de Kerr non extrémaux (tels que Sgr A*).

---

## 4. Pilier 3 — Équations de Picard–Fuchs, Cartes Miroirs & $\operatorname{Sym}^2(L_2)$

### 4.1. État de l'art mathématique

1. **Doran (1998/2000, arXiv:math/9812162) :** Répond à la conjecture de Lian–Yau sur la modularité des cartes miroirs (*mirror-moonshine*). Il établit un critère géométrique d'uniformisation orbifolde caractérisant quand la carte miroir d'une famille de courbes elliptiques (équation de Picard–Fuchs **d'ordre 2**) ou de surfaces $K3$ $M_n$-polarisées (équation de Picard–Fuchs **d'ordre 3**) est un *Hauptmodul* (fonction modulaire de genre zéro). Crucialement (§4–§5), pour les familles $K3$ de rang de Picard 19 dont le domaine des périodes réside sur une quadrique non dégénérée dans $\mathbb{P}^2$, l'opérateur différentiel de Picard–Fuchs d'ordre 3 est le **carré symétrique** $L_3 = \operatorname{Sym}^2(L_2)$ d'un opérateur d'ordre 2.
2. **Almkvist, van Enckevort, van Straten & Zudilin (2005, arXiv:math/0507430 — 130 pages) :** Classifient systématiquement les équations différentielles de type Calabi–Yau (MUM — *Maximal Unipotent Monodromy*, intégralité des développements miroirs et des nombres d'instantons, séquences sporadiques dont celles de Cooper et les séries hypergéométriques).
3. **Doran, Harder & Thompson (2016/2017, arXiv:1612.09439) :** Montrent comment calculer les nombres de Hodge de la cohomologie parabolique (structures de Hodge de Zucker) directement à partir des exposants locaux de l'équation de Picard–Fuchs sur $\mathbb{P}^1$, avec applications explicites aux familles de courbes elliptiques, surfaces $K3$ et variétés de Calabi–Yau de dimension 3.

### 4.2. Positionnement critique par rapport au dépôt RAMA

- **Validation du cœur algébrique (Niveau A) :** Le théorème algébrique $\operatorname{Sym}^2(L_2)$ (si $u_{n+2} + a u_{n+1} + b u_n = 0$, alors $v_n = u_n^2$ satisfait une récurrence linéaire d'ordre 3 explicite) est le pendant discret exact du carré symétrique différentiel de Doran (2000). Notre workflow le prouve désormais **en compilation noyau Lean 4 directe sur $\mathbb{Z}$** (`sym2_recurrence_int`) en plus de sa version réelle à coefficients variables dans `DualScale/K3Lock/Basic.lean`, où les anciens stubs `:= 0` (`picardFuchsL2`, `symSquareL2`) sont remplacés par de véritables structures d'opérateurs de récurrence.
- **Audit critique T2 sur $S_{12}$ (Découverte de provenance Niveau X) :** L'audit adversarial `pro` du dépôt a mis en évidence que la récurrence `s12_recurrence` stockée dans `dualscale/refs/values.json` correspond en réalité à la **suite d'Apéry pour $\zeta(3)$** (`OEIS A005259`, $u_0=1, u_1=5, \dots, u_5 = 819\,005$), et que les certificats hérités `S12_vs_K3.json` (résidu $u_5 - 54\,000 = 765\,005 \neq 0$) et `S12_vs_elliptic.json` sont des vérifications *mock-proxy* de **Niveau X** (`check_C3b_moduli_map.py`) et non une identification algébro-géométrique de $S_{12}$ avec une EDO elliptique d'ordre 2. Ce point est désormais documenté explicitement dans `DualScale/K3Lock/Basic.lean` et `AllNAndPropositionsVerified.lean` (`s12_coeff_5_exact`, `s12_k3_residual_exact`, `elliptic_pf_order_ne_k3`), préservant une honnêteté épistémique totale.

---

## 5. Pilier 4 — Correspondance Fluide/Gravité, Navier–Stokes 3D & Graphes de Ramanujan

### 5.1. État de l'art mathématique et physique

1. **Bhattacharyya, Hubeny, Minwalla & Rangamani (2007/2008, arXiv:0712.2456) & Rangamani (2009, arXiv:0905.4352) :** Fondent la **correspondance Fluide/Gravité** en promouvant la vitesse et la température des branes noires dans $\text{AdS}_5$ en champs lentement variables sur le bord. Via une **expansion perturbative en dérivées de bord** (régime hydrodynamique à grande longueur d'onde, valide à amplitudes arbitraires mais à faibles gradients), les équations d'Einstein de masse se réduisent aux équations de l'hydrodynamique visqueuse relativiste (conforme) sur le bord, avec un rapport viscosité/entropie universel $\eta/s = \frac{1}{4\pi}$.
2. **Tao (2014/2016, arXiv:1402.0290) :** Démontre l'**explosion en temps fini** d'une solution régulière d'une équation de Navier–Stokes 3D moyennée $\partial_t u = \Delta u + \tilde{B}(u, u)$ qui préserve exactement la même identité d'énergie $\langle \tilde{B}(u, u), u \rangle = 0$ et les mêmes estimations harmoniques/dyadiques (modèles en coquilles de type Katz–Pavlović) que la véritable équation de Navier–Stokes 3D. **Conséquence fondamentale (barrière de Tao) :** Aucun argument basé uniquement sur l'identité d'énergie, la compacité d'Aubin–Lions ou des bornes dyadiques génériques ne peut résoudre le problème du millénaire de la régularité globale de Navier–Stokes 3D ; il faut exploiter une structure géométrique/annulative fine propre à la non-linéarité exacte $B(u,u)$.
3. **Lubotzky–Phillips–Sarnak (1988) & Marcus–Spielman–Srivastava (2013/2015, arXiv:1304.4132) :** Les graphes de Ramanujan $k$-réguliers satisfont la borne spectrale optimale d'Alon–Boppana $|\lambda| \le 2\sqrt{k-1}$ pour toute valeur propre non triviale. LPS (1988) construisent des graphes de Cayley explicites via la conjecture de Ramanujan–Petersson démontrée par Deligne (1974) ($|\tau(p)| \le 2p^{11/2}$), tandis que Marcus, Spielman et Srivastava prouvent par la méthode des **polynômes entrelacés** (*interlacing families*) l'existence de familles infinies de graphes de Ramanujan bipartis pour **tout degré $k \ge 3$**.

### 5.2. Analyse critique impitoyable des conjectures du dépôt (Règles R1–R5)

- **Hypothèse U & pont Fluide/Gravité $\leftrightarrow$ Navier–Stokes 3D (Strictement Niveau C — Conjecture conditionnelle ouverte) :**
  - L'étude directe de BHMR (2008), Rangamani (2009) et Tao (2016) impose une distinction épistémique absolue : la correspondance Fluide/Gravité opère dans un **régime de dérivées lentes** (qui s'effondre précisément là où l'enstrophie $\int |\nabla \times u|^2$ diverge !), tandis que la barrière de Tao (2016) prouve que les modèles dyadiques/énergétiques sans structure fine de $B(u,u)$ peuvent exploser en temps fini.
  - Par conséquent, les théorèmes `DualScale/NS/HypothesisU.lean` et `DualScale/Physics/MasterDualScale.lean` sont valides **uniquement comme implications conditionnelles** (*si* l'Hypothèse U et le principe d'Aubin–Lions sont donnés en hypothèses explicites, *alors* la précompacité $L^2$ en découle). Ils ne constituent en aucun cas une preuve de régularité globale de Navier–Stokes 3D.
- **Réfutation CFM angle elliptique (Niveau X — Réfutée et formalisée en Lean 4) :** La constante de Lipschitz de Constantin–Fefferman–Majda ($\frac{4}{3}\pi$) diffère strictement de l'approximation angulaire elliptique ($\frac{16}{9}\pi$, écart $\frac{4}{9}\pi$). Notre workflow élimine la tautologie résiduelle de `DualScale/CFM/Basic.lean` et prouve cette réfutation dans le noyau Lean 4.
- **Réfutation spectrale M2 (Niveau X — Réfutée et formalisée en Lean 4) :** Les graphes circulants triadiques testés pour $p \in \{2, 3, 5\}$ ($k \in \{3, 4, 6\}$) violent massivement la borne d'Alon–Boppana ($\lambda_2 \in \{5{,}94;\, 7{,}88;\, 11{,}64\}$ vs $2\sqrt{k-1} \in \{2{,}83;\, 3{,}46;\, 4{,}47\}$), contrairement aux véritables graphes LPS ou MSS. Cette falsification est désormais prouvée exactement par inégalités entières au carré dans le noyau Lean 4.

---

## 6. Pilier 5 — Démonstration Neuro-Symbolique en Lean 4 & Architecture du Workflow

### 6.1. État de l'art (2023–2026)

1. **LeanDojo / ReProver (Yang et al., 2023, arXiv:2306.15626) :** Démontre l'efficacité déterminante de la **sélection de prémisses augmentée par récupération (RAG)** couplée à une interaction programmatique avec le noyau Lean (benchmark de 98 734 théorèmes Mathlib).
2. **Lean Copilot (Song, Yang & Anandkumar, 2024, arXiv:2404.12534) :** Intègre l'inférence LLM directement dans la boucle interactive de Lean 4, atteignant 74,2 % d'automatisation d'étapes de preuve (contre 40,1 % pour `aesop`) tout en garantissant l'absence d'hallucinations grâce au vérificateur de noyau.
3. **DeepSeek-Prover (Xin et al., 2024, arXiv:2405.14333) :** Valide le paradigme **autoformalisation $\to$ filtrage qualité $\to$ génération de preuves complètes vérifiées par Lean 4**, atteignant 52 % cumulé sur miniF2F-Lean4 et 5/148 sur FIMO.
4. **OpenProver (Kripner & Straka, 2026, arXiv:2607.09217) :** Formalise l'architecture agentique **Planificateur – Exécutants parallèles – Vérificateur Lean 4** (*Planner–Worker–Verifier*) avec tableau blanc compact et vérification formelle reproductible.

### 6.2. Traduction directe dans notre workflow `lean_proposition_validator_workflow.py`

Notre workflow multi-modèles (`tools/workflows/lean_proposition_validator_workflow.py`, exécuté via `run_workflow`) synthétise exactement ces 4 avancées tout en y ajoutant la discipline épistémique R1–R5 :

- **RAG scientifique (inspiration LeanDojo) :** Phase 0 interroge directement ChromaDB (`data/chromadb/`) sur les 24 articles pour ancrer chaque proposition dans ses références exactes avant toute écriture de preuve.
- **Architecture Planner–Worker–Verifier (inspiration OpenProver) :**
  - **Planificateur / Arbitre T2 (`pro`) :** Audite les propositions contre ChromaDB et rédige des spécifications formelles strictes.
  - **Exécutants parallèles disjoints :** Worker A (`pro`) produit et compile le module noyau autonome `AllNAndPropositionsVerified.lean` (preuves $\forall n$, algèbre universelle, $\operatorname{Sym}^2(L_2)$, réfutations) ; Worker B (`flash`) remédie aux 4 fichiers Mathlib (`TDuality.lean`, `CFM/Basic.lean`, `K3Lock/Basic.lean`, `SpectralGap/Basic.lean`).
  - **Vérificateur déterministe zéro-token :** Noyau `lean` v4.33.1 + `mathesis_gate.py` (empreintes `#print axioms` réelles) + `audit_lean.py` + `preflight_audit.py` + `run_certificates.py` + `pytest`.
  - **Critique adversarial T2 (`pro`) avec boucle de réparation bornée :** Réutilise la conversation T2 avec état pour auditer chaque preuve générée et émettre un certificat JSON (`dualscale/certificates/llm_lean_validation_report.json`).

---

## 7. Matrice Épistémique Consolidée des Propositions du Dépôt

| Proposition / Objet | Statut littérature | Niveau R1–R5 | Artefact formel / certificat |
|---|---|---|---|
| 54 quotients $\eta$ de Ramanujan (poids $k$, $c_{\text{eff}}(0)$, $E_0$, Ono Thm 1.64, 12 termes) | Ono (2004), Rouse–Webb (2015), Acres–Broadhurst (2018) | **Niveau A** | `CampaignV2Verified.lean` (270 thm., `#print axioms` $\subseteq \{\texttt{propext}\}$) |
| 4 identités de Ramanujan (`eq_d6899de389`, `eq_c23aa45585`, `eq_460927b577`, `eq_2847c49f95`) | Andrews–Berndt, Ramanujan NB 1–2 Ch. XV–XVI | **Niveau A ($\forall n \in \mathbb{N}$)** | `AllNAndPropositionsVerified.lean` (preuves universelles noyau Lean 4) |
| 5e identité (`eq_0722eebfe8`, $\Gamma_0(12)$, poids $1$) | Ryan–Scherr–Sirolli (2019), Sturm bound $B=2<15$ | **Niveau A (tronqué $q^{15}$) / Cond. $\forall n$ (Sturm)** | `CampaignV2Verified.lean` + `AllNAndPropositionsVerified.lean` |
| Algèbre universelle des quotients $\eta$ (additivité $k, E_0$, clôture Ono mod 24) | Ono (2004), Bhattacharya (2026) | **Niveau A ($\forall f, g$)** | `AllNAndPropositionsVerified.lean` |
| 10 fonctions thêta moqueuses & Rogers–Ramanujan $G(q)$ (ordres 3, 5, 6) | Zwegers (2002), Ballantine et al. (2022), Costin et al. (2026) | **Niveau B** | `namagiri.db` + `campaign_v2_report.json` |
| Verrouillage $\operatorname{Sym}^2(L_2)$ (récurrence d'ordre 2 $\to$ ordre 3) | Doran (2000), Deligne (1974) | **Niveau A ($\forall a, b, u$)** | `AllNAndPropositionsVerified.lean` (sur $\mathbb{Z}$, compilé live) + `K3Lock/Basic.lean` |
| Audit $S_{12}$ / Apéry $\zeta(3)$ (`u_5 = 819005`, résidu mock $765\,005$) & ordres $2 \neq 3$ | Doran (2000), Almkvist–Zudilin (2005) — *mock-proxy* `check_C3b_moduli_map.py` | **Niveau A (arithmétique) / Niveau X (provenance $S_{12}$)** | `AllNAndPropositionsVerified.lean` + `K3Lock/Basic.lean` + `s12_ledger.csv` |
| Involution T-dualité $R \mapsto \alpha'/R$ ($\forall \alpha'>0, R>0$, sans constante figée) | Dualité des cordes sur $S^1$ | **Niveau A ($\forall \alpha', R$)** | `AllNAndPropositionsVerified.lean` + `TDuality.lean` |
| Réfutation CFM angle elliptique ($\frac{4}{3}\pi \neq \frac{16}{9}\pi$) | Constantin–Fefferman–Majda (1996) | **Niveau X (Réfutée en Niveau A)** | `AllNAndPropositionsVerified.lean` + `CFM/Basic.lean` + `cfm_ledger.csv` |
| Falsification M2 Alon–Boppana ($p \in \{2,3,5\}$, graphes triadiques non-LPS) | LPS (1988), Marcus–Spielman–Srivastava (2015) | **Niveau X (Réfutée en Niveau A)** | `AllNAndPropositionsVerified.lean` + `SpectralGap/Basic.lean` + `ledger.csv` |
| 14 erreurs d'OCR de la Campagne v2 réfutées (`lhs ≠ rhs`) | Arithmétique exacte $\mathbb{Q}[[q]]$ | **Niveau X (Réfutées en Niveau A)** | `AllNAndPropositionsVerified.lean` + `campaign_v2_report.json` |
| Pont Fluide/Gravité $\leftrightarrow$ Hypothèse U Navier–Stokes 3D | BHMR (2008), Rangamani (2009), barrière de Tao (2016) | **Niveau C (Conjecture ouverte)** | `HypothesisU.lean` + `MasterDualScale.lean` (implications conditionnelles) |

---

## 8. Bibliographie Complète des 24 Articles arXiv Téléchargés et Indexés dans ChromaDB

### Pilier 1 — Fonctions thêta moqueuses, formes de Maass harmoniques & quotients $\eta$
1. S. Zwegers (2008 / thèse 2002), *Mock Theta Functions* — [https://arxiv.org/abs/0807.4834](https://arxiv.org/abs/0807.4834)
2. A. Malmendier, K. Ono (2008 / Geom. Topol. 2012), *SO(3)-Donaldson invariants of $\mathbb{CP}^2$ and Mock Theta Functions* — [https://arxiv.org/abs/0808.1442](https://arxiv.org/abs/0808.1442)
3. J. Rouse, J. J. Webb (2013 / Adv. Math. 2015), *On spaces of modular forms spanned by eta-quotients* — [https://arxiv.org/abs/1311.1460](https://arxiv.org/abs/1311.1460)
4. K. Acres, D. Broadhurst (2018), *Eta quotients and Rademacher sums* — [https://arxiv.org/abs/1810.07478](https://arxiv.org/abs/1810.07478)
5. N. C. Ryan, Z. Scherr, N. Sirolli, S. Treneer (2019), *Congruences satisfied by eta-quotients* — [https://arxiv.org/abs/1911.05799](https://arxiv.org/abs/1911.05799)
6. C. Ballantine, H. E. Burson, A. Folsom, C.-Y. Hsu, I. Negrini, B. Wen (2022), *Mock theta functions and related combinatorics* — [https://arxiv.org/abs/2202.03329](https://arxiv.org/abs/2202.03329)
7. O. Costin, G. V. Dunne, A. Saraeb (2026), *On Uniqueness of Mock Theta Functions* — [https://arxiv.org/abs/2604.20034](https://arxiv.org/abs/2604.20034)
8. S. Bhattacharya (2026), *The structure of irreducible cuspidal eta quotients* — [https://arxiv.org/abs/2610.10576](https://arxiv.org/abs/2610.10576)

### Pilier 2 — Trous noirs BPS, $K3 \times T^2$, Mathieu $M_{24}$ & Umbral Moonshine
9. T. Eguchi, H. Ooguri, Y. Tachikawa (2010 / Exp. Math. 2011), *Notes on the K3 Surface and the Mathieu group $M_{24}$* — [https://arxiv.org/abs/1004.0956](https://arxiv.org/abs/1004.0956)
10. M. C. N. Cheng, J. F. R. Duncan, J. A. Harvey (2012 / CNTP 2014), *Umbral Moonshine* — [https://arxiv.org/abs/1204.2779](https://arxiv.org/abs/1204.2779)
11. A. Dabholkar, S. Murthy, D. Zagier (2012), *Quantum Black Holes, Wall Crossing, and Mock Modular Forms* — [https://arxiv.org/abs/1208.4074](https://arxiv.org/abs/1208.4074)
12. T. Gannon (2012 / Adv. Math. 2016), *Much ado about Mathieu* — [https://arxiv.org/abs/1211.5531](https://arxiv.org/abs/1211.5531)
13. S. Gukov, D. Pei, P. Putrov, C. Vafa (2017 / JKTR 2020), *BPS spectra and 3-manifold invariants* — [https://arxiv.org/abs/1701.06567](https://arxiv.org/abs/1701.06567)

### Pilier 3 — Équations de Picard–Fuchs, Calabi–Yau / $K3$ & $\operatorname{Sym}^2(L_2)$
14. C. F. Doran (1998 / CMP 2000), *Picard-Fuchs Uniformization: Modularity of the Mirror Map and Mirror-Moonshine* — [https://arxiv.org/abs/math/9812162](https://arxiv.org/abs/math/9812162)
15. G. Almkvist, C. van Enckevort, D. van Straten, W. Zudilin (2005), *Tables of Calabi--Yau equations* — [https://arxiv.org/abs/math/0507430](https://arxiv.org/abs/math/0507430)
16. C. F. Doran, A. Harder, A. Thompson (2016 / SIGMA 2017), *Hodge Numbers from Picard-Fuchs Equations* — [https://arxiv.org/abs/1612.09439](https://arxiv.org/abs/1612.09439)

### Pilier 4 — Correspondance Fluide/Gravité, Navier–Stokes 3D & Graphes de Ramanujan
17. S. Bhattacharyya, V. E. Hubeny, S. Minwalla, M. Rangamani (2007 / JHEP 2008), *Nonlinear Fluid Dynamics from Gravity* — [https://arxiv.org/abs/0712.2456](https://arxiv.org/abs/0712.2456)
18. M. Rangamani (2009 / CQG 2009), *Gravity & Hydrodynamics: Lectures on the fluid-gravity correspondence* — [https://arxiv.org/abs/0905.4352](https://arxiv.org/abs/0905.4352)
19. A. W. Marcus, D. A. Spielman, N. Srivastava (2013 / Ann. Math. 2015), *Interlacing Families I: Bipartite Ramanujan Graphs of All Degrees* — [https://arxiv.org/abs/1304.4132](https://arxiv.org/abs/1304.4132)
20. T. Tao (2014 / JAMS 2016), *Finite time blowup for an averaged three-dimensional Navier-Stokes equation* — [https://arxiv.org/abs/1402.0290](https://arxiv.org/abs/1402.0290)

### Pilier 5 — Démonstration automatique & agentique en Lean 4
21. K. Yang, A. M. Swope, A. Gu et al. (2023 / NeurIPS), *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models* — [https://arxiv.org/abs/2306.15626](https://arxiv.org/abs/2306.15626)
22. P. Song, K. Yang, A. Anandkumar (2024), *Lean Copilot: Large Language Models as Copilots for Theorem Proving in Lean* — [https://arxiv.org/abs/2404.12534](https://arxiv.org/abs/2404.12534)
23. H. Xin, D. Guo, Z. Shao et al. (2024), *DeepSeek-Prover: Advancing Theorem Proving in LLMs through Large-Scale Synthetic Data* — [https://arxiv.org/abs/2405.14333](https://arxiv.org/abs/2405.14333)
24. M. Kripner, M. Straka (2026), *OpenProver: Agentic and Interactive Theorem Proving with Lean 4* — [https://arxiv.org/abs/2607.09217](https://arxiv.org/abs/2607.09217)
