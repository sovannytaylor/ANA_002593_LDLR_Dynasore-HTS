## 📊 FlowJo → Python Workflow

### **FlowJo Steps**

#### **1. Gate your cell populations**
Use FlowJo to gate all cell populations that you plan to analyze.

---

#### **2. Add experimental metadata using the Plate Editor**
Use the Plate Editor to assign me
![Plate Editor Example](https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS/blob/main/image%20(10).png)

---

#### **3. Export all gated populations**
Select all wells (`Ctrl + A`), right-click, and choose **Export** → CSV.

![FlowJo Export Panel](https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS/blob/main/image%20(11).png)

---

#### **4. Clean exported CSVs**
FlowJo exports every gate it finds.  
Delete gates/CSVs you don’t want before moving to Python.

---

## 🐍 Python Steps

#### **5. Use `sophbot.py` to merge all FlowJo CSVs**
The script located at:

https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS

will:

- load all FlowJo CSV files  
- load the plate map  
- attach metadata (peptide, treatment, media, replicate, well position, etc.)  
- combine everything into a **single dataframe** containing:
  - all single-cell events  
  - all fluorescence intensity values  
  - all experimental metadata

This gives you a full-plate event-level dataset instead of FlowJo’s per-well statistics.

Use this approach if you want to:
- preserve **single-cell–level measurements**
- create **per-well histograms**, ridge plots, density plots, etc.
- visualize **raw fluorescence distributions** for each well

FlowJo can still export summary stats if needed:

![FlowJo Stats Example](https://github.com/sovannytaylor/ANA_002593_LDLR_Dynasore-HTS/blob/main/image%20(12).png)

---

#### **6. Configure `sophbot.py`**
Edit the script to match your experiment:

- input/output paths  
- metadata keys (peptide, treatment, media, rep, etc.)  
- fluorescence channel names  

---

#### **7. Perform downstream analysis**
After generating `merged_df.csv`, use `importing_excel.py` to:

- index and sort your data  
- compute summary statistics  
- apply experimental groupings  
- calculate any parameters of interest  

---

tadata (peptide, treatment, media, etc.) to each well.  
Export this plate map as:

