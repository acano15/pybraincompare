'''
qa.py: part of pybraincompare package
Functions to check quality of statistical maps

'''
import numpy as np
import nibabel
from nipy.algorithms.registration.histogram_registration import HistogramRegistration

'''Metrics:
Extract metrics from the header
'''
def header_metrics(image):
  mr_affine = image.get_affine()
  mr_shape = image.shape
  header = image.get_header()
  return {"shape":mr_shape,"affine":mr_affine,"header":header}

'''Central tendency:
standard measures of central tendency and variance
'''
def central_tendency(data):
  if isinstance(data,nibabel.nifti1.Nifti1Image):
    data = data.get_data()
  mr_mean = data.mean()
  mr_var = data.var()
  mr_std = data.std()
  mr_med = np.median(data)
  return {"std":mr_std,"var":mr_var,"mean":mr_mean,"med":mr_med}


'''Normality across nonzero
normality of the distribution across non-zero voxels
'''
#def normality_across_nonzero(data,out_png=None):
#  x = np.c_[data]
#  enn = NormalEmpiricalNull(x)
#  enn.threshold(verbose=True)

'''Outliers
outliers (e.g., more than ~6 SD from the mean, maybe less depending on the action)
'''
def outliers(masked_data,n_std=6):
  mean = masked_data.mean()
  std = masked_data.std()
  six_dev_up = mean + n_std * std
  six_dev_down = mean - n_std*std
  high_outliers = len(np.where(masked_data>=six_dev_up)[0])
  low_outliers = len(np.where(masked_data<=six_dev_down)[0])
  return high_outliers,low_outliers

'''Mutual Information Against Standard
# mutual information against some mean map that is representative of an # expectation [really low --> something is funky]
'''
def mutual_information_against_standard(mr,mean_image):
  mi = HistogramRegistration(mean_image, mr, similarity='nmi')  
  T = mi.optimize("affine")
  return mi.explore(T)[0][0]


'''Estimate thresholded
We basically check to see if number of zero voxels exceeds some percentage (not thresholded)
'''
def get_percent_nonzero(masked_in):
  number_zeros = len(np.where(masked_in==0)[0])
  nonzeros = len(masked_in) - number_zeros
  return nonzeros / float(len(masked_in))

'''Is a nifti image thresholded?
Adopted from chrisfilo for neurovault
Threshold should be the percentage of voxels we want "good"
Returns True/False and ratio of good voxels
'''
def is_thresholded(nii_obj,brain_mask,threshold=0.95):
  data = nii_obj.get_data()
  # Set everything outside brain mask to zero
  data[brain_mask.get_data()==0] = 0
  zero_mask = (data == 0)
  nan_mask = (np.isnan(data))
  inside_brain = brain_mask.get_data().astype("bool")
  missing_mask = zero_mask | nan_mask
  missing_inside_brain = missing_mask & inside_brain
  ratio_bad = float(missing_inside_brain.sum())/float(inside_brain.sum())
  ratio_good = 1-ratio_bad
  if ratio_good < threshold:
      return (True, ratio_good)
  else:
      return (False, ratio_good)

'''Are there only positive values?'''
def is_only_positive(nii_obj):
  lower,upper = get_voxel_range(nii_obj)
  if lower>=0: return True
  else: return False

'''Get the maximum and minimum value in the image'''
def get_voxel_range(nii_obj):
  data = nii_obj.get_data()
  return (np.min(data), np.max(data))
  
'''Count voxels in and outside the mask'''
def count_voxels(masked_in,masked_out):
  # Here we are assuming a value of 0 == not in mask
  count_in = len(masked_in[masked_in!=0])
  count_out = len(masked_out[masked_out!=0])
  return count_in,count_out

