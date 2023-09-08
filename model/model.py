
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from typing import Optional, List

def compute_electrical_consumption(inventory_type: str, dict_list: List[pd.DataFrame], operator_data: pd.DataFrame, df_elec: List[pd.DataFrame]) -> List[pd.DataFrame]:
        
        # Adding the box consumption to the electricity consumption
        for i in [0, 3]:
                df_box = dict_list[i].loc[dict_list[i]["equipment"].str.contains('|'.join(['Box', 'ONT']))][["equipment", "quantity"]]
                elec_box_unit = pd.DataFrame([93.4675, 93.4675, 93.4675, 35.04, 93.4675], columns=['annual_elec'])
                elex_box_total = (df_box["quantity"]*elec_box_unit["annual_elec"]).sum()
                operator_data["conso_elec_fix"] += elex_box_total
        
        list_elec = []
        for i in range(0, 6):
                r = i%3
                # Allocation of electrical consumption among the equipments
                dict_list[i]["estimated_elec"] = dict_list[i]["quantity"]*df_elec[r]["elec"]
                total_elec_cat = dict_list[i]["estimated_elec"].sum()
                list_elec.append(total_elec_cat)

        total_elec_fixed = list_elec[0] + list_elec[3]
        total_elec_mobile = list_elec[2] + list_elec[5]
        
        # Allocation of electrical consumption among the equipments
        dict_list[0]["real_elec"] = dict_list[0]["estimated_elec"]*operator_data["conso_elec_fix"]/total_elec_fixed
        dict_list[1]["real_elec"] = dict_list[1]["estimated_elec"]
        dict_list[2]["real_elec"] = dict_list[2]["estimated_elec"]*operator_data["conso_elec_mob"]/total_elec_mobile
        dict_list[3]["real_elec"] = dict_list[3]["estimated_elec"]*operator_data["conso_elec_fix"]/total_elec_fixed
        dict_list[4]["real_elec"] = dict_list[4]["estimated_elec"]
        dict_list[5]["real_elec"] = dict_list[5]["estimated_elec"]*operator_data["conso_elec_mob"]/total_elec_mobile
        
        return dict_list, operator_data


def multiply_unitary_impacts_by_quantity(dict_impact: pd.DataFrame, dict_purchase: pd.DataFrame, dict_dismounting: pd.DataFrame) -> pd.DataFrame:
        # Separation between newly bought and reconditionned equipments
        dict_purchase["quantity_new"] = dict_purchase["quantity"]*(1-dict_purchase["reconditioning_percent"])
        dict_purchase["quantity_reconditioning"] = dict_purchase["quantity"]*dict_purchase["reconditioning_percent"]


        # Multiplication of the unitary impacts by the volume of equipments
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('BLD')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('BLD')]].multiply(dict_purchase["quantity_new"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('DIS')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('DIS')]].multiply(dict_purchase["quantity_new"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('USE')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('USE')]].multiply(dict_purchase["real_elec"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('EOL')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('EOL')]].multiply(dict_dismounting["quantity"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('REC')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('REC')]].multiply(dict_purchase["quantity_reconditioning"], axis="index")
        
        return dict_impact


def multiply_unitary_impacts_by_quantity_and_lifespan(dict_impact: pd.DataFrame, dict_inventory: pd.DataFrame) -> pd.DataFrame:
        # Separation between newly bought and reconditionned equipments
        dict_inventory["quantity_new"] = dict_inventory["quantity"]*(1-dict_inventory["reconditioning_percent"])
        dict_inventory["quantity_reconditioning"] = dict_inventory["quantity"]*dict_inventory["reconditioning_percent"]

        # Multiplication of the unitary impacts by the volume of equipments
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('BLD')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('BLD')]].multiply(dict_inventory["quantity_new"], axis="index").div(dict_inventory["lifespan"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('DIS')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('DIS')]].multiply(dict_inventory["quantity_new"], axis="index").div(dict_inventory["lifespan"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('USE')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('USE')]].multiply(dict_inventory["real_elec"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('EOL')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('EOL')]].multiply(dict_inventory["quantity"], axis="index").div(dict_inventory["lifespan"], axis="index")
        dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('REC')]] = dict_impact[dict_impact.columns[pd.Series(dict_impact.columns).str.startswith('REC')]].multiply(dict_inventory["quantity_reconditioning"], axis="index").div(dict_inventory["lifespan"], axis="index")
        dict_impact_clean = dict_impact.fillna(0)
        return dict_impact_clean


def allocation_ab_factors(dict_impact_op: List[pd.DataFrame], df_ab_factors: List[pd.DataFrame]) -> List[pd.DataFrame]:
        LC_STEPS = ["BLD", "DIS", "USE", "REC", "EOL"]
        INDICATOR_LIST = ["ADPe", "GWP", "AP", "PM", "IR", "TPE"]
        for i in range(0, 6):
                r = i%3
                for lc_step in LC_STEPS:
                        for ind in INDICATOR_LIST:
                                old_column_name = lc_step + " " + ind
                                a_column_name = lc_step + " typA"
                                b_column_name = lc_step + " typB"
                                new_column_name_a = lc_step + " " + ind + " typA"
                                new_column_name_b = lc_step + " " + ind + " typB"
                                # create two new columns with the impacts allocated to a and b types
                                dict_impact_op[i][new_column_name_a] = dict_impact_op[i][old_column_name] * (df_ab_factors[r][a_column_name].div(100))
                                dict_impact_op[i][new_column_name_b] = dict_impact_op[i][old_column_name] * (df_ab_factors[r][b_column_name].div(100))
                                # drop the old column
                                dict_impact_op[i] = dict_impact_op[i].drop([old_column_name], axis=1)
        return dict_impact_op


def compute_operator_weight(alloc_string: pd.Series, network_type: str, operators_data: pd.DataFrame):
        """Compute the repartition coefficients to distribute the impacts of shared equipments among the operators that are using them"""
        # Exemple of string : operateur1, 50 / operateur2, 60 / operateur3, 30
        # 1. Clean the string and convert it to a dictionnary
        alloc_dict_str = dict(x.split(",") for x in alloc_string.split("/"))
        alloc_dict = {k: int(v) for k, v in alloc_dict_str.items()} # dictionnary with {operator : nb equipment}
        for k, v in alloc_dict.items():
                operator_data = operators_data.loc[k]
                operator_weight_a = 0
                operator_weight_b = 0
                # 2. Depending on type of network, choose the appropriate weights for coeff. a and b
                # Hypothesis : An operator with a higher quantity of consummed data will supposedly use more the equipment
                if (network_type == "fixed"):
                        operator_weight_a = operator_data['quantite_donnees_fix']
                        operator_weight_b = operator_data['nb_abonnes_fix']
                elif(network_type == "mobile"):
                        operator_weight_a = operator_data['quantite_donnees_mob']
                        operator_weight_b = operator_data['nb_abonnes_mob']
                elif(network_type == "fixed_and_mobile"):
                        operator_weight_a = operator_data['quantite_donnees_mob'] + operator_data['quantite_donnees_fix']
                        operator_weight_b = operator_data['nb_abonnes_mob'] + operator_data['nb_abonnes_fix']
                # 3. Apply the a and b weights to the dictionnary containing the number of equipements
                alloc_dict[k] = {'a': v*operator_weight_a, 'b': v*operator_weight_b}
        # 4. Normalize the weights in order to obtain a total of 1 for a and b
        total_a = 0
        total_b = 0
        for k, v in alloc_dict.items():
                total_a += v['a']
                total_b += v['b']
        weight_dict = {k: {'a':v['a']/total_a, 'b':v['b']/total_b} for k, v in alloc_dict.items()}
        # We obtain weight_dict = dictionnary with {operator : {a : weight_a, b : weight_b}}
        return weight_dict


def allocation_multi_op(network_type: str, inventory_type: str, inventory_op_i: List[pd.DataFrame], dict_impact_list: dict[(str, list[pd.DataFrame])], operator: str, operators_data: pd.DataFrame) -> dict[(str, list[pd.DataFrame])]:
        """Distribute the impacts of shared equipments between the operators that are using them"""
        
        if (network_type == "fixed"): # Fixed network
                # We consider the inventory of one operator
                for index, row in inventory_op_i.iterrows():
                        if (not pd.isnull(row["sharing"])):
                                alloc_string = row['sharing'].replace(" ", "")
                                weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)
                                for k, v in weight_dict.items():
                                        # k : operator whose impacts need to be updated
                                        # v : dict of weights that needs to be applied to the impacts
                                        for col in dict_impact_list[k][0]:
                                                if (inventory_type == "purchase"):
                                                        if (("EOL" not in col) and ("typA" in col)):
                                                                dict_impact_list[k][0][col].iloc[[index]] = dict_impact_list[k][0][col].iloc[[index]].to_numpy() + dict_impact_list[operator][3][col].iloc[[index]].to_numpy()*v['a']
                                                        if (("EOL" not in col) and ("typB" in col)):
                                                                dict_impact_list[k][0][col].iloc[[index]] = dict_impact_list[k][0][col].iloc[[index]].to_numpy() + dict_impact_list[operator][3][col].iloc[[index]].to_numpy()*v['b']
                                                elif (inventory_type == "dismounting"):
                                                        if (("EOL" in col) and ("typA" in col)):
                                                                dict_impact_list[k][0][col].iloc[[index]] = dict_impact_list[k][0][col].iloc[[index]].to_numpy() + dict_impact_list[operator][3][col].iloc[[index]].to_numpy()*v['a']
                                                        if (("EOL" in col) and ("typB" in col)):
                                                                dict_impact_list[k][0][col].iloc[[index]] = dict_impact_list[k][0][col].iloc[[index]].to_numpy() + dict_impact_list[operator][3][col].iloc[[index]].to_numpy()*v['b']
                                                elif (inventory_type == "full_inventory"):
                                                        if ("typA" in col):
                                                                dict_impact_list[k][0][col].iloc[[index]] = dict_impact_list[k][0][col].iloc[[index]].to_numpy() + dict_impact_list[operator][3][col].iloc[[index]].to_numpy()*v['a']
                                                        if ("typB" in col):
                                                                dict_impact_list[k][0][col].iloc[[index]] = dict_impact_list[k][0][col].iloc[[index]].to_numpy() + dict_impact_list[operator][3][col].iloc[[index]].to_numpy()*v['b']
                                                
        
        if (network_type == "fixed_and_mobile"): # Mobile network
                # We consider the inventory of one operator
                for index, row in inventory_op_i.iterrows():
                        if (not pd.isnull(row["sharing"])):
                                alloc_string = row['sharing'].replace(" ", "")
                                weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)
                                for k, v in weight_dict.items():
                                        # k : operator whose impacts need to be updated
                                        # v : dict of weights that needs to be applied to the impacts
                                        for col in dict_impact_list[k][1]:
                                                if (inventory_type == "purchase"):
                                                        if (("EOL" not in col) and ("typA" in col)):
                                                                dict_impact_list[k][1][col].iloc[[index]] = dict_impact_list[k][1][col].iloc[[index]].to_numpy() + dict_impact_list[operator][4][col].iloc[[index]].to_numpy()*v['a']
                                                        if (("EOL" not in col) and ("typB" in col)):
                                                                dict_impact_list[k][1][col].iloc[[index]] = dict_impact_list[k][1][col].iloc[[index]].to_numpy() + dict_impact_list[operator][4][col].iloc[[index]].to_numpy()*v['b']
                                                elif (inventory_type == "dismounting"):
                                                        if (("EOL" in col) and ("typA" in col)):
                                                                dict_impact_list[k][1][col].iloc[[index]] = dict_impact_list[k][1][col].iloc[[index]].to_numpy() + dict_impact_list[operator][4][col].iloc[[index]].to_numpy()*v['a']
                                                        if (("EOL" in col) and ("typB" in col)):
                                                                dict_impact_list[k][1][col].iloc[[index]] = dict_impact_list[k][1][col].iloc[[index]].to_numpy() + dict_impact_list[operator][4][col].iloc[[index]].to_numpy()*v['b']
                                                elif (inventory_type == "full_inventory"):
                                                        if ("typA" in col):
                                                                dict_impact_list[k][1][col].iloc[[index]] = dict_impact_list[k][1][col].iloc[[index]].to_numpy() + dict_impact_list[operator][4][col].iloc[[index]].to_numpy()*v['a']
                                                        if ("typB" in col):
                                                                dict_impact_list[k][1][col].iloc[[index]] = dict_impact_list[k][1][col].iloc[[index]].to_numpy() + dict_impact_list[operator][4][col].iloc[[index]].to_numpy()*v['b']
                                                  

        if (network_type == "mobile"): # For both fixed and mobile networks
                # We consider the inventory of one operator
                for index, row in inventory_op_i.iterrows():
                        if (not pd.isnull(row["sharing"])):
                                alloc_string = row['sharing'].replace(" ", "")
                                weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)
                                for k, v in weight_dict.items():
                                        # k : operator whose impacts need to be updated
                                        # v : dict of weights that needs to be applied to the impacts
                                        for col in dict_impact_list[k][2]:
                                                if (inventory_type == "purchase"):
                                                        if (("EOL" not in col) and ("typA" in col)):
                                                                dict_impact_list[k][2][col].iloc[[index]] = dict_impact_list[k][2][col].iloc[[index]] + dict_impact_list[operator][5][col].iloc[[index]]*v['a']
                                                        if (("EOL" not in col) and ("typB" in col)):
                                                                dict_impact_list[k][2][col].iloc[[index]] = dict_impact_list[k][2][col].iloc[[index]] + dict_impact_list[operator][5][col].iloc[[index]]*v['b']
                                                elif (inventory_type == "dismounting"):
                                                        if (("EOL" in col) and ("typA" in col)):
                                                                dict_impact_list[k][2][col].iloc[[index]] = dict_impact_list[k][2][col].iloc[[index]] + dict_impact_list[operator][5][col].iloc[[index]]*v['a']
                                                        if (("EOL" in col) and ("typB" in col)):
                                                                dict_impact_list[k][2][col].iloc[[index]] = dict_impact_list[k][2][col].iloc[[index]] + dict_impact_list[operator][5][col].iloc[[index]]*v['b']
                                                elif (inventory_type == "full_inventory"):
                                                        if ("typA" in col):
                                                                dict_impact_list[k][2][col].iloc[[index]] = dict_impact_list[k][2][col].iloc[[index]] + dict_impact_list[operator][5][col].iloc[[index]]*v['a']
                                                        if ("typB" in col):
                                                                dict_impact_list[k][2][col].iloc[[index]] = dict_impact_list[k][2][col].iloc[[index]] + dict_impact_list[operator][5][col].iloc[[index]]*v['b']
                                                

        return dict_impact_list



def allocation_multi_network(impact_op : List[pd.DataFrame], operator_data: pd.DataFrame) -> List[pd.DataFrame]:
        """Distribute the impacts of the equipments used for both fixed and mobile networks between these two types"""

        operator_weight_a_fix = operator_data['quantite_donnees_fix']/(operator_data['quantite_donnees_fix']+operator_data['quantite_donnees_mob'])
        operator_weight_b_fix = operator_data['nb_abonnes_fix']/(operator_data['nb_abonnes_fix']+operator_data['nb_abonnes_mob'])
        operator_weight_a_mob = 1 - operator_weight_a_fix
        operator_weight_b_mob = 1 - operator_weight_b_fix

        impacts_fix = impact_op[1].copy()
        impacts_mob = impact_op[1].copy()

        for index, row in impacts_fix.iterrows():
                if (not pd.isnull(row["BLD ADPe typA"])):
                        for col in impacts_fix:
                                if ("typA" in col):
                                        impacts_fix[col].loc[index] = impacts_fix[col].loc[index]*operator_weight_a_fix
                                        impacts_mob[col].loc[index] = impacts_mob[col].loc[index]*operator_weight_a_mob
                                elif ("typB" in col):
                                        impacts_fix[col].loc[index] = impacts_fix[col].loc[index]*operator_weight_b_fix
                                        impacts_mob[col].loc[index] = impacts_mob[col].loc[index]*operator_weight_b_mob
                        impact_op[0] = impact_op[0].append(impacts_fix.loc[index], ignore_index=True)
                        impact_op[2] = impact_op[2].append(impacts_mob.loc[index], ignore_index=True)
        return impact_op


def compute_quality_score(operator_list: List[str], dict_purchase_list: dict[(str, list[pd.DataFrame])], dict_impact: dict[(str, list[pd.DataFrame])]) -> dict[(str, float)]:
        PLANETARY_BOUNDARIES = {'ADPe': 3.18e-2,
                                'GWP': 9.85e2,
                                'AP': 1.45e2,
                                'PM': 7.47e-5,
                                'IR': 7.62e4}
        quality_score_dict = {}
        for operator in operator_list:
                total_weighted_quality = 0
                total_impacts = 0
                for i in [0, 2]:
                        df_impacts = dict_impact[operator][i].drop(['category', 'equipment'], axis=1).T.reset_index()
                        df_impacts[['lc_step', 'indicator', 'type']] = df_impacts["index"].str.split(pat=' ', expand=True)
                        df_impacts = df_impacts.drop(["index", "lc_step", "type"], axis=1)
                        df_impacts = df_impacts.groupby(['indicator']).sum().reset_index()
                        df_impacts.index = df_impacts["indicator"]
                        df_impacts = df_impacts.drop(['indicator'], axis=1).T
                        df_impacts = df_impacts.drop(['TPE'], axis=1)
                        df_impacts_weight = df_impacts.divide(PLANETARY_BOUNDARIES, axis=1).sum(axis=1)
                        df_impacts["weighted_quality"] = df_impacts_weight*dict_purchase_list[operator][i]["quality_score"]
                        total_weighted_quality += df_impacts["weighted_quality"].sum()
                        total_impacts += df_impacts_weight.sum()
                quality_score_dict[operator] = total_weighted_quality/total_impacts
        return quality_score_dict


def sum_impacts_operator(impact_op : list[pd.DataFrame]) -> dict[(str, pd.DataFrame)]:
        dict_op = {}
        dict_op["fixed"] = impact_op[0].iloc[:, 1:].sum().to_frame(name="impact").reset_index()
        dict_op["fixed"][['lc_step', 'indicator', 'type']] = dict_op["fixed"]['index'].str.split(pat=' ', expand=True)
        dict_op["fixed"] = dict_op["fixed"].groupby(['indicator', 'type'])["impact"].sum().reset_index()

        dict_op["mobile"] = impact_op[2].iloc[:, 1:].sum().to_frame(name="impact").reset_index()
        dict_op["mobile"][['lc_step', 'indicator', 'type']] = dict_op["mobile"]['index'].str.split(pat=' ', expand=True)
        dict_op["mobile"] = dict_op["mobile"].groupby(['indicator', 'type'])["impact"].sum().reset_index()
        return dict_op


def allocation_fu(dict_impact_op : dict[(str, pd.DataFrame)], operator_data: pd.DataFrame) -> dict[(str, pd.DataFrame)]:
        # Temporal allocation on one month
        dict_impact_op["fixed"]["impact"] = dict_impact_op["fixed"]["impact"].div(12)
        dict_impact_op["mobile"]["impact"] = dict_impact_op["mobile"]["impact"].div(12)
        # Allocation with the quantity of consummed data
        normalisation_factor_fix_typA = operator_data['quantite_donnees_fix']*1024 / 12
        normalisation_factor_mob_typA = operator_data['quantite_donnees_mob']*1024 / 12
        dict_impact_op["fixed"]["impact"].loc[dict_impact_op["fixed"]["type"] == "typA"] = dict_impact_op["fixed"]["impact"][dict_impact_op["fixed"]["type"] == "typA"] / normalisation_factor_fix_typA
        dict_impact_op["mobile"]["impact"].loc[dict_impact_op["mobile"]["type"] == "typA"] = dict_impact_op["mobile"]["impact"][dict_impact_op["mobile"]["type"] == "typA"] / normalisation_factor_mob_typA
        # Allocation with the number of users
        normalisation_factor_fix_typB = operator_data['nb_abonnes_fix']
        normalisation_factor_mob_typB = operator_data['nb_abonnes_mob']
        dict_impact_op["fixed"]["impact"][dict_impact_op["fixed"]["type"] == "typB"] = dict_impact_op["fixed"]["impact"][dict_impact_op["fixed"]["type"] == "typB"] / normalisation_factor_fix_typB
        dict_impact_op["mobile"]["impact"][dict_impact_op["mobile"]["type"] == "typB"] = dict_impact_op["mobile"]["impact"][dict_impact_op["mobile"]["type"] == "typB"] / normalisation_factor_mob_typB

        return dict_impact_op