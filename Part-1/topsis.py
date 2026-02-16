import argparse
import pandas as pd
import numpy as np
import sys

def main():

    # taking command line inputs
    parser = argparse.ArgumentParser(description="TOPSIS program")

    parser.add_argument("input_file")
    parser.add_argument("weights")
    parser.add_argument("impacts")
    parser.add_argument("output_file")

    args = parser.parse_args()

    input_file = args.input_file
    weights = args.weights
    impacts = args.impacts
    output_file = args.output_file

    # -------- read file --------
    try:
        if input_file.endswith(".csv"):
            df = pd.read_csv(input_file)
        elif input_file.endswith(".xlsx"):
            df = pd.read_excel(input_file)
        else:
            print("Error: Only CSV or XLSX supported")
            sys.exit(1)
    except FileNotFoundError:
        print("Error: File not found")
        sys.exit(1)

    # remove empty columns
    df = df.dropna(axis=1, how='all')
    df.columns = df.columns.str.strip()

    # must have at least 3 columns
    if df.shape[1] < 3:
        print("Error: File must contain 3 or more columns")
        sys.exit(1)

    # first column = names, rest numeric
    data = df.iloc[:, 1:]

    if data.apply(pd.to_numeric, errors='coerce').isnull().values.any():
        print("Error: From 2nd column onwards must be numeric")
        sys.exit(1)

    # split weights and impacts
    weights_list = weights.split(',')
    impacts_list = impacts.split(',')

    n = df.shape[1] - 1

    # check counts match
    if not (len(weights_list) == len(impacts_list) == n):
        print("Error: Weights, impacts and columns must be same count")
        sys.exit(1)

    # impacts must be + or -
    for i in impacts_list:
        if i not in ['+', '-']:
            print("Error: Impacts must be + or -")
            sys.exit(1)

    # convert weights to float
    try:
        weights_list = [float(i) for i in weights_list]
    except:
        print("Error: Weights must be numeric")
        sys.exit(1)

    # -------- TOPSIS steps --------
    matrix = data.astype(float).values

    # normalize
    norm = matrix / np.sqrt((matrix**2).sum(axis=0))

    # multiply weights
    weighted = norm * weights_list

    # ideal best and worst
    best = []
    worst = []

    for i in range(n):
        if impacts_list[i] == '+':
            best.append(weighted[:, i].max())
            worst.append(weighted[:, i].min())
        else:
            best.append(weighted[:, i].min())
            worst.append(weighted[:, i].max())

    best = np.array(best)
    worst = np.array(worst)

    # distance
    d_best = np.sqrt(((weighted - best)**2).sum(axis=1))
    d_worst = np.sqrt(((weighted - worst)**2).sum(axis=1))

    # score
    score = d_worst / (d_best + d_worst)

    # rank
    rank = score.argsort()[::-1] + 1

    df["Topsis Score"] = score
    df["Rank"] = rank

    # save output
    try:
        if output_file.endswith(".csv"):
            df.to_csv(output_file, index=False)
        elif output_file.endswith(".xlsx"):
            df.to_excel(output_file, index=False)
        else:
            print("Error: Output must be csv or xlsx")
            sys.exit(1)
    except:
        print("Error saving file")
        sys.exit(1)

    print("Result saved to", output_file)


if __name__ == "__main__":
    main()
