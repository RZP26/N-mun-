from statistics import mean, median
from collections import Counter

def summarize_results(rows: list[dict]) -> dict:
    scores=[float(r.get('percent') or 0) for r in rows]
    if not rows:
        return {'students':0,'mean_percent':0,'median_percent':0,'min_percent':0,'max_percent':0,'score_bands':{},'question_analysis':[]}
    bands=Counter()
    for score in scores:
        label='0-49' if score<50 else '50-69' if score<70 else '70-89' if score<90 else '90-100'
        bands[label]+=1
    return {'students':len(rows),'mean_percent':round(mean(scores),2),'median_percent':round(median(scores),2),'min_percent':min(scores),'max_percent':max(scores),'score_bands':dict(bands)}

def item_difficulty(answer_rows: list[dict]) -> dict:
    """p = correct / answered; unanswered rows are not in the denominator."""
    answered=[r for r in answer_rows if r.get('status') in {'correct','wrong'}]
    correct=sum(1 for r in answered if r.get('status')=='correct')
    return {'answered':len(answered),'correct':correct,'p_correct':round(correct/len(answered),4) if answered else None,'interpretation':'nisbətən asan' if answered and correct/len(answered)>=0.8 else 'nisbətən çətin' if answered and correct/len(answered)<=0.3 else 'orta' if answered else 'məlumat yoxdur'}
