# Model for assessing the environmental impacts of Internet Service Provision (ISP) following the ISP PCR

### Description

At the beginning of 2023, ADEME published the methodological standard for the environmental assessment for Internet Service Provision (ISP). The document is available in French and English on the [ADEME website](https://librairie.ademe.fr/produire-autrement/6008-principes-generaux-pour-l-affichage-environnemental-des-produits-de-grande-consommation.html).

This repository contains the model for the collective action related to the evaluation of the environmental impacts of Internet Service Provider in France. It follows the methodology described in detail in the ISP Product Category Rule (PCR).

Indeed, from January 1st 2024, the AGEC law imposes a regulatory obligation for operators to communicate to their subscribers the gCO2/kByte ratio specific to their networks based on the common methodology provided by ADEME.

### Getting started

To run the model's calculation, use the Python file `run.py`. It uses the Excel test files to run the model. To use other data as input, the values given in these files can be modified. The code should return four Excel files containing the results.

### Prerequisites

#### Libraries
The following librairy is used : [pandas](https://pandas.pydata.org/) 2.1.2

#### Code

The folder model contains the following code files :
- **run** : file allowing to run the model
- **main** : file aggregating the entire model pipeline
- **model** : file containing the various functions that allow calculation and allocations
- **results** : file containing the various functions to prepare the results in the proper format
- **load_data** : file containing the various functions to load the input data and shape them in the right format
- **test_model** : file containing the functions to test the model

#### Additional content

The Excel files in the repository are test files filled with arbitrary values, that are used to test the model.

### Authors

Aubet Louise (Resilio), louise.aubet@resilio-solutions.com

### Project Status

The project was delivered to ADEME on the 17th of October 2023.
