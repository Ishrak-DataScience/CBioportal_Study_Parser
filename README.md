cBioPortal needs our data in a certain format with metadata information to be eligible to be uploaded.  We can use the script in the following path to make the necessary modifications and metadata. 

The modification script is located at `/usr/share/cbioportal/cbioportal_study_parser`(path from Pluto)

# cBioportal study parser

This script processes clinical sample data from an Excel file and prepares it for further analysis in cBioportal. The script requires several command-line arguments to define study parameters and file locations.

## Usage

Most of the libraries needed for running the cbioportal_study_parser.py are in the built-in Python package. Run the script using the following command:
` python cBioportal_study_parser.py -f <excel_file> -n <study_name> -ct <cancer_type> -csi <cancer_study_identifier> [options]`
## Example
` python cBioportal_study_parser.py -f 2422_DACHS-CRC-DX_CLINI.xlsx -n "2422_DACHS-CRC-DX_CLINI" -ct coadread -csi colorectal_cancer_NCT_Dresden_2025 `
