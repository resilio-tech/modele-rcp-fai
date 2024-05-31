# Model for assessing the environmental impacts of Internet Service Provision (ISP) following the ISP PCR

### Description

At the beginning of 2023, ADEME published the methodological standard for the environmental assessment for Internet Service Provision (ISP). The document is available in French and English on the [ADEME website](https://librairie.ademe.fr/produire-autrement/6103-methodological-standard-for-the-environmental-assessment-for-internet-service-provision-isp.html).

This repository contains the model for the collective action related to the evaluation of the environmental impacts of Internet Service Provider in France. It follows the methodology described in detail in the ISP Product Category Rule (PCR).

Indeed, from January 1st 2024, the AGEC law imposes a regulatory obligation for internet providers to communicate to their subscribers the gCO2/kByte ratio specific to their networks based on the common methodology provided by ADEME.

### Getting started

To run the model's calculation, use the Python file `run.py`. It uses the Excel test files to run the model. To use other data as input, the values given in these files can be modified. The code should return four Excel files containing the results.

### Prerequisites

#### Libraries
The following librairies are used : 
- [pandas](https://pandas.pydata.org/) 2.1.2
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/) 3.1.3

#### Code

The folder 'model' contains the following code files :
- **run** : file allowing to run the model
- **main** : file aggregating the entire model pipeline
- **model** : file containing the various functions that allow calculation and allocations
- **results** : file containing the various functions to prepare the results in the proper format
- **load_data** : file containing the various functions to load the input data and shape them in the right format
- **test_model** : file containing the functions to test the model

###  Input data

The main folder contains the Excel files that are used to do the computation :
- **Grille_collecte_test_operateurX** : file containing the inventory of equipments of provider X as well as complementory data such as lifetime, data quality, etc. The given file is an example with a partially completed inventory.
- **Facteurs_impacts_test** : file containing the environmental impacts of every equipment in the inventory. The given file is a test file with every impact value set to 1.
- **data_operateurs_test** : file containing a summary of the provider sizing data used for allocations.

These three files are test files and need to be filled with proper inventory data and impact values before being used for calculation.

Furthermore, you can find two other files :
- **Grille_allocation_ab** : file containing the percentage distribution of environmental impacts between types A and B according to the ISP PCR 
- **Grille_conso_elec** : file containing estimated unit electricity consumption by category of equipment

These two files are used during calculation but they don't have to be modified before calculation.


### Results

Once the model calculations have been made, 4 results files are created in the same location as the 'modele-rcp-fai' folder:
- **Results_flux_method_table** : file containing the detailed results using the 'flux method' (see ISP PCR for more details)
- **Results_flux_method_table_FU** : file containing the result for the functional unit (FU) of the ISP PCR using the 'flux method' (see ISP PCR for more details)
- **Results_lifespan_method_table** : file containing the detailed results using the 'lifespan method' (see ISP PCR for more details)
- **Results_lifespan_method_table_FU** : file containing the result for the functional unit (FU) of the ISP PCR using the 'lifespan method' (see ISP PCR for more details)


### Authors

Aubet Louise (Resilio), louise.aubet@resilio-solutions.com

### Project Status

The project was delivered to ADEME on the 17th of October 2023.
