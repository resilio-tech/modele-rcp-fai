
import os

import pandas as pd

from typing import Optional, List

from load_data import prepare_data_flux_method, prepare_data_lifespan_method, load_op_data, load_ab_factors, load_elec_consumption
from model import compute_electrical_consumption, multiply_unitary_impacts_by_quantity, multiply_unitary_impacts_by_quantity_and_lifespan, \
        allocation_ab_factors, allocation_multi_op, allocation_multi_network, allocation_fu, sum_impacts_operator, compute_quality_score
from results import save_results_detailed, save_results_by_category, save_results_percentage_by_category, save_results_global, save_quality_score_results, save_detail_table_excel, save_FU_table_excel


def model_pipeline_flux_method(method_name: str, operator_list : list[str], filename_list: dict[(str, str)], filename_impacts: str, filename_operator_data: str) -> pd.DataFrame:
        """Define the pipeline of the model"""

        # Load and clean the data. Put it in the right format
        dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)
        # dict_impact_list : contains impacts for every LC steps and indicators
        # dict_purchase_list : contains quantity of purchased equipments in year n, quality, sharing information, reconditioning ratio
        # dict_dismounting_list : contains quantity of dismounted equipments in year n, quality, sharing information

        operators_data = load_op_data(filename_operator_data) # suscriber count, volume of transfered data and total electrical consumption for every operators
        operators_data_updated = operators_data.copy()
        df_ab_factors = load_ab_factors() # coefficients to allocate impacts to fixed and variable part of the network
        df_elec = load_elec_consumption() # estimated values of electrical consumption for all the equipments

        # Step 0 : Approximate electrical consumption of every equipments using energy estimation and real total energy consumed
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator], operators_data_updated.loc[operator] = compute_electrical_consumption("purchase", dict_purchase_list[operator], operator_data, df_elec)

        # Step 1 : Multiply the unitary impacts for equipments by the number of equipments of each type
        for operator in operator_list:
                for i in range(0, 6):
                        dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])

        # Step 2 : Allocation with (a, b) for fixed and variable impacts of the network
        dict_impact_list_ab = {} # new dict that contains impacts for every LC steps, indicators and for a/b
        for operator in operator_list:
                dict_impact_list_ab[operator] = allocation_ab_factors(dict_impact_list[operator], df_ab_factors)



        # Step 3.a : Allocation for shared equipments
        for operator in operator_list:
                # Allocation for shared equipments for fixed network
                dict_impact_list_modif_fix = allocation_multi_op("fixed", "purchase", dict_purchase_list[operator][3], dict_impact_list_ab, operator, operators_data)
                dict_impact_list_modif_fix = allocation_multi_op("fixed", "dismounting", dict_dismounting_list[operator][3], dict_impact_list_modif_fix, operator, operators_data)
                # Allocation for shared equipments for mobile network
                dict_impact_list_modif_mob = allocation_multi_op("mobile", "purchase", dict_purchase_list[operator][5], dict_impact_list_modif_fix, operator, operators_data)
                dict_impact_list_modif_mob = allocation_multi_op("mobile", "dismounting", dict_dismounting_list[operator][5], dict_impact_list_modif_mob, operator, operators_data)
                # Allocation for shared equipments that are used for both fixed and mobile network
                dict_impact_list_modif_mob_fix = allocation_multi_op("fixed_and_mobile", "purchase", dict_purchase_list[operator][4], dict_impact_list_modif_mob, operator, operators_data)
                dict_impact_list_modif_mob_fix = allocation_multi_op("fixed_and_mobile", "dismounting", dict_dismounting_list[operator][4], dict_impact_list_modif_mob_fix, operator, operators_data)


        # Step 3.b : Allocation for shared equipments between fixed and mobile network
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_impact_list_modif_mob_fix[operator] = allocation_multi_network(dict_impact_list_modif_mob_fix[operator], operator_data)


        # Quality analysis
        quality_dict = compute_quality_score(operator_list, dict_purchase_list, dict_impact_list_modif_mob_fix)
        #save_quality_score_results("../Results_" + method_name + "_quality.xlsx", quality_dict)

        # Save intermediate results for analysis
        save_detail_table_excel("../Results_" + method_name + "_table.xlsx", operator_list, dict_impact_list_modif_mob_fix)
        

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
                dict_impact_op[operator] = allocation_fu(dict_impact_op[operator], operator_data)


        # Save FU results of operators
        save_FU_table_excel("../Results_" + method_name + "_table_FU.xlsx", operator_list, dict_impact_op)

        return dict_impact_op


#################################################################################

#################################################################################


def model_pipeline_lifespan_method(method_name: str, operator_list : list[str], filename_list: dict[(str, str)], filename_impacts: str, filename_operator_data: str) -> pd.DataFrame:
        """Define the pipeline of the model"""

        # Load and clean the data. Put it in the right format
        dict_impact_list, dict_inventory_list = prepare_data_lifespan_method(operator_list, filename_list, filename_impacts)
        # dict_impact_list : contains impacts for every LC steps and indicators
        # dict_purchase_list : contains quantity of purchased equipments in year n, quality, sharing information, reconditioning ratio
        # dict_dismounting_list : contains quantity of dismounted equipments in year n, quality, sharing information

        operators_data = load_op_data(filename_operator_data) # suscriber count, volume of transfered data and total electrical consumption for every operators
        operators_data_updated = operators_data.copy()
        df_ab_factors = load_ab_factors() # coefficients to allocate impacts to fixed and variable part of the network
        df_elec = load_elec_consumption() # estimated values of electrical consumption for all the equipments

        # Step 0 : Approximate electrical consumption of every equipments using energy estimation and real total energy consumed
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_inventory_list[operator], operators_data_updated.loc[operator] = compute_electrical_consumption("full_inventory", dict_inventory_list[operator], operator_data, df_elec)

        # Step 1 : Multiply the unitary impacts for equipments by the number of equipments of each type
        for operator in operator_list:
                for i in range(0, 6):
                        dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity_and_lifespan(dict_impact_list[operator][i], dict_inventory_list[operator][i])
        

        # Step 2 : Allocation with (a, b) for fixed and variable impacts of the network
        dict_impact_list_ab = {} # new dict that contains impacts for every LC steps, indicators and for a/b
        for operator in operator_list:
                dict_impact_list_ab[operator] = allocation_ab_factors(dict_impact_list[operator], df_ab_factors)


        # Step 3.a : Allocation for shared equipments
        for operator in operator_list:
                # Allocation for shared equipments for fixed network
                dict_impact_list_modif_fix = allocation_multi_op("fixed", "full_inventory", dict_inventory_list[operator][3], dict_impact_list_ab, operator, operators_data)
                # Allocation for shared equipments for mobile network
                dict_impact_list_modif_mob = allocation_multi_op("mobile", "full_inventory", dict_inventory_list[operator][5], dict_impact_list_modif_fix, operator, operators_data)
                # Allocation for shared equipments that are used for both fixed and mobile network
                dict_impact_list_modif_mob_fix = allocation_multi_op("fixed_and_mobile", "full_inventory", dict_inventory_list[operator][4], dict_impact_list_modif_mob, operator, operators_data)


        # Step 3.b : Allocation for shared equipments between fixed and mobile network
        for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_impact_list_modif_mob_fix[operator] = allocation_multi_network(dict_impact_list_modif_mob_fix[operator], operator_data)
        

        # Quality analysis
        quality_dict = compute_quality_score(operator_list, dict_inventory_list, dict_impact_list_modif_mob_fix)

        # Save intermediate results for analysis
        save_detail_table_excel("../Results_" + method_name + "_table.xlsx", operator_list, dict_impact_list_modif_mob_fix)
        
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
                dict_impact_op[operator] = allocation_fu(dict_impact_op[operator], operator_data)

        # Save FU results of operators
        save_FU_table_excel("../Results_" + method_name + "_table_FU.xlsx", operator_list, dict_impact_op)

        return dict_impact_op