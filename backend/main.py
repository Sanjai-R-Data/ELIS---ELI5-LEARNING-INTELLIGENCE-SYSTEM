from dataclasses import asdict
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.content.pdf_processor import extract_text
from backend.content.source_segments import create_source_segments
from backend.content.text_processor import clean_text
from backend.content.pdf_validator import validate_pdf

from backend.learning.adaptive_engine import (
    get_adaptive_action,
)
from backend.learning.adaptive_executor import (
    execute_adaptive_action,
    generate_adaptive_quiz,
)
from backend.learning.adaptive_loop import (
    run_adaptive_cycle,
)
from backend.learning.analogy import generate_analogy
from backend.learning.class_levels import (
    get_class_level,
    get_class_levels,
)
from backend.learning.explanation import generate_explanation
from backend.learning.glossary import generate_glossary
from backend.learning.learner_state import LearnerState
from backend.learning.learning_progress import (
    record_quiz_result,
)
from backend.learning.mastery import (
    calculate_mastery,
)
from backend.learning.quiz import generate_quiz
from backend.learning.quiz_evaluator import evaluate_answer
from backend.learning.quiz_scoring import calculate_quiz_score
from backend.learning.topic_extractor import extract_topics
from backend.llm.ollama_client import generate_response



BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="ELIS",
    description="ELI5 Intelligent Learning System",
    version="1.8.0",
)


# --------------------------------------------------
# GLOBAL LEARNER STATE
# --------------------------------------------------

learner_state = LearnerState()


# --------------------------------------------------
# IN-MEMORY DOCUMENT STORAGE
# --------------------------------------------------

documents = {}


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class PromptRequest(BaseModel):
    prompt: str


class ClassSelectionRequest(BaseModel):
    class_id: int


class ExplanationRequest(BaseModel):
    class_id: int
    source_text: str
    instruction: str


class DocumentExplanationRequest(BaseModel):
    document_id: str
    class_id: int
    instruction: str = (
        "Explain the main concept from the provided "
        "textbook material in a simple way."
    )


class DocumentTopicsRequest(BaseModel):
    document_id: str
    class_id: int


class DocumentAnalogyRequest(BaseModel):
    document_id: str
    class_id: int
    topic: str


class AnalogyRequest(BaseModel):
    class_id: int
    source_text: str
    concept: str


class GlossaryRequest(BaseModel):
    class_id: int
    source_text: str


class DocumentGlossaryRequest(BaseModel):
    document_id: str
    class_id: int
    topic: str


class DocumentQuizRequest(BaseModel):
    document_id: str
    class_id: int
    topic: str
    number_of_questions: int = 3


class QuizRequest(BaseModel):
    class_id: int
    source_text: str
    topic: str
    number_of_questions: int = 3


class AnswerEvaluationRequest(BaseModel):
    selected_answer: str
    correct_answer: str


class QuizScoreRequest(BaseModel):
    answers: list[dict]


class MasteryRequest(BaseModel):
    score: int
    total: int


class LearningProgressRequest(BaseModel):
    topic: str
    answers: list[dict]


class AdaptiveActionRequest(BaseModel):
    class_id: int
    topic: str
    source_text: str


class AdaptiveQuizRequest(BaseModel):
    class_id: int
    topic: str
    source_text: str


class AdaptiveCycleRequest(BaseModel):
    class_id: int
    topic: str
    source_text: str
    answers: list[dict]


# --------------------------------------------------
# FRONTEND STATIC FILES
# --------------------------------------------------

if FRONTEND_DIR.exists():

    app.mount(
        "/static",
        StaticFiles(
            directory=FRONTEND_DIR
        ),
        name="static",
    )


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==================================================
# DOCUMENT PROCESSING
# ==================================================

@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename was provided.",
        )


    file_extension = Path(
        file.filename
    ).suffix.lower()


    if file_extension != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )


    temporary_path = None


    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temporary_file:

            temporary_path = temporary_file.name

            shutil.copyfileobj(
                file.file,
                temporary_file,
            )


        validation_result = validate_pdf(
            temporary_path
        )


        return {
            "message": (
                "PDF uploaded and validated "
                "successfully."
            ),
            "document": validation_result,
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred "
                "while processing the PDF."
            ),
        ) from error


    finally:

        if temporary_path:

            temporary_file_path = Path(
                temporary_path
            )

            if temporary_file_path.exists():

                temporary_file_path.unlink()


# --------------------------------------------------
# PROCESS PDF
# --------------------------------------------------

@app.post("/documents/process")
async def process_document(
    file: UploadFile = File(...),
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename was provided.",
        )


    file_extension = Path(
        file.filename
    ).suffix.lower()


    if file_extension != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )


    temporary_path = None


    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temporary_file:

            temporary_path = temporary_file.name

            shutil.copyfileobj(
                file.file,
                temporary_file,
            )


        validation_result = validate_pdf(
            temporary_path
        )


        pages = extract_text(
            temporary_path
        )


        cleaned_pages = []


        for page_data in pages:

            cleaned_text = clean_text(
                page_data["text"]
            )


            cleaned_pages.append(
                {
                    "page": page_data["page"],
                    "text": cleaned_text,
                }
            )


        source_segments = create_source_segments(
            cleaned_pages
        )


        document_id = str(
            uuid4()
        )


        documents[document_id] = {

            "document_id": document_id,

            "filename": file.filename,

            "pages": cleaned_pages,

            "segments": source_segments,

            # Topics will be generated later
            # and cached here.
            "topics": None,

        }


        preview_segments = []


        for segment in source_segments[:3]:

            preview_segments.append(
                asdict(segment)
            )


        return {

            "message": (
                "PDF processed successfully."
            ),

            "document": {

                "document_id": document_id,

                "filename": file.filename,

                "pages": validation_result.get(
                    "pages",
                    len(cleaned_pages),
                ),

                "size_mb": validation_result.get(
                    "size_mb",
                    0,
                ),

                "source_segments": len(
                    source_segments
                ),

                "preview": preview_segments,

            },

        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred "
                "while processing the PDF."
            ),
        ) from error


    finally:

        if temporary_path:

            temporary_file_path = Path(
                temporary_path
            )

            if temporary_file_path.exists():

                temporary_file_path.unlink()


# --------------------------------------------------
# GET PROCESSED DOCUMENT
# --------------------------------------------------

@app.get("/documents/{document_id}")
def get_document(
    document_id: str,
):

    document = documents.get(
        document_id
    )


    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    return {

        "document_id": document_id,

        "filename": document["filename"],

        "pages": len(
            document["pages"]
        ),

        "source_segments": len(
            document["segments"]
        ),

        "topics_available":
            document.get("topics") is not None,

    }


# --------------------------------------------------
# GET SOURCE CONTENT FOR LEARNING
# --------------------------------------------------

@app.get(
    "/documents/{document_id}/source"
)
def get_document_source(
    document_id: str,
):

    document = documents.get(
        document_id
    )


    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    segments = document["segments"]


    if not segments:

        raise HTTPException(
            status_code=404,
            detail=(
                "No source content was found "
                "for this document."
            ),
        )


    source_text_parts = []


    for segment in segments:

        source_text_parts.append(
            segment.text
        )


    source_text = "\n\n".join(
        source_text_parts
    )


    return {

        "document_id": document_id,

        "filename": document["filename"],

        "source_text": source_text,

        "segments": len(segments),

    }


# ==================================================
# AI
# ==================================================

@app.post("/ai/generate")
def generate_ai_response(
    request: PromptRequest,
):

    response = generate_response(
        request.prompt
    )


    return {
        "response": response,
    }


# ==================================================
# CLASS LEVELS
# ==================================================

@app.get("/classes")
def get_classes():

    return {
        "classes": get_class_levels(),
    }


@app.post("/classes/select")
def select_class(
    request: ClassSelectionRequest,
):

    try:

        selected_class = get_class_level(
            request.class_id
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Unsupported class level.",
        )


    return {

        "message":
            "Class selected successfully.",

        "selected_class":
            selected_class,

    }


# ==================================================
# TOPIC EXTRACTION
# ==================================================

@app.post(
    "/ai/topics/document"
)
def get_document_topics(
    request: DocumentTopicsRequest,
):

    document = documents.get(
        request.document_id
    )


    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    # --------------------------------------------------
    # RETURN CACHED TOPICS
    # --------------------------------------------------

    cached_topics = document.get(
        "topics"
    )


    if cached_topics is not None:

        return {

            "document_id":
                request.document_id,

            "filename":
                document["filename"],

            "topics":
                cached_topics,

            "cached":
                True,

        }


    # --------------------------------------------------
    # GET SOURCE SEGMENTS
    # --------------------------------------------------

    segments = document["segments"]


    if not segments:

        raise HTTPException(
            status_code=404,
            detail=(
                "No source content was found "
                "for this document."
            ),
        )


    # --------------------------------------------------
    # COMBINE SOURCE SEGMENTS
    # --------------------------------------------------

    source_text_parts = []


    for segment in segments:

        if segment.text.strip():

            source_text_parts.append(
                segment.text
            )


    source_text = "\n\n".join(
        source_text_parts
    )


    if not source_text.strip():

        raise HTTPException(
            status_code=404,
            detail=(
                "The document contains no "
                "usable source text."
            ),
        )


    # --------------------------------------------------
    # EXTRACT TOPICS
    # --------------------------------------------------

    try:

        topics = extract_topics(
            class_id=request.class_id,
            source_text=source_text,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    # --------------------------------------------------
    # CACHE TOPICS
    # --------------------------------------------------

    document["topics"] = topics


    # --------------------------------------------------
    # RETURN TOPICS
    # --------------------------------------------------

    return {

        "document_id":
            request.document_id,

        "filename":
            document["filename"],

        "topics":
            topics,

        "cached":
            False,

    }


# ==================================================
# LEARNING
# ==================================================

@app.post("/ai/explain")
def explain_source(
    request: ExplanationRequest,
):

    try:

        result = generate_explanation(
            class_id=request.class_id,
            source_text=request.source_text,
            instruction=request.instruction,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


# --------------------------------------------------
# DOCUMENT-BASED EXPLANATION
# --------------------------------------------------

@app.post(
    "/ai/explain/document"
)
def explain_document(
    request: DocumentExplanationRequest,
):

    document = documents.get(
        request.document_id
    )


    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    segments = document["segments"]


    if not segments:

        raise HTTPException(
            status_code=404,
            detail=(
                "No source content was found "
                "for this document."
            ),
        )


    source_text_parts = []


    for segment in segments:

        source_text_parts.append(
            segment.text
        )


    source_text = "\n\n".join(
        source_text_parts
    )


    try:

        result = generate_explanation(
            class_id=request.class_id,
            source_text=source_text,
            instruction=request.instruction,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return {

        "document_id":
            request.document_id,

        "filename":
            document["filename"],

        "explanation":
            result,

    }


# --------------------------------------------------
# DOCUMENT-BASED ANALOGY
# --------------------------------------------------

@app.post(
    "/ai/analogy/document"
)
def create_document_analogy(
    request: DocumentAnalogyRequest,
):

    document = documents.get(
        request.document_id
    )


    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    if not request.topic.strip():

        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )


    segments = document["segments"]


    if not segments:

        raise HTTPException(
            status_code=404,
            detail=(
                "No source content was found "
                "for this document."
            ),
        )


    source_text_parts = []


    for segment in segments:

        if segment.text.strip():

            source_text_parts.append(
                segment.text
            )


    source_text = "\n\n".join(
        source_text_parts
    )


    if not source_text.strip():

        raise HTTPException(
            status_code=404,
            detail=(
                "The document contains no "
                "usable source text."
            ),
        )


    try:

        result = generate_analogy(
            class_id=request.class_id,
            source_text=source_text,
            concept=request.topic,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return {

        "document_id":
            request.document_id,

        "filename":
            document["filename"],

        "topic":
            request.topic,

        "analogy":
            result,

    }


# --------------------------------------------------
# ANALOGY
# --------------------------------------------------

@app.post("/ai/analogy")
def create_analogy(
    request: AnalogyRequest,
):

    try:

        result = generate_analogy(
            class_id=request.class_id,
            source_text=request.source_text,
            concept=request.concept,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


# --------------------------------------------------
# GLOSSARY
# --------------------------------------------------

@app.post("/ai/glossary")
def create_glossary(
    request: GlossaryRequest,
):

    try:

        result = generate_glossary(
            class_id=request.class_id,
            source_text=request.source_text,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


# --------------------------------------------------
# DOCUMENT-BASED GLOSSARY
# --------------------------------------------------

@app.post(
    "/ai/glossary/document"
)
def create_document_glossary(
    request: DocumentGlossaryRequest,
):

    document = documents.get(
        request.document_id
    )


    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )


    if not request.topic.strip():

        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )


    segments = document["segments"]


    if not segments:

        raise HTTPException(
            status_code=404,
            detail=(
                "No source content was found "
                "for this document."
            ),
        )


    source_text_parts = []


    for segment in segments:

        if segment.text.strip():

            source_text_parts.append(
                segment.text
            )


    source_text = "\n\n".join(
        source_text_parts
    )


    if not source_text.strip():

        raise HTTPException(
            status_code=404,
            detail=(
                "The document contains no "
                "usable source text."
            ),
        )


    try:

        result = generate_glossary(
            class_id=request.class_id,
            source_text=source_text,
            topic=request.topic,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return {

        "document_id":
            request.document_id,

        "filename":
            document["filename"],

        "topic":
            request.topic,

        "glossary":
            result,

    }


# --------------------------------------------------
# DOCUMENT-BASED QUIZ
# --------------------------------------------------

@app.post("/ai/quiz/document")
def create_document_quiz(
    request: DocumentQuizRequest,
):

    document = documents.get(
        request.document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if not request.topic.strip():
        raise HTTPException(
            status_code=400,
            detail="Topic cannot be empty.",
        )

    if request.number_of_questions < 1 or request.number_of_questions > 10:
        raise HTTPException(
            status_code=400,
            detail="Number of questions must be between 1 and 10.",
        )

    segments = document["segments"]

    if not segments:
        raise HTTPException(
            status_code=404,
            detail="No source content was found for this document.",
        )

    source_text_parts = []

    for segment in segments:
        if segment.text.strip():
            source_text_parts.append(segment.text)

    source_text = "\n\n".join(source_text_parts)

    if not source_text.strip():
        raise HTTPException(
            status_code=404,
            detail="The document contains no usable source text.",
        )

    try:
        result = generate_quiz(
            class_id=request.class_id,
            source_text=source_text,
            topic=request.topic,
            number_of_questions=request.number_of_questions,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return {
        "document_id": request.document_id,
        "filename": document["filename"],
        "topic": request.topic,
        "quiz": result,
    }


# --------------------------------------------------
# QUIZ
# --------------------------------------------------

@app.post("/ai/quiz")
def create_quiz(
    request: QuizRequest,
):

    try:

        result = generate_quiz(
            class_id=request.class_id,
            source_text=request.source_text,
            topic=request.topic,
            number_of_questions=request.number_of_questions,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


# ==================================================
# QUIZ
# ==================================================

@app.post("/quiz/evaluate")
def evaluate_quiz_answer(
    request: AnswerEvaluationRequest,
):

    try:

        result = evaluate_answer(
            selected_answer=request.selected_answer,
            correct_answer=request.correct_answer,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


@app.post("/quiz/score")
def score_quiz(
    request: QuizScoreRequest,
):

    try:

        result = calculate_quiz_score(
            answers=request.answers,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


# ==================================================
# MASTERY
# ==================================================

@app.post("/mastery")
def calculate_mastery_result(
    request: MasteryRequest,
):

    try:

        result = calculate_mastery(
            score=request.score,
            total=request.total,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return result


# ==================================================
# LEARNER PROGRESS
# ==================================================

@app.post("/learner/progress")
def record_learning_progress(
    request: LearningProgressRequest,
):

    try:

        result = record_quiz_result(
            learner=learner_state,
            topic=request.topic,
            answers=request.answers,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


@app.get("/learner/progress")
def get_learning_progress():

    return {
        "topics":
            learner_state.get_all_topics(),
    }


# ==================================================
# ADAPTIVE LEARNING
# ==================================================

@app.get(
    "/learner/adaptive/{topic}"
)
def get_adaptive_recommendation(
    topic: str,
):

    try:

        result = get_adaptive_action(
            learner=learner_state,
            topic=topic,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


    return result


@app.post(
    "/learner/adaptive/action"
)
def execute_adaptive_learning_action(
    request: AdaptiveActionRequest,
):

    try:

        result = execute_adaptive_action(
            learner=learner_state,
            class_id=request.class_id,
            topic=request.topic,
            source_text=request.source_text,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


@app.post(
    "/learner/adaptive/quiz"
)
def create_adaptive_quiz(
    request: AdaptiveQuizRequest,
):

    try:

        result = generate_adaptive_quiz(
            learner=learner_state,
            class_id=request.class_id,
            topic=request.topic,
            source_text=request.source_text,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result


@app.post(
    "/learner/adaptive/cycle"
)
def run_complete_adaptive_cycle(
    request: AdaptiveCycleRequest,
):

    try:

        result = run_adaptive_cycle(
            learner=learner_state,
            class_id=request.class_id,
            topic=request.topic,
            source_text=request.source_text,
            answers=request.answers,
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return result