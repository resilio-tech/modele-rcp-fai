
import pandas as pd

from typing import Optional, List


def sum_impacts_on_type(dict_impact_op: List[pd.DataFrame]) -> pd.DataFrame:
    LC_STEPS = ["BLD", "DIS", "USE", "REC", "EOL"]
    INDICATOR_LIST = ["ADPe", "GWP", "AP", "PM", "IR", "TPE"]
    dict_impact_op_summed = dict_impact_op.copy()
    for i in range(0, 6):
            for lc_step in LC_STEPS:
                    for ind in INDICATOR_LIST:
                            old_column_name_a = lc_step + " " + ind + " typA"
                            old_column_name_b = lc_step + " " + ind + " typB"
                            new_column_name = lc_step + " " + ind
                            # create one new column that is the sum of the columns typA and typB
                            dict_impact_op_summed[i][new_column_name] = dict_impact_op_summed[i][old_column_name_a] + dict_impact_op_summed[i][old_column_name_b]
                            # drop the old columns
                            dict_impact_op_summed[i] = dict_impact_op_summed[i].drop([old_column_name_a], axis=1)
                            dict_impact_op_summed[i] = dict_impact_op_summed[i].drop([old_column_name_b], axis=1)
    dict_impact_op_summed[0].insert(0, 'type', 'fixe')
    dict_impact_op_summed[2].insert(0, 'type', 'mobile')
    frames = [dict_impact_op_summed[0], dict_impact_op_summed[2]]
    df_impact_op_summed = pd.concat(frames)
    return df_impact_op_summed



def sum_impacts_on_category(df_impact_op_summed: pd.DataFrame) -> pd.DataFrame:
    df_impact_cat = df_impact_op_summed.groupby(['type', 'category']).sum().reset_index()
    return df_impact_cat


def percentage_by_category(df_impact_cat: pd.DataFrame) -> pd.DataFrame:
    df_percentage_cat = df_impact_cat.copy()
    for col in df_impact_cat.columns[2:]:
        df_percentage_cat[col] = df_impact_cat[col] / df_impact_cat[col].sum()
    return df_percentage_cat



#################################################################

def save_detail_table_excel(filename: str, operator_list: List[str], dict_impact_op: List[pd.DataFrame]):
    dict_impact_op_concat = []
    for operator in operator_list:
        dict_impact_op[operator][0].insert(0, 'network_type', 'fixe')
        dict_impact_op[operator][2].insert(0, 'network_type', 'mobile')
        frames = [dict_impact_op[operator][0], dict_impact_op[operator][2]]
        impact_op_concat = pd.concat(frames)
        impact_op_concat.insert(0, 'operator', operator)
        dict_impact_op_concat.append(impact_op_concat)
    impact_op_concat = pd.concat(dict_impact_op_concat)
    all_cols = list(impact_op_concat.columns)
    cols = [el for el in all_cols if el not in ['operator', 'network_type', 'category', 'equipment']]
    df_table = pd.melt(impact_op_concat, id_vars=['operator','network_type', 'category', 'equipment'], value_vars=cols)
    df_table[['lc_step', 'indicator', 'indicator_type']] = df_table['variable'].str.split(pat=' ', expand=True)
    df_table = df_table.drop('variable', axis=1)
    col_value = df_table.pop('value')
    df_table.insert(len(df_table.columns), 'value', col_value)
    with pd.ExcelWriter(filename) as writer:
        df_table.to_excel(writer, index=False)


def save_FU_table_excel(filename: str, operator_list: List[str], dict_impact_op: List[pd.DataFrame]):
    dict_impact_op_concat = []
    for operator in operator_list:
        dict_impact_op[operator]['fixed'].insert(0, 'network_type', "fixe")
        dict_impact_op[operator]['mobile'].insert(0, 'network_type', "mobile")
        frames = [dict_impact_op[operator]['fixed'], dict_impact_op[operator]['mobile']]
        impact_op_concat = pd.concat(frames)
        impact_op_concat = impact_op_concat.rename(columns={'type': 'indicator_type'})
        impact_op_concat.insert(0, 'operator', operator)
        dict_impact_op_concat.append(impact_op_concat)
    df_impact = pd.concat(dict_impact_op_concat)
    with pd.ExcelWriter(filename) as writer:
            df_impact.to_excel(writer, index=False)


def save_results_detailed(filename: str, operator_list: List[str], dict_impact_op: List[pd.DataFrame]):
    """ Save in one file all the detailed results for every indicators (one sheet per operator)"""

    with pd.ExcelWriter(filename) as writer:
        for operator in operator_list:
            df_impact_op_summed = sum_impacts_on_type(dict_impact_op[operator])
            df_impact_op_summed.to_excel(writer, sheet_name=operator, index=False)


def save_results_by_category(filename: str, operator_list: List[str], dict_impact_op: List[pd.DataFrame]):
    """ Save in one file the results by category for every indicators (one sheet per operator)"""

    with pd.ExcelWriter(filename) as writer:
        for operator in operator_list:
            df_impact_op_summed = sum_impacts_on_type(dict_impact_op[operator])
            df_impact_cat = sum_impacts_on_category(df_impact_op_summed)
            df_impact_cat.to_excel(writer, sheet_name=operator, index=False)


def save_results_percentage_by_category(filename: str, operator_list: List[str], dict_impact_op: List[pd.DataFrame]):
    """ Save in one file the results by category for every indicators (one sheet per operator)"""

    with pd.ExcelWriter(filename) as writer:
        for operator in operator_list:
            df_impact_op_summed = sum_impacts_on_type(dict_impact_op[operator])
            df_impact_cat = sum_impacts_on_category(df_impact_op_summed)
            df_percentage_cat = percentage_by_category(df_impact_cat)
            df_percentage_cat.to_excel(writer, sheet_name=operator, index=False)


def save_results_global(filename: str, operator_list: List[str], dict_data_operator: pd.DataFrame):
    """ Put the global impacts per operator in the right format to display them in one single table """
    list_results = []
    index_list = []
    for operator in operator_list:
            if (operator == "orange"):
                print(dict_data_operator[operator]['fixed'])
            index_list.append(operator+' fixed')
            index_list.append(operator+' mobile')
            list_results.append(dict_data_operator[operator]['fixed']['impact'])
            list_results.append(dict_data_operator[operator]['mobile']['impact'])
    
    dict_data_operator['adista']['fixed']['index'] = dict_data_operator['adista']['fixed']['indicator']+ " " + dict_data_operator['adista']['fixed']['type']
    
    # New dataframe
    df_results = pd.DataFrame(data=list_results)
    df_results.index = index_list
    df_results.columns = dict_data_operator['adista']['fixed']['index']
    df_results.to_excel(filename)


def save_quality_score_results(filename: str, quality_dict: dict[(str, float)]):
    """ Save the quality score per operator in one file """
    df_quality = pd.DataFrame.from_dict(quality_dict, orient='index')
    df_quality.to_excel(filename)


#################################################################