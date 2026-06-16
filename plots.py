
# import measures
import matplotlib.pyplot as plt


# ============================== #
# READ INPUT 

def read_data_from_file(filename):
    """ returns a dict """
    with open(filename, 'r') as file:
        header = map(lambda s : s[1:-1], file.readline().split(" ")[1:])
        data = {hi: [] for hi in header}  # eliminating brackets '[...]'

        # we assume the first column is a string (filename), and convert the others to strings

        for ln in file.readlines():
            cols = ln.split(" ")
            data[header[0]].append(cols[0])
            for i, c in enumerate(cols[1:]):
                data[header[i + 1]].append(int(c))

    return data



# ============================== #
# MAIN PLOTS




