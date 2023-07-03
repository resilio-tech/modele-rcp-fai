

from main import model_pipeline
from load_data import prepare_data, load_ab_factors, load_op_data, load_elec_consumption
from model import compute_electrical_consumption, multiply_unitary_impacts_by_quantity, allocation_ab_factors, compute_operator_weight, allocation_multi_network, allocation_multi_op, sum_impacts_operator


def test_data_format():
    # GIVEN
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx", 
                    'orange': "../Grille_collecte_test_orange.xlsx", 
                    'sfr': "../Grille_collecte_test_sfr.xlsx"}
    
    # WHEN 
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    # THEN
    assert len(dict_impact_list) == len(dict_purchase_list)
    assert len(dict_impact_list) == len(dict_dismounting_list)



def test_compute_elec():
    # GIVEN
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx", 
                    'orange': "../Grille_collecte_test_orange.xlsx", 
                    'sfr': "../Grille_collecte_test_sfr.xlsx"}
    operators_data = load_op_data()
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    # WHEN
    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator] = compute_electrical_consumption(dict_purchase_list[operator], operator_data, df_elec)

    # THEN
    assert dict_purchase_list['iliad'][0]["real_elec"].iloc[0] == 50*3504*operators_data.loc['iliad']["conso_elec_fix"]/(150*3504)



def test_impact_multiplication():
    # GIVEN
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx", 
                    'orange': "../Grille_collecte_test_orange.xlsx", 
                    'sfr': "../Grille_collecte_test_sfr.xlsx"}
    operators_data = load_op_data()
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator] = compute_electrical_consumption(dict_purchase_list[operator], operator_data, df_elec)

    # WHEN the unitary impacts are multiplied by quantity
    for operator in operator_list:
            for i in range(6):
                dict_impact_list[operator][i] = multiply_unitary_impacts_by_quantity(dict_impact_list[operator][i], dict_purchase_list[operator][i], dict_dismounting_list[operator][i])

    # THEN
    assert dict_impact_list['iliad'][0]["BLD ADPe"].iloc[0] == 50*0.8*1
    assert dict_impact_list['iliad'][0]["DIS ADPe"].iloc[0] == 50*0.8*2
    assert dict_impact_list['iliad'][0]["INS ADPe"].iloc[0] == 0
    assert dict_impact_list['iliad'][0]["USE ADPe"].iloc[0] == (348333+1/3)*3
    assert dict_impact_list['iliad'][0]["REC ADPe"].iloc[0] == 50*0.2*4
    assert dict_impact_list['iliad'][0]["EOL ADPe"].iloc[0] == 10*5
    assert dict_impact_list['iliad'][3]["BLD ADPe"].iloc[0] == 100*1
    assert dict_impact_list['iliad'][3]["EOL ADPe"].iloc[0] == 0



def test_allocation_ab():
    # GIVEN
    operator_list = ['iliad']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx"}
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data()
    df_elec = load_elec_consumption()

    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    dict_purchase_list['iliad'] = compute_electrical_consumption(dict_purchase_list['iliad'], operators_data.loc['iliad'], df_elec)

    for i in range(0, 6):
            dict_impact_list['iliad'][i] = multiply_unitary_impacts_by_quantity(dict_impact_list['iliad'][i], dict_purchase_list['iliad'][i], dict_dismounting_list['iliad'][i])
    
    # WHEN the allocation with coeff. a and b is done
    dict_impact_list_ab = {}
    dict_impact_list_ab['iliad'] = allocation_ab_factors(dict_impact_list['iliad'], df_ab_factors)

    # THEN
    assert dict_impact_list_ab['iliad'][0]["BLD ADPe typA"].iloc[0] == 50*0.8*1*1
    assert dict_impact_list_ab['iliad'][0]["BLD ADPe typB"].iloc[0] == 50*0.8*1*0
    assert dict_impact_list_ab['iliad'][3]["BLD ADPe typA"].iloc[0] == 100*1*1*1
    assert dict_impact_list_ab['iliad'][3]["BLD ADPe typB"].iloc[0] == 100*1*1*0



def test_compute_operator_weight_fixed_network():
    # GIVEN iliad as an operator and one exemple allocation in alloc_string, for fixed network
    operators_data = load_op_data()
    operator_data = operators_data.loc["iliad"]
    alloc_string = "orange,50/sfr,60/iliad,30"
    network_type = "fixed"

    # WHEN the computation of the weights is done
    weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)

    # THEN 
    weight_iliad_a = 30*1024
    weight_iliad_b = 30*400
    weight_sfr_a = 60*2048
    weight_sfr_b = 60*500
    weight_orange_a = 50*4096
    weight_orange_b = 50*700

    total_weight_a = weight_iliad_a + weight_sfr_a + weight_orange_a
    total_weight_b = weight_iliad_b + weight_sfr_b + weight_orange_b

    norm_weight_iliad_a = weight_iliad_a / total_weight_a
    norm_weight_iliad_b = weight_iliad_b / total_weight_b
    print(norm_weight_iliad_a)
    assert weight_dict["iliad"]["a"] == norm_weight_iliad_a
    assert weight_dict["iliad"]["b"] == norm_weight_iliad_b
    assert (weight_dict["iliad"]["a"] + weight_dict["sfr"]["a"] + weight_dict["orange"]["a"]) == 1
    assert (weight_dict["iliad"]["b"] + weight_dict["sfr"]["b"] + weight_dict["orange"]["b"]) == 1


def test_compute_operator_weight_fixed_and_mobile_network():
    # GIVEN iliad as an operator and one exemple allocation in alloc_string, for fixed and mobile network
    operators_data = load_op_data()
    operator_data = operators_data.loc["iliad"]
    alloc_string = "orange,50/sfr,60/iliad,30"
    network_type = "fixed_and_mobile"

    # WHEN the computation of the weights is done
    weight_dict = compute_operator_weight(alloc_string, network_type, operators_data)

    # THEN 
    weight_iliad_a = 30*(1024+1000)
    weight_iliad_b = 30*(400+300)
    weight_sfr_a = 60*(2048+2000)
    weight_sfr_b = 60*(500+700)
    weight_orange_a = 50*(4096+4000)
    weight_orange_b = 50*(700+500)

    total_weight_a = weight_iliad_a + weight_sfr_a + weight_orange_a
    total_weight_b = weight_iliad_b + weight_sfr_b + weight_orange_b

    norm_weight_iliad_a = weight_iliad_a / total_weight_a
    norm_weight_iliad_b = weight_iliad_b / total_weight_b

    assert weight_dict["iliad"]["a"] == norm_weight_iliad_a
    assert weight_dict["iliad"]["b"] == norm_weight_iliad_b
    assert (weight_dict["iliad"]["a"] + weight_dict["sfr"]["a"] + weight_dict["orange"]["a"]) == 1
    assert (weight_dict["iliad"]["b"] + weight_dict["sfr"]["b"] + weight_dict["orange"]["b"]) == 1




def test_allocation_multi_op():
    # GIVEN
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx", 
                    'orange': "../Grille_collecte_test_orange.xlsx", 
                    'sfr': "../Grille_collecte_test_sfr.xlsx"}
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data()
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator] = compute_electrical_consumption(dict_purchase_list[operator], operator_data, df_elec)
    
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
    weight_iliad_a = 30*1024
    weight_iliad_b = 30*400
    weight_sfr_a = 60*2048
    weight_sfr_b = 60*500
    weight_orange_a = 50*4096
    weight_orange_b = 50*700

    total_weight_a = weight_iliad_a + weight_sfr_a + weight_orange_a
    total_weight_b = weight_iliad_b + weight_sfr_b + weight_orange_b

    norm_weight_iliad_a = weight_iliad_a / total_weight_a
    norm_weight_iliad_b = weight_iliad_b / total_weight_b

    impact_iliad_a = 50*0.8*1 + 100*1*norm_weight_iliad_a + 110*1*norm_weight_iliad_a + 200*1*norm_weight_iliad_a
    impact_iliad_b = 50*0.8*0 + 100*0*norm_weight_iliad_b + 110*0*norm_weight_iliad_b + 200*0*norm_weight_iliad_b

    assert dict_impact_list_modif_fix['iliad'][0]["BLD ADPe typA"].iloc[0] == impact_iliad_a
    assert dict_impact_list_modif_fix['iliad'][0]["DIS ADPe typB"].iloc[0] == impact_iliad_b



def test_allocation_multi_network():
    # GIVEN
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx", 
                    'orange': "../Grille_collecte_test_orange.xlsx", 
                    'sfr': "../Grille_collecte_test_sfr.xlsx"}
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data()
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    for operator in operator_list:
                operator_data = operators_data.loc[operator]
                dict_purchase_list[operator] = compute_electrical_consumption(dict_purchase_list[operator], operator_data, df_elec)
    
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
    impact_fibre_a = dict_impact_list_modif_mob_fix['iliad'][1]["BLD ADPe typA"].iloc[0]
    impact_fibre_b = dict_impact_list_modif_mob_fix['iliad'][1]["BLD ADPe typB"].iloc[0]
    operator_weight_a_fix = 1024/(1024+1000)
    operator_weight_b_fix = 400/(300+400)
    operator_weight_a_mob = 1 - operator_weight_a_fix
    operator_weight_b_mob = 1 - operator_weight_b_fix
    
    assert dict_impact_list_modif_mob_fix['iliad'][0]["BLD ADPe typA"].iloc[43] == impact_fibre_a*operator_weight_a_fix
    assert dict_impact_list_modif_mob_fix['iliad'][0]["BLD ADPe typB"].iloc[43] == impact_fibre_b*operator_weight_b_fix
    assert dict_impact_list_modif_mob_fix['iliad'][2]["BLD ADPe typA"].iloc[43] == impact_fibre_a*operator_weight_a_mob
    assert dict_impact_list_modif_mob_fix['iliad'][2]["BLD ADPe typB"].iloc[43] == impact_fibre_b*operator_weight_b_mob



def test_sum_impacts():
    # GIVEN
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad': "../Grille_collecte_test_iliad.xlsx", 
                    'orange': "../Grille_collecte_test_orange.xlsx", 
                    'sfr': "../Grille_collecte_test_sfr.xlsx"}
    df_ab_factors = load_ab_factors()
    operators_data = load_op_data()
    df_elec = load_elec_consumption()
    
    dict_impact_list, dict_purchase_list, dict_dismounting_list = prepare_data(operator_list, filename_list)

    for operator in operator_list:
            operator_data = operators_data.loc[operator]
            dict_purchase_list[operator] = compute_electrical_consumption(dict_purchase_list[operator], operator_data, df_elec)
    
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
    diff = dict_impact_op['iliad']["fixed"]["impact"].iloc[0] - (75.1428571428571+115.142857142857+228504.935714286+40+59.4285714285714)
    assert diff <= 0.01

"""
def test_model():
    operator_list = ['iliad', 'orange', 'sfr'] # 'adista', 'bouygues']
    filename_list = {'iliad':"../Grille_collecte_test_iliad.xlsx", 
                    'orange':"../Grille_collecte_test_orange.xlsx", 
                    'sfr':"../Grille_collecte_test_sfr.xlsx"}
    dict_impact_list = model_pipeline(operator_list, filename_list)
    assert False
"""
