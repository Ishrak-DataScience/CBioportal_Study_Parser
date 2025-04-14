import pandas as pd
import numpy as np
import os
from os.path import exists
def parse_arguments():
    f = input("Enter the Excel file path : ") 
    n = input("Enter the name of the study:  ") 
    ct = input("Enter the cancer type (or 'coadread' if not provided): ")  or 'coadread'
    csi = input("Enter the cancer study identifier : ")
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
    
    
def main():
    args = parse_arguments()
    print(f"args:   {args}")  
    sample_columns = ['PATIENT_ID', 'SAMPLE_ID', 'CANCER_TYPE', 'CANCER_TYPE_DETAILED', 'TUMOR_TISSUE_SITE', 'SAMPLE_DISPLAY_NAME', 'SAMPLE_CLASS', 'METASTATIC_SITE', 'OTHER_SAMPLE_ID','BRAF','KRAS']
    patient_columns = ['PATIENT_ID', 'AGE', 'SEX', 'DFS_MONTHS', 'OS_MONTHS', 'OS_STATUS', 'DFS_STATUS', 'TUMOR_SITE']
    gene_collums =['SAMPLE_ID','BRAF','KRAS']  

    if not exists(os.path.join(args['wd'], args['n'])):
        os.mkdir(os.path.join(args['wd'], args['n']))
        
    print("Parsing to cBioPortal study structure if possible...")

    df = read_input_file(args['f'])
    df = clean_dataframe(df)
    print(df.head())
    df.to_excel("output.xlsx", index=False)

        
if __name__ == "__main__":
    main()
