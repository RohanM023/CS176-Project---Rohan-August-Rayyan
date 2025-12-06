import pandas as pd

stats = pd.read_csv("2022-2023 NBA Player Stats - Regular.csv",encoding="latin-1", sep=";",)
salaries = pd.read_csv("nba_salaries.csv")

# Normalize player names to improve matching between the two files
stats["player_key"] = stats["Player"].str.strip().str.lower()
salaries["player_key"] = salaries["Player Name"].str.strip().str.lower()

filtered_stats = stats[stats["player_key"].isin(salaries["player_key"])]
