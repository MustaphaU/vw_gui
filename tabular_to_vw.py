import pandas as pd

def tabular_to_vw(working_dir, input_file, output_file, feature_index_output_file,
                  numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace):
    # Load the dataset
    file_path = f"{working_dir}/{input_file}"
    df = pd.read_csv(file_path, sep=sep)

    # Remove quotes from column names
    df.columns = df.columns.str.replace('"', '').str.strip()

    # Map feature names to indices
    feature_index_map = {name: idx for idx, name in enumerate(df.columns)}

    # Write feature index mappings
    with open(f"{working_dir}/{feature_index_output_file}", 'w') as feature_map_file:
        for feature, idx in feature_index_map.items():
            feature_map_file.write(f"F{idx}: {feature}\n")

    # Indices for numerical and categorical features
    numerical_indices = [feature_index_map[feat] for feat in numerical_features if feat in feature_index_map]
    categorical_indices = [feature_index_map[feat] for feat in categorical_features if feat in feature_index_map]
    label_index = feature_index_map.get(target_label)

    if label_index is None:
        raise ValueError(f"Target label '{target_label}' not found in dataset header.")

    pos_count = 0
    neg_count = 0

    # Write VW formatted data
    with open(f"{working_dir}/{output_file}", 'w') as vw_file:
        for _, row in df.iterrows():
            label = str(row.iloc[label_index]).strip().replace('"', '')

            if label == positive_label:
                pos_count += 1
                label = "1"
            else:
                neg_count += 1
                label = "-1"

            # Numerical features
            int_features = [
                f"F{idx}:{row.iloc[idx]}" for idx in numerical_indices
                if pd.notnull(row.iloc[idx]) and row.iloc[idx] != ""
            ]

            # Categorical features (no filtering for "unknown" or missing values)
            cat_features = [
                f"F{idx}={row.iloc[idx]}" for idx in categorical_indices
                if pd.notnull(row.iloc[idx])
            ]

            if separate_namespace:
                vw_file.write(f"{label} |i {' '.join(int_features)} |c {' '.join(cat_features)}\n")
            else:
                vw_file.write(f"{label} |f {' '.join(int_features + cat_features)}\n")

    print(f"Number of negative examples: {neg_count}")
    print(f"Number of positive examples: {pos_count}")
    print(f"Generated files in {working_dir}: {output_file} and {feature_index_output_file}")



# Example Usage
working_dir = "data_py"
input_file = "bank-full.csv"
output_file = "train.vw"
feature_index_output_file = "featuresIndexes.txt"

numerical_features = ["age", "balance", "duration", "campaign", "pdays", "previous"]
categorical_features = ["job", "marital", "education", "default", "housing", "contact", "day", "month", "poutcome"]
target_label = "y"
positive_label = "yes"
sep = ";"
separate_namespace = True

tabular_to_vw(working_dir, input_file, output_file, feature_index_output_file,
              numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace)
