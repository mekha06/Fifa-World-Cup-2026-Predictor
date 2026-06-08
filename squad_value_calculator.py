import pandas as pd

wc_df = pd.read_csv("world_cup_dataset.csv")

squad_values = [
    # gk, defense, midfield, attack

    [3.70,44.80,16.70,30.33],   # Austria 2014
    []  # Belgium 2014

    
]

stats_df = pd.DataFrame(
    squad_values,
    columns=[
        "goalkeeper_value",
        "defense_value",
        "midfield_value",
        "attack_value"
    ]
)

stats_df["squad_value"] = (
    stats_df["goalkeeper_value"]
    + stats_df["defense_value"]
    + stats_df["midfield_value"]
    + stats_df["attack_value"]
)

wc_df["goalkeeper_value"] = stats_df["goalkeeper_value"]
wc_df["defense_value"] = stats_df["defense_value"]
wc_df["midfield_value"] = stats_df["midfield_value"]
wc_df["attack_value"] = stats_df["attack_value"]
wc_df["squad_value"] = stats_df["squad_value"]

wc_df.to_csv("world_cup_dataset.csv", index=False)