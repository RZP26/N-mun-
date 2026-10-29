from app.services.reports import make_excel, make_pdf

def test_reports_return_expected_file_signatures():
    rows=[{'student_no':'S001','student_name':'Numune Telebe','assessment_title':'Test','score':8,'max_score':10,'percent':80,'correct_count':4,'wrong_count':1,'blank_count':0,'needs_review':''}]
    assert make_excel(rows)[:2] == b'PK'
    assert make_pdf(rows).startswith(b'%PDF')
