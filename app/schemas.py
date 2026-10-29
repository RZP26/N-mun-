from pydantic import BaseModel, Field
from typing import Literal

class TeacherIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: str | None = Field(default=None, max_length=254)

class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    qualification: str = Field(default='', max_length=160)
    academic_year: str = Field(default='', max_length=30)

class StudentIn(BaseModel):
    student_no: str = Field(min_length=1, max_length=40)
    full_name: str = Field(min_length=2, max_length=160)
    group_id: int | None = None

class AssessmentIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    module_name: str = Field(default='', max_length=160)
    learning_outcome: str = Field(default='', max_length=500)
    criterion: str = Field(default='', max_length=500)
    teacher_id: int | None = None

class QuestionIn(BaseModel):
    assessment_id: int
    question_no: int = Field(ge=1, le=500)
    prompt: str = Field(min_length=1, max_length=4000)
    question_type: Literal['mcq', 'true_false', 'short', 'open'] = 'mcq'
    correct_answer: str = Field(min_length=1, max_length=2000)
    points: float = Field(gt=0, le=1000)

class GradeIn(BaseModel):
    assessment_id: int
    student_id: int | None = None
    answers: dict[str, str | None]
    source_file: str | None = None

class ReviewIn(BaseModel):
    result_id: int
    approved_score: float = Field(ge=0)
    reviewer_note: str = Field(default='', max_length=2000)
