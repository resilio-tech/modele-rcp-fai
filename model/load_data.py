
import os

import pandas as pd

from typing import Optional, List


def prepare_data(operator_list: list[str], filename_list: dict[(str, str)]) -> list[ dict[(str, list[pd.DataFrame])], dict[(str, list[pd.DataFrame])]]:
        """Define the pipeline of treatment of the inventories"""
        dict_purchase_list = {} # purchase : quantity of equipements that are purchased
        dict_dismounting_list = {} # dismouting : quantity of equipements tbat are dismounted
        dict_impact_list = {} # impacts : environmental impacts for all LC steps
        for operator in operator_list:
                purchase_list = load_purchase(filename_list[operator])
                dismounting_list = load_dismounting(filename_list[operator])
                impact_list = load_impacts(filename_list[operator])
                dict_purchase_list[operator] = purchase_list
                dict_dismounting_list[operator] = dismounting_list
                dict_impact_list[operator] = impact_list
        return dict_impact_list, dict_purchase_list, dict_dismounting_list


#######################################################################
"""Functions to load the data"""

def load_purchase(filename: str) -> list[pd.DataFrame]:
        """Load the Excel sheet containing the purchase inventory and create a Dataframe"""
        df = load_excel(filename, sheet_name="achats_2022", skiprows=1, header=0, index_col=None,
                        usecols="C,E:H,K,M:P,S,U:X",)
        df_list = separate_inventory_by_category(df)
        return df_list

def load_dismounting(filename: str) -> list[pd.DataFrame]:
        """Load the Excel sheet containing the dismounting inventory and create a Dataframe"""
        df = load_excel(filename, sheet_name="démontage_2022", skiprows=1, header=0, index_col=None,
                        usecols="C,E:H,K,M:P,S,U:X",)
        df_list = separate_inventory_by_category(df)
        return df_list


def load_impacts(filename :str) -> list[pd.DataFrame]:
        """Load the Excel sheet containing the unitary impacts and create a Dataframe"""
        df = load_excel(filename, sheet_name="facteurs_impacts", skiprows=2, header=0, index_col=None,
                        usecols="C,E:AN,AQ,AS:CB,CE,CG:DP")
        df_list = separate_impacts_by_category(df)
        return df_list

def load_op_data() -> pd.DataFrame:
        """Load the global Telecom data and create a Dataframe"""
        filename = "../data_operateurs.xlsx"
        df = load_excel(filename, sheet_name="Feuil1", skiprows=0, header=0, index_col=0)
        return df

def load_ab_factors() -> list[pd.DataFrame]:
        """Load the Excel file containing the allocation rules from one indicator to its a and b coefficients.
        Create the corresponding Dataframe"""
        filename = "../Grille_allocation_ab.xlsx"
        df = load_excel(filename, sheet_name="Feuil1", skiprows=2, header=0, index_col=None, usecols="B:N,P:AB,AD:AP")
        df_list = separate_ab_factors_by_category(df)
        return df_list

def load_elec_consumption() -> list[pd.DataFrame]:
        """Load the Excel file containing the estimated electrical consumption values for all the equipments.
        Create the corresponding Dataframe"""
        filename = "../Grille_conso_elec.xlsx"
        df = load_excel(filename, sheet_name="Feuil1", skiprows=1, header=0, index_col=None, usecols="B:C,E:F,H:I")
        df_list = separate_elec_by_category(df)
        return df_list

def load_excel(filename: str, skiprows: int, header: int, sheet_name: Optional[str]=None, index_col: Optional[str]=None, usecols: Optional[str]=None) -> pd.DataFrame:
        full_file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
        df = pd.read_excel(full_file_name, 
                           sheet_name=sheet_name,
                           skiprows=skiprows, 
                           header=header, 
                           index_col=index_col, 
                           usecols=usecols)
        return df

#######################################################################


def separate_inventory_by_category(df: pd.DataFrame) -> list[pd.DataFrame]:
        """Separate one Dataframe into 6, each corresponding to one RCP category"""
        column_names = ["equipment", "quantity", "quality", "sharing", "reconditioning_percent"]
        half_length_row = 43
        length_row = half_length_row*2
        df_mono_mob = df.iloc[0:half_length_row, 0:5].reset_index(drop=True)
        df_mono_mobfix = df.iloc[0:half_length_row, 5:10].reset_index(drop=True)
        df_mono_fix = df.iloc[0:half_length_row, 10:15].reset_index(drop=True)
        df_multi_mob = df.iloc[half_length_row:length_row, 0:5].reset_index(drop=True)
        df_multi_mobfix = df.iloc[half_length_row:length_row, 5:10].reset_index(drop=True)
        df_multi_fix = df.iloc[half_length_row:length_row, 10:15].reset_index(drop=True)
        df_list = [df_mono_mob, df_mono_mobfix, df_mono_fix, df_multi_mob, df_multi_mobfix, df_multi_fix]
        for df in df_list:
                df.columns = column_names
        return df_list


def separate_impacts_by_category(df: pd.DataFrame) -> List[pd.DataFrame]:
        """Separate one Dataframe into 6, each corresponding to one RCP category"""
        column_names = ["equipment",
                        "BLD ADPe", "BLD GWP", "BLD AP", "BLD PM", "BLD IR", "BLD TPE",
                        "DIS ADPe", "DIS GWP", "DIS AP", "DIS PM", "DIS IR", "DIS TPE",
                        "INS ADPe", "INS GWP", "INS AP", "INS PM", "INS IR", "INS TPE",
                        "USE ADPe", "USE GWP", "USE AP", "USE PM", "USE IR", "USE TPE",
                        "REC ADPe", "REC GWP", "REC AP", "REC PM", "REC IR", "REC TPE",
                        "EOL ADPe", "EOL GWP", "EOL AP", "EOL PM", "EOL IR", "EOL TPE"]
        half_length_row = 43
        length_row = half_length_row*2
        width_col = len(column_names)
        two_width_col = width_col*2
        three_width_col = width_col*3
        df_mono_mob = df.iloc[0:half_length_row, 0:width_col].reset_index(drop=True)
        df_mono_mobfix = df.iloc[0:half_length_row, width_col:two_width_col].reset_index(drop=True)
        df_mono_fix = df.iloc[0:half_length_row, two_width_col:three_width_col].reset_index(drop=True)
        df_multi_mob = df.iloc[half_length_row:length_row, 0:width_col].reset_index(drop=True)
        df_multi_mobfix = df.iloc[half_length_row:length_row, width_col:two_width_col].reset_index(drop=True)
        df_multi_fix = df.iloc[half_length_row:length_row, two_width_col:three_width_col].reset_index(drop=True)
        df_list = [df_mono_mob, df_mono_mobfix, df_mono_fix, df_multi_mob, df_multi_mobfix, df_multi_fix]
        for df in df_list:
                df.columns = column_names
        return df_list


def separate_ab_factors_by_category(df: pd.DataFrame) -> List[pd.DataFrame]:
        """Separate the unique Dataframe into 3 ones, corresponding to mobile, fixed or both
        The same factors are applied to the categories 0, 1, 2 and 3, 4, 5"""
        column_names = ["equipment", 
                        "BLD typA", "BLD typB",
                        "DIS typA", "DIS typB",
                        "INS typA", "INS typB",
                        "USE typA", "USE typB",
                        "REC typA", "REC typB",
                        "EOL typA", "EOL typB"]
        half_length_row = 43
        width_col = len(column_names)
        two_width_col = width_col*2
        three_width_col = width_col*3
        df_mob = df.iloc[0:half_length_row, 0:width_col].reset_index(drop=True)
        df_mobfix = df.iloc[0:half_length_row, width_col:two_width_col].reset_index(drop=True)
        df_fix = df.iloc[0:half_length_row, two_width_col:three_width_col].reset_index(drop=True)
        df_list = [df_mob, df_mobfix, df_fix]
        for df in df_list:
                df.columns = column_names
        return df_list

def separate_elec_by_category(df: pd.DataFrame) -> List[pd.DataFrame]:
        """Separate the unique Dataframe into 3 ones, corresponding to mobile, fixed or both
        The same factors are applied to the categories 0, 1, 2 and 3, 4, 5"""
        column_names = ["equipment", "elec"]
        half_length_row = 43
        width_col = len(column_names)
        two_width_col = width_col*2
        three_width_col = width_col*3
        df_mob = df.iloc[0:half_length_row, 0:width_col].reset_index(drop=True)
        df_mobfix = df.iloc[0:half_length_row, width_col:two_width_col].reset_index(drop=True)
        df_fix = df.iloc[0:half_length_row, two_width_col:three_width_col].reset_index(drop=True)
        df_list = [df_mob, df_mobfix, df_fix]
        for df in df_list:
                df.columns = column_names
        return df_list

#######################################################################