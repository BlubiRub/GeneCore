from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# function to create plot
def create_plot():
    # import data
    variante = pd.read_csv('training_variants.csv')

    # Gene with the most variations
    top_gene = (
        variante.groupby('Gene')
        .size()
        .reset_index(name='ct')
        .query('ct > 40')
    )

    # create plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=top_gene,
        x='ct',
        y=top_gene['Gene'].str.strip(),
        size=4,
        legend=False,
    )
    plt.xlabel("Frequency")
    plt.ylabel("Gene")
    plt.title("Gene with the Most Variants")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # save plot
    plot_path = os.path.join('static', 'plot.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

@app.route("/")
def index():
    plot_path = create_plot()
    return render_template("index.html", plot_url=plot_path)

if __name__ == "__main__":
    app.run(debug=True)
