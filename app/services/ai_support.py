"""A small rubric-based helper placeholder for future AI provider integration.

The current web app uses deterministic keyword hints; this module intentionally does
not assign final marks. Connect a vetted AI provider only after configuring secrets,
data handling, retention policy, and teacher approval.
"""

def suggest_rubric_review(answer: str, rubric_items: list[str]) -> dict:
    normalized = answer.casefold()
    matched = [item for item in rubric_items if item.strip() and item.casefold() in normalized]
    return {
        'matched_items': matched,
        'unmatched_items': [item for item in rubric_items if item not in matched],
        'teacher_approval_required': True,
        'notice': 'Açar söz uyğunluğu məna qiymətləndirməsini əvəz etmir.'
    }
