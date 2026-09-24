"""
Moteur de correspondance intelligente des colonnes.
Utilise fuzzywuzzy pour détecter les colonnes similaires entre deux DataFrames.
"""
import pandas as pd
from fuzzywuzzy import fuzz
from apps.imports.analyzer import clean_dataframe, EXCEL_ENGINE


def normalize_col(name: str) -> str:
    return (str(name)
            .lower()
            .strip()
            .replace(' ', '_')
            .replace('°', '')
            .replace('n°', 'n')
            .replace('n⁰', 'n')
            .replace('/', '_')
            .replace('-', '_')
            .replace('.', '_'))


def _is_rec_key(name: str) -> bool:
    """Vrai si la colonne ressemble à une clé N° REC."""
    n = normalize_col(name).replace('_', '')
    return n in ('nrec', 'rec') or n.startswith('nrec') or n.endswith('rec')


def suggest_join_keys(left_cols: list, right_cols: list, threshold: int = 70) -> list:
    suggestions = []
    for lc in left_cols:
        best_score = 0
        best_match = None
        lc_norm = normalize_col(lc)
        for rc in right_cols:
            rc_norm = normalize_col(rc)
            score = max(
                fuzz.ratio(lc_norm, rc_norm),
                fuzz.partial_ratio(lc_norm, rc_norm),
                fuzz.token_sort_ratio(lc_norm, rc_norm),
            )
            # Priorité absolue : N° REC des deux côtés
            if _is_rec_key(lc) and _is_rec_key(rc):
                score = 200
            if score > best_score:
                best_score = score
                best_match = rc
        if best_score >= threshold:
            suggestions.append({
                'left_col': lc,
                'right_col': best_match,
                'score': min(best_score, 100),
                'is_exact': best_score >= 100,
                'is_rec_key': best_score == 200,
            })
    suggestions.sort(key=lambda x: (-x.get('is_rec_key', False), -x['score']))
    return suggestions


# Colonnes d'identification du fichier de référence où chercher une valeur
# saisie à la place du N° REC (téléphone, n° abonné, n° contrat, ligne...)
ID_COL_HINTS = ('ABONNE', 'CONTACT', 'MSISDN', 'TELEPHONE', 'TÉLÉPHONE',
                'NUMERO', 'NUMÉRO', 'CONTRAT', 'LIGNE', 'REC', 'EMAIL', 'MAIL')


def _norm_phone(v: str) -> str:
    """Ne garde que les chiffres, sans indicatif 225 ni zéro initial."""
    digits = ''.join(ch for ch in str(v) if ch.isdigit())
    if digits.startswith('225'):
        digits = digits[3:]
    return digits.lstrip('0')


def _norm_value(v: str) -> str:
    return str(v).strip().upper().replace(' ', '')


def _rescue_keys(main_df, ref_df, right_key):
    """
    Cas fréquent : l'agent a saisi autre chose que le N° REC (téléphone,
    n° abonné, n° de contrat...). On cherche cette valeur dans les colonnes
    d'identification du fichier de référence et, si elle pointe vers UN SEUL
    ticket (pas d'ambiguïté), on récupère le bon N° REC.
    Retourne (df, nb_récupérés, détail_par_colonne).
    """
    id_cols = [c for c in ref_df.columns
               if any(h in str(c).upper() for h in ID_COL_HINTS) and c != right_key]
    if not id_cols:
        return main_df, 0, {}

    # Index valeur normalisée -> (N° REC, colonne source). None = ambigu, ignoré.
    value_to_rec = {}
    for col in id_cols:
        recs = ref_df['_join_key_']
        for raw, rec in zip(ref_df[col], recs):
            for key in {_norm_value(raw), _norm_phone(raw)}:
                if len(key) < 6:  # trop court = risque de fausse correspondance
                    continue
                existing = value_to_rec.get(key)
                if existing is None:
                    value_to_rec[key] = (rec, str(col))
                elif existing[0] != rec:
                    value_to_rec[key] = ('__AMBIGU__', '')

    fixed = 0
    fixed_by = {}
    ref_keys = set(ref_df['_join_key_'])

    def fix(val):
        nonlocal fixed
        if val in ref_keys:
            return val
        for key in (_norm_value(val), _norm_phone(val)):
            hit = value_to_rec.get(key)
            if hit and hit[0] != '__AMBIGU__':
                fixed += 1
                fixed_by[hit[1]] = fixed_by.get(hit[1], 0) + 1
                return hit[0]
        return val

    main_df['_join_key_'] = main_df['_join_key_'].map(fix)
    return main_df, fixed, fixed_by


def perform_join(main_df: pd.DataFrame, ref_df: pd.DataFrame,
                 left_key: str, right_key: str,
                 join_type: str = 'LEFT',
                 columns_to_add: list = None) -> tuple[pd.DataFrame, float]:

    main_df = main_df.copy()
    ref_df = ref_df.copy()

    # Normaliser les clés des deux côtés (espaces, casse) pour maximiser les correspondances
    def norm_key(s):
        return s.astype(str).str.strip().str.upper().str.replace(' ', '', regex=False)

    main_df['_join_key_'] = norm_key(main_df[left_key])
    ref_df['_join_key_'] = norm_key(ref_df[right_key])

    # Secours : valeur d'identification saisie à la place du N° REC
    keys_before = main_df['_join_key_'].copy()
    main_df, rescued, rescued_by = _rescue_keys(main_df, ref_df, right_key)

    # Uniformisation : la valeur fautive (téléphone, n° abonné...) est REMPLACÉE
    # par le vrai N° REC dans la colonne du fichier final
    corrected = main_df['_join_key_'] != keys_before
    if corrected.any():
        main_df.loc[corrected, left_key] = main_df.loc[corrected, '_join_key_']

    if columns_to_add:
        cols_needed = ['_join_key_'] + [c for c in columns_to_add if c in ref_df.columns and c != right_key]
        ref_df = ref_df[cols_needed]
    else:
        ref_df = ref_df.drop(columns=[right_key])

    # Dédupliquer la référence sur la clé (éviter la multiplication des lignes)
    ref_df = ref_df.drop_duplicates(subset='_join_key_')

    how_map = {'LEFT': 'left', 'INNER': 'inner', 'FULL': 'outer'}
    how = how_map.get(join_type, 'left')

    merged = main_df.merge(ref_df, on='_join_key_', how=how, suffixes=('', '_ref'), indicator=True)

    matched = int((merged['_merge'] == 'both').sum())
    total = len(main_df)
    match_rate = round(matched / total * 100, 2) if total > 0 else 0.0

    # Lignes restées sans correspondance : remontées à l'utilisateur pour correction
    unmatched_mask = merged['_merge'] != 'both'
    unmatched_sample = merged.loc[unmatched_mask, left_key].astype(str).head(5).tolist() if left_key in merged.columns else []

    stats = {
        'rescued': rescued,
        'rescued_by': rescued_by,
        'unmatched': int(unmatched_mask.sum()),
        'unmatched_sample': unmatched_sample,
    }

    merged = merged.drop(columns=['_join_key_', '_merge'])
    return merged, match_rate, stats


def _clean_header_cells(row) -> list:
    """Transforme une ligne brute en noms de colonnes propres et dédupliqués."""
    cols, seen = [], {}
    for i, v in enumerate(row):
        s = str(v).strip()
        if not s or s.lower() in ('nan', 'none', 'nat'):
            s = f'col_{i}'
        if s in seen:
            seen[s] += 1
            s = f'{s}.{seen[s]}'
        else:
            seen[s] = 0
        cols.append(s)
    return cols


def _detect_header_row(head: pd.DataFrame) -> int:
    """Trouve la ligne d'en-têtes : les rapports ont parfois des titres au-dessus."""
    best_row, best_count = 0, -1
    for i in range(min(8, len(head))):
        vals = [str(v).strip() for v in head.iloc[i]
                if str(v).strip() and str(v).strip().lower() not in ('nan', 'none')]
        # Priorité absolue : la ligne qui contient une colonne N° REC
        if any(_is_rec_key(v) for v in vals):
            return i
        if len(vals) > best_count:
            best_row, best_count = i, len(vals)
    return best_row


def _rows_to_df(rows: list, header_row: int) -> pd.DataFrame:
    """Construit un DataFrame de chaînes à partir des lignes brutes calamine."""
    cols = _clean_header_cells(rows[header_row])
    width = len(cols)
    data = [
        ['' if v is None else str(v) for v in (row + [None] * (width - len(row)))[:width]]
        for row in rows[header_row + 1:]
    ]
    return pd.DataFrame(data, columns=cols)


def analyze_ref_file(filepath: str, cache_writer=None) -> dict:
    """Liste les feuilles/colonnes (en-têtes détectés même après des lignes de titre)
    et choisit la feuille N° REC la plus complète comme cible de jointure.

    Le xlsx n'est parsé qu'UNE seule fois : les feuilles candidates (avec N° REC)
    sont transmises à `cache_writer(sheet_name, df)` pour que l'exécution de la
    jointure n'ait pas à relire le classeur.
    """
    result = {'sheets': {}, 'header_rows': {}, 'best_sheet': None, 'best_key': None}
    candidates = []

    if EXCEL_ENGINE == 'calamine':
        from python_calamine import CalamineWorkbook
        wb = CalamineWorkbook.from_path(filepath)
        for sheet in wb.sheet_names:
            rows = wb.get_sheet_by_name(sheet).to_python()
            rows = [list(r) for r in rows]
            if not rows:
                result['sheets'][sheet] = []
                result['header_rows'][sheet] = 0
                continue
            head = pd.DataFrame(rows[:8])
            hr = _detect_header_row(head.astype(str))
            cols = _clean_header_cells(['' if v is None else str(v) for v in rows[hr]])
            result['sheets'][sheet] = cols
            result['header_rows'][sheet] = hr
            rec = next((c for c in cols if _is_rec_key(c)), None)
            if rec:
                real_cols = sum(1 for c in cols if not c.startswith('col_'))
                candidates.append((real_cols, sheet, rec))
                if cache_writer:
                    cache_writer(sheet, _rows_to_df(rows, hr))
    else:
        # Repli openpyxl (plus lent) si calamine n'est pas installé
        with pd.ExcelFile(filepath) as xl:
            for sheet in xl.sheet_names:
                head = pd.read_excel(xl, sheet_name=sheet, header=None, nrows=8, dtype=str)
                if head.empty:
                    result['sheets'][sheet] = []
                    result['header_rows'][sheet] = 0
                    continue
                hr = _detect_header_row(head)
                cols = _clean_header_cells(head.iloc[hr])
                result['sheets'][sheet] = cols
                result['header_rows'][sheet] = hr
                rec = next((c for c in cols if _is_rec_key(c)), None)
                if rec:
                    real_cols = sum(1 for c in cols if not c.startswith('col_'))
                    candidates.append((real_cols, sheet, rec))

    if candidates:
        # La feuille avec le plus de colonnes = la liste de tickets complète
        candidates.sort(reverse=True)
        _, result['best_sheet'], result['best_key'] = candidates[0]
    return result


def read_ref_sheet(filepath: str, sheet_name, header_row: int = 0) -> pd.DataFrame:
    """Lit une feuille de référence en sautant les éventuelles lignes de titre.
    Utilise calamine (Rust, ~4x plus rapide qu'openpyxl) si disponible."""
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_row,
                       dtype=str, engine=EXCEL_ENGINE)
    df.columns = _clean_header_cells(df.columns)
    return df
