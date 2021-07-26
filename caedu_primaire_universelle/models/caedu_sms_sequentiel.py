# -*- coding: utf-8 -*-
##############################################################################
#    FullSoft, Cameroon Education
#    Francklin TAGNE
##############################################################################

from openerp import models, fields, api
import logging
from openerp import exceptions
from subprocess import Popen
from openerp.tools.translate import _
import requests
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError

#import subprocess
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class CaeduSmsSequentiel(models.TransientModel):
    _inherit = 'caedu.sms.sequentiel'
    _group_ats = {'caedu_man':'crud', 'caedu_par':'crud', 'caedu_eco':'cru', 'caedu_sur':'cru'}
    message = fields.Text('Message', 
        default= u'Cher parent, votre enfant #nom_enfant, a eu une moyenne de #moyenne et un rang de #rang/#effectif pour le compte de cette #periode ; THE VISION INTERNATIONAL SCHOOL.', required=True)
    
    filtrage = fields.Selection(
        selection=[
            ('orange', 'Orange Uniquement'),
            ('mtn', 'MTN Uniquement'),
            ('nexttel', 'Nextel Uniquement'),
            ('camtel', 'Camtel Uniquement'),
            ('yoomee', 'Yoomee Uniquement'),
            ('none', 'Pas de filtrage'),
        ], string='Filtrage', default='orange') 
    
    #fonction retournant le numéro de telephone string sans espace 
    #ni tiret contenu dans un numero de telephone formaté a la maniere user
    @api.model
    def buildGoodNumStr(self, numberStr):
        numStr = ""
        if " " in numberStr :
            numStr = numberStr.replace(" ","")
        elif "-" in numberStr :
            numStr = numberStr.replace("-","")
        else :
            numStr = numberStr
        return numStr
    
    #tester si le numéro est valide
    @api.model
    def is_telephone_number(self, numberStr):
        try : 
            
            numStr = self.buildGoodNumStr(numberStr)    
            numInt = int(numStr)
            
            #verifier que le num n'as que 9 chiffres
            if len(numStr)!=9 :
                _logger.debug('La chaine [%s] ne represente pas un numero de telephone camerounais valide (lenght).',numberStr)
                return False
            
            #verifier que le num commence par 6, 2 ou 3
            if numStr[0]!="6" and numStr[0]!="2" and numStr[0]!="3" :
                _logger.debug('La chaine [%s] n as pas un premier chiffre de numero camerounais valide.',numberStr)
                return False
            
        except :
            _logger.debug('La chaine [%s] ne represente pas un numero de telephone valide.',numberStr)
            return False
        else :
            _logger.debug('numero de telephone [%s] valide',numberStr)
        return True
        
    
    #methode principale d envois des sms
    @api.one
    def do_send_sms(self):
        
        #chech date exp licence
        rec = self.env['base.bus.usb'].search([])
        rec.chech_date()
        
        try :
            
            #recuperer les ids des patients selectionnés, autres params
            operateurSelect = self.filtrage
            message = self.message
            bulletin_ids = self._context['bulletin_ids']
            mode_envoi = self.mode_envoi
            
            #initialisation des listes et dicts de travail
            list_dic_donnees = list() 
                     
            for bulletin_id in bulletin_ids :
                
                #recupérer le bulletin, l elve et la liste de ses parent
                bulletin = self.env['caedu.etude.bulletin.sequentiel'].search([('id', '=', bulletin_id)])
                eleve = bulletin.eleve_id
                parents = eleve.ligne_parents_ids
                
                if operateurSelect == "none":
                    for parent in parents :
                        
                        dict_donnee = dict()
                        dict_donnee['nom_parent'] = parent.nom
                        dict_donnee['numero_parent'] = parent.telephone.replace(" ",'')
                        dict_donnee['nom_eleve'] = eleve.name
                        dict_donnee['nom_enfant'] = eleve.name
                        dict_donnee['moyenne'] = bulletin.moyenne_eleve
                        dict_donnee['rang'] = bulletin.rang_eleve
                        dict_donnee['effectif'] = bulletin.effectif
                        dict_donnee['periode'] = bulletin.sequence_id.name
                        list_dic_donnees.append(dict_donnee)
                else:
                    for parent in parents :
                        if parent.operateur == operateurSelect :
                            dict_donnee = dict()
                            dict_donnee['nom_parent'] = parent.nom
                            dict_donnee['numero_parent'] = parent.telephone.replace(" ",'')
                            dict_donnee['nom_eleve'] = eleve.name
                            dict_donnee['nom_enfant'] = eleve.name
                            dict_donnee['moyenne'] = bulletin.moyenne_eleve
                            dict_donnee['rang'] = bulletin.rang_eleve
                            dict_donnee['effectif'] = bulletin.effectif
                            dict_donnee['periode'] = bulletin.sequence_id.name
                            list_dic_donnees.append(dict_donnee)
            
            if mode_envoi == 'internet':  
                self._writeSmsBatchFile("camedSmsCmd.bat",list_dic_donnees, message,mode_envoi)
            else: 
                #ecrire le fichier bat
                self._writeSmsBatchFile("camedSmsCmd.bat", list_dic_donnees, message,mode_envoi)
                
                #executer le bat d'envoi des sms
                #subprocess.call('camedSmsCmd.bat')
                p = Popen('camedSmsCmd.bat')
                stdout, stderr = p.communicate()
                    
        except Exception as e :
            _logger.debug(str(e))
            raise exceptions.ValidationError(_("Erreur lors des envois"))
        else :
            _logger.debug('Messages envoyes')
        return True
    
    #OBSOLETE on prefere use simplement l operateur entré lors de l enregistrement de l eleve
    # c est a dire parent.operateur == Xxx
    #fonction permettant de renvoyer le type d'un numéro de telphone
    #note : nous avons fait express de prendre en parametre un num de tel à transformer
    #meme comme on pouvais prendre l autre, pour limiter au max les erreurs de codage possible
    #en utilisant cette fonctin dans l'avenir
    #on suppose ici que le num est deja passé par la fonction de validation is_mumero_telephone
    @api.model
    def getOperateurForNumber(self,numberStr):
        numStr = self.buildGoodNumStr(numberStr)
        if numStr[0]=="2" or numStr[0]=="3" :
            if numStr[1]=="2" or numStr[1]=="3" :
                return "camtel"
        elif numStr[0]=="6" :
            if numStr[1]=="9" : 
                return "orange"
            elif numStr[1]=="7" :
                return "mtn"
            elif numStr[1]=="6" :
                return "nexttel"
            if numStr[1]=="5" :
                chiffre3 = int(numStr[2])
                if chiffre3 < 5 :
                    return "mtn"
                else :
                    return "orange"
            else :
                return "inconnu"
        else :
            return "inconnu"  

    #cette methode permet d ecrire le fichier des batch des sms
    #listNumPat est une liste dictionnaires, chacun contenant le numéro du patient et son nom
    @api.model
    def writeSmsBatchFile(self, fileName, list_dic_donnees, message,mode_envoi):
        
        try :
            
            fichier = open(fileName,"w")
            LONGUEUR_MAX_MESSAGE = 155
            for dic in list_dic_donnees :
                numero_parent = dic["numero_parent"]
                messageFormate = message.replace("#nom_eleve",dic['nom_eleve'])
                messageFormate = messageFormate.replace("#nom_parent",dic['nom_parent'])
                messageFormate = messageFormate.replace("#numero_parent",dic['numero_parent'])
                messageFormate = messageFormate.replace("#nom_enfant",dic['nom_enfant'])
                messageFormate = messageFormate.replace("#moyenne",str(dic['moyenne']))
                messageFormate = messageFormate.replace("#rang",str(dic['rang']))
                messageFormate = messageFormate.replace("#effectif",str(dic['effectif']))
                messageFormate = messageFormate.replace("#periode",dic['periode'])
                
                messageFormate = messageFormate.replace("#date_limite_encours",dic['date_limite_encours']) if 'date_limite_encours' in dic else messageFormate
                messageFormate = messageFormate.replace("#solde_total",dic['solde_total']) if 'solde_total' in dic else messageFormate
                messageFormate = messageFormate.replace("#solde_encours",dic['solde_encours']) if 'solde_encours' in dic else messageFormate
                messageFormate = messageFormate.replace("#nom_tranche_encours",dic['nom_tranche_encours']) if 'nom_tranche_encours' in dic else messageFormate
                
                
                messageFormate = messageFormate.replace("#nom_type_decompte_discipline",dic['nom_type_decompte_discipline']) if 'nom_type_decompte_discipline' in dic else messageFormate
                messageFormate = messageFormate.replace("#valeur",dic['valeur']) if 'valeur' in dic else messageFormate
                messageFormate = messageFormate.replace("#nom_semaine",dic['nom_semaine']) if 'nom_semaine' in dic else messageFormate
                messageFormate = messageFormate.replace("#nom_classe",dic['nom_classe']) if 'nom_classe' in dic else messageFormate
                
                
                #traitement accents
                messageFormate = messageFormate.replace(u"é","e")
                messageFormate = messageFormate.replace(u"è","e")
                messageFormate = messageFormate.replace(u"à","a")
                messageFormate = messageFormate.replace(u"ê","e")
                messageFormate = messageFormate.replace(u"ç","c")
                messageFormate = messageFormate.replace(u"â","a")
                
                if mode_envoi == 'cle':
                    #decouper le message en plusieurs lorsqu on depasse 155cc (160=max normal)
                    indexFin = 0
                    indexDeb = 0 
                    curseur = 0
                    longMessFormate = len(messageFormate)
                    while curseur<longMessFormate :
                        indexDeb = indexFin
                        curseur = curseur + LONGUEUR_MAX_MESSAGE
                        indexFin = curseur if curseur<longMessFormate else longMessFormate
                        messagePart = messageFormate[indexDeb:indexFin]
                        strCmd = 'start /b SendSMS /p:' + numero_parent + ' /m:"' + messagePart + '" &\n ping -n 7 127.0.0.1 \n '
                        strCmd = strCmd + 'taskkill /f /im SendSMS.exe \n ping -n 10 127.0.0.1 \n'
                        #strCmd = 'echo ' + numero_parent + ' "' + messagePart + '"\n'
                        #strCmd = strCmd + 'ping -n 2 127.0.0.1 > nul \n'
                        strUnicode = u" " + strCmd
                        fichier.write(strUnicode.encode('mbcs'))
                        
                        #fichier.write("pause")
                        fichier.close()
                
                elif mode_envoi == 'internet':
                    #===========================================================
                    # response = requests.post("https://randomuser.me/api", verify=False)
                    # #response = requests.post(req, data=None, json=None)
                    # #response = requests.get(req, verify=False)
                    # user_json = response.json()['results'][0]
                    #  
                    # _logger.debug('utilisateur nom : '+user_json['name']['title'] + ' '+ user_json['name']['first'] + ' '+ user_json['name']['last'] + ', sexe : '+ user_json['gender'] +', '+ user_json['location']['state'])
                    #===========================================================
                    #x = https://smsvas.com/bulk/public/index.php/api/v1/sendsms?user=user&password=password&senderid=sender&sms=message&mobiles=XXXXXXXXX,XXXXXXXXX,XXXXXXXXX
                    ecole = "FRATERNITE"
                    resp = requests.get("https://smsvas.com/bulk/public/index.php/api/v1/sendsms?user=ouamba@gmail.com&password=atsservice2020&senderid=" +ecole +"&sms="+ messageFormate +"&mobiles="+ numero_parent)  #ajouter le message dans l url comme dans la documentation de l api
                    
                    #resp = requests.get("https://sms.etech-keys.com/ss/api.php?login=690133446&password=1074350&sender_id="+ecole +"&destinataire="+ numero_parent +"&message="+ messageFormate)  #ajouter le message dans l url comme dans la documentation de l api
        except Exception as e:
            _logger.debug(str(e))
            _logger.debug('Erreur lors de l ecriture de fichier bat final.')
            return False
        else :
            _logger.debug('Ecriture fichier batch final valide.')
        return True
    
