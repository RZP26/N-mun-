from typing import Any

OBJECTIVE_TYPES = {"mcq", "true_false"}

def grade_answers(questions: list[dict[str, Any]], answers: dict[str, str | None]) -> dict[str, Any]:
    """Automatically score only objective questions; open/short responses require review."""
    score = 0.0
    maximum = sum(float(q["points"]) for q in questions)
    correct = wrong = blank = 0
    review: list[int] = []
    detail = []
    for q in questions:
        question_no = int(q["question_no"])
        no = str(question_no)
        answer = answers.get(no)
        qtype = str(q.get("question_type", "mcq")).strip().casefold()
        if qtype not in OBJECTIVE_TYPES:
            review.append(question_no)
            detail.append({"question_no": question_no, "answer": answer, "status": "review_open_answer", "points": 0,
                           "message": "Açıq/qısa cavab müəllim tərəfindən qiymətləndirilməlidir."})
            continue
        if answer is None or not str(answer).strip():
            blank += 1
            detail.append({"question_no": question_no, "answer": None, "status": "blank", "points": 0})
            continue
        actual = str(answer).strip()
        if actual.upper() in {"UNCERTAIN", "AMBIGUOUS", "QEYRI-MUEYYEN"}:
            review.append(question_no)
            detail.append({"question_no": question_no, "answer": actual, "status": "review", "points": 0})
            continue
        expected = str(q["correct_answer"]).strip().casefold()
        if actual.casefold() == expected:
            score += float(q["points"])
            correct += 1
            detail.append({"question_no": question_no, "answer": actual, "status": "correct", "points": float(q["points"])})
        else:
            wrong += 1
            detail.append({"question_no": question_no, "answer": actual, "status": "wrong", "points": 0})
    return {
        "score": round(score, 2),
        "max_score": round(maximum, 2),
        "percent": round(score / maximum * 100, 2) if maximum else 0,
        "correct_count": correct,
        "wrong_count": wrong,
        "blank_count": blank,
        "needs_review": sorted(set(review)),
        "details": detail,
    }
