# -*- coding: utf-8 -*-
"""
Crée les modèles VOC EBU, 4G et FTTH (fidèles aux codes SAS d'Uriel)
et le compte agent de démonstration. Relançable sans risque.

Usage : python setup_templates.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.imports.analyzer import load_and_analyze, clean_dataframe
from apps.imports.models import SurveyTemplate

DROPS_COMMON = ['collector_id', 'date_modified', 'ip_address',
                'email_address', 'first_name', 'last_name', 'custom_1']

FILES = {
    'VOC EBU': r'C:\Users\DELL\Downloads\SURVEY VOC EBU_202547.xlsx',
    '4G': r'C:\Users\DELL\Downloads\SURVEY 4G_20256.xlsx',
    'FTTH': r'C:\Users\DELL\Downloads\ftth.xlsx',
    # Même structure SurveyMonkey pour les deux populations (codes SAS identiques)
    'Transactions EU': r'C:\Users\DELL\Downloads\eu.xlsx',
    'Transactions Agents': r'C:\Users\DELL\Downloads\eu.xlsx',
}

# Préfixe de la colonne détectée -> nom cible (codes SAS)
RULES = {
    'VOC EBU': {
        'drops': ['email_address', 'first_name', 'last_name', 'custom_1'],
        'map': [
            ('respondent_id', 'respondent_id'), ('collector_id', 'collector_id2'),
            ('date_created', 'date_created'), ('date_modified', 'date_modified'),
            ('ip_address', 'ip_address'),
            ('AGENTS ACI', 'Agents'), ('N° REC', 'N° REC'),
            ('Type de client', 'Type_client'),
            ('Par quel moyen', 'Contact'),
            ('Pouvez vous décrire', 'Cause'),
            ("Sur une échelle de 0 à 10, quelle est la probabilité que vous recommanderiez l'agent", 'NPS_agent'),
            ('Pourquoi?.1', 'Verbatims_servives'),
            ('Pourquoi?', 'Verbatims'),
            ('Sur une échelle de 0 à 10, quelle est la probabilité que vous recommanderiez notre service', 'NPS_service'),
            ('RECOMMANDATIONS', 'Recommandations'),
        ],
    },
    '4G': {
        'drops': DROPS_COMMON,
        'map': [
            ('respondent_id', 'respondent_id'), ('date_created', 'date_created'),
            ('AGENT_ACI', 'Nom_Agent'),
            ('MSISDN EQUIPEMENT', 'FTTH_Line'),
            ('CONTACT CLIENT', 'MSISDN'),
            ("TYPE D'EQUIPEMENT", 'Segment client'),
            ('NPS 4G', 'Note_NPS'),
            ('VERBATIM AGENT', 'verbatim_agent'),
            ('VERBATIM.1', 'verbatims_Portail_dutilisation'),
            ('VERBATIM.2', 'verbatims_Support_technique'),
            ('VERBATIM.3', 'verbatims_CES_configuration'),
            ('VERBATIM.4', 'verbatims_CES_support_technique'),
            ('VERBATIM', 'VERBATIM'),
            ('Root_Cause - Detraction', 'Root_Cause_Detraction'),
            ('Root_Cause - Promotion', 'Root_Cause_Promotion'),
            ('Par quel canal', 'moyen_connaissance'),
            ('Où avez-vous acheté', 'lieu_achat'),
            ('A combien noter vous', 'nps_agent'),
            ('CSAT portail', 'CSAT_Portail_dutilisation'),
            ('CSAT Support Technique', 'CSAT_Support_technique'),
            ('CES configuration', 'CES_configuration'),
            ('CES Support Technique', 'CES_support_technique'),
            ('Quelles sont les activités', 'use_of_services'),
            ('Quels problèmes', 'frequent_problems'),
            ('Suggestions', 'Suggestions'),
        ],
    },
    'FTTH': {
        'drops': DROPS_COMMON + ['COMMUNE'],  # SAS garde COMMUNE_1 (la 2e)
        'map': [
            ('respondent_id', 'respondent_id'), ('date_created', 'date_created'),
            ('AGENTS ACI', 'Nom_Agent'),
            ('FTTH MSISDN', 'FTTH_Line'),
            ('CONTACT DU CLIENT', 'MSISDN'),
            ('COMMUNE.1', 'COMMUNE_1'),
            ('FORFAIT', 'Segment client'),
            ('NPS de la FIBRE', 'Note_NPS'),
            ('VERBATIMS.1', 'Verbatims_others'),
            ('VERBATIMS', 'VERBATIMS'),
            ('ROOT CAUSE-PROMOTION.1', 'ATTRIBUT_OTHERS'),
            ('ROOT CAUSE-DETRACTION.1', 'Root_Cause_Others'),
            ('ROOT CAUSE-PROMOTION', 'ATTRIBUT'),
            ('ROOT CAUSE-DETRACTION', 'Root_Cause'),
            ('Utilisez-vous un autre Opérateur', 'Network_Others'),
            ('NPS of Other FIBRE', 'Note_NPS_Others'),
            ('Verbatim - CSAT Installation', 'Verbatims_instaConfig'),
            ('CSAT Installation', 'CSAT_instaConfig'),
            ('Verbatim - CSAT Attitude', 'Verbatims_AttitudeTechnicien'),
            ('CSAT Attitude', 'CSAT_AttitudeTechnicien'),
            ('Verbatim - CSAT Vitesse', 'Verbatims_VitesseConnexion'),
            ('CSAT Vitesse', 'CSAT_VitesseConnexion'),
            ('Verbatim - CSAT Fiabilité', 'Verbatims_Fiabilité_Stabilité'),
            ('CSAT Fiabilité', 'CSAT_Fiabilité_Stabilité'),
            ('Verbatim - CSAT Support', 'Verbatims_Support_Communication'),
            ('CSAT Support et Communication', 'CSAT_Support_Communication'),
            ('Verbatim - CSAT Tarification', 'verbatims_Tarification'),
            ('CSAT Tarification', 'CSAT_Tarification'),
            ('Verbatim - CES Accès au support', 'Verbatims_AccèsSupport'),
            ('CES Accès au support', 'CES_AccèsSupport'),
            ('Verbatim - CES Disponibilité', 'Verbatims_DispoEff'),
            ('CES Disponibilité', 'CES_DispoEff'),
            ('Verbatim - CES Accès aux infos', 'Verbatims_AccèsInfos'),
            ('CES Accès aux infos', 'CES_AccèsInfos'),
            ('Verbatim - CES Renouvellement', 'Verbatims_RenouvellementForfait'),
            ('CES Renouvellement', 'CES_RenouvellementForfait'),
            ('Verbatim - Seriez vous intéressé', 'Verbatims_Service_Supplementaire'),
            ('Seriez vous intéressé', 'Service_Supplementaire'),
            ('RECOMMANDATIONS', 'RECOMMANDATIONS'),
        ],
    },
}

# Historique des transactions : même mapping pour End Users et Agents (codes SAS identiques)
_TRANSACTION_MAP = [
    ('respondent_id', 'respondent_id'), ('date_created', 'date_created'),
    ('AGENT_ACI', 'AGENT_ACI'), ('MSISDN', 'MSISDN'),
    ('Savez-vous', 'connaissance_hist'),
    ('Avez vous déjà eu recours', 'recours_hist'),
    ('Avez-vous facilement trouvé', 'facilite_hist'),
    ('Combien de temps', 'temps_hist'),
    ('COMMENTAIRE.1', 'verb_clarte'),
    ('COMMENTAIRE.2', 'verb_filtre'),
    ('COMMENTAIRE', 'verbatim_acces'),
    ('La présentation', 'clarte'),
    ('Trouvez-vous que le filtrage', 'filtre'),
    ('Les informations affichées', 'info'),
    ('POURQUOI?', 'verb_comp'),
    ('Y a-t-il des informations', 'autre_info'),
    ('Dans quelle mesure', 'global'),
    ('POURQUOI', 'verbatim'),
]
RULES['Transactions EU'] = {'drops': DROPS_COMMON, 'map': _TRANSACTION_MAP}
RULES['Transactions Agents'] = {'drops': DROPS_COMMON, 'map': _TRANSACTION_MAP}


def build_mapping(detected_names, rules):
    """Associe chaque colonne détectée à son nom cible (préfixes SAS, plus long d'abord)."""
    mapping = {}
    used_targets = set()
    for name in detected_names:
        candidates = [(prefix, target) for prefix, target in rules
                      if name.lower().startswith(prefix.lower()) and target not in used_targets]
        if candidates:
            prefix, target = max(candidates, key=lambda c: len(c[0]))
            mapping[name] = target
            used_targets.add(target)
        else:
            mapping[name] = name
    return mapping


def main():
    User = get_user_model()
    admin = User.objects.filter(role='ADMIN').first() or User.objects.first()

    # Compte agent pour la démo des rôles
    if not User.objects.filter(username='agent.cex').exists():
        User.objects.create_user(username='agent.cex', password='Agent@2026',
                                 first_name='Agent', last_name='CEX', role='AGENT')
        print('+ Compte agent.cex créé (mot de passe: Agent@2026)')

    for survey_type, filepath in FILES.items():
        if not os.path.exists(filepath):
            print(f'! {survey_type}: fichier introuvable, ignoré ({filepath})')
            continue
        structure = load_and_analyze(filepath)
        names = [c['original_name'] for c in structure['detected_columns']]
        rules = RULES[survey_type]
        mapping = build_mapping(names, rules['map'])
        drops = [n for n in names if n in set(rules['drops'])]

        tpl, created = SurveyTemplate.objects.update_or_create(
            name=f'Modèle {survey_type}',
            defaults={
                'survey_type': survey_type,
                'created_by': admin,
                'column_mapping': mapping,
                'columns_to_drop': drops,
                'header_rows_to_skip': structure['header_rows_to_skip'],
            },
        )
        # Test de nettoyage immédiat
        df = clean_dataframe(filepath, {
            'header_rows_to_skip': tpl.header_rows_to_skip,
            'columns_to_drop': drops,
            'column_mapping': mapping,
        })
        print(f"+ Modèle {survey_type} {'créé' if created else 'mis à jour'} : "
              f"{len(df)} lignes, {len(df.columns)} colonnes")
        print('   ->', ', '.join(list(df.columns)[:14]), '…')


if __name__ == '__main__':
    main()
