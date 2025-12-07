import pandas as pd

stats = pd.read_csv("2022-2023 NBA Player Stats - Regular.csv",encoding="latin-1", sep=";",)
salaries = pd.read_csv("nba_salaries.csv")

# Normalize player names to improve matching between the two files
stats["player_key"] = stats["Player"].str.strip().str.lower()
salaries["player_key"] = salaries["Player Name"].str.strip().str.lower()

filtered_stats = stats[stats["player_key"].isin(salaries["player_key"])]

# Average stats for duplicate player names and keep a single row per player
numeric_cols = filtered_stats.select_dtypes(include="number").columns
non_numeric_cols = filtered_stats.columns.difference(numeric_cols + ["player_key"])

averaged_stats = (
    filtered_stats.groupby("player_key").agg(
        {**{col: "first" for col in non_numeric_cols}, **{col: "mean" for col in numeric_cols}}
    )
    .reset_index(drop=True)
)

# Save the deduped/averaged stats to CSV
averaged_stats.to_csv("filtered_stats.csv", index=False)
