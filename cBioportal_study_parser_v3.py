import pandas as pd
import numpy as np
import os
from os.path import exists

def parse_arguments():
    f = input("Enter the Clinical data Excel or csv file path : ") 
    n = input("Enter the name of the study:  ") 
    ct = input("Enter the cancer type (or 'coadread' if not provided): ")  or 'coadread'
    csi = input("Enter the cancer study identifier (or 'name of the study' if not provided) : ") or n
    d = input("Enter the description of the study (default: 'name of the study'): ") or n
    gat = input("Enter the genetic alteration type (default: 'CLINICAL'): ") or 'CLINICAL'
    wd = input("Enter the working directory (default: './'): ") or './'
    return {
        'f': f,
        'n': n,
        'ct': ct,
        'csi': csi,
        'd': d,
        'gat': gat,
        'wd': wd
    }
    
def read_input_file(file_path):
    try:
        if file_path.endswith(".xlsx"):
            return pd.read_excel(open(file_path, 'rb'), sheet_name=0)
        else:
            return pd.read_csv(open(file_path, 'rb'))
    except PermissionError as e:
        print(f"Error: Permission denied while trying to read the file: {file_path}")
        print("Ensure the file is not open in another program and that you have sufficient permissions.")
        exit(1)
    except FileNotFoundError as e:
        print(f"Error: The file {file_path} was not found.")
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        exit(1)

def clean_dataframe(df):
    df = df.replace("n.a.", np.nan).replace("n.a", np.nan)
    df = df.replace({"\r\n": "\n", "\r": '\n'}, regex=True)  
    df = df.replace({"\n": " "}, regex=True)
    df.columns = df.columns.str.strip().str.replace(' ', '_')  
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  
    df = df.dropna(how='all')  
    df = df.dropna(axis=1, how='all')  
    return df

def rename_columns(df):
    if 'PATIENT' in df.columns:
        df.rename(columns={'PATIENT': 'PATIENT_ID'}, inplace=True)
    if 'DSE_E' in df.columns:
        df.rename(columns={'DSE_E': 'DFS_STATUS'}, inplace=True)
    if 'DFS_months' in df.columns:
        df.rename(columns={'DFS_months': 'DFS_MONTHS'}, inplace=True)
    if 'death_event' in df.columns:
        df.rename(columns={'death_event': 'OS_STATUS'}, inplace=True)
    if 'GENDER' in df.columns:
        df.rename(columns={'GENDER': 'SEX'}, inplace=True)
    if 'DFS_STATUS_' in df.columns:
        df.rename(columns={'DFS_STATUS_': 'DFS_STATUS'}, inplace=True)
    if 'SAMPLE_ID' not in df.columns:
        df['SAMPLE_ID'] = df['PATIENT_ID']
    #df['PATIENT_ID'] = df['PATIENT_ID'].replace(' ', '_', regex=True)
    #if 'SAMPLE_ID' in df.columns:
       # df['SAMPLE_ID'] = df['SAMPLE_ID'].replace(' ', '_', regex=True)
    return df
def prepare_meta_study(args):
    meta_study_content = [
        f"type_of_cancer: {args['ct']}\n",
        f"cancer_study_identifier: {args['csi']}\n",
        f"name: {args['n']}\n",
        f"description: {args['d']}\n",
        f"add_global_case_list: true\n"
        f"reference_genome: hg38"
    ]
    with open(f"{os.path.join(args['wd'], args['n'])}/meta_study.txt", 'w') as f:
        f.writelines(meta_study_content)
        
        
        
def prepare_patient_data(df, patient_columns, args):
    print(f"writing meta for clinica patient columns: {patient_columns}")
  

    meta_clinical_patient_content = [
        f"cancer_study_identifier: {args['csi']}\n",
        f"genetic_alteration_type: {args['gat']}\n",
        f"datatype: PATIENT_ATTRIBUTES\n",
        "data_filename: data_clinical_patient.txt"
    ]
    with open(f"{os.path.join(args['wd'], args['n'])}/meta_clinical_patient.txt", 'w') as f:
        f.writelines(meta_clinical_patient_content)

    p_df = df.filter(patient_columns, axis=1)
    
    for c in p_df.columns:
      if c.upper() == "OS_STATUS":
          p_df[c] = p_df[c].astype(str)
          p_df.loc[p_df[c] == "0", c] = "0:LIVING"
          p_df.loc[p_df[c] == "1", c] = "1:DECEASED"
          p_df.loc[p_df[c] == "2", c] = "1:DECEASED"
      if c.upper() == "DFS_STATUS":
          p_df[c] = p_df[c].astype(str)
          p_df.loc[p_df[c] == "0", c] = "0:DiseaseFree"
          p_df.loc[p_df[c] == "1", c] = "1:Recurred"
    p_df.drop_duplicates(inplace=True)
    return p_df



def prepare_sample_data(df, sample_columns, args):
    #print("Removing patient-specific columns from sample data...")
    print(f"writing meta for clinical sample columns: {sample_columns}")
    s_df = df.filter(sample_columns, axis=1)
    

    meta_clinical_sample_content = [
        f"cancer_study_identifier: {args['csi']}\n",
        f"genetic_alteration_type: {args['gat']}\n",
        f"datatype: SAMPLE_ATTRIBUTES\n",
        "data_filename: data_clinical_sample.txt"
    ]
    with open(f"{os.path.join(args['wd'], args['n'])}/meta_clinical_sample.txt", 'w') as f:
        f.writelines(meta_clinical_sample_content)
    s_df.drop_duplicates(inplace=True)
    return s_df



def write_clini_data(df, f_name, work_dir, study_name):
    print(f"Writing columns for {f_name}: {list(df.columns)}")  # Log the column names
    df_cols = "\t".join(list(df.columns))
    cols = '#' + df_cols + '\n'

    column_types = []
    for col in df.columns:
        if col in ["T_STATUS", "TUMOR_STATUS", "METASTATIC_SITE"]:
            col_type = "STRING"
        elif col == "AGE":
            col_type = "NUMBER"
        elif col.endswith("_MONTHS") or col.lower().endswith("months"):
            col_type = "NUMBER"
        #elif df[col].dropna().astype(str).str.lower().isin(["yes", "no", "true", "false"]).all():
            #col_type = "BOOLEAN"
            # Convert BOOLEAN values to uppercase strings
            df[col] = df[col].astype(str).str.lower().map({
                "yes": "TRUE", 
                "no": "FALSE", 
                "true": "TRUE", 
                "false": "FALSE"
            })
        else:
            col_type = "STRING"
        column_types.append(col_type)
        print(f"Column '{col}' assigned type: {col_type}")

    sample_header = [
        cols,
        cols,
        "#" + "\t".join(column_types) + '\n',
        "#" + "\t".join(["1" for _ in range(len(list(df.columns)))]) + '\n',
        df_cols.upper() + '\n'
    ]

    df = df.to_csv(header=None, index=False, sep="\t",lineterminator='\n')
  
    with open(f"{os.path.join(work_dir, study_name)}/{f_name}", "w") as f:
        f.writelines(sample_header)
        f.write(df)
        
        
        
def main():
    args = parse_arguments()
    print(f"args:   {args}")  
    
    patient_columns = ['PATIENT_ID', 'AGE', 'SEX', 'DFS_MONTHS', 'OS_MONTHS', 'OS_STATUS', 'DFS_STATUS', 'TUMOR_SITE','study','compassid','pooledcompassid']
    Irrelevent_columns = ['Relative_Path_1','Relative_Path_2']


    if not exists(os.path.join(args['wd'], args['n'])):
        os.mkdir(os.path.join(args['wd'], args['n']))
        
    
   

    df = read_input_file(args['f'])
    print("name of the features/ collumns in the input file:")
    print(df.columns)  
    df = clean_dataframe(df)
    df = rename_columns(df)
    prepare_meta_study(args)
    key_columns = ['PATIENT_ID', 'SAMPLE_ID']
    df = df.dropna(subset=key_columns, how='any')
    # For Prining and testing output and debugging
    print("DataFrame after cleaning and renaming columns: check if that is what you want you want")
    print(df.head())
    
    df.to_excel("output.xlsx", index=False)
    
    print("Parsing to cBioPortal study structure if possible...")
    # Taking question from the user if there are any irrellevant columns in the data
    Modify_irrelevent_columns = input("do you want to specify irrelevent columns. Press y for yes and n for no(tool will search predefined irrelevent collumns features in the data) :  ")
    if Modify_irrelevent_columns == 'y':
        Irrelevent_columns = input("Enter the patient columns separated by commas: ").split(",")
        Irrelevent_columns = [col.strip() for col in Irrelevent_columns]
        print(f"Found irrelevent columns: {Irrelevent_columns}")
    else:
        print("Using default irrelerent columns.") 
    
    
    # Check if the user what to modify the patient columns or not
    Modify = input("do you want to specify patient_collumns. Press y for yes and n for no(tool will search predefined features in the data) :  ")
    if Modify == 'y':
        patient_columns = input("Enter the patient columns separated by commas: ").split(",")
        
        patient_columns = [col.strip() for col in patient_columns]
    else:
        print("Using default patient columns.") 
    Found_patient_columns = [col for col in patient_columns if col in df.columns]
    
   # Check if the user what to modify the sample columns or not
    Found_sample_columns = []
    Modify2 = input("do you want to specify sample_collumns. If Press y, the tool will look for the collums you define in the input file. If Press n, the tool will take all the collumns in found sample collumn without the patient collumns(This usually is most of the case) :  ")
    if Modify2 == 'y':
        sample_columns = input("Enter the patient columns separated by commas: ").split(",")
        sample_columns = [col.strip() for col in patient_columns]
        Found_sample_columns = [col for col in sample_columns if col in df.columns]
    if Modify2 == 'n':
        Found_sample_columns = [col for col in df.columns 
                        if col not in Found_patient_columns 
                        and col not in Irrelevent_columns  # Exclude irrelevant columns
                        or col == 'PATIENT_ID']# Keep the PATIENT_ID column
    
    
    
    ## Check patients collumn only consist of PATIENT_ID 
    ## if all the minimum required columns are not found in the input file
    if len(Found_patient_columns) == 1 and Found_patient_columns[0] == 'PATIENT_ID':
        print(f'Found patient columns length: {len(Found_patient_columns)}')
        print("Only PATIENT_ID column found in the input file. No patient-specific columns to process.")
        
      
    
    if  len(Found_patient_columns) > 1:
        print(f"Found patient columns: {Found_patient_columns}")
        p_df = prepare_patient_data(df, Found_patient_columns, args)
        write_clini_data(p_df, "data_clinical_patient.txt", args['wd'], args['n'])
        
    if len(Found_sample_columns) > 1:
        print(f"Found sample columns: {Found_sample_columns}")
        s_df = prepare_sample_data(df, Found_sample_columns, args)
        write_clini_data(s_df, "data_clinical_sample.txt", args['wd'], args['n'])
       
        
    if not Found_sample_columns:
        print("No Sample columns found in the input file. It is required to have it.")
        return 0
    
   


if __name__ == "__main__":
    main()
