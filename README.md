# uavsar-coherence

Exploring the controlling factors of L-band coherence in seasonal snowpacks using time-series of UAVSAR, an aerial L-band platform from NASA, over multiple sites along with extensive field, modeling, and lidar datasets. Pushing towards an article in Cryosphere answering the following research questions:

1. How do snow depth, depth change, incidence angle, vegetation, and wetness impact the coherence of L-band InSAR images in seasonal snow?
2. Can we use our temporal decay model for L-band coherence to estimate coherence in seasonal snow coverage and snow-water retrieval uncertainties for the upcoming NISAR satellite mission?

## Project To-Do

- [ ] Introduction
  - [ ] Write Significance
  - [ ] Write Coherence InSAR Theory
  - [ ] Write InSAR SWE retrievals Theory
  - [ ] Write Previous Work
    - [ ] Identify most relevant previous work papers
      - [ ] L-band coherence generally - trees, incidence angle
      - [ ] L-band coherence in snow - modeling, stations, ALOS, ELI
    - [ ] Outline
    - [ ] Write
    
- [ ] Methods
  - [ ] Field site descriptions
  - [ ] Datasets
    - [ ] snowpit dataset
      - [ ] find DOI
    - [ ] depths dataset
      - [ ] find DOI
    - [ ] interval board dataset
      - [ ] find DOI
    - [ ] Snotels
    - [ ] Lidar snowdepths
    - [ ] USGS land cover
    - [ ] UAVSAR dataset
      - [ ] JPL processing
      - [ ] my processing
  - [ ] Comparison to in-situ datasets
    - [ ] Snow depth (snowpits, depths, snotels) (pearson r, linear model)
    - [ ] Snow wetness (snowpits) (mean coherence for wet vs dry, p-value)
    - [ ] Snow depth change (snotels, interval boards) (pearson r, linear model)
  - [ ] Comparison to lidar snowdepth datasets
    - [ ] (pearson r, linear model)
    - [ ] Controlling for trees, incidence angle
  - [ ] Comparison to SNOWMODEL
    - [ ] Depth vs coherence (pearson r, linear model)
    - [ ] Wetness vs coherence (pearson r, linear model)
    - [ ] Depth change vs coherence (pearson r, linear model)
  - [ ] NISAR estimate winter coherence
    - [ ] Solving temporal decay model at each study site
    - [ ] Set t = 12
    - [ ] Plot maps of estimated NISAR coherence
    - [ ] Random forest to solve NISAR coherence with USGS tree density, landcover, SNOWMODEL depth and wetness
    - [ ] Solve random forest over western US
  - [ ] SWE uncertainty
    - [ ] use random forest results of coherence to solve standard deviation of phase
    - [ ] insert standard deviation of phase into SWE retrieval equations
    - [ ] plot NISAR SWE uncertainty over western US
  
  - [ ] Results
    - [ ] Field Datasets
      - [ ] Facet plot (scatter or box) of UAVSAR coherence vs snow depth (all sources), snow depth
      change (all source), snow wetness (all sources), incidence angle with p, r, linear model (for significant).
    - [ ] Comparison of lidar snow depth
      - [ ] Scatter plot of UAVSAR coherence vs lidar snow depth for tree-free, treed
      with r, p
    - [ ] SNOWMODEL comparison
      - [ ] facet plot of depth, wetness, depth change to coherence (r, p, linear model)
    - [ ] NISAR estimated coherence
      - [ ] maps of estimated NISAR coherence (left) with temporal decay model on right (t - x axis, coherence - y)
      with RMSE
      - [ ] random forest feature importances for coherence
      - [ ] NISAR estimated coherence over western US using data from January
    - [ ] SWE uncertainty
      - [ ] map of SWE uncertainty for US
  
  - [ ] Discussion
    - [ ] How does snow depth impact L-band coherence?
    - [ ] How does snow depth change impact L-band coherence?
    - [ ] How does snow wetness impact L-band coherence?
    - [ ] Where do we expect reasonable NISAR coherence over the western US in winter?
    - [ ] What is the uncertainty associated with SWE retrievals from NISAR?
    
  - [ ] Conclusion
