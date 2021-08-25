# -*- coding: utf-8 -*-
##############################################################################
#    FullSoft, Cameroon Education
#    Francklin TAGNE
##############################################################################

from openerp import fields, models, api

class CaeduPensionInscription(models.Model):
    _inherit = 'caedu.pension.inscription' 
    
    ancienne_classe = fields.Char(string=u'Ancienne classe', related='eleve_id.ancienne_classe', readonly='true')
    