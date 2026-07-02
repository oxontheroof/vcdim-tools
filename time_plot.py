
# import matplotlib.pyplot as plt
from io_data import log_to_dict, get_all_files
from typing import Dict


# Compare execution times from the logs 
# first : check consistency

# then : find a way to plot the times properly
# e.g : given a 'base algorithm', order its instances by times, and plot other on it
# 
# 
# 


ground_truth : Dict = list(map(log_to_dict, get_all_files("../test-timings/ground_truth", 0)))


def check_consistency(alg_output : Dict) -> bool:
    """ check if alg_output is consistent with the base """
    # print(f"{alg_output = }")
    # print(f"{ground_truth = }")

    for k in alg_output.keys():
        alg_vc = alg_output[k]['vc-dim']
        checked = False
        for gt_dict in ground_truth:    
            try:
                gt_vc = gt_dict[k]['vc-dim']
                checked = True
                if gt_vc != alg_vc:
                    print(f" Inconsistency : found distinct vc-dims at {k} ({gt_vc = } vs {alg_vc = })")
                    return False
            except KeyError:
                # we do nothing at this time : the data was not checked for one dict
                pass

        if not checked:
            print(f"graph {k} was not found in ground_truth; cannot check consistency")

    return True


def check_ground_truth_consistency():
    """ This checks whether the logs in ground_truth are consistent (really necessary) """
    print(f"Found {len(ground_truth)} outputs as ground-truth ")
    
    for gt_dict in ground_truth:
        if not check_consistency(gt_dict):
            print(" --- WARNING : ground_truth is not consistent ---")
            return
    print(" --- INFO : succesfully checked ground_truth consistency ---")
    


def plot_ordered(alg_output, base_output):
    """ plots both exec times, base on decreasing times of base_output """
    ...


def main():
    # just for sanity
    check_ground_truth_consistency()


    # e.g, to check if main_01 produced results in accordance with main_02 :
    # alg_output = log_to_dict('../test-timings/safe/timetest_main_01.txt')
    # check_consistency(alg_output)


if __name__ == '__main__':
    main()

