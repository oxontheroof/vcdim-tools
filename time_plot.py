
import matplotlib.pyplot as plt
from io_data import log_to_dict

# Compare execution times from the logs 
# first : check consistency

# then : find a way to plot the times properly
# e.g : given a 'base algorithm', order its instances by times, and plot other on it
# 
# 
# 


base_ground_truth = ...  # somehow plot


def check_consistency(alg_output, base_output=base_ground_truth):
    # check if alg_output is consistent with the base
    ...


def plot_ordered(alg_output, base_output):
    """ plots both exec times, base on decreasing times of base_output """
    ...


def main():
    ...

