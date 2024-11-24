# from flask import Flask, render_template, request
# import pandas as pd

# app = Flask(__name__)

# def tabular_to_vw(working_dir, input_file, output_file, feature_index_output_file,
#                   numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace):
#     df = pd.read_csv(f"{working_dir}/{input_file}", sep=sep)
#     df.columns = df.columns.str.replace('"', '').str.strip()
#     feature_index_map = {name: idx for idx, name in enumerate(df.columns)}
#     with open(f"{working_dir}/{feature_index_output_file}", 'w') as feature_map_file:
#         for feature, idx in feature_index_map.items():
#             feature_map_file.write(f"F{idx}: {feature}\n")
#     numerical_indices = [feature_index_map[feat] for feat in numerical_features if feat in feature_index_map]
#     categorical_indices = [feature_index_map[feat] for feat in categorical_features if feat in feature_index_map]
#     label_index = feature_index_map.get(target_label)
#     if label_index is None:
#         raise ValueError(f"Target label '{target_label}' not found in dataset header.")
#     with open(f"{working_dir}/{output_file}", 'w') as vw_file:
#         for _, row in df.iterrows():
#             label = str(row.iloc[label_index]).strip().replace('"', '')
#             label = "1" if label == positive_label else "-1"
#             int_features = [f"F{idx}:{row.iloc[idx]}" for idx in numerical_indices if pd.notnull(row.iloc[idx])]
#             cat_features = [f"F{idx}={row.iloc[idx]}" for idx in categorical_indices if pd.notnull(row.iloc[idx])]
#             if separate_namespace:
#                 vw_file.write(f"{label} |i {' '.join(int_features)} |c {' '.join(cat_features)}\n")
#             else:
#                 vw_file.write(f"{label} |f {' '.join(int_features + cat_features)}\n")

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         try:
#             working_dir = request.form['working_dir']
#             input_file = request.form['input_file']
#             output_file = request.form['output_file']
#             feature_index_output_file = request.form['feature_index_output_file']
#             numerical_features = request.form['numerical_features'].split(',')
#             categorical_features = request.form['categorical_features'].split(',')
#             target_label = request.form['target_label']
#             positive_label = request.form['positive_label']
#             sep = request.form['sep']
#             separate_namespace = 'separate_namespace' in request.form
            
#             tabular_to_vw(working_dir, input_file, output_file, feature_index_output_file,
#                           numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace)
#             return f"VW file generated: {output_file}"
#         except Exception as e:
#             return f"Error: {str(e)}"
#     return render_template('index.html')



from flask import Flask, render_template, request
import os
import pandas as pd

app = Flask(__name__)

# Ensure directories for uploads and outputs exist
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def tabular_to_vw(input_file_path, output_file_path, feature_index_output_path,
                  numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace):
    df = pd.read_csv(input_file_path, sep=sep)
    df.columns = df.columns.str.replace('"', '').str.strip()
    feature_index_map = {name: idx for idx, name in enumerate(df.columns)}
    with open(feature_index_output_path, 'w') as feature_map_file:
        for feature, idx in feature_index_map.items():
            feature_map_file.write(f"F{idx}: {feature}\n")
    numerical_indices = [feature_index_map[feat] for feat in numerical_features if feat in feature_index_map]
    categorical_indices = [feature_index_map[feat] for feat in categorical_features if feat in feature_index_map]
    label_index = feature_index_map.get(target_label)
    if label_index is None:
        raise ValueError(f"Target label '{target_label}' not found in dataset header.")
    with open(output_file_path, 'w') as vw_file:
        for _, row in df.iterrows():
            label = str(row.iloc[label_index]).strip().replace('"', '')
            label = "1" if label == positive_label else "-1"
            int_features = [f"F{idx}:{row.iloc[idx]}" for idx in numerical_indices if pd.notnull(row.iloc[idx])]
            cat_features = [f"F{idx}={row.iloc[idx]}" for idx in categorical_indices if pd.notnull(row.iloc[idx])]
            if separate_namespace:
                vw_file.write(f"{label} |i {' '.join(int_features)} |c {' '.join(cat_features)}\n")
            else:
                vw_file.write(f"{label} |f {' '.join(int_features + cat_features)}\n")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Handle file upload
            uploaded_file = request.files['input_file']
            if uploaded_file.filename == '':
                return "Error: No file selected."

            input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(input_file_path)

            # Generate output file paths
            output_file_name = request.form['output_file']
            feature_index_file_name = request.form['feature_index_output_file']
            output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], output_file_name)
            feature_index_output_path = os.path.join(app.config['OUTPUT_FOLDER'], feature_index_file_name)

            # Collect other form inputs
            numerical_features = request.form['numerical_features'].split(',')
            categorical_features = request.form['categorical_features'].split(',')
            target_label = request.form['target_label']
            positive_label = request.form['positive_label']
            sep = request.form['sep']
            separate_namespace = 'separate_namespace' in request.form

            # Process the file
            tabular_to_vw(input_file_path, output_file_path, feature_index_output_path,
                          numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace)

            return f"<h3>VW file generated successfully!<br>Output file: {output_file_name}</h3>"

        except Exception as e:
            return f"<h3>Error: {str(e)}</h3>"

    return render_template('index.html')





if __name__ == '__main__':
    app.run(debug=True)