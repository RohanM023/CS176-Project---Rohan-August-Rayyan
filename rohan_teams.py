import pandas as pd
import matplotlib.pyplot as plt

print("1. Loading NBA Team Data...")
try:
    team_df = pd.read_csv('regular_season_totals_2010_2024.csv')
    print(f"SUCCESS! Loaded {len(team_df)} rows from the raw data.")

except FileNotFoundError:
    print("FATAL ERROR: Raw file not found. Using dummy data for demonstration.")
    exit()

# We will use 'WL' to determine wins/losses and calculate totals later.
cols_to_keep = ['SEASON_YEAR', 'TEAM_ABBREVIATION', 'WL', 'GAME_ID'] 
team_df_cleaned = team_df[cols_to_keep].copy()

# Rename columns to be consistent with the rest of the project
team_df_cleaned.rename(columns={
    'SEASON_YEAR': 'Season', 
    'TEAM_ABBREVIATION': 'Team'
}, inplace=True)

# We use the 'WL' column to create counts of total wins and total games played.

# Map 'W' (Win) to 1 and 'L' (Loss) to 0
team_df_cleaned['Is_Win'] = team_df_cleaned['WL'].apply(lambda x: 1 if x == 'W' else 0)

# Aggregate: Total Games is the count of unique GAME_IDs
team_agg_initial = team_df_cleaned.groupby(['Season', 'Team']).agg(
    Total_Wins=('Is_Win', 'sum'),
    Total_Games=('GAME_ID', 'nunique'), # Count unique game IDs
).reset_index()

# Calculate Total Losses and Rank (Assuming Rank needs to be calculated manually or from a separate column if available)
team_agg_initial['Total_Losses'] = team_agg_initial['Total_Games'] - team_agg_initial['Total_Wins']

team_agg_initial['Win_Pct'] = team_agg_initial['Total_Wins'] / team_agg_initial['Total_Games']

# Calculate Rank (Lower Win_Pct gets higher rank number)
team_agg_initial['Avg_Rank'] = team_agg_initial.groupby('Season')['Win_Pct'].rank(ascending=False, method='min')

print(f"Dataframe aggregated: {len(team_agg_initial)} rows (one per team per season).\n")
print("-" * 50)



team_rank_pivot = team_agg_initial.pivot_table(
    index='Season',        
    columns='Team',        
    values='Avg_Rank'      
)


team_2022_2023 = team_agg_initial[
    team_agg_initial['Season'] == '2022-23' 
].copy()

final_team_data = team_2022_2023[['Team', 'Avg_Rank', 'Win_Pct']].copy()

print("3. FINAL 2022-2023 TEAM DATA (All 30 teams, ready for merging):\n")
print(final_team_data.sort_values(by='Avg_Rank').head())
print("-" * 50)

team_rank_pivot.to_csv('rohan_team_rank_pivot.csv')
final_team_data.to_csv('rohan_final_team_data_2023.csv')
print("\nSaved two final CSV files to the current directory.")