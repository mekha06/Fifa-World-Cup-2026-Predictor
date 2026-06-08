import pandas as pd


df = pd.read_csv("world_cup_dataset.csv")

stats_data = [
    [29,11,43,41,32],#austria
    [31,16,51,29,58],#belgium
    [29,16,56,30,52],#bosnia
    [34,17,51,33,59],#croatia
    [35,15,47,35,54],#czech rep
    [34,19,69,34,67],#england
    [39,20,58,29,71],#france
    [39,26,103,54,85],#germany
    [36,20,88,33,69],#netherlands
    [34,12,36,41,43],#norway
    [36,20.68,41,66],#portugal
    [28,13,34,34,44],#scotland
    [45,36,119,35,113],#spain
    [43,26,90,56,83],#sweden
    [27,15,41,24,53],#switzerland
    [32,15,48,37,53],#turkey
    [44,24,91,49,85],#argentina
    [48,31,108,39,102],#brazil
    [33,20,51,20,66],#colombia
    [38,16,62,43,60],#ecuador
    [40,16,62,60,58],#paraguay
    [43,21,83,59,74],#uruguay
    [26,16,40,22,52],#algeria
    [18,8,25,19,28],#cabo verde
    [25,10,36,20,39],#congo dr
    [32,23,81,37,75],#ivory coast
    [41,24,82,46,79],#egypt
    [37,20,70,36,67],#ghana
    [40,17,62,38,63],#morocco
    [25,9,30,24,33],#senegal
    [38,16,49,28,60],#south africa
    [39,16,63,45,61],#tunisia
    [34,10,33,39,39],#canada
    [55,30,97,48,102],#mexico
    [53,31,90,56,102],#usa
    [17,3,24,38,11],#curacao
    [29,14,50,35,45],#haiti
    [55,29,93,58,98],#panama
    [41,23,86,45,87],#australia
    [40,25,79,22,85],#iran
    [57,25,65,58,86],#iraq
    [46,26,89,51,87],#japan
    [43,21,79,63,74],#jordan
    [41,20,71,52,69],#korea
    [40,17,59,58,59],#qatar
    [33,10,36,43,38],#saudi
    [42,20,66,50,69],#uzbekistan
    [23,11,36,33,38],#new zealand
    [28,13,42,30,46],#austria
    [34,24,93,35,77],#belgium
    [25,15,57,33,77],#bosnia
    [33,19,66,29,64],#croatia
    [33,14,54,38,49],#czech
    [34,20,58,24,59],#england
    [38,26,76,36,83],#france
    [40,27,103,38,88],#germany
    [31,17,59,39,55],#netherlands
    [28,9,33,39,32],#norway
    [42,29,94,33,92],#portugal
    [24,11,39,26,39],#scotland
    [34,24,81,21,78],#spain
    [38,19,69,32,63],#sweden
    [31,20,59,30,64],#switzerland
    [33,18,48,31,61],#turkey
    [40,24,84,40,81],#arg
    [37,25,78,25,82],#bra
    [38,18,62,41,63],#col
    [33,11,49,45,39],#ecua
    [35,9,35,58,35],#para
    [34,15,50,38,51],#uru
    [],#alg
    [],#cabo
    [],#congo
    [],#ivory
    [],#egypt
    [],#ghana
    [],#morocco
    [],#senegal
    [],#south africa
    [],#tunisia
    [],#can
    [],#mexico
    [],#usa
    [],#curacao
    [],#haiti
    [],#panama
    [],#australia
    [],#iran
    [],#iraq
    [],#japan
    [],#jordan
    [],#korea
    [],#qatar
    [],#saudi
    [],#uzb
    [24,10,34,25,35],#new
    [28,13,42,30,46],
    [34,24,93,35,77],
    [25,15,57,33,49],
    [33,19,66,29,64],
    [33,14,54,38,49],
    [34,20,58,24,59],
    [38,26,76,36,83],
    [40,27,103,38,88],
    [31,17,59,39,55],
    [28,9,33,39,32],
    [42,29,94,33,92],
    [24,11,39,26,39],
    [34,24,81,21,78],
    [38,19,69,32,63],
    [31,20,59,30,64],
    [33,18,48,31,61],
    [40,24,84,40,81],
    [37,25,78,25,82],
    [38,18,62,41,63],
    [33,11,49,45,39],
    [35,9,35,58,35],
    [34,15,50,38,51]
]

stats_df = pd.DataFrame(
    stats_data,
    columns=[
        "matches_played",
        "wins",
        "goals_scored",
        "goals_conceded",
        "points"
    ]
)

# Create derived features
stats_df["win_percentage_since_last_cup"] = (
    (stats_df["wins"] / stats_df["matches_played"]).round(2)
)

stats_df["goals_scored_per_game"] = (
    (stats_df["goals_scored"] / stats_df["matches_played"]).round(2)
)

stats_df["goals_conceded_per_game"] = (
    (stats_df["goals_conceded"] / stats_df["matches_played"]).round(2)
)

stats_df['points_per_game'] = (
    (stats_df['points']/stats_df['matches_played']).round(2)
)

df["win_percentage_since_last_cup"] = stats_df["win_percentage_since_last_cup"]

df["goals_scored_per_game"] = stats_df["goals_scored_per_game"]

df["goals_conceded_per_game"] = stats_df["goals_conceded_per_game"]

df['points_per_game'] = stats_df['points_per_game']

df.to_csv("world_cup_dataset.csv", index=False)
