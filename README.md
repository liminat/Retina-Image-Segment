# Retina-Image-Segmentation

Java implementation of vasculature segmentation on retina image based on the [Hoover](http://www.uhu.es/retinopathy/General/000301IEEETransMedImag.pdf)'s and [Zhang](http://azadproject.ir/wp-content/uploads/2014/12/2009-Retinal-Vessel-Extraction-by-Matched-Filter-with-First-Order-Derivative-of-Gaussian.pdf)'s works.

## Approach: Matched Filter with First-Order Derivative of Gaussian (FDoG) and Genetic Algorithm (GA) Optimization
The approach is based on [Zhang](http://azadproject.ir/wp-content/uploads/2014/12/2009-Retinal-Vessel-Extraction-by-Matched-Filter-with-First-Order-Derivative-of-Gaussian.pdf)'s work.

### Usage
```Python
python mfr.py RETINAL_IMAGE MASK_IMAGE
```
Note: the mask image represents the outside area. 

Optional: To obtain a better set of hyper-parameters, I also provide the code of genetic algorithm for parameter optimization. 
```Python
python ga.py RETINAL_IMAGE GROUND_TRUTH_IMAGE
```

### Results (Image from [DRIVE](https://www.isi.uu.nl/Research/Databases/DRIVE/) database)
Original image.  

![ ](images/21_training.png). 

Result of Gaussian Matched Filter. 

![ ](images/DOG_21_training.png). 

Result of First Order Derivative of Gaussian. 

![ ](images/FDOG21_training.png). 

Final segmentation.  

![ ](images/Final_21_training.png).  

## Approach: Piecewise Threshold Probing of the Matched Filter Response
This approach is based on [Hoover](http://www.uhu.es/retinopathy/General/00030