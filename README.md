###FlowJo 
  #1. Use flowjo to gate the cell populations desired 
  #2. Use plate editor tool to add metadata of the experimental conditions to wells and export that csv as "EXPERIMENTID_map". csv 
![Example Panel](https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS/blob/main/image%20(10).png)
  #3. Export all of the gated populations in flowjo by "CTRL+A", "right-click", and click export 
![Example Panel](https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS/blob/main/image%20(11).png)
  #4. Once exported csvs into a folder, go through and delete the gates that you dont want (cause couldnt figure out how to easily click the ones without going through manually)

###Python
  #5. Use the sophbot.py script from https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS to load all exported FlowJo CSV files—including the plate map—and merge them into a single dataframe containing: 
    - all cellular events
    - all fluorescence intensity measurements, and
    - all metadata (peptide, treatment, media, well ID, replicate, etc.).
This gives you one unified dataframe with every single event from the entire 96-well plate, instead of FlowJo’s default per-well stats.
You only need to do this full concatenation if you want to:  
    - preserve single-cell–level measurements across the whole plate,
    - make plots that show distributions per well (e.g., histograms, ridge plots), or
    - visualize raw event-level data rather than summary statistics. 
Things you CAN plot or export stats on flowjo:
![Example Panel](https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS/blob/main/image%20(12).png)
  #6. Things to configure on the script: 
    - paths 
    - metadata (conditions, peptide, treatment, rep, etc)  
    - column (laser you want to quantify from)
  #7. Once you have merged all data into a single df and "merged_df.csv" you use the "impoting_excel.py" to index the dataframe or calculate parameters of interest based on your use-case groupings 
