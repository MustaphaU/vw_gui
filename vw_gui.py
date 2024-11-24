import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None




def tabular_to_vw(working_dir, input_file, output_file, feature_index_output_file,
                  numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace):
    df = pd.read_csv(f"{working_dir}/{input_file}", sep=sep)
    df.columns = df.columns.str.replace('"', '').str.strip()
    feature_index_map = {name: idx for idx, name in enumerate(df.columns)}
    with open(f"{working_dir}/{feature_index_output_file}", 'w') as feature_map_file:
        for feature, idx in feature_index_map.items():
            feature_map_file.write(f"F{idx}: {feature}\n")
    numerical_indices = [feature_index_map[feat] for feat in numerical_features if feat in feature_index_map]
    categorical_indices = [feature_index_map[feat] for feat in categorical_features if feat in feature_index_map]
    label_index = feature_index_map.get(target_label)
    if label_index is None:
        raise ValueError(f"Target label '{target_label}' not found in dataset header.")
    pos_count = 0
    neg_count = 0
    with open(f"{working_dir}/{output_file}", 'w') as vw_file:
        for _, row in df.iterrows():
            label = str(row.iloc[label_index]).strip().replace('"', '')
            if label == positive_label:
                pos_count += 1
                label = "1"
            else:
                neg_count += 1
                label = "-1"
            int_features = [
                f"F{idx}:{row.iloc[idx]}" for idx in numerical_indices
                if pd.notnull(row.iloc[idx]) and row.iloc[idx] != ""
            ]
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

def generate_vw_file():
    try:
        working_dir = working_dir_entry.get()
        input_file = input_file_entry.get()
        output_file = output_file_entry.get()
        feature_index_output_file = feature_index_file_entry.get()
        numerical_features = numerical_features_entry.get().split(",")
        categorical_features = categorical_features_entry.get().split(",")
        target_label = target_label_entry.get()
        positive_label = positive_label_entry.get()
        sep = sep_entry.get()
        separate_namespace = namespace_var.get()
        
        tabular_to_vw(working_dir, input_file, output_file, feature_index_output_file,
                      numerical_features, categorical_features, target_label, sep, positive_label, separate_namespace)
        messagebox.showinfo("Success", f"VW file generated successfully!\nOutput file: {output_file}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create GUI
root = tk.Tk()
root.title("VW File Generator")


# Input Fields with Descriptions
tk.Label(root, text="Working Directory:").grid(row=0, column=0, sticky="w")
working_dir_entry = tk.Entry(root, width=50)
working_dir_entry.grid(row=0, column=1)
tk.Label(root, text="Path to the folder containing your dataset.").grid(row=0, column=2, sticky="w")
Tooltip(working_dir_entry, "The folder where your dataset is stored.")

tk.Label(root, text="Input File Name:").grid(row=1, column=0, sticky="w")
input_file_entry = tk.Entry(root, width=50)
input_file_entry.grid(row=1, column=1)
tk.Label(root, text="The name of your input dataset file.").grid(row=1, column=2, sticky="w")
Tooltip(input_file_entry, "Example: bank-full.csv")

tk.Label(root, text="Output File Name:").grid(row=2, column=0, sticky="w")
output_file_entry = tk.Entry(root, width=50)
output_file_entry.grid(row=2, column=1)
tk.Label(root, text="Name for the output VW file.").grid(row=2, column=2, sticky="w")
Tooltip(output_file_entry, "Example: train.vw")

tk.Label(root, text="Feature Index File Name:").grid(row=3, column=0, sticky="w")
feature_index_file_entry = tk.Entry(root, width=50)
feature_index_file_entry.grid(row=3, column=1)
tk.Label(root, text="Name for the feature index file.").grid(row=3, column=2, sticky="w")
Tooltip(feature_index_file_entry, "Example: featuresIndexes.txt")

tk.Label(root, text="Numerical Features:").grid(row=4, column=0, sticky="w")
numerical_features_entry = tk.Entry(root, width=50)
numerical_features_entry.grid(row=4, column=1)
tk.Label(root, text="Comma-separated list of numerical feature names.").grid(row=4, column=2, sticky="w")
Tooltip(numerical_features_entry, "Example: age,balance,duration")

tk.Label(root, text="Categorical Features:").grid(row=5, column=0, sticky="w")
categorical_features_entry = tk.Entry(root, width=50)
categorical_features_entry.grid(row=5, column=1)
tk.Label(root, text="Comma-separated list of categorical feature names.").grid(row=5, column=2, sticky="w")
Tooltip(categorical_features_entry, "Example: job,marital,education")

tk.Label(root, text="Target Label:").grid(row=6, column=0, sticky="w")
target_label_entry = tk.Entry(root, width=50)
target_label_entry.grid(row=6, column=1)
tk.Label(root, text="The name of the column with target labels.").grid(row=6, column=2, sticky="w")
Tooltip(target_label_entry, "Example: y")

tk.Label(root, text="Positive Label:").grid(row=7, column=0, sticky="w")
positive_label_entry = tk.Entry(root, width=50)
positive_label_entry.grid(row=7, column=1)
tk.Label(root, text="The value of the target label for positive examples.").grid(row=7, column=2, sticky="w")
Tooltip(positive_label_entry, "Example: yes")

tk.Label(root, text="Separator:").grid(row=8, column=0, sticky="w")
sep_entry = tk.Entry(root, width=10)
sep_entry.grid(row=8, column=1, sticky="w")
tk.Label(root, text="Column separator (e.g., , or ;).").grid(row=8, column=2, sticky="w")
Tooltip(sep_entry, "Example: ;")

namespace_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Separate Namespaces", variable=namespace_var).grid(row=9, column=1, sticky="w")
Tooltip(tk.Checkbutton(root), "Separate numerical and categorical features into namespaces.")

# Generate Button
generate_button = tk.Button(root, text="Generate VW File", command=generate_vw_file)
generate_button.grid(row=10, column=1, pady=10, sticky="e")

# Run GUI
root.mainloop()

# # Input Fields
# tk.Label(root, text="Working Directory:").grid(row=0, column=0, sticky="w")
# working_dir_entry = tk.Entry(root, width=50)
# working_dir_entry.grid(row=0, column=1)

# tk.Label(root, text="Input File Name:").grid(row=1, column=0, sticky="w")
# input_file_entry = tk.Entry(root, width=50)
# input_file_entry.grid(row=1, column=1)

# tk.Label(root, text="Output File Name:").grid(row=2, column=0, sticky="w")
# output_file_entry = tk.Entry(root, width=50)
# output_file_entry.grid(row=2, column=1)

# tk.Label(root, text="Feature Index File Name:").grid(row=3, column=0, sticky="w")
# feature_index_file_entry = tk.Entry(root, width=50)
# feature_index_file_entry.grid(row=3, column=1)

# tk.Label(root, text="Numerical Features (comma-separated):").grid(row=4, column=0, sticky="w")
# numerical_features_entry = tk.Entry(root, width=50)
# numerical_features_entry.grid(row=4, column=1)

# tk.Label(root, text="Categorical Features (comma-separated):").grid(row=5, column=0, sticky="w")
# categorical_features_entry = tk.Entry(root, width=50)
# categorical_features_entry.grid(row=5, column=1)

# tk.Label(root, text="Target Label:").grid(row=6, column=0, sticky="w")
# target_label_entry = tk.Entry(root, width=50)
# target_label_entry.grid(row=6, column=1)

# tk.Label(root, text="Positive Label:").grid(row=7, column=0, sticky="w")
# positive_label_entry = tk.Entry(root, width=50)
# positive_label_entry.grid(row=7, column=1)

# tk.Label(root, text="Separator (e.g., ; or ,):").grid(row=8, column=0, sticky="w")
# sep_entry = tk.Entry(root, width=10)
# sep_entry.grid(row=8, column=1, sticky="w")

# namespace_var = tk.BooleanVar(value=True)
# tk.Checkbutton(root, text="Separate Namespaces", variable=namespace_var).grid(row=9, column=1, sticky="w")

# # Generate Button
# generate_button = tk.Button(root, text="Generate VW File", command=generate_vw_file)
# generate_button.grid(row=10, column=1, pady=10, sticky="e")

# # Run GUI
# root.mainloop()
