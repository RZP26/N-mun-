from app.services.student_matcher import match_page_identities

def test_match_and_flag_ambiguous_pages():
    result = match_page_identities([(1, 'S001'), (2, None), (3, 'X999'), (4, 'S001')], {'S001', 'S002'})
    assert [x.status for x in result] == ['matched', 'unidentified', 'unknown_code', 'duplicate_code']
