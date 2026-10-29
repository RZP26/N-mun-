from dataclasses import dataclass

@dataclass
class PageIdentity:
    page_number: int
    student_no: str | None
    status: str
    message: str

def match_page_identities(page_codes: list[tuple[int, str | None]], known_student_numbers: set[str]) -> list[PageIdentity]:
    """Match decoded codes to the roster; never guess identity from handwriting."""
    seen: dict[str, int] = {}
    output = []
    for page, raw in page_codes:
        code = (raw or '').strip()
        if not code:
            output.append(PageIdentity(page, None, 'unidentified', 'Kod aşkarlanmayıb; müəllim təsdiqi lazımdır.'))
        elif code not in known_student_numbers:
            output.append(PageIdentity(page, code, 'unknown_code', 'Kod qrup siyahısında yoxdur; yoxlayın.'))
        elif code in seen:
            output.append(PageIdentity(page, code, 'duplicate_code', f'Eyni kod {seen[code]}-ci səhifədə də var; təkrar yoxlanmalıdır.'))
        else:
            seen[code] = page
            output.append(PageIdentity(page, code, 'matched', 'Kod tələbə siyahısı ilə uyğun gəldi.'))
    return output
