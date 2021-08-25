# -*- coding: utf-8 -*-
##############################################################################
#    FullSoft, Cameroon Medical
#    Francklin TAGNE
##############################################################################

{
    'name': 'Caedu Primaire UNIVERSELLE',
    'version': '8.0.1',
    'category': 'Education',
    'author': 'FullSoft',
    'website': 'http://www.fullsoft.cm',
    'depends': ['caedu_be', 'caedu_fe_core', 'caedu_primaire_core_reports'],
    'data': [
        
		
        #les vues        
        'views/caedu_scolarite_eleve_view.xml', 
        'views/caedu_pension_inscription_view.xml', 
        
		# les entetes
        'reports/entete/caedu_custom_invoice_head2.xml',  #heritage
        'reports/entete/caedu_prim_client_entete_generale_french.xml', #heritage
        'reports/entete/caedu_prim_client_mini_entete_bulletins_apc.xml', #heritage
        'reports/entete/caedu_fraternite_french_entete_recu.xml',
        'reports/entete/caedu_fraternite_eng_entete_recu.xml',
        'reports/entete/caedu_fraternite_french_entete_recu_new.xml',
        'reports/entete/caedu_fraternite_french_entete_recu_eng_new.xml',
        
        'reports/entete/caedu_primaire_mini_entete_recu_2021.xml',  #heritage
        'reports/entete/caedu_primaire_mini_entete_recu_eng_2021.xml',  #heritage
        
        
        
        # ----- fe core ----- 
        
        'reports/fe_core/caedu_trimestre_tableau_honneur.xml',
        'reports/fe_core/caedu_annee_tableau_honneur.xml',
        'reports/fe_core/caedu_bulletin_trimestriel_apc_deux_pages_new_fraternite.xml',
        'reports/fe_core/caedu_bulletin_trimestriel_apc_deux_pages_new_eng_fraternite.xml',
        'reports/fe_core/caedu_bulletin_annuel_apc_deux_pages_fraternite.xml',
        'reports/fe_core/caedu_bulletin_annuel_apc_deux_pages_fraternite_eng.xml',
        
        
        
        
        # ----- finances ----- 
        
        
        # ----- pension -----
        'reports/pension/caedu_certificat_scolarite.xml',
        'reports/pension/caedu_carte_scolaire.xml',
        'reports/pension/caedu_pension_moratoire.xml',
        
        'reports/pension/caedu_recu_encaissement_eng_2021.xml',
        'reports/pension/caedu_recu_encaissement_2021.xml',
       
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
