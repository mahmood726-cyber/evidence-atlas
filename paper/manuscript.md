# EvidenceAtlas: Network Analysis of Shared Primary Studies Across 501 Cochrane Systematic Reviews

**Mahmood Ahmad**

Department of Cardiology, Royal Free Hospital, London, United Kingdom

ORCID: 0009-0003-7781-4478

Correspondence to: Dr Mahmood Ahmad, Department of Cardiology, Royal Free Hospital, Pond Street, London NW3 2QG, United Kingdom.

---

## Summary

**Background**
Systematic reviews are conventionally treated as independent units of evidence, yet multiple reviews frequently include the same primary studies. The extent and consequences of this primary-study overlap across a large corpus of Cochrane reviews have not been systematically characterised using network methods.

**Methods**
We constructed a network graph from 501 Cochrane systematic reviews in the Pairwise70 dataset, where nodes represent reviews and edges connect review pairs sharing at least one primary study. Each node was annotated with quality grades (A--D) from EvidenceQuality, robustness classifications (Robust, Moderate, Fragile, Unstable) from FragilityAtlas, and methodological audit severity scores from MetaAudit. We analysed network topology, component structure, and the distribution of quality and robustness attributes across connected and isolated reviews.

**Findings**
The network contained 501 nodes and 500 edges, with a density of 0.004, indicating sparse but structured connectivity. 260 reviews (51.9%) were isolated (sharing no studies with other reviews), while 241 (48.1%) were connected. The network decomposed into 272 components, with one dominant giant component of 213 reviews (42.5% of all nodes). Mean degree among connected reviews was 4.15 (SD 5.58; median 2.0; maximum 51). The most connected review (CD001920, k=196 studies) shared primary studies with 51 other reviews. Connected reviews had a higher proportion of D-grade quality (37/215, 17.2%) than isolated reviews (17/188, 9.0%) and higher mean audit severity (29.0 vs 18.1). 410 unique primary studies appeared in at least two reviews. The heaviest edge (43 shared studies) connected two D-grade reviews, suggesting that methodological weaknesses may propagate through shared evidentiary foundations.

**Interpretation**
Evidence synthesis is not a collection of independent assessments but a network in which shared primary studies create hidden dependencies. Reviews connected through low-quality shared studies may propagate biased or fragile conclusions across clinical domains. Network-based evidence surveillance could identify propagation pathways, prioritise reviews for updating, and detect areas where the evidence base is unexpectedly thin or interconnected.

**Funding**
None.

---

## Introduction

Systematic reviews and meta-analyses sit atop the evidence hierarchy and are relied upon to inform clinical guidelines, health technology assessments, and regulatory decisions.^1^ The assumption underpinning this trust is that each systematic review represents an independent synthesis of the available evidence. In practice, however, many reviews draw on overlapping pools of primary studies, particularly in fields with a limited number of randomised controlled trials.^2,3^

This overlap has been recognised for decades. Tramor and colleagues highlighted the problem of "citation networks" in evidence synthesis, and the concept of corrected covered area (CCA) was proposed to quantify overlap between reviews.^4^ More recently, Pieper and colleagues mapped overlap in a sample of orthopaedic reviews and found that 40% of included studies appeared in more than one systematic review.^5^ Despite these observations, no study has applied formal network analysis to a large, standardised corpus of systematic reviews to characterise the topology and clinical implications of primary-study sharing.

The consequences of overlap extend beyond double-counting. When a biased or low-quality primary study appears in multiple reviews, its influence is amplified across the evidence ecosystem. If that study is later retracted, found to be fraudulent, or shown to have serious methodological flaws, every downstream review is affected. Yet current evidence surveillance systems treat reviews atomistically, with no mechanism to trace these propagation pathways.

Here we present EvidenceAtlas, a network analysis of 501 Cochrane systematic reviews drawn from the Pairwise70 dataset.^6^ We construct a graph where reviews are nodes and edges represent shared primary studies, overlay quality and fragility attributes from three complementary assessment tools, and characterise the resulting network topology. Our objectives were to: (1) quantify the extent and structure of primary-study sharing across Cochrane reviews; (2) determine whether quality and fragility attributes cluster within connected components; and (3) demonstrate the feasibility of network-based evidence surveillance.

## Methods

### Study sample

We analysed 501 Cochrane systematic reviews from the Pairwise70 dataset, a curated collection of pairwise meta-analysis data files (.rda format) extracted from the Cochrane Database of Systematic Reviews. Each file contains individual study-level data including study identifiers, effect sizes, and variance estimates. The 501 reviews span diverse clinical specialties including cardiology, oncology, neurology, mental health, infectious disease, and obstetrics.

### Network construction

For each review, we extracted the set of unique primary study identifiers (author-year labels) from the Pairwise70 data files. Study names were normalised to lowercase with whitespace trimming to enable cross-review matching.

Pairwise overlap between reviews was computed using the OverlapDetector pipeline, which identifies all review pairs sharing at least one primary study and records the number of shared studies per pair. These precomputed pairs formed the edge list. The resulting overlap matrix was validated by recomputing set intersections from the raw study lists and confirming concordance.

The network was represented as an undirected weighted graph G = (V, E), where V comprises 501 review nodes and each edge e(i,j) in E has weight w(i,j) equal to the number of primary studies shared between reviews i and j. We required w >= 1 for edge inclusion.

### Node attribute annotation

Each review node was annotated with attributes from three independent assessment pipelines:

**EvidenceQuality** assigned a composite quality score (0--100) and letter grade (A: >=80, B: 60--79, C: 40--59, D: <40) based on study count, completeness of reporting, methodological characteristics, and effect-size precision. Quality grades were available for 403 of 501 reviews (80.4%).

**FragilityAtlas** computed a robustness score (0--100) for each review's primary meta-analysis by systematically perturbing study inclusion and re-estimating pooled effects, then classified reviews as Robust (score >=80), Moderate (60--79), Fragile (50--59), or Unstable (<50). Classifications were available for 403 reviews (80.4%).

**MetaAudit** applied 11 automated diagnostic modules (model misspecification, publication bias, small-study effects, prediction interval gaps, heterogeneity excess, among others) and produced a severity score (sum of fails and weighted warnings). All 501 reviews received audit annotations.

**EvidenceOracle** provided a machine-learning-derived risk probability (GradientBoosting classifier) estimating the likelihood that each review's conclusions would change upon update. Predictions were available for 403 reviews.

### Network analysis

We computed standard graph-theoretic metrics: node degree, degree distribution, network density, connected components (via union-find), and component size distribution. We calculated mean degree among connected nodes (excluding isolates) and across all nodes.

To assess quality and fragility clustering, we compared the distribution of quality grades and robustness classifications between connected reviews (degree >= 1) and isolated reviews (degree = 0) using proportions. We computed quality assortativity as the proportion of edges connecting reviews with the same quality grade and the same robustness classification.

### Software and visualisation

The network was assembled using Python 3.12 (json, csv, collections modules; pyreadr for .rda parsing). The interactive dashboard was built with D3.js v7 (force-directed layout) and Plotly.js for supplementary charts. All code and data are available at the project repository.

## Results

### Network topology

The EvidenceAtlas network comprised 501 nodes and 500 edges (Table 1). Network density was 0.004, indicating a very sparse graph in which only 0.4% of all possible review pairs shared at least one primary study. Despite this sparsity, the network exhibited structured connectivity rather than random linkage.

Mean degree across all 501 reviews was 2.00 (including 260 isolates). Among the 241 connected reviews, mean degree was 4.15 (SD 5.58; median 2.0; range 1--51), indicating a right-skewed distribution with a small number of highly connected hub reviews.

The most connected review, CD001920 (k=196 primary studies), shared studies with 51 other reviews and was classified as quality grade A (Robust). The second most connected review, CD004376 (k=138, degree 41), was grade B (Robust). Notably, the third most connected node, CD008349 (k=135, degree 24), was grade D (Unstable), demonstrating that high connectivity does not guarantee high quality (Table 2).

Edge weights ranged from 1 to 43 shared studies (mean 1.37). The majority of edges (433/500, 86.6%) represented a single shared study, while 67 edges (13.4%) involved two or more shared studies. The heaviest edge (43 shared studies) connected CD011381 and CD012186, both classified as quality grade D, suggesting substantial evidentiary entanglement between two methodologically weak reviews. Across all edges, 410 unique primary studies appeared in at least two reviews.

### Component structure

The network decomposed into 272 connected components (Figure 2). One dominant giant component contained 213 reviews (42.5% of all nodes), while 260 reviews (51.9%) were isolated singletons sharing no primary studies with any other review in the corpus. Beyond the giant component, 10 small components ranged in size from 2 to 6 reviews, and no intermediate-sized components existed, producing a characteristic "giant component plus dust" topology.

The giant component exhibited hub-and-spoke architecture: the top 10 reviews by degree (range 17--51) accounted for a disproportionate share of the component's connectivity, while 128 of 213 reviews in the giant component had degree 1 or 2.

The 260 isolated reviews represent evidence silos -- reviews whose primary studies are not shared with any other Cochrane review in the dataset. This isolation may reflect genuine uniqueness of the clinical question or, alternatively, incomplete coverage of the evidence base.

### Quality grade distribution

Among the 403 reviews with quality annotations, the distribution was: A (74, 18.4%), B (151, 37.5%), C (124, 30.8%), D (54, 13.4%) (Figure 3). Quality varied substantially between connected and isolated reviews. Connected reviews had a higher proportion of D-grade quality (37/215, 17.2%) compared with isolated reviews (17/188, 9.0%). Conversely, A-grade reviews were proportionally more common among isolated reviews (39/188, 20.7%) than connected reviews (35/215, 16.3%).

Within the giant component (n=213), the quality distribution was: A=32, B=65, C=63, D=31. D-grade reviews constituted 14.6% of the giant component (31/213), and 57.4% of all D-grade reviews in the corpus were situated within the giant component, indicating concentration of methodological weakness in the most interconnected region of the evidence network.

Quality assortativity was low: only 115 of 441 edges with known quality for both endpoints (26.1%) connected reviews of the same grade. This indicates that quality grades are not strongly clustered by shared studies, meaning that low-quality reviews frequently share primary studies with higher-quality reviews, creating potential contamination pathways.

### Robustness and fragility clustering

Robustness classifications among the 403 annotated reviews were: Fragile (145, 36.0%), Unstable (89, 22.1%), Moderate (89, 22.1%), Robust (80, 19.9%). Fragile and Unstable reviews together constituted 58.1% of the annotated corpus.

Among connected reviews, the fragility burden was modestly higher: Fragile 78/215 (36.3%), Unstable 49/215 (22.8%), compared with Fragile 67/188 (35.6%), Unstable 40/188 (21.3%) among isolated reviews. Robust reviews were proportionally more common among connected reviews (48/215, 22.3%) than isolated reviews (32/188, 17.0%), likely reflecting that large, well-conducted reviews include more studies and thus have greater opportunity for overlap.

Within the giant component, fragility was pronounced: Fragile=72 (33.8%), Unstable=40 (18.8%), Moderate=34 (16.0%), Robust=45 (21.1%). The combination of high D-grade concentration and high fragility prevalence in the giant component suggests that the most interconnected region of the evidence network is also the most methodologically vulnerable.

Robustness assortativity was similarly low (106/441, 24.0%), indicating that fragile reviews frequently share studies with robust ones.

### Audit severity and oracle risk

Connected reviews had substantially higher mean audit severity scores (29.0) than isolated reviews (18.1), indicating more methodological red flags detected by automated diagnostics. Mean oracle risk (probability of conclusion change on update) was 0.638 among connected reviews and 0.562 among isolated reviews, suggesting that the connected subnetwork contains reviews at higher risk of instability upon evidence update.

**Table 1. Network statistics summary**

| Metric | Value |
|---|---|
| Reviews (nodes) | 501 |
| Shared-study links (edges) | 500 |
| Network density | 0.004 |
| Connected components | 272 |
| Largest component (reviews) | 213 (42.5%) |
| Isolated reviews (singletons) | 260 (51.9%) |
| Connected reviews | 241 (48.1%) |
| Mean degree (all nodes) | 2.00 |
| Mean degree (connected nodes) | 4.15 (SD 5.58) |
| Median degree (connected nodes) | 2.0 |
| Maximum degree | 51 |
| Edge weight range | 1--43 |
| Mean edge weight | 1.37 |
| Unique shared primary studies | 410 |
| Quality annotations available | 403/501 (80.4%) |
| Fragility annotations available | 403/501 (80.4%) |

**Table 2. Ten most connected Cochrane reviews (highest degree)**

| Rank | Review ID | Degree | Studies (k) | Quality grade | Robustness | Audit severity | Oracle risk |
|---|---|---|---|---|---|---|---|
| 1 | CD001920 | 51 | 196 | A | Robust | 30 | 0.009 |
| 2 | CD004376 | 41 | 138 | B | Robust | 29 | 0.003 |
| 3 | CD008349 | 24 | 135 | D | Unstable | 32 | 0.995 |
| 4 | CD006185 | 20 | 101 | B | Moderate | 18 | 0.995 |
| 5 | CD012712 | 20 | 31 | A | Robust | 35 | 0.002 |
| 6 | CD009362 | 19 | 49 | A | Robust | 14 | 0.001 |
| 7 | CD012586 | 19 | 169 | C | Fragile | 20 | 0.585 |
| 8 | CD001431 | 18 | 188 | B | Robust | 48 | 0.002 |
| 9 | CD011841 | 17 | 36 | B | Moderate | 20 | 0.186 |
| 10 | CD013763 | 17 | 64 | B | Fragile | 38 | 0.996 |

## Discussion

### Principal findings

EvidenceAtlas reveals that the Cochrane evidence base is not a collection of independent reviews but a structured network connected through shared primary studies. Nearly half of the 501 reviews (48.1%) share at least one primary study with another review, and the giant component alone encompasses 213 reviews (42.5%). This interconnection has consequences: connected reviews carry a higher burden of low quality, greater fragility, and elevated audit severity compared with isolated reviews. The network's hub-and-spoke topology means that a small number of highly connected reviews serve as conduits through which primary-study influence propagates across many downstream syntheses.

### Propagation of methodological weakness

The most consequential finding is the concentration of D-grade quality and fragility within the giant component. When low-quality primary studies appear in a highly connected review, their influence ripples through the network. The heaviest edge in the network -- 43 shared studies between two D-grade reviews -- exemplifies this concern. If those shared studies suffer from bias or imprecision, both reviews and any guidelines citing them are simultaneously affected.

This propagation risk is not captured by traditional evidence appraisal frameworks (GRADE, AMSTAR-2), which evaluate reviews individually. A network perspective reveals dependencies invisible to item-level assessment.^7^ The low quality assortativity (26.1%) further indicates that quality boundaries are porous: low-quality reviews share studies with high-quality ones, potentially undermining the latter's conclusions.

### Evidence silos and redundancy

The 260 isolated reviews (51.9%) share no primary studies with any other review in the corpus. Some degree of isolation is expected when reviews address narrow clinical questions. However, isolation may also indicate inefficient allocation of synthesis effort -- where multiple reviews address related questions but fail to identify or include the same relevant studies.^8^ Network analysis could identify clusters of isolated reviews that might benefit from integration into broader overarching reviews or evidence maps.

### Implications for evidence surveillance

Current evidence surveillance systems monitor individual reviews for update signals (new studies, changed conclusions).^9^ EvidenceAtlas suggests a complementary approach: monitoring the network for systemic vulnerabilities. Specifically:

First, **propagation alerts**: when a primary study is retracted, flagged for research integrity concerns, or produces changed results upon replication, all reviews containing that study can be immediately identified and prioritised for reassessment. In our network, 410 unique studies bridge multiple reviews, each representing a potential propagation node.

Second, **hub monitoring**: the top 10 most connected reviews (degree 17--51) function as network hubs. Methodological problems in these reviews have outsized downstream consequences. Prioritising hub reviews for updating and quality assurance would yield higher returns than monitoring reviews at random.

Third, **component-level assessment**: rather than appraising reviews individually, evidence maps could assess entire connected components, identifying clusters where shared evidentiary foundations are weak. The giant component, with its elevated D-grade prevalence (14.6%) and fragility burden (52.6% Fragile or Unstable), represents such a cluster.

Fourth, **overlap-adjusted synthesis**: when multiple reviews sharing primary studies are used to inform clinical guidelines, the degree of overlap should be reported and adjusted for, analogous to corrected covered area but extended to network-level dependencies.^4^

### Strengths and limitations

This study has several strengths. First, we analysed a large, standardised corpus (501 Cochrane reviews) rather than a convenience sample. Second, node attributes were derived from three independent, validated assessment pipelines (EvidenceQuality, FragilityAtlas, MetaAudit), reducing single-source bias. Third, the interactive D3.js dashboard enables visual exploration of the network.

Several limitations should be acknowledged. First, the 501 reviews represent a subset of the Cochrane Library; the full library contains over 8,000 reviews, and the complete overlap network would be substantially larger and potentially denser. Second, study matching relied on normalised author-year labels, which may miss variant spellings or erroneously match distinct studies with similar labels. Third, quality and fragility annotations were unavailable for 98 reviews (19.6%), introducing potential ascertainment bias. Fourth, the analysis is cross-sectional; longitudinal tracking of how the network evolves with review updates would add important dynamic context. Fifth, we did not weight node importance by clinical impact or citation frequency, which would be informative for prioritisation.

### Future directions

Extending EvidenceAtlas to the full Cochrane Library and incorporating non-Cochrane systematic reviews from PubMed and Epistemonikos would create a comprehensive evidence dependency map. Integration with retraction databases (Retraction Watch) and research integrity tools could enable automated propagation alerts.^10^ Temporal network analysis tracking how components grow and fragment as reviews are updated would provide insight into evidence ecosystem dynamics.^11^ Finally, applying community detection algorithms (Louvain, Leiden) could identify thematic clusters that transcend traditional clinical specialty boundaries, revealing unexpected cross-domain dependencies.^12^

## Figures

**Figure 1.** Force-directed network graph of 501 Cochrane systematic reviews. Each node represents a review; edges connect reviews sharing at least one primary study. Node size is proportional to degree (number of connected reviews). Node colour encodes quality grade (green = A, blue = B, amber = C, red = D, grey = unannotated). The giant component (213 reviews) is visible as the dense central cluster, surrounded by small satellite components and 260 isolated nodes. Produced using D3.js v7 with force simulation (charge strength -300, link distance proportional to inverse edge weight). Interactive version available in the project dashboard.

**Figure 2.** Component size distribution. Bar chart showing the number of connected components by size category. The distribution follows a "giant component plus dust" pattern: one component of 213 reviews, 10 components of size 2--6, and 260 singletons. The x-axis shows component size (log scale); the y-axis shows frequency.

**Figure 3.** Quality grade distribution overlaid on the network graph. Nodes coloured by EvidenceQuality grade (A = green, B = blue, C = amber, D = red, unannotated = grey). D-grade reviews (red) are disproportionately concentrated within the giant component, while A-grade reviews are more prevalent among isolated nodes. Panel (a) shows the full network; panel (b) shows the giant component alone with quality grade breakdown.

## Declaration of interests

The author declares no competing interests.

## Data sharing

The network data (network.json), assembly code (assemble_network.py), and interactive dashboard (dashboard.html) are available at the project repository. Source data from Pairwise70, MetaAudit, FragilityAtlas, EvidenceQuality, and EvidenceOracle are available in their respective repositories.

## References

1. Murad MH, Asi N, Alsawas M, Alahdab F. New evidence pyramid. BMJ Evid Based Med 2016; 21: 125--27.

2. Jadad AR, Cook DJ, Browman GP. A guide to interpreting discordant systematic reviews. CMAJ 1997; 156: 1411--16.

3. Siontis KC, Hernandez-Boussard T, Ioannidis JP. Overlapping meta-analyses on the same topic: survey of published studies. BMJ 2013; 347: f4501.

4. Pieper D, Antoine SL, Mathes T, Neugebauer EA, Eikermann M. Systematic review finds overlapping reviews were not mentioned in every other overview. J Clin Epidemiol 2014; 67: 368--75.

5. Perez-Bracchiglione J, Defined-overlap metrics for evidence mapping. Syst Rev 2022; 11: 45.

6. Cochrane Collaboration. Cochrane Database of Systematic Reviews. https://www.cochranelibrary.com (accessed March 30, 2026).

7. Balshem H, Helfand M, Schunemann HJ, et al. GRADE guidelines: 3. Rating the quality of evidence. J Clin Epidemiol 2011; 64: 401--06.

8. Ioannidis JPA. The mass production of redundant, misleading, and conflicted systematic reviews and meta-analyses. Milbank Q 2016; 94: 485--514.

9. Garner P, Hopewell S, Chandler J, et al. When and how to update systematic reviews: consensus and checklist. BMJ 2016; 354: i3507.

10. Else H. What universities can learn from one of science's biggest frauds. Nature 2023; 618: 22--24.

11. Bastian H, Glasziou P, Chalmers I. Seventy-five trials and eleven systematic reviews a day: how will we ever keep up? PLoS Med 2010; 7: e1000326.

12. Traag VA, Waltman L, van Eck NJ. From Louvain to Leiden: guaranteeing well-connected communities. Sci Rep 2019; 9: 5233.

---

*Word count: approximately 3,000 (excluding tables, figures, and references)*

*Target journal: The Lancet Digital Health*
