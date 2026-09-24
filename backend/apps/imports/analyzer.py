"""
Moteur d'analyse et de nettoyage des fichiers SurveyMonkey.

Principe :
- Ligne 0 = titres des questions, Ligne 1 = sous-titres ("Response", options multi-choix...)
- Une question à choix multiples occupe PLUSIEURS colonnes : la question sur la
  première, puis des colonnes sans titre pour chaque option. On les FUSIONNE
  en une seule colonne logique (valeurs jointes par ", ").
"""
import pandas as pd
from typing import Any

# Moteur de lecture Excel : calamine (Rust, ~4x plus rapide) si installé, sinon openpyxl
try:
    import python_calamine  # noqa: F401
    EXCEL_ENGINE = 'calamine'
except ImportError:
    EXCEL_ENGINE = None

SURVEYMONKEY_SYSTEM_COLS = {
    'respondent_id', 'collector_id', 'date_created', 'date_modified',
    'ip_address', 'email_address', 'first_name', 'last_name', 'custom_1',
    'start_date', 'end_date', 'collector_name',
}

# Colonnes système vides par défaut à supprimer
DEFAULT_DROPS = {'email_address', 'first_name', 'last_name', 'custom_1'}

JOIN_KEY_PATTERNS = ['n° rec', 'n°rec', 'nrec', 'rec_id', 'record_id', 'numero rec', 'n rec']

SM_SUBTITLE_MARKERS = {'response', 'open-ended response', 'open ended response'}


def _normalize(s: str) -> str:
    return str(s).lower().strip().replace(' ', '').replace('°', '').replace('_', '')


def detect_join_key(columns: list) -> str | None:
    """Cherche automatiquement la colonne clé de jointure (N° REC)."""
    for col in columns:
        norm = _normalize(col)
        for pattern in JOIN_KEY_PATTERNS:
            p = _normalize(pattern)
            if p == norm or p in norm:
                return col
    return None


def _read_raw(filepath: str, sheet_name: Any = 0) -> pd.DataFrame:
    if str(filepath).lower().endswith('.csv'):
        return pd.read_csv(filepath, header=None, dtype=str)
    return pd.read_excel(filepath, sheet_name=sheet_name, header=None, dtype=str, engine=EXCEL_ENGINE)


OPEN_ENDED_MARKERS = {'open-ended response', 'open ended response', 'réponse ouverte', 'reponse ouverte',
                      'raison de la note', 'pourquoi?', 'pourquoi'}


def _build_column_groups(row0: list, row1: list) -> list[dict]:
    """
    Construit les colonnes LOGIQUES : chaque question = 1 colonne.
    - Colonnes sans titre = options multi-choix -> fusionnées avec la question.
    - EXCEPTION : une colonne sans titre marquée "Open-Ended Response" est un
      VERBATIM libre -> colonne séparée (comme dans les codes SAS).
    """
    groups = []
    current = None

    for i, name in enumerate(row0):
        subtitle = row1[i] if i < len(row1) else ''
        if name:  # nouvelle colonne / question
            if current:
                groups.append(current)
            current = {
                'start': i, 'end': i,
                'name': name,
                'subtitles': [subtitle] if subtitle else [],
            }
        elif subtitle and subtitle.lower().strip() in OPEN_ENDED_MARKERS and current:
            # Verbatim libre accolé à une question (CSAT/CES) -> colonne à part
            base = current['name']
            groups.append(current)
            current = {'start': i, 'end': i, 'name': f'Verbatim - {base[:40]}', 'subtitles': []}
        else:  # colonne sans titre -> option de la question précédente
            if current is None:
                current = {'start': i, 'end': i, 'name': subtitle or f'col_{i}', 'subtitles': []}
            else:
                current['end'] = i
                if subtitle:
                    current['subtitles'].append(subtitle)
    if current:
        groups.append(current)

    # Dédupliquer les noms (ex: 3x "VERBATIM")
    seen = {}
    for g in groups:
        n = g['name']
        if n in seen:
            seen[n] += 1
            g['display_name'] = f"{n}.{seen[n]}"
        else:
            seen[n] = 0
            g['display_name'] = n
        g['is_multi'] = g['end'] > g['start']
    return groups


def detect_structure(df_raw: pd.DataFrame) -> dict:
    result = {
        'is_surveymonkey': False,
        'header_rows_to_skip': 1,
        'total_rows_raw': len(df_raw),
        'detected_columns': [],
        'suggested_drops': [],
        'suggested_mapping': {},
        'warnings': [],
        'join_key': None,
        'column_groups': [],
    }
    if len(df_raw) < 2:
        return result

    def cell(v):
        s = str(v).strip()
        return '' if not s or s.lower() in ('nan', 'none', 'nat') else s

    row0 = [cell(v) for v in df_raw.iloc[0]]
    row1 = [cell(v) for v in df_raw.iloc[1]]

    sm_markers = {'respondent_id', 'collector_id', 'ip_address', 'date_created', 'date_modified'}
    row0_set = {v.lower() for v in row0 if v}

    if len(sm_markers & row0_set) >= 2:
        result['is_surveymonkey'] = True
        row1_has_responses = any(v.lower() in SM_SUBTITLE_MARKERS for v in row1 if v)
        row1_empty_ratio = sum(1 for v in row1 if not v) / max(len(row1), 1)
        if row1_has_responses or row1_empty_ratio > 0.4:
            result['header_rows_to_skip'] = 2
            result['warnings'].append(
                "Format SurveyMonkey détecté : la ligne de sous-titres a été retirée automatiquement."
            )

    groups = _build_column_groups(row0, row1)
    result['column_groups'] = [
        {'start': g['start'], 'end': g['end'], 'display_name': g['display_name']} for g in groups
    ]

    for idx, g in enumerate(groups):
        display = g['display_name']
        is_system = g['name'].lower() in SURVEYMONKEY_SYSTEM_COLS
        suggested_drop = g['name'].lower() in DEFAULT_DROPS
        col_info = {
            'index': idx,
            'original_name': display,
            'raw_name': g['name'],
            'subtitle': (
                f"{g['end'] - g['start'] + 1} options (choix multiple) : " + ', '.join(g['subtitles'][:4])
                + ('…' if len(g['subtitles']) > 4 else '')
            ) if g['is_multi'] else (g['subtitles'][0] if g['subtitles'] and g['subtitles'][0].lower() not in SM_SUBTITLE_MARKERS else ''),
            'is_multi': g['is_multi'],
            'suggested_name': display,
            'is_system': is_system,
            'suggested_drop': suggested_drop,
            'type': 'system' if is_system else ('multi' if g['is_multi'] else 'business'),
            'is_join_key': False,
        }
        if suggested_drop:
            result['suggested_drops'].append(display)
        else:
            result['suggested_mapping'][display] = display
        result['detected_columns'].append(col_info)

    join_key = detect_join_key([c['original_name'] for c in result['detected_columns']])
    if join_key:
        result['join_key'] = join_key
        for c in result['detected_columns']:
            if c['original_name'] == join_key:
                c['is_join_key'] = True
    return result


def load_and_analyze(filepath: str, sheet_name: Any = 0) -> dict:
    df_raw = _read_raw(filepath, sheet_name)
    structure = detect_structure(df_raw)
    try:
        structure['sheets'] = pd.ExcelFile(filepath).sheet_names
    except Exception:
        structure['sheets'] = []
    return structure


def clean_dataframe(filepath: str, config: dict) -> pd.DataFrame:
    """
    Nettoie le fichier brut :
    1. Reconstruit les colonnes logiques (fusion des groupes multi-choix)
    2. Supprime les lignes d'en-tête superflues et lignes vides
    3. Supprime les colonnes indésirables
    4. Renomme selon le mapping (avec déduplication des noms cibles)
    """
    skip = int(config.get('header_rows_to_skip', 2))
    columns_to_drop = set(config.get('columns_to_drop', []) or [])
    mapping = config.get('column_mapping', {}) or {}

    df_raw = _read_raw(filepath, config.get('sheet_name', 0))
    structure = detect_structure(df_raw)
    groups = structure['column_groups']

    data = df_raw.iloc[skip:].reset_index(drop=True)

    def cell(v):
        s = str(v).strip()
        return '' if not s or s.lower() in ('nan', 'none', 'nat') else s

    out = {}
    order = []
    for g in groups:
        name = g['display_name']
        if name in columns_to_drop:
            continue
        start, end = g['start'], g['end']
        if end > start:
            # Fusion multi-choix : joindre les valeurs non vides par ", "
            block = data.iloc[:, start:end + 1]
            merged = block.apply(lambda r: ', '.join(cell(v) for v in r if cell(v)), axis=1)
            out[name] = merged
        else:
            if start < data.shape[1]:
                out[name] = data.iloc[:, start].map(cell)
            else:
                out[name] = ''
        order.append(name)

    df = pd.DataFrame(out, columns=order)

    # Supprimer lignes entièrement vides
    df = df[~df.apply(lambda r: all(not str(v).strip() for v in r), axis=1)].reset_index(drop=True)

    # Comme le code SAS : exclure les lignes sans respondent_id
    if 'respondent_id' in df.columns:
        df = df[df['respondent_id'].astype(str).str.strip() != ''].reset_index(drop=True)

    # Renommer avec déduplication des noms cibles
    new_names = []
    seen = {}
    for c in df.columns:
        target = str(mapping.get(c, c)).strip() or c
        if target in seen:
            seen[target] += 1
            target = f'{target}.{seen[target]}'
        else:
            seen[target] = 0
        new_names.append(target)
    df.columns = new_names

    df = df.drop_duplicates().reset_index(drop=True)

    # Réordonner selon l'ordre choisi par l'utilisateur (noms finaux) ;
    # les colonnes absentes de la liste restent à la suite, dans leur ordre actuel
    order = config.get('column_order') or []
    if order:
        ordered = [c for c in order if c in df.columns]
        ordered += [c for c in df.columns if c not in ordered]
        df = df[ordered]

    # Statuts NPS automatiques (comme le code SAS) :
    # 1-6 = DETRACTEUR, 7-8 = NEUTRE, 9-10 = PROMOTEUR
    def nps_statut(v):
        try:
            n = float(str(v).replace(',', '.'))
        except (ValueError, TypeError):
            return ''
        if 0 <= n <= 6:
            return 'DETRACTEUR'
        if n in (7, 8):
            return 'NEUTRE'
        if n in (9, 10):
            return 'PROMOTEUR'
        return ''

    # Noms exacts attendus par les fichiers de référence MTN
    lower_cols = {c.lower() for c in df.columns}
    special = {'note_nps': 'STATUT_NPS', 'nps_service': 'Statut_ NPS_service',
               'note_nps_others': 'STATUT_NPS_Others'}
    if 'note_nps' not in lower_cols:
        special['nps_agent'] = 'Statut_NPS'  # convention VOC (pas de Note_NPS dans ce survey)

    new_cols = {}
    for col in df.columns:
        low = col.lower()
        if 'nps' in low and 'statut' not in low and 'verbatim' not in low:
            numeric = pd.to_numeric(df[col].str.replace(',', '.', regex=False), errors='coerce')
            # Colonne de notes valide si majorité des valeurs non vides sont 0-10
            valid = numeric.dropna()
            if len(valid) > 0 and valid.between(0, 10).mean() > 0.9:
                statut_name = special.get(low, f'Statut_{col}')
                if statut_name not in df.columns:
                    new_cols[col] = (statut_name, df[col].map(nps_statut))

    # Insérer chaque statut juste après sa colonne de note
    if new_cols:
        cols = list(df.columns)
        for src, (name, series) in new_cols.items():
            df[name] = series
            cols.insert(cols.index(src) + 1, name)
        df = df[cols]
    return df


def detect_missing_values(df: pd.DataFrame) -> dict:
    report = {}
    total = max(len(df), 1)
    for col in df.columns:
        missing = int((df[col].astype(str).str.strip() == '').sum())
        if missing > 0:
            report[col] = {'missing_count': missing, 'missing_pct': round(missing / total * 100, 1)}
    return report


def compute_nps_metrics(df: pd.DataFrame) -> list:
    """
    Calcule le score NPS de chaque colonne de notes (0-10) :
    NPS = %Promoteurs (9-10) − %Détracteurs (0-6). Les passifs (7-8) ne comptent pas.
    Ignore les CSAT/CES (échelle 1-5) qui ne portent pas 'nps' dans leur nom.
    """
    results = []
    for col in df.columns:
        low = col.lower()
        if 'nps' not in low or 'statut' in low or 'verbatim' in low:
            continue
        numeric = pd.to_numeric(df[col].astype(str).str.replace(',', '.', regex=False), errors='coerce')
        valid = numeric.dropna()
        valid = valid[(valid >= 0) & (valid <= 10)]
        if len(valid) < 1:
            continue
        total = len(valid)
        promoters = int((valid >= 9).sum())
        passives = int(((valid >= 7) & (valid <= 8)).sum())
        detractors = int((valid <= 6).sum())
        results.append({
            'column': col,
            'nps': round((promoters - detractors) / total * 100, 1),
            'promoters': promoters, 'passives': passives, 'detractors': detractors,
            'promoters_pct': round(promoters / total * 100, 1),
            'passives_pct': round(passives / total * 100, 1),
            'detractors_pct': round(detractors / total * 100, 1),
            'total': total,
            'avg': round(float(valid.mean()), 2),
        })
    return results


# Colonnes d'IDENTITÉ d'un répondant (un même numéro = potentiellement la même
# personne qui a répondu deux fois). On EXCLUT volontairement les colonnes de
# canal/catégorie comme « Contact » (Mail, Téléphone...) qui se répètent normalement.
DUP_KEYS = ['msisdn', 'numero_abonne', 'numero abonne', 'ftth_line', 'contact client',
            'msisdn equipement', 'numero_contrat']


def detect_duplicate_respondents(df: pd.DataFrame) -> dict:
    """
    Détecte quand le même client (même numéro de téléphone/abonné) a répondu
    plusieurs fois. Ne s'applique qu'aux colonnes qui ressemblent vraiment à des
    identifiants (valeurs majoritairement numériques et longues), pour éviter de
    confondre avec une colonne de catégorie.
    """
    report = {}
    for col in df.columns:
        if col.lower().strip() not in DUP_KEYS:
            continue
        vals = df[col].astype(str).str.strip()
        vals = vals[(vals != '') & (vals.str.lower() != 'nan')]
        if len(vals) < 2:
            continue
        # Garde-fou : un vrai numéro fait au moins 6 chiffres. Si la colonne
        # contient surtout du texte court, ce n'est pas un identifiant.
        digit_ratio = vals.str.replace(r'\D', '', regex=True).str.len().ge(6).mean()
        if digit_ratio < 0.6:
            continue
        dup = int(vals.duplicated().sum())
        if dup > 0:
            examples = vals[vals.duplicated(keep=False)].value_counts().head(3)
            report[col] = {
                'duplicate_rows': dup,
                'examples': [{'value': str(k), 'count': int(v)} for k, v in examples.items()],
            }
    return report
