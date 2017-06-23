
# hf.futuretex.sim

Simulations on quantitative metrics in BHT productions

This software attempts to simulate the efficiency and quality of BHT production,
depending on variable input parameters on bast fiber geometry and selection.

We aim for predictions of the following BHT metrics:

  * thickness
  * width
  * joins per meter
  * length

We also predict variability for those metrics.  We make that prediction
dependent on the properties of the used bast fibers:

  * length distribution
  * head widths distribution
  * width change over length
  * head thickness distriution
  * thickness change over length

Given the geometries of the bast peeler, we assume the followin min/max
constraints to apply:

| metric    | symbol | unit |    min |     max |    mean |   steps |
| :-------- | -----: | ---: | -----: | ------: | ------: | ------: |
| length    |      L |   mm | 500.00 | 1600.00 | 1000.00 |    1.00 |
| width     |      W |   mm |   0.00 |   22.00 |   10.00 |    0.10 |
| thickness |      T |   mm |   0.10 |    0.70 |    0.45 |    0.01 |

We will model different discrete distributions of those metrics. Step 


The process of BHT
creation is modeled on stitching, with specific stitching parameters derived
from the technology demonstrater used at HFU:

  * max throughput: 33mm/s, 16stiches/s (0.48 stitches/mm)
  * BHT width: 5mm


