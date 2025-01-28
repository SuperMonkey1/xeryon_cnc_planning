# xeryon_cnc_planning
env\Scripts\activate



print("quadrants_df: " + str(quadrants_df))
quadrants_df.to_csv("quadrants_df.csv", index=False)
print("Saved quadrants_df to quadrants_df.csv for inspection.")
sys.exit()