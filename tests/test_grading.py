from app.services.grading import grade_answers

def test_grade_objective_answers():
    questions=[{'question_no':1,'correct_answer':'B','points':5},{'question_no':2,'correct_answer':'DOĞRU','points':5},{'question_no':3,'correct_answer':'A','points':10}]
    result=grade_answers(questions,{'1':'b','2':'DOĞRU','3':'C'})
    assert result['score']==10
    assert result['max_score']==20
    assert result['percent']==50
    assert result['correct_count']==2
    assert result['wrong_count']==1

def test_uncertain_goes_to_review():
    result=grade_answers([{'question_no':1,'correct_answer':'A','points':2}],{'1':'UNCERTAIN'})
    assert result['needs_review']==[1]
    assert result['score']==0

def test_blank_not_marked_wrong():
    result=grade_answers([{'question_no':1,'correct_answer':'A','points':2}],{})
    assert result['blank_count']==1
    assert result['wrong_count']==0
