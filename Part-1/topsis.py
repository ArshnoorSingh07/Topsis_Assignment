import argparse
import pandas as pd
import numpy as np
import sys

def main():

    parser = argparse.ArgumentParser(description="TOPSIS tool")

    parser.add_argument("input_file")
    parser.add_argument("weights")
    parser.add_argument("impacts")
    parser.add_argument("output_file")

    args = parser.parse_args()

    input_file = args.input_file
    weights = args.weights
    impacts = args.impacts
    output_file = args.output_file

    # READ FILE
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

    # clean empty columns
    df = df.dropna(axis=1, how='all')
    df.columns = df.columns.str.strip()

    # must have at least 3 columns
    if df.shape[1] < 3:
        print("Error: File must have 3 or more columns")
        sys.exit(1)

    criteria_data = df.iloc[:, 1:]

    # convert to numeric
    try:
        criteria_data = criteria_data.astype(float)
    except:
        print("Error: From 2nd column onwards must be numeric")
        sys.exit(1)

    # split weights & impacts
    weights_list = [w.strip() for w in weights.split(',')]
    impacts_list = [i.strip() for i in impacts.split(',')]

    criteria_count = df.shape[1] - 1

    if not (len(weights_list) == len(impacts_list) == criteria_count):
        print("Error: weights, impacts and columns must match")
        sys.exit(1)

    for i in impacts_list:
        if i not in ['+', '-']:
            print("Error: impacts must be + or -")
            sys.exit(1)

    try:
        weights_list = [float(w) for w in weights_list]
    except:
        print("Error: weights must be numeric")
        sys.exit(1)

    # TOPSIS 
    matrix = criteria_data.values

    # normalize
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))

    # multiply weights
    weighted_matrix = norm_matrix * weights_list

    # ideal best & worst
    ideal_best = []
    ideal_worst = []

    for i in range(criteria_count):
        if impacts_list[i] == '+':
            ideal_best.append(weighted_matrix[:, i].max())
            ideal_worst.append(weighted_matrix[:, i].min())
        else:
            ideal_best.append(weighted_matrix[:, i].min())
            ideal_worst.append(weighted_matrix[:, i].max())

    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)

    # distance
    dist_best = np.sqrt(((weighted_matrix - ideal_best)**2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_matrix - ideal_worst)**2).sum(axis=1))

    # score
    scores = dist_worst / (dist_best + dist_worst)

    # correct ranking
    ranks = pd.Series(scores).rank(method='max', ascending=False).astype(int)

    df['Topsis Score'] = scores
    df['Rank'] = ranks

    #SAVE 
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