from typing import Any

def grade_answers(questions: list[dict[str, Any]], answers: dict[str, str | None]) -> dict[str, Any]:
    """Score objective answers. Unknown/ambiguous values go to teacher review."""
    score = 0.0
    maximum = sum(float(q['points']) for q in questions)
    correct = wrong = blank = 0
    review: list[int] = []
    detail = []
    for q in questions:
        no = str(q['question_no'])
        answer = answers.get(no)
        expected = str(q['correct_answer']).strip().casefold()
        if answer is None or not str(answer).strip():
            blank += 1
            detail.append({'question_no': int(q['question_no']), 'answer': None, 'status': 'blank', 'points': 0})
            continue
        actual = str(answer).strip()
        if actual.upper() in {'UNCERTAIN', 'AMBIGUOUS', 'QEYRI-MUEYYEN'}:
            review.append(int(q['question_no']))
            detail.append({'question_no': int(q['question_no']), 'answer': actual, 'status': 'review', 'points': 0})
            continue
        if actual.casefold() == expected:
            score += float(q['points'])
            correct += 1
            detail.append({'question_no': int(q['question_no']), 'answer': actual, 'status': 'correct', 'points': float(q['points'])})
        else:
            wrong += 1
            detail.append({'question_no': int(q['question_no']), 'answer': actual, 'status': 'wrong', 'points': 0})
    return {'score': round(score, 2), 'max_score': round(maximum, 2), 'percent': round(score / maximum * 100, 2) if maximum else 0, 'correct_count': correct, 'wrong_count': wrong, 'blank_count': blank, 'needs_review': review, 'details': detail}
