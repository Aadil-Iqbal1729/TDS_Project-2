
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai
from sklearn.cluster import KMeans

# Set your OpenAI API key
#openai.api_key = ""
import os

os.environ["OPENAI_API_KEY"] = "API_KEY"

from google.colab import files
import pandas as pd

# Upload your CSV file
uploaded = files.upload()

# Load the CSV into a Pandas DataFrame
filename = list(uploaded.keys())[0]
df = pd.read_csv(filename)
print(f"Dataset loaded: {filename}")

def analyze_data(df):
    """Perform basic analysis on the dataset."""
    analysis = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "missing_values": df.isnull().sum().to_dict(),
        "summary_statistics": df.describe(include="all").to_dict()}
    return analysis

analysis = analyze_data(df)
print(analysis)

def advanced_analysis(df):
    """Perform advanced analyses like outlier detection and clustering."""
    insights = {}

    # Outlier detection using IQR
    numeric_columns = df.select_dtypes(include=["number"]).columns
    if not numeric_columns.empty:
        outliers = {}
        for col in numeric_columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers[col] = ((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum()
        insights["outliers"] = outliers

    # Clustering using KMeans (if applicable)
    if len(numeric_columns) > 1:
        kmeans = KMeans(n_clusters=3, random_state=42).fit(df[numeric_columns].dropna())
        insights["clusters"] = pd.Series(kmeans.labels_).value_counts().to_dict()

    return insights

advanced = advanced_analysis(df)
print(advanced)

def visualize_data(df, output_prefix):
    """Generate visualizations for the dataset."""
    charts = []

    # Correlation Heatmap
    numeric_columns = df.select_dtypes(include=["number"]).columns
    if not numeric_columns.empty:
        plt.figure(figsize=(5.12, 5.12))
        sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm")
        heatmap_file = f"{output_prefix}_heatmap.png"
        plt.savefig(heatmap_file, dpi=300)
        charts.append(heatmap_file)
        plt.close()

    # Bar Plot for the first categorical column
    categorical_columns = df.select_dtypes(include=["object"]).columns
    if not categorical_columns.empty:
        plt.figure(figsize=(5.12, 5.12))
        df[categorical_columns[0]].value_counts().head(10).plot(kind="bar")
        barplot_file = f"{output_prefix}_barplot.png"
        plt.savefig(barplot_file, dpi=300)
        charts.append(barplot_file)
        plt.close()

    return charts

charts = visualize_data(df, "output")
print("Generated charts:", charts)

import openai
import os

# Set the API base and your AIPROXY_TOKEN
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
os.environ["OPENAI_API_KEY"] = "API_KEY"
def narrate_story(analysis, advanced, charts, filename):
    """Use GPT to narrate a story about the analysis."""
    summary_prompt = f"""
    I analyzed a dataset from {filename}. Here are the details:
    - Shape: {analysis['shape']}
    - Columns: {analysis['columns']}
    - Missing Values: {analysis['missing_values']}
    - Summary Statistics: {analysis['summary_statistics']}
    - Outliers Detected: {advanced.get('outliers', 'Not computed')}
    - Cluster Analysis: {advanced.get('clusters', 'Not computed')}

    Based on these insights, write a story summarizing the data, key findings, and recommendations. Refer to the charts where necessary.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Supported model for chat completion
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.7
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        return f"An error occurred: {str(e)}"

# Example input
filename = "example_dataset.csv"  # Replace with your actual filename
story = narrate_story(analysis, advanced, charts, filename)
print(story)

def save_markdown(story, charts, output_file):
    """Save the narrated story and chart references to a README.md file."""
    with open(output_file, "w") as f:
        f.write("# Analysis Report\n\n")
        f.write(story + "\n\n")
        for chart in charts:
            f.write(f"![Chart](./{chart})\n")

save_markdown(story, charts, "README.md")
print("Analysis saved to README.md")