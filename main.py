import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# import csv
variante = pd.read_csv("training_variants.csv")

# most occuring variations
variation_occurency = (
    variante.groupby("Variation")
    .size()
    .reset_index(name="ct")
    .sort_values(by="ct", ascending=False)
)

# print most occuring
print(variation_occurency.head())

# genes with the most variations
top_gene = (
    variante.groupby("Gene")
    .size()
    .reset_index(name="ct")
    .query("ct > 40")
)

# print genes with most variations
print(top_gene.head())

# plot data
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=top_gene,
    x="ct",
    y=top_gene["Gene"].str.strip(),
    size=4,
    legend=False,
)
plt.xlabel("Frequency")
plt.ylabel("Gene")
plt.title("Gene with the Most Variants")
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()
