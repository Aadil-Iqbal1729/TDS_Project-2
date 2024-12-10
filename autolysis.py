from dotenv import load_dotenv  # Add this import to load the .env file
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai



# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
openai.api_key = os.getenv("AIPROXY_TOKEN")  # This will now use the token from the .env file

def read_csv(filename):
    """Read the CSV file and return a DataFrame."""
    try:
        df = pd.read_csv(filename, encoding="utf-8")
        print(f"Dataset loaded: {filename}")
        return df
    except UnicodeDecodeError:
        print(f"Encoding issue detected with {filename}. Trying 'latin1'.")
        return pd.read_csv(filename, encoding="latin1")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        exit()

def analyze_data(df):
    """Perform basic analysis on the dataset."""
    analysis = {}
    analysis["shape"] = df.shape
    analysis["columns"] = df.columns.tolist()
    analysis["missing_values"] = df.isnull().sum().to_dict()
    analysis["summary_statistics"] = df.describe(include="all").to_dict()
    return analysis

def visualize_data(df, output_prefix):
    """Generate visualizations for the dataset."""
    charts = []
    
    # Example 1: Correlation Heatmap (if numeric data exists)
    numeric_columns = df.select_dtypes(include=["number"]).columns
    if len(numeric_columns) > 0:
        plt.figure(figsize=(8, 6))
        sns.heatmap(df[numeric_columns].corr(), annot=True, cmap="coolwarm", fmt=".2f")
        heatmap_file = f"{output_prefix}_heatmap.png"
        plt.savefig(heatmap_file)
        charts.append(heatmap_file)
        plt.close()

    # Example 2: Bar Plot for the first categorical column
    categorical_columns = df.select_dtypes(include=["object"]).columns
    if len(categorical_columns) > 0:
        plt.figure(figsize=(10, 6))
        df[categorical_columns[0]].value_counts().head(10).plot(kind="bar", color="skyblue")
        barplot_file = f"{output_prefix}_barplot.png"
        plt.savefig(barplot_file)
        charts.append(barplot_file)
        plt.close()

    return charts
openai.api_key = os.getenv("AIPROXY_TOKEN")
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
def narrate_story(analysis, charts, filename):
    """Use GPT-4o-Mini to narrate a story about the analysis."""
    summary_prompt = f"""
    I analyzed a dataset from {filename}. It has the following details:
    - Shape: {analysis['shape']}
    - Columns: {analysis['columns']}
    - Missing Values: {analysis['missing_values']}
    - Summary Statistics: {analysis['summary_statistics']}

    Write a short summary of the dataset, key insights, and recommendations. Refer to the charts where necessary.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use the specific model
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.7
        )
        return response.choices[0].message['content']
    except openai.error.AuthenticationError:
        return "Authentication failed. Check your token and environment setup."
    except Exception as e:
        return f"Story generation failed: {e}"




def save_markdown(story, charts, output_file):
    """Save the narrated story and chart references to a README.md file."""
    with open(output_file, "w") as f:
        f.write("# Analysis Report\n\n")
        f.write(story + "\n\n")
        for chart in charts:
            f.write(f"![Chart](./{chart})\n")

def main():
    # Define the folder path
    folder_path = r"C:\Users\aadil\OneDrive\Desktop\aadil\TDS-2"

    # Change to the specified folder
    try:
        os.chdir(folder_path)
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {e}")
        return
    
    # Automatically process all CSV files in the folder
    csv_files = [f for f in os.listdir() if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in the directory.")
        return
    
    for filename in csv_files:
        print(f"Processing {filename}...")
        
        # Load dataset
        df = read_csv(filename)
        
        # Analyze dataset
        analysis = analyze_data(df)
        
        # Visualize data
        output_prefix = filename.split(".")[0]
        charts = visualize_data(df, output_prefix)
        
        # Narrate story
        story = narrate_story(analysis, charts, filename)
        
        # Save README.md
        readme_file = f"README_{output_prefix}.md"
        save_markdown(story, charts, readme_file)
        print(f"Analysis completed for {filename}. Check {readme_file} and charts.")

if __name__ == "__main__":
    main()
