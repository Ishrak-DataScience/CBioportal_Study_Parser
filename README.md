# cBioportal study parser

This script processes clinical sample data from an Excel file and prepares it for further analysis in cBioportal. 

## General User Guide:

There are two ways we use cBioportal_study_parser tool. There are two different versions. 

1. **v3** takes prompts( it will ask questions) from the user and behaves according to the instructions from the user.  More intuitive and flexible. 
2. **v2** takes all arguments at once as an argument in the code. More useful when used as part of a pipeline. 

## V3 User guide: User question/answer way :

We need to use the cBioportal_study_parser_v3.py.  Required packages are standard Python 3.6+ (tested on Python 3.11 ), pandas, numpy, and os. The os library is included in the standard Python 3  distribution, so most likely not required to be installed.   

```bash
# pip install numpy pandas
python cBioportal_study_parser_v3.py
```

Then there will be the following prompt(question/answer-like) on the commend line or terminal: 

1. Enter the Clinical data Excel or csv file path :

Please copy the full path of the clinical data (excel/csv). We tested on PC (windows 11) like path. Please me know if it works with other path style mac, Linux etc. 

1. The following intuitive questions will be asked. 

Enter the name of the study:  
Enter the cancer type (or 'coadread' if not provided):
Enter the cancer study identifier (or 'name of the study' if not provided) :
Enter the description of the study (default: 'name of the study'):

1. Then there will question on the genetic alteration type.  If not provided, clinical will be used since we are currently working mostly with that.

Enter the genetic alteration type (default: 'CLINICAL'):

1. Lastly the tool will ask where to save the study. If nothing is provided the study will be saved in the  current working directory. 

Enter the working directory (default: './'):

1. There will be next questions on customization of the study according to the user need. (Details coming up)
- do you want to specify irrelevant columns. Press y for yes and n for no(tool will search predefined irrelevant collumns features in the data) :  
Using default irreverent columns
- do you want to specify patient_collumns. Press y for yes and n for no(tool will search predefined features in the data) :  
Using default patient columns.
- do you want to specify sample_collumns. If Press y, the tool will look for the collums you define in the input file. If Press n, the tool will take all the collumns in found sample collumn without the patient collumns(This usually is most of the case) :

## V2 user guide: User pass command-line arguments:

The script requires several command-line arguments to define study parameters and file locations.

```bash
python cBioportal_study_parser.py -f <excel_file> -n <study_name> -ct <cancer_type> -csi <cancer_study_identifier> [options]

```

Example: