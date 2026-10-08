"""Checks for inference ambiguity and aggregation across case specialties."""
import unittest
from export_case_roster import summarize


def row(staff, code, category, count, region='NE Ohio'):
    return dict(StaffId=staff, FullName=f'Test physician {staff}', SpecialtyCode=code,
                SpecialtyCategory=category, CaseCount=count, CaseRegion=region, RoleEvidenceCases=1)


class CaseRosterTests(unittest.TestCase):
    def test_combines_clinical_categories_and_excludes_administrative_labels(self):
        profiles, count = summarize([
            row(1, 'GI SMALL', 'Gi', 8), row(1, 'REFGX', 'Reference', 3, 'Akron'),
            row(1, 'NULL', 'NA', 20), row(1, 'BILLINGS', 'Billings', 10),
        ], 25)
        person = profiles[0]
        self.assertEqual(count, 1)
        self.assertEqual(person['recent_case_count'], 41)
        self.assertEqual(person['classified_case_count'], 11)
        self.assertEqual(person['case_mix'], [{'subspecialty': 'Gastrointestinal Pathology', 'cases': 11}])
        self.assertEqual(person['subspecialty'], 'Gastrointestinal Pathology')

    def test_ties_and_unmapped_values_are_not_guessed(self):
        profiles, _ = summarize([
            row(1, 'BR BX', 'Breast', 5, 'Akron'), row(1, 'GU SMALL', 'Gu', 5, 'Weston'),
            row(2, 'CON', 'Consult', 8, None),
        ], 25)
        self.assertEqual(profiles[0]['subspecialty'], 'Mixed case mix')
        self.assertEqual(profiles[0]['region'], 'Multiple regions')
        self.assertEqual(profiles[1]['subspecialty'], 'Undetermined')
        self.assertEqual(profiles[1]['classified_case_count'], 0)
        self.assertEqual(profiles[1]['region'], 'Unknown')

    def test_stable_identity_when_case_volume_changes(self):
        first, _ = summarize([row(1, 'NEU1', 'Neuro', 5), row(2, 'NEU1', 'Neuro', 10)], 1)
        second, _ = summarize([row(1, 'NEU1', 'Neuro', 15), row(2, 'NEU1', 'Neuro', 10)], 2)
        self.assertEqual(first[0]['physician_id'], second[1]['physician_id'])
        self.assertEqual(first[0]['username'], second[1]['username'])
        self.assertTrue(first[0]['username'].startswith('DEMO\\'))


if __name__ == '__main__':
    unittest.main()
