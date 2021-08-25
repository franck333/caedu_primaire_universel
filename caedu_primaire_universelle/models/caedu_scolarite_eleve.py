# -*- coding: utf-8 -*-
##############################################################################
#    FullSoft, Cameroon Education
#    Francklin TAGNE
##############################################################################

from openerp import models, fields, api

class CaeduScoloriteEleve(models.Model):
    _inherit = 'caedu.scolarite.eleve'
    
    ancienne_classe = fields.Char('Ancienne classe')
    
    
        