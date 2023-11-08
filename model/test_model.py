
from load_data import prepare_data_flux_method, load_ab_factors, load_op_data, load_elec_consumption
from model import compute_electrical_consumption, multiply_unitary_impacts_by_quantity, allocation_ab_factors, compute_operator_weight, allocation_multi_network, allocation_multi_op, sum_impacts_operator

def test_data_format():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"

    # WHEN 
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)
    print(dict_impact_list)
    print(dict_purchase_list)
    # THEN
    assert len(dict_impact_list) == len(dict_purchase_list)
    assert len(dict_impact_list) == len(dict_dismounting_list)


def test_impact_multiplication():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    operators_data = load_op_data(filename_operator_data)
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator], operators_data.loc[operator] = compute_electrical_consumption("purchase", dict_purchase_list[operator], operator_data, df_elec)

    # WHEN the unitary impacts are multiplied by quantity
    for operator in operator_list:
            for i in range(6):
                dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])

    # THEN
    assert dict_impact_list['operateur1'][0]["BLD ADPe"].iloc[0] == 50*0.8*1
    assert dict_impact_list['operateur1'][0]["DIS ADPe"].iloc[0] == 50*0.8*1
    assert dict_impact_list['operateur1'][0]["REC ADPe"].iloc[0] == 50*0.2*1
    assert dict_impact_list['operateur1'][0]["EOL ADPe"].iloc[0] == 10*1
    assert dict_impact_list['operateur1'][3]["BLD ADPe"].iloc[0] == 100*1
    assert dict_impact_list['operateur1'][3]["EOL ADPe"].iloc[0] == 0



def test_allocation_ab():
    # GIVEN
    operator_list = ['operateur1']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data(filename_operator_data)
    df_elec = load_elec_consumption()

    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)

    dict_purchase_list['operateur1'], operators_data.loc['operateur1'] = compute_electrical_consumption("purchase", dict_purchase_list['operateur1'], operators_data.loc['operateur1'], df_elec)

    for i in range(0, 6):
            dict_impact_list['operateur1'][i] = multiply_unitary_impacts_by_quantity(dict_impact_list['operateur1'][i], dict_purchase_list['operateur1'][i], dict_dismounting_list['operateur1'][i])
    
    # WHEN the allocation with coeff. a and b is done
    dict_impact_list_ab = {}
    dict_impact_list_ab['operateur1'] = allocation_ab_factors(dict_impact_list['operateur1'], df_ab_factors)

    # THEN
    assert dict_impact_list_ab['operateur1'][0]["BLD ADPe typA"].iloc[0] == 50*0.8*1*1
    assert dict_impact_list_ab['operateur1'][0]["BLD ADPe typB"].iloc[0] == 50*0.8*1*0
    assert dict_impact_list_ab['operateur1'][3]["BLD ADPe typA"].iloc[0] == 100*1*1*1
    assert dict_impact_list_ab['operateur1'][3]["BLD ADPe typB"].iloc[0] == 100*1*1*0



def test_compute_operator_weight_fixed_network():
    # GIVEN operateur1 as an operator and one exemple allocation in alloc_string, for fixed network
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    filename_operator_data = "../data_operateurs_test.xlsx"
    operators_data = load_op_data(filename_operator_data)
    operator_data = operators_data.loc["operateur1"]
    alloc_string = "operateur2,50/operateur3,60/operateur1,30"
    network_type = "fixed"

    # WHEN the computation of the weights is done
    weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)

    # THEN 
    weight_operateur1_a = 30*1024
    weight_operateur1_b = 30*400
    weight_operateur3_a = 60*2048
    weight_operateur3_b = 60*500
    weight_operateur2_a = 50*4096
    weight_operateur2_b = 50*700

    total_weight_a = weight_operateur1_a + weight_operateur3_a + weight_operateur2_a
    total_weight_b = weight_operateur1_b + weight_operateur3_b + weight_operateur2_b

    norm_weight_operateur1_a = weight_operateur1_a / total_weight_a
    norm_weight_operateur1_b = weight_operateur1_b / total_weight_b
    print(norm_weight_operateur1_a)
    assert weight_dict["operateur1"]["a"] == norm_weight_operateur1_a
    assert weight_dict["operateur1"]["b"] == norm_weight_operateur1_b
    assert (weight_dict["operateur1"]["a"] + weight_dict["operateur3"]["a"] + weight_dict["operateur2"]["a"]) == 1
    assert (weight_dict["operateur1"]["b"] + weight_dict["operateur3"]["b"] + weight_dict["operateur2"]["b"]) == 1


def test_compute_operator_weight_fixed_and_mobile_network():
    # GIVEN operateur1 as an operator and one exemple allocation in alloc_string, for fixed and mobile network
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    filename_operator_data = "../data_operateurs_test.xlsx"
    operators_data = load_op_data(filename_operator_data)
    operator_data = operators_data.loc["operateur1"]
    alloc_string = "operateur2,50/operateur3,60/operateur1,30"
    network_type = "fixed_and_mobile"

    # WHEN the computation of the weights is done
    weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)

    # THEN 
    weight_operateur1_a = 30*(1024+1000)
    weight_operateur1_b = 30*(400+300)
    weight_operateur3_a = 60*(2048+2000)
    weight_operateur3_b = 60*(500+700)
    weight_operateur2_a = 50*(4096+4000)
    weight_operateur2_b = 50*(700+500)

    total_weight_a = weight_operateur1_a + weight_operateur3_a + weight_operateur2_a
    total_weight_b = weight_operateur1_b + weight_operateur3_b + weight_operateur2_b

    norm_weight_operateur1_a = weight_operateur1_a / total_weight_a
    norm_weight_operateur1_b = weight_operateur1_b / total_weight_b

    assert weight_dict["operateur1"]["a"] == norm_weight_operateur1_a
    assert weight_dict["operateur1"]["b"] == norm_weight_operateur1_b
    assert (weight_dict["operateur1"]["a"] + weight_dict["operateur3"]["a"] + weight_dict["operateur2"]["a"]) == 1
    assert (weight_dict["operateur1"]["b"] + weight_dict["operateur3"]["b"] + weight_dict["operateur2"]["b"]) == 1




def test_allocation_multi_op():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data(filename_operator_data)
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator], operators_data.loc[operator] = compute_electrical_consumption("purchase", dict_purchase_list[operator], operator_data, df_elec)
    
    for operator in operator_list:
            for i in range(6):
                    dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])
    
    dict_impact_list_ab = {}
    for operator in operator_list:
            dict_impact_list_ab[operator] = allocation_ab_factors(dict_impact_list[operator], df_ab_factors)

    # WHEN the allocation for shared equipments for fixed network is done
    for operator in operator_list:
            dict_impact_list_modif_fix = allocation_multi_op("fixed", "purchase", dict_purchase_list[operator][3], dict_impact_list_ab, operator, operators_data)


    # THEN
    weight_operateur1_a = 30*1024
    weight_operateur1_b = 30*400
    weight_operateur2_a = 50*4096
    weight_operateur2_b = 50*700
    weight_operateur3_a = 60*2048
    weight_operateur3_b = 60*500

    total_weight_a = weight_operateur1_a + weight_operateur3_a + weight_operateur2_a
    total_weight_b = weight_operateur1_b + weight_operateur3_b + weight_operateur2_b

    norm_weight_operateur1_a = weight_operateur1_a / total_weight_a
    norm_weight_operateur1_b = weight_operateur1_b / total_weight_b

    impact_operateur1_a = 50*0.8*1 + 100*1*norm_weight_operateur1_a + 100*1*norm_weight_operateur1_a + 100*1*norm_weight_operateur1_a
    impact_operateur1_b = 50*0.8*0 + 100*0*norm_weight_operateur1_b + 100*0*norm_weight_operateur1_b + 100*0*norm_weight_operateur1_b

    assert dict_impact_list_modif_fix['operateur1'][0]["BLD ADPe typA"].iloc[0] == impact_operateur1_a
    assert dict_impact_list_modif_fix['operateur1'][0]["DIS ADPe typB"].iloc[0] == impact_operateur1_b



def test_allocation_multi_network():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data(filename_operator_data)
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator], operators_data.loc[operator] = compute_electrical_consumption("purchase", dict_purchase_list[operator], operator_data, df_elec)
    
    for operator in operator_list:
            for i in range(6):
                    dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])
    
    dict_impact_list_ab = {}
    for operator in operator_list:
            dict_impact_list_ab[operator] = allocation_ab_factors(dict_impact_list[operator], df_ab_factors)

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

   
    # WHEN
    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_impact_list_modif_mob_fix[operator] = allocation_multi_network(dict_impact_list_modif_mob_fix[operator], operator_data)

    # THEN
    impact_fibre_a = dict_impact_list_modif_mob_fix['operateur1'][1]["BLD ADPe typA"].iloc[0]
    impact_fibre_b = dict_impact_list_modif_mob_fix['operateur1'][1]["BLD ADPe typB"].iloc[0]
    operator_weight_a_fix = 1024/(1024+1000)
    operator_weight_b_fix = 400/(300+400)
    operator_weight_a_mob = 1 - operator_weight_a_fix
    operator_weight_b_mob = 1 - operator_weight_b_fix
    
    print(dict_impact_list_modif_mob_fix['operateur1'][0]["BLD ADPe typB"])
    print(dict_impact_list_modif_mob_fix['operateur1'][2]["BLD ADPe typB"])
    assert dict_impact_list_modif_mob_fix['operateur1'][0]["BLD ADPe typA"].iloc[47] == impact_fibre_a*operator_weight_a_fix
    assert dict_impact_list_modif_mob_fix['operateur1'][0]["BLD ADPe typB"].iloc[47] == impact_fibre_b*operator_weight_b_fix
    assert dict_impact_list_modif_mob_fix['operateur1'][2]["BLD ADPe typA"].iloc[30] == impact_fibre_a*operator_weight_a_mob
    assert dict_impact_list_modif_mob_fix['operateur1'][2]["BLD ADPe typB"].iloc[30] == impact_fibre_b*operator_weight_b_mob



def test_sum_impacts():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data(filename_operator_data)
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data_flux_method(operator_list, filename_list, filename_impacts)

    for operator in operator_list:
            operator_data = operators_data.loc[operator]
            dict_purchase_list[operator], operators_data.loc[operator] = compute_electrical_consumption("purchase", dict_purchase_list[operator], operator_data, df_elec)
    
    for operator in operator_list:
            for i in range(6):
                    dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])
    
    dict_impact_list_ab = {}
    for operator in operator_list:
            dict_impact_list_ab[operator] = allocation_ab_factors(dict_impact_list[operator], df_ab_factors)

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

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_impact_list_modif_mob_fix[operator] = allocation_multi_network(dict_impact_list_modif_mob_fix[operator], operator_data)
   
    # WHEN
    dict_impact_op = {}
    for operator in operator_list:
            dict_op = sum_impacts_operator(dict_impact_list_modif_mob_fix[operator])
            # dict_impact_op = dictionnary with {operator : {"fixed" : impacts , "mobile" : impacts}}
            dict_impact_op[operator] = dict_op

    # THEN
    diff = dict_impact_op['operateur1']["fixed"]["impact"].iloc[0] - (75.1428571428571+115.142857142857+228504.935714286+40+59.4285714285714)
    assert diff <= 0.01

