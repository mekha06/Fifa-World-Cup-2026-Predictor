"""
simulation.py
Adapter module that wraps the existing Monte Carlo simulation scripts
with correct path resolution relative to this project.
"""

import os
import sys
import pandas as pd
import numpy as np
import random

# Resolve the project root (two levels up from webapp/backend/)
BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PREDICTIONS_PATH = os.path.join(BASE_PATH, 'finalmodel', 'final_predictions_2026.csv')
RANDOM_RESULTS_PATH = os.path.join(BASE_PATH, 'monte_carlo', 'monte_carlo_results_2026.csv')
SCHEDULED_RESULTS_PATH = os.path.join(BASE_PATH, 'monte_carlo', 'scheduled_results_2026.csv')

# Official 2026 Groups
OFFICIAL_GROUPS = {
    'A': ['Mexico', 'South Africa', 'Korea Republic', 'Czech Republic'],
    'B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Haiti', 'Morocco', 'Scotland'],
    'D': ['USA', 'Paraguay', 'Australia', 'Turkey'],
    'E': ['Germany', 'Curacao', 'Ivory Coast', 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cabo Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'Congo DR', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama']
}

# Confederation mapping for UI
CONFEDERATION_MAP = {
    'Australia': 'AFC', 'Iran': 'AFC', 'Iraq': 'AFC', 'Japan': 'AFC',
    'Jordan': 'AFC', 'Korea Republic': 'AFC', 'Qatar': 'AFC',
    'Saudi Arabia': 'AFC', 'Uzbekistan': 'AFC',
    'Algeria': 'CAF', 'Cabo Verde': 'CAF', 'Congo DR': 'CAF',
    'Ivory Coast': 'CAF', 'Egypt': 'CAF', 'Ghana': 'CAF',
    'Morocco': 'CAF', 'Senegal': 'CAF', 'South Africa': 'CAF', 'Tunisia': 'CAF',
    'Canada': 'CONCACAF', 'Mexico': 'CONCACAF', 'USA': 'CONCACAF',
    'Curacao': 'CONCACAF', 'Haiti': 'CONCACAF', 'Panama': 'CONCACAF',
    'Argentina': 'CONMEBOL', 'Brazil': 'CONMEBOL', 'Colombia': 'CONMEBOL',
    'Ecuador': 'CONMEBOL', 'Paraguay': 'CONMEBOL', 'Uruguay': 'CONMEBOL',
    'New Zealand': 'OFC',
    'Austria': 'UEFA', 'Belgium': 'UEFA', 'Bosnia and Herzegovina': 'UEFA',
    'Croatia': 'UEFA', 'Czech Republic': 'UEFA', 'England': 'UEFA',
    'France': 'UEFA', 'Germany': 'UEFA', 'Netherlands': 'UEFA',
    'Norway': 'UEFA', 'Portugal': 'UEFA', 'Scotland': 'UEFA',
    'Spain': 'UEFA', 'Sweden': 'UEFA', 'Switzerland': 'UEFA', 'Turkey': 'UEFA'
}

# Flag emoji mapping
FLAG_MAP = {
    'Argentina': '🇦🇷', 'Australia': '🇦🇺', 'Austria': '🇦🇹',
    'Algeria': '🇩🇿', 'Belgium': '🇧🇪', 'Bosnia and Herzegovina': '🇧🇦',
    'Brazil': '🇧🇷', 'Cabo Verde': '🇨🇻', 'Canada': '🇨🇦',
    'Colombia': '🇨🇴', 'Congo DR': '🇨🇩', 'Croatia': '🇭🇷',
    'Curacao': '🇨🇼', 'Czech Republic': '🇨🇿', 'Ecuador': '🇪🇨',
    'Egypt': '🇪🇬', 'England': '🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'France': '🇫🇷',
    'Germany': '🇩🇪', 'Ghana': '🇬🇭', 'Haiti': '🇭🇹',
    'Iran': '🇮🇷', 'Iraq': '🇮🇶', 'Ivory Coast': '🇨🇮',
    'Japan': '🇯🇵', 'Jordan': '🇯🇴', 'Korea Republic': '🇰🇷',
    'Mexico': '🇲🇽', 'Morocco': '🇲🇦', 'Netherlands': '🇳🇱',
    'New Zealand': '🇳🇿', 'Norway': '🇳🇴', 'Panama': '🇵🇦',
    'Paraguay': '🇵🇾', 'Portugal': '🇵🇹', 'Qatar': '🇶🇦',
    'Saudi Arabia': '🇸🇦', 'Scotland': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Senegal': '🇸🇳',
    'South Africa': '🇿🇦', 'Spain': '🇪🇸', 'Sweden': '🇸🇪',
    'Switzerland': '🇨🇭', 'Tunisia': '🇹🇳', 'Turkey': '🇹🇷',
    'Uruguay': '🇺🇾', 'USA': '🇺🇸', 'Uzbekistan': '🇺🇿'
}


def load_teams_df():
    """Load the predictions CSV and compute hybrid strength."""
    df = pd.read_csv(PREDICTIONS_PATH)
    df.columns = [c.strip() for c in df.columns]
    df['Strength'] = df['Elo_Rating'] + df['Predicted_Stage'] * 50
    return df


def get_teams_data():
    """Return enriched team list for the API."""
    df = load_teams_df()
    teams = []
    for _, row in df.iterrows():
        name = row['Team']
        teams.append({
            'team': name,
            'elo': round(float(row['Elo_Rating']), 1),
            'predicted_stage': round(float(row['Predicted_Stage']), 3),
            'strength': round(float(row['Strength']), 1),
            'confederation': CONFEDERATION_MAP.get(name, 'UEFA'),
            'flag': FLAG_MAP.get(name, '🏳️'),
        })
    # Sort by strength descending
    teams.sort(key=lambda x: x['strength'], reverse=True)
    return teams


def get_groups_data():
    """Return official group assignments enriched with team stats."""
    teams_df = load_teams_df()
    team_index = teams_df.set_index('Team').to_dict('index')
    groups = {}
    for gname, members in OFFICIAL_GROUPS.items():
        groups[gname] = []
        for t in members:
            info = team_index.get(t, {})
            groups[gname].append({
                'team': t,
                'flag': FLAG_MAP.get(t, '🏳️'),
                'elo': round(float(info.get('Elo_Rating', 1600)), 1),
                'strength': round(float(info.get('Strength', 1600)), 1),
                'confederation': CONFEDERATION_MAP.get(t, 'UEFA'),
            })
    return groups


# ─── Simulation Core ─────────────────────────────────────────────────────────

def _simulate_match(s1, s2, knockout=False):
    base = 1.4
    adj = (s1 - s2) / 100 * 0.2
    l1 = max(0.1, base + adj)
    l2 = max(0.1, base - adj)
    g1 = np.random.poisson(l1)
    g2 = np.random.poisson(l2)
    if g1 > g2:
        return g1, g2, 0
    elif g2 > g1:
        return g1, g2, 1
    else:
        if knockout:
            p = 1 / (1 + 10 ** (-(s1 - s2) / 400))
            return g1, g2, (0 if random.random() < p else 1)
        return g1, g2, 2


def _simulate_group(teams):
    stats = {t['Team']: {'points': 0, 'gf': 0, 'ga': 0, 'td': t} for t in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            t1, t2 = teams[i], teams[j]
            g1, g2, w = _simulate_match(t1['Strength'], t2['Strength'])
            stats[t1['Team']]['gf'] += g1
            stats[t1['Team']]['ga'] += g2
            stats[t2['Team']]['gf'] += g2
            stats[t2['Team']]['ga'] += g1
            if w == 0:
                stats[t1['Team']]['points'] += 3
            elif w == 1:
                stats[t2['Team']]['points'] += 3
            else:
                stats[t1['Team']]['points'] += 1
                stats[t2['Team']]['points'] += 1
    ranked = sorted(stats.values(),
                    key=lambda x: (x['points'], x['gf'] - x['ga'], x['gf']),
                    reverse=True)
    return ranked


def run_random_simulation(num_simulations=1000, progress_cb=None):
    """Random-seeded Monte Carlo (groups drawn randomly)."""
    df = load_teams_df()
    team_names = df['Team'].tolist()
    stats = {t: {'R32': 0, 'R16': 0, 'QF': 0, 'SF': 0, 'Final': 0, 'Winner': 0}
             for t in team_names}

    for i in range(num_simulations):
        teams = df.sample(frac=1).to_dict('records')
        groups = {}
        for gi in range(12):
            gname = chr(65 + gi)
            groups[gname] = teams[gi * 4:(gi + 1) * 4]

        # Group stage
        thirds = []
        advancers = []
        for gname, gmembers in groups.items():
            ranked = _simulate_group(gmembers)
            advancers.append(ranked[0]['td'])
            advancers.append(ranked[1]['td'])
            thirds.append(ranked[2])

        best_thirds = sorted(thirds, key=lambda x: (x['points'], x['gf'] - x['ga'], x['gf']),
                             reverse=True)[:8]
        r32 = advancers + [t['td'] for t in best_thirds]

        # Knockout
        random.shuffle(r32)
        current = r32
        for stage in ['R16', 'QF', 'SF', 'Final']:
            winners = []
            for k in range(0, len(current), 2):
                t1, t2 = current[k], current[k + 1]
                _, _, w = _simulate_match(t1['Strength'], t2['Strength'], knockout=True)
                winner = t1 if w == 0 else t2
                winners.append(winner)
                stats[winner['Team']][stage] += 1
            current = winners

        if current:
            stats[current[0]['Team']]['Winner'] += 1

        if progress_cb and (i + 1) % max(1, num_simulations // 20) == 0:
            progress_cb(int((i + 1) / num_simulations * 100))

    results = []
    for team, s in stats.items():
        row = {'Team': team}
        for stage in ['R32', 'R16', 'QF', 'SF', 'Final', 'Winner']:
            row[f'{stage}_prob'] = round(s[stage] / num_simulations, 4)
        results.append(row)

    df_out = pd.DataFrame(results).sort_values('Winner_prob', ascending=False)
    df_out.to_csv(RANDOM_RESULTS_PATH, index=False)
    return df_out


def run_scheduled_simulation(num_simulations=1000, progress_cb=None):
    """Official-bracket Monte Carlo."""
    df = load_teams_df()
    team_data = df.set_index('Team').to_dict('index')
    team_names = df['Team'].tolist()
    stats = {t: {'R32': 0, 'R16': 0, 'QF': 0, 'SF': 0, 'Final': 0, 'Winner': 0}
             for t in team_names}

    for i in range(num_simulations):
        groups = {}
        for gname, members in OFFICIAL_GROUPS.items():
            groups[gname] = []
            for name in members:
                d = team_data[name].copy()
                d['Team'] = name
                groups[gname].append(d)

        # Group stage
        positions = {}
        thirds = []
        for gname, gmembers in groups.items():
            ranked = _simulate_group(gmembers)
            positions[f'{gname}1'] = ranked[0]['td']
            positions[f'{gname}2'] = ranked[1]['td']
            thirds.append(ranked[2])

        best_thirds = sorted(thirds, key=lambda x: (x['points'], x['gf'] - x['ga'], x['gf']),
                             reverse=True)[:8]
        best_thirds_teams = [t['td'] for t in best_thirds]

        # Mark all R32 entrants
        for t in list(positions.values()) + best_thirds_teams:
            stats[t['Team']]['R32'] += 1

        # R32 bracket
        r32_matches = [
            (positions['A1'], best_thirds_teams[0]),
            (positions['B1'], best_thirds_teams[1]),
            (positions['C1'], best_thirds_teams[2]),
            (positions['D1'], best_thirds_teams[3]),
            (positions['E1'], best_thirds_teams[4]),
            (positions['F1'], best_thirds_teams[5]),
            (positions['G1'], best_thirds_teams[6]),
            (positions['H1'], best_thirds_teams[7]),
            (positions['I1'], positions['A2']),
            (positions['J1'], positions['B2']),
            (positions['K1'], positions['C2']),
            (positions['L1'], positions['D2']),
            (positions['E2'], positions['F2']),
            (positions['G2'], positions['H2']),
            (positions['I2'], positions['J2']),
            (positions['K2'], positions['L2']),
        ]
        current = []
        for t1, t2 in r32_matches:
            _, _, w = _simulate_match(t1['Strength'], t2['Strength'], knockout=True)
            winner = t1 if w == 0 else t2
            current.append(winner)
            stats[winner['Team']]['R16'] += 1

        for stage in ['QF', 'SF', 'Final']:
            winners = []
            for k in range(0, len(current), 2):
                t1, t2 = current[k], current[k + 1]
                _, _, w = _simulate_match(t1['Strength'], t2['Strength'], knockout=True)
                winner = t1 if w == 0 else t2
                winners.append(winner)
                stats[winner['Team']][stage] += 1
            current = winners

        if current:
            stats[current[0]['Team']]['Winner'] += 1

        if progress_cb and (i + 1) % max(1, num_simulations // 20) == 0:
            progress_cb(int((i + 1) / num_simulations * 100))

    results = []
    for team, s in stats.items():
        row = {'Team': team}
        for stage in ['R32', 'R16', 'QF', 'SF', 'Final', 'Winner']:
            row[f'{stage}_prob'] = round(s[stage] / num_simulations, 4)
        results.append(row)

    df_out = pd.DataFrame(results).sort_values('Winner_prob', ascending=False)
    df_out.to_csv(SCHEDULED_RESULTS_PATH, index=False)
    return df_out


def load_results(mode='random'):
    """Load cached simulation results from CSV."""
    path = RANDOM_RESULTS_PATH if mode == 'random' else SCHEDULED_RESULTS_PATH
    if not os.path.exists(path):
        return []
    df = pd.read_csv(path)
    df = df.sort_values('Winner_prob', ascending=False)
    records = df.to_dict('records')
    # Enrich with flag/confederation
    for r in records:
        t = r['Team']
        r['flag'] = FLAG_MAP.get(t, '🏳️')
        r['confederation'] = CONFEDERATION_MAP.get(t, '?')
    return records
