import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Set up the folder for images
output_folder = 'visualizations_final'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print("Starting Analysis for 2022-2023 Season...")

# ==========================================
# 1. Load and Clean Player Data
# ==========================================

# Read the CSV files
# We use sep=';' because the stats file is formatted differently
stats_df = pd.read_csv("2022-2023 NBA Player Stats - Regular.csv", encoding="latin-1", sep=";")
salary_df = pd.read_csv("nba_salaries.csv")

# Create a normalized key (lowercase, no spaces) to match players between files
stats_df["player_key"] = stats_df["Player"].str.strip().str.lower()
salary_df["player_key"] = salary_df["Player Name"].str.strip().str.lower()

# Clean the Salary column (remove '$' and commas so we can do math)
if 'Salary' in salary_df.columns:
    salary_df['Salary'] = salary_df['Salary'].replace({r'\$': '', ',': ''}, regex=True).astype(float)

# Filter stats to only include players we have salary info for
filtered_stats = stats_df[stats_df["player_key"].isin(salary_df["player_key"])]

# Handle Traded Players 
# Separate columns into numbers (to average) and text (to keep)
numeric_cols = filtered_stats.select_dtypes(include="number").columns
all_cols = filtered_stats.columns
text_cols = [c for c in all_cols if c not in numeric_cols and c != 'player_key']

# Create simple rules: Average the numbers, keep the first text value found
agg_rules = {}
for col in numeric_cols:
    agg_rules[col] = 'mean'
for col in text_cols:
    agg_rules[col] = 'first'

# Group by player key using our rules
stats_aggregated = filtered_stats.groupby("player_key").agg(agg_rules).reset_index()

# Merge the averaged stats with the salary data
salary_subset = salary_df[['player_key', 'Salary']]
player_data = pd.merge(stats_aggregated, salary_subset, on='player_key', how='inner')

# Clean up Position column (e.g., change 'C-PF' to just 'C')
player_data['Pos_Clean'] = player_data['Pos'].astype(str).apply(lambda x: x.split('-')[0])

print(f"Player data ready: {len(player_data)} players processed.")

# ==========================================
# 2. Load and Clean Team Data
# ==========================================

# Calculate Total Payroll per Team (Summing player salaries)
team_payroll = player_data.groupby('Tm')['Salary'].sum().reset_index()
team_payroll.rename(columns={'Tm': 'Team', 'Salary': 'Total_Payroll'}, inplace=True)

# Load the historical team data
team_raw = pd.read_csv('regular_season_totals_2010_2024.csv')
team_raw.rename(columns={'SEASON_YEAR': 'Season', 'TEAM_ABBREVIATION': 'Team'}, inplace=True)

# Filter for ONLY the 2022-23 Season
target_season = '2022-23'
team_season = team_raw[team_raw['Season'] == target_season].copy()

# Convert W/L column to numbers (1 for Win, 0 for Loss)
team_season['Is_Win'] = team_season['WL'].apply(lambda x: 1 if x == 'W' else 0)

# Calculate Wins and Win Percentage
team_stats = team_season.groupby(['Team']).agg(
    Total_Wins=('Is_Win', 'sum'),
    Total_Games=('GAME_ID', 'nunique')
).reset_index()

team_stats['Win_Pct'] = team_stats['Total_Wins'] / team_stats['Total_Games']

# Merge Payroll data with Win data for plotting trends
team_trend_data = pd.merge(team_stats, team_payroll, on='Team', how='inner')

# Create the Pivot Table (Required for project)
team_stats['Season'] = target_season
team_pivot = team_stats.pivot_table(index='Season', columns='Team', values='Win_Pct')

print(f"Team data ready: {len(team_trend_data)} teams processed.")

# ==========================================
# 3. Generate Visualizations
# ==========================================

# Histogram of Salaries
plt.figure(figsize=(10, 6))
# Divide by 1 million to make the numbers readable
salaries_in_millions = player_data['Salary'] / 1_000_000
plt.hist(salaries_in_millions, bins=20, color='skyblue', edgecolor='black')
plt.title(f'Visualization 1: Salary Distribution ({target_season})')
plt.xlabel('Salary (Millions USD)')
plt.ylabel('Count of Players')
plt.grid(axis='y', alpha=0.5)
plt.savefig(os.path.join(output_folder, 'viz_1_salary_histogram.png'))
plt.close()

#Boxplot of Salary by Position
plt.figure(figsize=(10, 6))
unique_positions = sorted(player_data['Pos_Clean'].unique())
# Create a list of salary arrays for each position
box_data = []
for pos in unique_positions:
    values = player_data[player_data['Pos_Clean'] == pos]['Salary'].values
    box_data.append(values)

plt.boxplot(box_data, labels=unique_positions, patch_artist=True,
            boxprops=dict(facecolor='lightgreen'))
plt.title(f'Visualization 2: Salary Ranges by Position ({target_season})')
plt.xlabel('Position')
plt.ylabel('Salary (USD)')
plt.ticklabel_format(style='plain', axis='y') # Disable scientific notation
plt.grid(axis='y', alpha=0.3)
plt.savefig(os.path.join(output_folder, 'viz_2_salary_boxplot.png'))
plt.close()

#Bar Chart of Avg Points by Position
pos_scoring = player_data.groupby('Pos_Clean')['PTS'].mean().reset_index()

plt.figure(figsize=(10, 6))
plt.bar(pos_scoring['Pos_Clean'], pos_scoring['PTS'], color='salmon', edgecolor='black')
plt.title(f'Visualization 3: Average Scoring by Position ({target_season})')
plt.xlabel('Position')
plt.ylabel('Average Points Per Game (PPG)')
plt.grid(axis='y', alpha=0.3)
plt.savefig(os.path.join(output_folder, 'viz_3_scoring_bar.png'))
plt.close()

# Scatter Plot (Team Payroll vs Wins)
plt.figure(figsize=(12, 8))
x_values = team_trend_data['Total_Payroll'] / 1_000_000 # Millions
y_values = team_trend_data['Total_Wins']
labels = team_trend_data['Team']

plt.scatter(x_values, y_values, c='purple', s=100, alpha=0.6)

# Label each point with the team name
for i, label in enumerate(labels):
    plt.annotate(label, (x_values[i], y_values[i]), fontsize=9)

plt.title(f'Visualization 4: Team Payroll vs Wins ({target_season})')
plt.xlabel('Total Payroll (Millions USD)')
plt.ylabel('Total Wins')
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig(os.path.join(output_folder, 'viz_4_payroll_wins_scatter.png'))
plt.close()

# Horizontal Bar Chart (Standings)
# Transpose the pivot table so Teams are the rows
viz5_data = team_pivot.T.sort_values(by=target_season, ascending=True)

plt.figure(figsize=(10, 8))
plt.barh(viz5_data.index, viz5_data[target_season], color='gold', edgecolor='black')
plt.title(f'Visualization 5: Team Win % Rankings ({target_season})')
plt.xlabel('Win Percentage')
plt.ylabel('Team')
plt.xlim(0, 1.0)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, 'viz_5_standings_bar.png'))
plt.close()

print(f"Done! Check the '{output_folder}' folder for images.")