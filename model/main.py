
import os

import pandas as pd

from typing import Optional, List

from load_data import prepare_data, load_op_data, load_ab_factors, load_elec_consumption
from model import compute_electrical_consumption, multiply_unitary_impacts_by_quantity, allocation_ab_factors, allocation_multi_op, allocation_multi_network, sum_impacts_on_type, sum_impacts_operator


def model_pipeline(operator_list : list[str], filename_list: dict[(str, str)]) -> pd.DataFrame:
        """Define the pipeline of the model"""

        # Load and clean the data. Put it in the right format
        dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)
        # dict_impact_list : contains impacts for every LC steps and indicators
        # dict_purchase_list : contains quantity of purchased equipments in year n, quality, sharing information, reconditioning ratio
        # dict_dismounting_list : contains quantity of dismounted equipments in year n, quality, sharing information

        operators_data = load_op_data() # suscriber count, volume of transfered data and total electrical consumption for every operators
        df_ab_factors = load_ab_factors() # coefficients to allocate impacts to fixed and variable part of the network
        df_elec = load_elec_consumption() # estimated values of electrical consumption for all the equipments


        # Step 0 : Approximate electrical consumption of every equipments using energy estimation and real total energy consumed
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator] = compute_electrical_consumption(dict_purchase_list[operator], operator_data, df_elec)


        # Step 0 : Multiply the unitary impacts for equipments by the number of equipments of each type
        for operator in operator_list:
                for i in range(0, 6):
                        dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])
        

        # Step 1 : Allocation with (a, b) for fixed and variable impacts of the network
        dict_impact_list_ab = {} # new dict that contains impacts for every LC steps, indicators and for a/b
        for operator in operator_list:
                dict_impact_list_ab[operator] = allocation_ab_factors(dict_impact_list[operator], df_ab_factors)


        # Step 3.a : Allocation for shared equipments
        for operator in operator_list:
                # Allocation for shared equipments for fixed network
                dict_impact_list_modif_fix = allocation_multi_op("fixed", "purchase", dict_purchase_list[operator][3], dict_impact_list_ab, operator, operators_data)
                dict_impact_list_modif_fix = allocation_multi_op("fixed", "dismounting", dict_dismounting_list[operator][3], dict_impact_list_modif_fix, operator, operators_data)
                # Allocation for shared equipments for mobile network
                dict_impact_list_modif_mob = allocation_multi_op("mobile", "purchase", dict_purchase_list[operator][4], dict_impact_list_modif_fix, operator, operators_data)
                dict_impact_list_modif_mob = allocation_multi_op("mobile", "dismounting", dict_dismounting_list[operator][4], dict_impact_list_modif_mob, operator, operators_data)
                # Allocation for shared equipments that are used for both fixed and mobile network
                dict_impact_list_modif_mob_fix = allocation_multi_op("fixed_and_mobile", "purchase", dict_purchase_list[operator][5], dict_impact_list_modif_mob, operator, operators_data)
                dict_impact_list_modif_mob_fix = allocation_multi_op("fixed_and_mobile", "dismounting", dict_dismounting_list[operator][5], dict_impact_list_modif_mob_fix, operator, operators_data)


        # Step 3.b : Allocation for shared equipments between fixed and mobile network
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_impact_list_modif_mob_fix[operator] = allocation_multi_network(dict_impact_list_modif_mob_fix[operator], operator_data)


        # Save intermediate results for analysis
        for operator in operator_list:

                dict_impact_list_summed = sum_impacts_on_type(dict_impact_list_modif_mob_fix[operator])

                file_name = "./Resultats_test_" + operator + ".xlsx"
                with pd.ExcelWriter(file_name) as writer:
                        dict_impact_list_summed[0].to_excel(writer, sheet_name='fixed', index=False)
                        dict_impact_list_summed[1].to_excel(writer, sheet_name='fixed_and_mobile', index=False)
                        dict_impact_list_summed[2].to_excel(writer, sheet_name='mobile', index=False)

        # Step 4 : Sum the impacts for each operator
        # We sum over all equipments and all life cycle steps.
        dict_impact_op = {}
        for operator in operator_list:
                dict_op = sum_impacts_operator(dict_impact_list_modif_mob_fix[operator])

                # dict_impact_op = dictionnary with {operator : {"fixed" : impacts , "mobile" : impacts}}
                dict_impact_op[operator] = dict_op


        # Step 5 : Allocation for the FU calculations
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                # Temporal allocation on one month
                dict_impact_op[operator]["fixed"]["impact"] = dict_impact_op[operator]["fixed"]["impact"].div(12)
                dict_impact_op[operator]["mobile"]["impact"] = dict_impact_op[operator]["mobile"]["impact"].div(12)
                # Allocation with the quantity of consummed data
                normalisation_factor_fix_typA = operator_data['quantite_donnees_fix'] / 12
                normalisation_factor_mob_typA = operator_data['quantite_donnees_mob'] / 12
                dict_impact_op[operator]["fixed"]["impact"].loc[dict_impact_op[operator]["fixed"]["type"] == "typA"] = dict_impact_op[operator]["fixed"]["impact"][dict_impact_op[operator]["fixed"]["type"] == "typA"] / normalisation_factor_fix_typA
                dict_impact_op[operator]["mobile"]["impact"].loc[dict_impact_op[operator]["mobile"]["type"] == "typA"] = dict_impact_op[operator]["mobile"]["impact"][dict_impact_op[operator]["mobile"]["type"] == "typA"] / normalisation_factor_mob_typA
                # Allocation with the number of users
                normalisation_factor_fix_typB = operator_data['nb_abonnes_fix'] / 12
                normalisation_factor_mob_typB = operator_data['nb_abonnes_mob'] / 12
                dict_impact_op[operator]["fixed"]["impact"][dict_impact_op[operator]["fixed"]["type"] == "typB"] = dict_impact_op[operator]["fixed"]["impact"][dict_impact_op[operator]["fixed"]["type"] == "typB"] / normalisation_factor_fix_typB
                dict_impact_op[operator]["mobile"]["impact"][dict_impact_op[operator]["mobile"]["type"] == "typB"] = dict_impact_op[operator]["mobile"]["impact"][dict_impact_op[operator]["mobile"]["type"] == "typB"] / normalisation_factor_mob_typB

        return dict_impact_op