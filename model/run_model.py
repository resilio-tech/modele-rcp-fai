
import pandas as pd
import array as ar

from main import model_pipeline_flux_method, model_pipeline_lifespan_method
from load_data import prepare_data_flux_method, prepare_data_lifespan_method, load_ab_factors, load_op_data, load_elec_consumption



def test_model_flux_method():
    # GIVEN
    operator_list = ['adista', 'bouygues', 'iliad', 'orange', 'sfr']
    filename_list = {'adista': "../../Grille_collecte_adista.xlsx", 
                    'bouygues': "../../Grille_collecte_bouygues.xlsx",
                    'iliad': "../../Grille_collecte_iliad.xlsx",
                    'orange': "../../Grille_collecte_orange.xlsx",
                    'sfr': "../../Grille_collecte_sfr.xlsx"
                    }
    filename_impacts = "../../Facteurs impacts consolides_20230809.xlsx"
    filename_operator_data = "../../data_operateurs.xlsx"

    dict_data_operator = model_pipeline_flux_method(operator_list, filename_list, filename_impacts, filename_operator_data)

    assert False
