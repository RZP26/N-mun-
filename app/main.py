from pathlib import Path
from uuid import uuid4
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from io import BytesIO
from app.database import init_db, get_db
from app.schemas import TeacherIn, GroupIn, StudentIn, AssessmentIn, QuestionIn, GradeIn, ReviewIn
from app.services.file_processing import validate_file, UnsafeUpload, pdf_pages_as_images, pdf_page_count
from app.services.qr_adapter import decode_student_qr
from app.services.student_matcher import match_page_identities
from app.services.grading import grade_answers
from app.services.ocr import extract_text
from app.services.reports import make_excel, make_pdf

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / 'templates' / 'index.html'
STORAGE = Path('storage')
STORAGE.mkdir(exist_ok=True)
MAX_FILES_PER_REQUEST = 30

app = FastAPI(title='Peşə Təhsilində Elektron Qiymətləndirmə', version='0.1.0')

@app.on_event('startup')
def startup():
    init_db()

@app.get('/health')
def health():
    return {'status': 'ok', 'prototype': True}

@app.get('/', response_class=HTMLResponse)
def home():
    return HTMLResponse(TEMPLATE.read_text(encoding='utf-8'))

@app.post('/api/teachers')
def create_teacher(data: TeacherIn):
    with get_db() as db:
        try:
            cur = db.execute('INSERT INTO teachers(full_name,email) VALUES (?,?)',(data.full_name,data.email))
        except Exception:
            raise HTTPException(409,'Bu e-poçtla müəllim artıq qeydiyyatdadır.')
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('teacher.created',data.full_name))
        return dict(db.execute('SELECT * FROM teachers WHERE id=?',(cur.lastrowid,)).fetchone())

@app.get('/api/teachers')
def list_teachers():
    with get_db() as db: return [dict(x) for x in db.execute('SELECT * FROM teachers ORDER BY full_name')]

@app.post('/api/groups')
def create_group(data: GroupIn):
    with get_db() as db:
        try: cur = db.execute('INSERT INTO groups_table(name,qualification,academic_year) VALUES (?,?,?)',(data.name,data.qualification,data.academic_year))
        except Exception: raise HTTPException(409,'Bu qrup adı artıq mövcuddur.')
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('group.created',data.name))
        return dict(db.execute('SELECT * FROM groups_table WHERE id=?',(cur.lastrowid,)).fetchone())

@app.get('/api/groups')
def list_groups():
    with get_db() as db: return [dict(x) for x in db.execute('SELECT * FROM groups_table ORDER BY name')]

@app.post('/api/students')
def create_student(data: StudentIn):
    with get_db() as db:
        if data.group_id is not None and not db.execute('SELECT id FROM groups_table WHERE id=?',(data.group_id,)).fetchone(): raise HTTPException(404,'Qrup tapılmadı.')
        try: cur = db.execute('INSERT INTO students(student_no,full_name,group_id) VALUES (?,?,?)',(data.student_no,data.full_name,data.group_id))
        except Exception: raise HTTPException(409,'Tələbə nömrəsi artıq mövcuddur.')
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('student.created',data.student_no))
        return dict(db.execute('SELECT * FROM students WHERE id=?',(cur.lastrowid,)).fetchone())

@app.get('/api/students')
def list_students():
    with get_db() as db:
        return [dict(x) for x in db.execute('SELECT s.*,g.name AS group_name FROM students s LEFT JOIN groups_table g ON g.id=s.group_id ORDER BY s.full_name')]

@app.post('/api/assessments')
def create_assessment(data: AssessmentIn):
    with get_db() as db:
        if data.teacher_id is not None and not db.execute('SELECT id FROM teachers WHERE id=?',(data.teacher_id,)).fetchone(): raise HTTPException(404,'Müəllim tapılmadı.')
        cur=db.execute('INSERT INTO assessments(title,module_name,learning_outcome,criterion,teacher_id) VALUES (?,?,?,?,?)',(data.title,data.module_name,data.learning_outcome,data.criterion,data.teacher_id))
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('assessment.created',data.title))
        return dict(db.execute('SELECT * FROM assessments WHERE id=?',(cur.lastrowid,)).fetchone())

@app.get('/api/assessments')
def list_assessments():
    with get_db() as db: return [dict(x) for x in db.execute('SELECT * FROM assessments ORDER BY id DESC')]

@app.post('/api/questions')
def create_question(data: QuestionIn):
    with get_db() as db:
        if not db.execute('SELECT id FROM assessments WHERE id=?',(data.assessment_id,)).fetchone(): raise HTTPException(404,'Qiymətləndirmə tapılmadı.')
        cur=db.execute('INSERT INTO questions(assessment_id,question_no,prompt,question_type,correct_answer,points) VALUES (?,?,?,?,?,?)',(data.assessment_id,data.question_no,data.prompt,data.question_type,data.correct_answer.strip(),data.points))
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('question.created',f'{data.assessment_id}:{data.question_no}'))
        return dict(db.execute('SELECT * FROM questions WHERE id=?',(cur.lastrowid,)).fetchone())

@app.get('/api/questions/{assessment_id}')
def list_questions(assessment_id: int):
    with get_db() as db: return [dict(x) for x in db.execute('SELECT * FROM questions WHERE assessment_id=? ORDER BY question_no',(assessment_id,))]

@app.post('/api/grade')
def grade(data: GradeIn):
    with get_db() as db:
        assessment=db.execute('SELECT title FROM assessments WHERE id=?',(data.assessment_id,)).fetchone()
        if not assessment: raise HTTPException(404,'Qiymətləndirmə tapılmadı.')
        if data.student_id is not None and not db.execute('SELECT id FROM students WHERE id=?',(data.student_id,)).fetchone(): raise HTTPException(404,'Tələbə tapılmadı.')
        qs=[dict(x) for x in db.execute('SELECT * FROM questions WHERE assessment_id=? ORDER BY question_no',(data.assessment_id,))]
        if not qs: raise HTTPException(400,'Bu qiymətləndirmə üçün sual və cavab açarı əlavə edilməyib.')
        result=grade_answers(qs,data.answers)
        review=json.dumps(result['needs_review'],ensure_ascii=False)
        cur=db.execute('INSERT INTO results(assessment_id,student_id,source_file,score,max_score,percent,correct_count,wrong_count,blank_count,needs_review) VALUES (?,?,?,?,?,?,?,?,?,?)',(data.assessment_id,data.student_id,data.source_file,result['score'],result['max_score'],result['percent'],result['correct_count'],result['wrong_count'],result['blank_count'],review))
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('result.graded',f"result_id={cur.lastrowid}; percent={result['percent']}"))
        result['result_id']=cur.lastrowid
        result['assessment_title']=assessment['title']
        return result

@app.post('/api/upload')
async def upload_files(files: list[UploadFile] = File(...)):
    if not files: raise HTTPException(400,'Fayl seçilməyib.')
    if len(files) > MAX_FILES_PER_REQUEST: raise HTTPException(413,f'Bir sorğuda maksimum {MAX_FILES_PER_REQUEST} fayl qəbul olunur.')
    output=[]
    for upload in files:
        # Stream the file with a strict bound, avoiding unbounded read() calls.
        chunks=[]; total=0
        while True:
            chunk=await upload.read(1024*1024)
            if not chunk: break
            total += len(chunk)
            if total > 15*1024*1024:
                raise HTTPException(413,f'{upload.filename}: fayl 15 MB limitini keçir.')
            chunks.append(chunk)
        content=b''.join(chunks)
        try: detected=validate_file(upload.filename or '',content)
        except UnsafeUpload as exc: raise HTTPException(400,f'{upload.filename}: {exc}')
        file_id=uuid4().hex
        ext=Path(upload.filename or '').suffix.lower()
        dest=STORAGE / f'{file_id}{ext}'
        dest.write_bytes(content)
        item={'file_id':file_id,'filename':Path(upload.filename or 'upload').name,'detected_type':detected,'bytes':len(content),'status':'yükləndi','pages':1,'ocr':None}
        if detected == 'application/pdf':
            try:
                item['pages']=pdf_page_count(content)
                item['note']='Səhifələr QR/tələbə kodu əsasında uyğunlaşdırıla bilər; naməlum səhifələr müəllim yoxlamasına göndərilir.'
            except Exception: item['note']='PDF metadatası oxunmadı.'
        else:
            try:
                from PIL import Image
                import io
                image=Image.open(io.BytesIO(content))
                ocr=extract_text(image)
                item['ocr']={'available':ocr.get('available',False),'text_preview':ocr.get('text','')[:2000],'needs_review':ocr.get('needs_review',True),'message':ocr.get('message','')}
            except Exception: item['ocr']={'available':False,'needs_review':True,'message':'Şəkil OCR üçün açıla bilmədi; müəllim yoxlamalıdır.'}
        with get_db() as db: db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('file.uploaded',f'{file_id} type={detected} size={len(content)}'))
        output.append(item)
    return {'count':len(output),'files':output,'warning':'OCR nəticələri qaralama xarakterlidir. Şübhəli cavablar müəllim tərəfindən təsdiqlənməlidir.'}

@app.get('/api/analysis/summary')
def analysis_summary():
    from app.services.assessment_analysis import summarize_results
    return summarize_results(result_rows())

@app.get('/api/reports/results')
def result_rows():
    with get_db() as db:
        rows=db.execute('''SELECT s.student_no,s.full_name AS student_name,a.title AS assessment_title,r.score,r.max_score,r.percent,r.correct_count,r.wrong_count,r.blank_count,r.needs_review,r.approved,r.created_at FROM results r LEFT JOIN students s ON s.id=r.student_id JOIN assessments a ON a.id=r.assessment_id ORDER BY r.created_at DESC''').fetchall()
        output=[dict(x) for x in rows]
        for row in output:
            try:
                pending=json.loads(row.get('needs_review') or '[]')
                row['needs_review']='; '.join(str(q) for q in pending)
            except (ValueError, TypeError):
                row['needs_review']=str(row.get('needs_review') or '')
        return output

@app.get('/api/reports.xlsx')
def excel_report():
    data=result_rows()
    content=make_excel(data)
    return StreamingResponse(BytesIO(content),media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename=qiymetlendirme-hesabati.xlsx'})

@app.get('/api/reports.pdf')
def pdf_report():
    data=result_rows()
    content=make_pdf(data)
    return StreamingResponse(BytesIO(content),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename=qiymetlendirme-hesabati.pdf'})

@app.post('/api/review')
def approve_result(data: ReviewIn):
    with get_db() as db:
        row=db.execute('SELECT id,max_score FROM results WHERE id=?',(data.result_id,)).fetchone()
        if not row: raise HTTPException(404,'Nəticə tapılmadı.')
        if data.approved_score > row['max_score']: raise HTTPException(400,'Təsdiqlənən bal maksimum baldan çox ola bilməz.')
        db.execute('UPDATE results SET score=?,percent=?,approved=1 WHERE id=?',(data.approved_score,round(data.approved_score/row['max_score']*100,2) if row['max_score'] else 0,data.result_id))
        db.execute('INSERT INTO audit_log(event,details) VALUES (?,?)',('result.approved',json.dumps({'result_id':data.result_id,'score':data.approved_score,'note':data.reviewer_note},ensure_ascii=False)))
        return {'status':'təsdiqləndi','result_id':data.result_id,'score':data.approved_score}

@app.post('/api/open-answer-suggestion')
def open_answer_suggestion(payload: dict):
    """Safe demo rubric helper: no external AI call and no final automated grading."""
    answer=str(payload.get('answer','')).strip()
    rubric=str(payload.get('rubric','')).strip()
    if not answer or not rubric: raise HTTPException(400,'Cavab və rubrika daxil edilməlidir.')
    terms=[x.strip(' ,.;:!?()[]').casefold() for x in rubric.replace('\n',',').split(',') if x.strip()]
    found=[x for x in terms if len(x)>2 and x in answer.casefold()]
    return {'mode':'demo_rubric_assistant','suggested_review_points':found,'matched_terms':len(found),'rubric_items':len(terms),'suggestion':'Bu yalnız açar sözlərə əsaslanan ilkin köməkçidir. Məna üzrə qiymətləndirmə deyil. Yekun balı müəllim təsdiqləməlidir.','teacher_approval_required':True}

@app.get('/api/pages/{file_id}')
def list_pdf_pages(file_id: str):
    # Only accept opaque UUID-like IDs generated by this service.
    if not file_id.isalnum() or len(file_id) != 32: raise HTTPException(400,'Fayl identifikatoru düzgün deyil.')
    candidates=list(STORAGE.glob(file_id+'.pdf'))
    if not candidates: raise HTTPException(404,'PDF tapılmadı.')
    try:
        pages=pdf_pages_as_images(candidates[0].read_bytes(), dpi=120)
        decoded=[]
        for i, image in enumerate(pages, start=1):
            identity=decode_student_qr(image)
            decoded.append((i, identity.get('student_code')))
        with get_db() as db:
            known={r['student_no'] for r in db.execute('SELECT student_no FROM students')}
        matched=match_page_identities(decoded, known)
        return {'file_id':file_id,'page_count':len(pages),'pages':[{'page':x.page_number,'student_no':x.student_no,'student_id_status':x.status,'message':x.message,'requires_teacher_confirmation':x.status != 'matched'} for x in matched]}
    except Exception as exc:
        raise HTTPException(400,'PDF səhifələri emal edilə bilmədi.') from exc
