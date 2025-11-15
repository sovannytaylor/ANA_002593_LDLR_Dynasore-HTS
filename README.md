FlowJo 
Use flowjo to gate the cell populations desired 
Use plate editor tool to add metadata of the experimental conditions to wells and export that csv as "EXPERIMENTID_map". csv 
image.png
3. Export all of the gated populations in flowjo by "CTRL+A", "right-click", and click export 

image.png
4. Once exported csvs into a folder, go through and delete the gates that you dont want (cause couldnt figure out how to easily click the ones without going through manually)

Python
5. Use the "sophbot.py" on https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS to read in all the csv files, including the map, and combine all metadata with flourescence intensity data - so you end up with a df with all cellular events throughout your entire 96 well plate instead of per well quantifications *which is what flowjo will give you 
this is only really necessary if you want to preserve the single cell data quants on a plot or want to show histograms for each well 
if you need to quantify measurements not on flowjo, for example getting the mean of the top 25% YG582-A intensities per well 
Things you CAN plot or export stats on flowjo:
image.png
6. Things to configure on the script: 
paths 
metadata (conditions, peptide, treatment, rep, etc) 
column (laser you want to quantify from)
7. Once you have merged all data into a single df and "merged_df.csv" you use the "impoting_excel.py" to index the dataframe or calculate parameters of interest based on your use-case groupings 
