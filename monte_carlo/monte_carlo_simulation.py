import pandas as pd
import numpy as np
import os
import random

# Setup paths
base_path = r"D:\Coding journey\Fifa World Cup 2026 Predictor"
predictions_path = os.path.join(base_path, "finalmodel", "final_predictions_2026.csv")

def load_teams():
    df = pd.read_csv(predictions_path)
    df.columns = [c.strip() for c in df.columns]
    # Create hybrid strength metric combining Elo and ML predictions
    df['Strength'] = df['Elo_Rating'] + df['Predicted_Stage'] * 50
    return df

def simulate_match(team1_strength, team2_strength, is_knockout=False):
    """
    Simulates a match between two teams using their hybrid Strength ratings.
    Returns: (team1_goals, team2_goals, winner_index)
    winner_index: 0 for team1 win, 1 for team2 win, 2 for draw
    """
    base_avg_goals = 1.4
    
    # Calculate strength difference
    strength_diff = team1_strength - team2_strength
    
    # Every 100 points of difference adds ~0.2 expected goals
    diff_adjustment = (strength_diff / 100) * 0.2
    
    t1_lambda = max(0.1, base_avg_goals + diff_adjustment)
    t2_lambda = max(0.1, base_avg_goals - diff_adjustment)
    
    t1_goals = np.random.poisson(t1_lambda)
    t2_goals = np.random.poisson(t2_lambda)
    
    if t1_goals > t2_goals:
        return t1_goals, t2_goals, 0
    elif t2_goals > t1_goals:
        return t1_goals, t2_goals, 1
    else:
        if is_knockout:
            # Simulate extra time / penalties favoring higher strength team
            win_prob = 1 / (1 + 10**(-strength_diff / 400))
            winner = 0 if random.random() < win_prob else 1
            return t1_goals, t2_goals, winner
        return t1_goals, t2_goals, 2

def setup_groups(teams_df):
    """
    Assigns teams to 12 groups (A-L) of 4.
    """
    # Sort by strength for simple seeding
    teams = teams_df.sort_values('Strength', ascending=False)
    
    # 48 teams / 4 = 12 groups
    groups = {chr(65 + i): [] for i in range(12)} # A to L
    
    # Snake draft / pot distribution
    pot1 = teams.iloc[0:12].sample(frac=1).to_dict('records')
    pot2 = teams.iloc[12:24].sample(frac=1).to_dict('records')
    pot3 = teams.iloc[24:36].sample(frac=1).to_dict('records')
    pot4 = teams.iloc[36:48].sample(frac=1).to_dict('records')
    
    for i in range(12):
        group_name = chr(65 + i)
        groups[group_name] = [pot1[i], pot2[i], pot3[i], pot4[i]]
        
    return groups

def simulate_group_stage(groups):
    """
    Simulates all matches in the group stage.
    """
    standings = {}
    
    for group_name, teams in groups.items():
        stats = {t['Team']: {'points': 0, 'goals_for': 0, 'goals_against': 0, 'gd': 0, 'team_data': t} for t in teams}
        
        # Each team plays every other team once
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                t1 = teams[i]
                t2 = teams[j]
                
                g1, g2, winner = simulate_match(t1['Strength'], t2['Strength'])
                
                stats[t1['Team']]['goals_for'] += g1
                stats[t1['Team']]['goals_against'] += g2
                stats[t2['Team']]['goals_for'] += g2
                stats[t2['Team']]['goals_against'] += g1
                
                if winner == 0:
                    stats[t1['Team']]['points'] += 3
                elif winner == 1:
                    stats[t2['Team']]['points'] += 3
                else:
                    stats[t1['Team']]['points'] += 1
                    stats[t2['Team']]['points'] += 1
        
        for team in stats:
            stats[team]['gd'] = stats[team]['goals_for'] - stats[team]['goals_against']
            
        ranked_teams = sorted(stats.values(), key=lambda x: (x['points'], x['gd'], x['goals_for']), reverse=True)
        standings[group_name] = ranked_teams
        
    return standings

def get_advancing_teams(standings):
    """
    Determines which 32 teams advance to the knockout stage.
    """
    advancers = []
    third_place_pool = []
    
    for group_name, ranked in standings.items():
        # Top 2 advance directly
        advancers.append(ranked[0]['team_data']) # 1st
        advancers.append(ranked[1]['team_data']) # 2nd
        
        third_place_info = ranked[2].copy()
        third_place_pool.append(third_place_info)
        
    best_thirds = sorted(third_place_pool, key=lambda x: (x['points'], x['gd'], x['goals_for']), reverse=True)[:8]
    
    for team_stat in best_thirds:
        advancers.append(team_stat['team_data'])
        
    return advancers

def simulate_knockout_stage(teams):
    """
    Simulates knockout rounds until a winner is found.
    """
    results = {
        'R32': [t['Team'] for t in teams],
        'R16': [],
        'QF': [],
        'SF': [],
        'Final': [],
        'Winner': None
    }
    
    current_round_teams = teams.copy()
    random.shuffle(current_round_teams) # Randomize bracket
    
    rounds = ['R16', 'QF', 'SF', 'Final']
    
    for round_name in rounds:
        winners = []
        for i in range(0, len(current_round_teams), 2):
            t1 = current_round_teams[i]
            t2 = current_round_teams[i+1]
            
            _, _, winner_idx = simulate_match(t1['Strength'], t2['Strength'], is_knockout=True)
            winner = t1 if winner_idx == 0 else t2
            winners.append(winner)
            results[round_name].append(winner['Team'])
            
        current_round_teams = winners
        
    # Final Match
    t1 = current_round_teams[0]
    t2 = current_round_teams[1]
    _, _, winner_idx = simulate_match(t1['Strength'], t2['Strength'], is_knockout=True)
    winner = t1 if winner_idx == 0 else t2
    results['Winner'] = winner['Team']
    
    return results

def run_monte_carlo(num_simulations=10000):
    df = load_teams()
    team_names = df['Team'].tolist()
    
    stats = {team: {
        'R32': 0, 'R16': 0, 'QF': 0, 'SF': 0, 'Final': 0, 'Winner': 0
    } for team in team_names}
    
    print(f"Starting Random-Seeded Monte Carlo Simulation ({num_simulations} iterations)...")
    
    for i in range(num_simulations):
        groups = setup_groups(df)
        standings = simulate_group_stage(groups)
        advancers = get_advancing_teams(standings)
        knockout_results = simulate_knockout_stage(advancers)
        
        for stage in ['R32', 'R16', 'QF', 'SF', 'Final']:
            for team in knockout_results[stage]:
                stats[team][stage] += 1
        
        stats[knockout_results['Winner']]['Winner'] += 1
        
        if (i + 1) % 1000 == 0:
            print(f"Progress: {i + 1}/{num_simulations}")
            
    # Convert to probabilities
    results_list = []
    for team, stages in stats.items():
        row = {'Team': team}
        for stage, count in stages.items():
            row[f'{stage}_prob'] = count / num_simulations
        results_list.append(row)
        
    results_df = pd.DataFrame(results_list)
    results_df = results_df.sort_values('Winner_prob', ascending=False)
    
    return results_df

if __name__ == "__main__":
    num_sims = 10000 # Increased to 10,000 for standard Monte Carlo statistical precision
    results = run_monte_carlo(num_sims)
    
    output_path = os.path.join(base_path, "monte_carlo", "monte_carlo_results_2026.csv")
    results.to_csv(output_path, index=False)
    
    print(f"\nSimulation Complete. Results saved to: {output_path}")
    print("\nTop 10 Teams by Win Probability:")
    print(results[['Team', 'Winner_prob', 'Final_prob', 'SF_prob']].head(10).to_string(index=False))
