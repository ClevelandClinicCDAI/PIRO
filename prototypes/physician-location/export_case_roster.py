"""Export case-derived demo profiles using a read-only SQL Server connection.

Run separately from the presence API. Only this exporter connects to PIRO;
the prototype consumes the resulting local JSON file.
"""
import argparse
import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


CATEGORIES = {
    'gi': 'Gastrointestinal Pathology', 'derm': 'Dermatopathology',
    'cyto': 'Cytopathology', 'gyn': 'Gynecologic Pathology',
    'orthopedic': 'Soft Tissue and Bone Pathology', 'soft': 'Soft Tissue and Bone Pathology',
    'breast': 'Breast Pathology', 'gu': 'Genitourinary Pathology',
    'head': 'Head and Neck Pathology', 'cardiac': 'Cardiovascular Pathology',
    'hematology': 'Hematopathology', 'lymphoma': 'Hematopathology',
    'pulmonary': 'Thoracic Pathology', 'hepatobiliary': 'Hepatobiliary Pathology',
    'neuro': 'Neuropathology', 'eye': 'Ophthalmic Pathology',
    'pediatric': 'Pediatric Pathology',
}
CODE_OVERRIDES = {
    'REFGX': 'Gastrointestinal Pathology', 'MKD.': 'Renal Pathology',
    'SKIN DIF': 'Dermatopathology', 'ORAL/MAXILLO': 'Oral and Maxillofacial Pathology',
}


def specialty_for(row):
    code = (row['SpecialtyCode'] or '').strip().upper()
    return CODE_OVERRIDES.get(code) or CATEGORIES.get((row['SpecialtyCategory'] or '').strip().lower())


def summarize(rows, limit):
    people = {}
    for row in rows:
        person = people.setdefault(row['StaffId'], {
            'name': row['FullName'], 'cases': 0, 'specialties': Counter(), 'regions': Counter(),
            'role_cases': row['RoleEvidenceCases'],
        })
        count = row['CaseCount']
        person['cases'] += count
        label = specialty_for(row)
        if label:
            person['specialties'][label] += count
        person['regions'][(row['CaseRegion'] or '').strip() or 'Unknown'] += count
    ranked = sorted(people.items(), key=lambda item: (-item[1]['cases'], item[0]))[:limit]
    roster = []
    for staff_id, person in ranked:
        mix = sorted(person['specialties'].items(), key=lambda item: (-item[1], item[0]))
        if not mix:
            primary = 'Undetermined'
        elif len(mix) > 1 and mix[0][1] == mix[1][1]:
            primary = 'Mixed case mix'
        else:
            primary = mix[0][0]
        regions = sorted(person['regions'].items(), key=lambda item: (-item[1], item[0]))
        region = 'Multiple regions' if len(regions) > 1 and regions[0][1] == regions[1][1] else regions[0][0]
        roster.append({
            'physician_id': f'case-staff-{staff_id}', 'name': person['name'],
            'username': f'DEMO\\case-staff-{staff_id}', 'subspecialty': primary, 'region': region,
            'subspecialty_source': 'Inferred from recent case mix',
            'role_source': 'STAFF PATHOLOGIST in SSIS_CaseStaff',
            'role_evidence_cases': person['role_cases'],
            'recent_case_count': person['cases'],
            'classified_case_count': sum(person['specialties'].values()),
            'case_mix': [{'subspecialty': label, 'cases': count} for label, count in mix],
        })
    return roster, len(people)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--days', type=int, default=90)
    parser.add_argument('--max-cases', type=int, default=25000)
    parser.add_argument('--limit', type=int, default=25)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('roster.local.json'))
    args = parser.parse_args()
    if min(args.days, args.max_cases, args.limit) < 1:
        parser.error('--days, --max-cases and --limit must be positive')
    end = datetime.now(ZoneInfo('America/New_York')).date() + timedelta(days=1)
    start = end - timedelta(days=args.days)
    import pyodbc
    # Escape ODBC values without logging credentials or the connection string.
    def quoted(value):
        return '{' + value.replace('}', '}}') + '}'
    connection_string = ';'.join([
        'DRIVER=' + quoted(os.environ['MSSQL_DRIVER']),
        'SERVER=' + quoted(os.environ['MSSQL_SERVER']),
        'DATABASE=' + quoted(os.environ['MSSQL_DB']),
        'UID=' + quoted(os.environ['MSSQL_USER']),
        'PWD=' + quoted(os.environ['MSSQL_PASSWORD']),
        'TrustServerCertificate=yes', 'APP=PIRO Prototype Read Only',
    ])
    sql = Path(__file__).with_name('recent_case_profiles.sql').read_text()
    conn = pyodbc.connect(connection_string, readonly=True, timeout=10)
    try:
        conn.timeout = 60
        cursor = conn.execute(sql, args.max_cases, start.year, start, end, end)
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()
    if not rows:
        raise SystemExit('No staff with explicit STAFF PATHOLOGIST evidence found. Existing roster file was not changed.')
    roster, staff_count = summarize(rows, args.limit)
    sample = rows[0]
    output = {
        'source': 'PIRO recent completed cases', 'real_names': True,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'window_start': str(start), 'window_end': str(end - timedelta(days=1)),
        'sample_cases': sample['SampleCases'], 'max_cases': args.max_cases,
        'earliest_accession': str(sample['EarliestAccession']),
        'latest_accession': str(sample['LatestAccession']), 'latest_signout': str(sample['LatestSignout']),
        'candidate_staff_count': staff_count,
        'selection': f'Up to {args.limit} role-confirmed staff pathologists with the most linked cases in the sample',
        'role_method': 'Requires STAFF PATHOLOGIST responsibility in SSIS_CaseStaff on at least one sampled case; staging coverage is incomplete',
        'specialty_method': 'Most frequent mapped clinical specialty; ties are mixed and unmapped labels are excluded',
        'region_method': 'Most frequent case hospital region, not staff affiliation or physical location',
        'physicians': roster,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(output, stream, indent=2)
        stream.write('\n')
    temporary.replace(args.output)
    print(json.dumps({
        'sample_cases': output['sample_cases'], 'candidate_staff': staff_count,
        'exported_profiles': len(roster), 'earliest_accession': output['earliest_accession'],
        'latest_accession': output['latest_accession'],
        'inferred_specialties': dict(Counter(person['subspecialty'] for person in roster)),
    }))


if __name__ == '__main__':
    main()
