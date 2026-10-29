from app.services.assessment_analysis import summarize_results, item_difficulty

def test_summary():
    result=summarize_results([{'percent':50},{'percent':80},{'percent':90}])
    assert result['students']==3
    assert result['mean_percent']==73.33
    assert result['score_bands']['50-69']==1

def test_item_difficulty_ignores_blank():
    result=item_difficulty([{'status':'correct'},{'status':'wrong'},{'status':'blank'}])
    assert result['answered']==2
    assert result['p_correct']==0.5
