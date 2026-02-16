import sys
import os
import pandas as pd
import numpy as np


def show_error(text):
    print("Error:", text)
    sys.exit()


def main():

    if len(sys.argv) != 5:
        show_error("Usage: python topsis.py input_file weights impacts output_file")

    input_file = sys.argv[1]
    weights_text = sys.argv[2]
    impacts_text = sys.argv[3]
    output_file = sys.argv[4]

    if not os.path.exists(input_file):
        show_error("Input file not found")

    # read csv or xlsx
    try:
        if input_file.endswith(".csv"):
            df = pd.read_csv(input_file)
        elif input_file.endswith(".xlsx"):
            df = pd.read_excel(input_file)
        else:
            show_error("Only CSV or XLSX supported")
    except:
        show_error("Problem while reading file")

    if df.shape[1] < 3:
        show_error("File must have at least 3 columns")

    values = df.iloc[:, 1:]

    # convert to numeric
    try:
        values = values.astype(float)
    except:
        show_error("All criteria columns must be numeric")

    # weights and impacts
    try:
        weights = [float(w) for w in weights_text.split(',')]
        impacts = impacts_text.split(',')
    except:
        show_error("Weights and impacts must be comma separated")

    if len(weights) != values.shape[1] or len(impacts) != values.shape[1]:
        show_error("Weights, impacts and columns count must match")

    if any(i not in ['+', '-'] for i in impacts):
        show_error("Impacts must be + or -")

    # -------- TOPSIS --------

    # normalize column-wise
    norm_matrix = values / np.sqrt((values ** 2).sum(axis=0))

    weighted_matrix = norm_matrix * weights

    best_ref = []
    worst_ref = []

    for i in range(len(impacts)):
        col = weighted_matrix.iloc[:, i]
        if impacts[i] == '+':
            best_ref.append(col.max())
            worst_ref.append(col.min())
        else:
            best_ref.append(col.min())
            worst_ref.append(col.max())

    best_ref = np.array(best_ref)
    worst_ref = np.array(worst_ref)

    dist_best = np.sqrt(((weighted_matrix - best_ref) ** 2).sum(axis=1))
    dist_worst = np.sqrt(((weighted_matrix - worst_ref) ** 2).sum(axis=1))

    score = dist_worst / (dist_best + dist_worst)

    df["Topsis Score"] = score
    df["Rank"] = score.rank(method='max', ascending=False).astype(int)

    # save output
    try:
        if output_file.endswith(".csv"):
            df.to_csv(output_file, index=False)
        elif output_file.endswith(".xlsx"):
            df.to_excel(output_file, index=False)
        else:
            show_error("Output must be CSV or XLSX")
    except:
        show_error("Problem saving file")

    print("Done. Result saved to", output_file)


if __name__ == "__main__":
    main()
