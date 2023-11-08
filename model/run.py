
from main import model_pipeline_flux_method, model_pipeline_lifespan_method

def run_model_flux_method():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"

    _ = model_pipeline_flux_method("flux_method", operator_list, filename_list, filename_impacts, filename_operator_data)

def run_model_lifespan_method():
    # GIVEN
    operator_list = ['operateur1', 'operateur2', 'operateur3']
    filename_list = {'operateur1': "../Grille_collecte_test_operateur1.xlsx", 
                    'operateur2': "../Grille_collecte_test_operateur2.xlsx", 
                    'operateur3': "../Grille_collecte_test_operateur3.xlsx"}
    filename_operator_data = "../data_operateurs_test.xlsx"
    filename_impacts = "../Facteurs_impacts_test.xlsx"

    _ = model_pipeline_lifespan_method("lifespan_method", operator_list, filename_list, filename_impacts, filename_operator_data)


run_model_flux_method()
run_model_lifespan_method()