

let selectedFile = null;

let currentDocumentId = null;

let selectedClassId = null;

let topics = [];

let selectedTopic = null;

let currentQuiz = [];
let currentQuizIndex = 0;
let quizAnswers = [];
let selectedQuizAnswer = null;
let quizAnswerLocked = false;




const fileInput =
    document.getElementById(
        "fileInput"
    );


const chooseButton =
    document.getElementById(
        "chooseButton"
    );


const uploadCard =
    document.getElementById(
        "uploadCard"
    );


const fileCard =
    document.getElementById(
        "fileCard"
    );


const fileName =
    document.getElementById(
        "fileName"
    );


const fileSize =
    document.getElementById(
        "fileSize"
    );


const status =
    document.getElementById(
        "status"
    );


const readyCard =
    document.getElementById(
        "readyCard"
    );


const startButton =
    document.getElementById(
        "startButton"
    );


const classOptions =
    document.getElementById(
        "classOptions"
    );


const continueButton =
    document.getElementById(
        "continueButton"
    );


const selectedClassTitle =
    document.getElementById(
        "selectedClassTitle"
    );


const dashboardTitle =
    document.getElementById(
        "dashboardTitle"
    );


const dashboardFileName =
    document.getElementById(
        "dashboardFileName"
    );


const explainButton =
    document.getElementById(
        "explainButton"
    );


const analogyButton =
    document.getElementById(
        "analogyButton"
    );


const glossaryButton =
    document.getElementById(
        "glossaryButton"
    );


const quizButton =
    document.getElementById(
        "quizButton"
    );


const topicsStatus =
    document.getElementById("topicsStatus");


const topicList =
    document.getElementById("topicList");


const selectedTopicElement =
    document.getElementById("selectedTopic");


const learningActions =
    document.getElementById("learningActions");


const explanationCard =
    document.getElementById(
        "explanationCard"
    );


const backToDashboardButton =
    document.getElementById(
        "backToDashboardButton"
    );


const analogyCard =
    document.getElementById(
        "analogyCard"
    );


const backFromAnalogyButton =
    document.getElementById(
        "backFromAnalogyButton"
    );


const glossaryCard =
    document.getElementById(
        "glossaryCard"
    );


const backFromGlossaryButton =
    document.getElementById(
        "backFromGlossaryButton"
    );


const quizCard =
    document.getElementById(
        "quizCard"
    );


const backFromQuizButton =
    document.getElementById(
        "backFromQuizButton"
    );


/* =========================================
   CONFIG
========================================== */

const MAX_FILE_SIZE =
    20 * 1024 * 1024;


/* =========================================
   SCREEN SWITCHING
========================================== */

function showScreen(screenId) {

    document
        .querySelectorAll(".screen")
        .forEach(
            screen => {

                screen.classList.remove(
                    "active"
                );

            }
        );


    document
        .getElementById(screenId)
        .classList.add(
            "active"
        );

}


/* =========================================
   CHOOSE FILE
========================================== */

chooseButton.addEventListener(
    "click",
    () => {

        fileInput.click();

    }
);


fileInput.addEventListener(
    "change",
    () => {

        const file =
            fileInput.files[0];


        if (!file) {
            return;
        }


        handleFile(file);

    }
);


function handleFile(file) {

    clearStatus();


    const isPdf =
        file.type ===
            "application/pdf"
        ||
        file.name
            .toLowerCase()
            .endsWith(".pdf");


    if (!isPdf) {

        showStatus(
            "Please select a PDF file.",
            "error"
        );

        return;
    }


    if (
        file.size >
        MAX_FILE_SIZE
    ) {

        showStatus(
            "The PDF is larger than the 20 MB limit.",
            "error"
        );

        return;
    }


    selectedFile = file;


    fileName.textContent =
        file.name;


    fileSize.textContent =
        formatFileSize(
            file.size
        );


    fileCard.classList.add(
        "visible"
    );


    processPdf();

}


async function processPdf() {

    if (!selectedFile) {
        return;
    }


    chooseButton.disabled = true;


    showStatus(
        "Preparing your textbook... This may take a moment.",
        "processing"
    );


    const formData =
        new FormData();


    formData.append(
        "file",
        selectedFile
    );


    try {

        const response =
            await fetch(
                "/documents/process",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail
                ||
                "Failed to process the PDF."
            );

        }


        currentDocumentId =
            data.document.document_id;


        showStatus(
            "Your textbook has been processed successfully.",
            "success"
        );


        readyCard.classList.add(
            "visible"
        );


    } catch (error) {

        console.error(
            error
        );


        showStatus(
            error.message
            ||
            "Something went wrong.",
            "error"
        );


    } finally {

        chooseButton.disabled =
            false;

    }

}



startButton.addEventListener(
    "click",
    async () => {

        if (!currentDocumentId) {
            return;
        }


        showScreen(
            "setupScreen"
        );


        await loadClasses();

    }
);



async function loadClasses() {

    classOptions.innerHTML =
        "<p>Loading learning levels...</p>";


    try {

        const response =
            await fetch(
                "/classes"
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail
                ||
                "Unable to load class levels."
            );

        }


        renderClasses(
            data.classes
        );


    } catch (error) {

        console.error(
            error
        );


        classOptions.innerHTML =
            `
                <p style="color:#c62828;">
                    Failed to load learning levels.
                </p>
            `;

    }

}



function renderClasses(classes) {

    classOptions.innerHTML = "";


    classes.forEach(
        learningClass => {

            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.className =
                "class-option";


            button.innerHTML =
                `
                    <div class="class-number">
                        ${learningClass.name}
                    </div>

                    <div class="class-label">
                        Learning Level
                    </div>
                `;


            button.addEventListener(
                "click",
                () => {

                    selectClass(
                        learningClass,
                        button
                    );

                }
            );


            classOptions.appendChild(
                button
            );

        }
    );

}



function selectClass(
    learningClass,
    button
) {

    document
        .querySelectorAll(
            ".class-option"
        )
        .forEach(
            option => {

                option.classList.remove(
                    "selected"
                );

            }
        );


    button.classList.add(
        "selected"
    );


    selectedClassId =
        learningClass.id;


    selectedClassTitle.textContent =
        learningClass.name;


    continueButton.disabled =
        false;

}


continueButton.addEventListener(
    "click",
    async () => {

        if (
            selectedClassId ===
            null
        ) {
            return;
        }


        try {

            const response =
                await fetch(
                    "/classes/select",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                {
                                    class_id:
                                        selectedClassId
                                }
                            )
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail
                    ||
                    "Unable to select class."
                );

            }


            selectedClassTitle.textContent =
                data.selected_class.name;


            dashboardFileName.textContent =
                selectedFile
                    ? selectedFile.name
                    : "Your textbook";


            showScreen(
                "learningScreen"
            );


            resetTopicSelection();


            await loadTopics();


        } catch (error) {

            console.error(
                error
            );


            alert(
                error.message
            );

        }

    }
);


/* =========================================
   TOPICS
========================================== */

async function loadTopics() {

    if (
        !currentDocumentId ||
        selectedClassId === null
    ) {
        return;
    }


    resetTopicSelection();


    topicsStatus.textContent =
        "🧠 ELIS is identifying the main topics in your textbook...";


    try {

        const response =
            await fetch(
                "/ai/topics/document",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        document_id:
                            currentDocumentId,

                        class_id:
                            selectedClassId
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to load textbook topics."
            );

        }


        topics =
            Array.isArray(
                data.topics
            )
                ? data.topics
                : [];


        if (topics.length === 0) {

            topicsStatus.textContent =
                "No learning topics were found in this textbook.";

            return;

        }


        topicsStatus.style.display =
            "none";


        renderTopics(
            topics
        );


    } catch (error) {

        console.error(
            "Topic loading error:",
            error
        );


        topicsStatus.style.display =
            "block";


        topicsStatus.textContent =
            error.message ||
            "Something went wrong while loading topics.";

    }

}


function renderTopics(topicItems) {

    topicList.innerHTML = "";


    topicItems.forEach(
        topic => {

            const button =
                document.createElement(
                    "button"
                );


            button.type =
                "button";


            button.className =
                "topic-card";


            button.dataset.topicId =
                topic.id;


            button.innerHTML =
                `
                    <div class="topic-title">
                        ${escapeHtml(
                            topic.title ||
                            "Untitled topic"
                        )}
                    </div>

                    <div class="topic-description">
                        ${escapeHtml(
                            topic.description ||
                            "Learn this topic from your textbook."
                        )}
                    </div>
                `;


            button.addEventListener(
                "click",
                () => {

                    selectTopic(
                        topic,
                        button
                    );

                }
            );


            topicList.appendChild(
                button
            );

        }
    );

}


function selectTopic(
    topic,
    button
) {

    document
        .querySelectorAll(
            ".topic-card"
        )
        .forEach(
            card => {

                card.classList.remove(
                    "selected"
                );

            }
        );


    button.classList.add(
        "selected"
    );


    selectedTopic =
        topic;


    selectedTopicElement.innerHTML =
        `
            <strong>Selected topic:</strong>
            ${escapeHtml(
                topic.title ||
                "Untitled topic"
            )}
        `;


    selectedTopicElement.classList.add(
        "visible"
    );


    enableLearningActions();

}


function resetTopicSelection() {

    selectedTopic = null;

    topics = [];

    topicList.innerHTML = "";


    topicsStatus.style.display =
        "block";


    topicsStatus.textContent =
        "🧠 Loading topics from your textbook...";


    selectedTopicElement.innerHTML =
        "";


    selectedTopicElement.classList.remove(
        "visible"
    );


    disableLearningActions();

}


function enableLearningActions() {

    learningActions.classList.remove(
        "disabled-actions"
    );


    explainButton.disabled =
        false;


    analogyButton.disabled =
        false;


    glossaryButton.disabled =
        false;


    quizButton.disabled =
        false;

}


function disableLearningActions() {

    learningActions.classList.add(
        "disabled-actions"
    );


    explainButton.disabled =
        true;


    analogyButton.disabled =
        true;


    glossaryButton.disabled =
        true;


    quizButton.disabled =
        true;

}



explainButton.addEventListener(
    "click",
    async () => {

        if (!currentDocumentId) {

            alert(
                "No processed document is available."
            );

            return;

        }


        if (
            selectedClassId ===
            null
        ) {

            alert(
                "Please select a learning level first."
            );

            return;

        }


        if (!selectedTopic) {

            alert(
                "Please select a topic first."
            );

            return;

        }


        showScreen(
            "explanationScreen"
        );


        showExplanationLoading();


        await generateDocumentExplanation();

    }
);



async function generateDocumentExplanation() {

    try {

        const response =
            await fetch(
                "/ai/explain/document",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                document_id:
                                    currentDocumentId,

                                class_id:
                                    selectedClassId,

                                instruction:
                                    selectedTopic
                                        ? `Explain the topic "${selectedTopic.title}" from this textbook material in a simple, clear and easy-to-understand way for the student. Focus specifically on this selected topic and do not choose a different topic.`
                                        : "Explain the main concepts from this textbook material in a simple, clear and easy-to-understand way for the student."
                            }
                        )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail
                ||
                "Failed to generate the explanation."
            );

        }


        renderExplanation(
            data.explanation
        );


    } catch (error) {

        console.error(
            "Explanation error:",
            error
        );


        renderExplanationError(
            error.message
            ||
            "Something went wrong while generating the explanation."
        );

    }

}


function showExplanationLoading() {

    explanationCard.innerHTML =
        `
            <div class="explanation-loading">

                <div class="loading-icon">
                    🧠
                </div>

                <div>
                    ELIS is thinking...
                </div>

                <div
                    style="
                        font-size:13px;
                        margin-top:6px;
                    "
                >
                    Creating a simple,
                    source-grounded explanation.
                </div>

            </div>
        `;

}


function renderExplanation(
    explanation
) {

    const title =
        escapeHtml(
            explanation.title
            ||
            "Explanation"
        );


    const simpleExplanation =
        escapeHtml(
            explanation.simple_explanation
            ||
            ""
        );


    const simpleExample =
        escapeHtml(
            explanation.simple_example
            ||
            ""
        );


    const keyPoints =
        Array.isArray(
            explanation.key_points
        )
            ? explanation.key_points
            : [];


    const importantTerms =
        Array.isArray(
            explanation.important_terms
        )
            ? explanation.important_terms
            : [];


    const keyPointsHtml =
        keyPoints
            .map(
                point =>
                    `
                        <li>
                            ${escapeHtml(point)}
                        </li>
                    `
            )
            .join("");


    const termsHtml =
        importantTerms
            .map(
                item =>
                    `
                        <div class="term">

                            <div class="term-name">
                                ${escapeHtml(
                                    item.term
                                    ||
                                    ""
                                )}
                            </div>

                            <div class="term-meaning">
                                ${escapeHtml(
                                    item.meaning
                                    ||
                                    ""
                                )}
                            </div>

                        </div>
                    `
            )
            .join("");


    explanationCard.innerHTML =
        `
            <div class="explanation-label">
                Simple Explanation
            </div>

            <div class="explanation-title">
                ${title}
            </div>


            <div class="section-heading">
                💡 In simple words
            </div>

            <div class="simple-explanation">
                ${simpleExplanation}
            </div>


            ${
                keyPoints.length > 0
                    ? `
                        <div class="section-heading">
                            🔑 Key Points
                        </div>

                        <ul class="key-points">
                            ${keyPointsHtml}
                        </ul>
                    `
                    : ""
            }


            ${
                simpleExample
                    ? `
                        <div class="section-heading">
                            🌱 Simple Example
                        </div>

                        <div class="example-box">
                            ${simpleExample}
                        </div>
                    `
                    : ""
            }


            ${
                importantTerms.length > 0
                    ? `
                        <div class="section-heading">
                            📖 Important Terms
                        </div>

                        <div class="terms">
                            ${termsHtml}
                        </div>
                    `
                    : ""
            }

        `;

}


function renderExplanationError(
    message
) {

    explanationCard.innerHTML =
        `
            <div class="explanation-error">

                <strong>
                    We couldn't generate the explanation.
                </strong>

                <br><br>

                ${escapeHtml(message)}

            </div>
        `;

}


backToDashboardButton.addEventListener(
    "click",
    () => {

        showScreen(
            "learningScreen"
        );

    }
);



glossaryButton.addEventListener(
    "click",
    async () => {

        if (!currentDocumentId) {

            alert(
                "No processed document is available."
            );

            return;

        }


        if (selectedClassId === null) {

            alert(
                "Please select a learning level first."
            );

            return;

        }


        if (!selectedTopic) {

            alert(
                "Please select a topic first."
            );

            return;

        }


        showScreen(
            "glossaryScreen"
        );


        showGlossaryLoading();


        await generateDocumentGlossary();

    }
);


async function generateDocumentGlossary() {

    try {

        const response =
            await fetch(
                "/ai/glossary/document",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                document_id:
                                    currentDocumentId,

                                class_id:
                                    selectedClassId,

                                topic:
                                    selectedTopic.title
                            }
                        )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail
                ||
                "Failed to generate the glossary."
            );

        }


        renderGlossary(
            data.glossary
        );


    } catch (error) {

        console.error(
            "Glossary error:",
            error
        );


        renderGlossaryError(
            error.message
            ||
            "Something went wrong while generating the glossary."
        );

    }

}


function showGlossaryLoading() {

    glossaryCard.innerHTML =
        `
            <div class="glossary-loading">

                <div class="loading-icon">
                    📖
                </div>

                <div>
                    ELIS is creating your glossary...
                </div>

                <div
                    style="
                        font-size:13px;
                        margin-top:6px;
                    "
                >
                    Finding the important terms
                    for your selected topic.
                </div>

            </div>
        `;

}


function renderGlossary(result) {

    const glossaryData =
        result && result.glossary
            ? result.glossary
            : {};


    const terms =
        Array.isArray(
            glossaryData.terms
        )
            ? glossaryData.terms
            : [];


    if (terms.length === 0) {

        renderGlossaryError(
            "No glossary terms were returned."
        );

        return;

    }


    const termsHtml =
        terms
            .map(
                item =>
                    `
                        <div class="glossary-item">

                            <div class="glossary-term">
                                ${escapeHtml(
                                    item.term
                                    ||
                                    "Untitled term"
                                )}
                            </div>

                            <div class="glossary-definition">
                                ${escapeHtml(
                                    item.definition
                                    ||
                                    "No definition was returned."
                                )}
                            </div>

                        </div>
                    `
            )
            .join("");


    glossaryCard.innerHTML =
        `
            <div class="explanation-label">
                Selected Topic
            </div>

            <div class="glossary-title">
                ${escapeHtml(
                    selectedTopic
                        ? selectedTopic.title
                        : "Glossary"
                )}
            </div>

            <div class="section-heading">
                📖 Important Terms
            </div>

            <div class="glossary-list">
                ${termsHtml}
            </div>
        `;

}


function renderGlossaryError(
    message
) {

    glossaryCard.innerHTML =
        `
            <div class="explanation-error">

                <strong>
                    We couldn't generate the glossary.
                </strong>

                <br><br>

                ${escapeHtml(message)}

            </div>
        `;

}


backFromGlossaryButton.addEventListener(
    "click",
    () => {

        showScreen(
            "learningScreen"
        );

    }
);



analogyButton.addEventListener(
    "click",
    async () => {

        if (!currentDocumentId) {

            alert(
                "No processed document is available."
            );

            return;

        }


        if (
            selectedClassId ===
            null
        ) {

            alert(
                "Please select a learning level first."
            );

            return;

        }


        if (!selectedTopic) {

            alert(
                "Please select a topic first."
            );

            return;

        }


        showScreen(
            "analogyScreen"
        );


        showAnalogyLoading();


        await generateDocumentAnalogy();

    }
);


async function generateDocumentAnalogy() {

    try {

        const response =
            await fetch(
                "/ai/analogy/document",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            {
                                document_id:
                                    currentDocumentId,

                                class_id:
                                    selectedClassId,

                                topic:
                                    selectedTopic.title
                            }
                        )
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail
                ||
                "Failed to generate the analogy."
            );

        }


        renderAnalogy(
            data.analogy
        );


    } catch (error) {

        console.error(
            "Analogy error:",
            error
        );


        renderAnalogyError(
            error.message
            ||
            "Something went wrong while generating the analogy."
        );

    }

}


function showAnalogyLoading() {

    analogyCard.innerHTML =
        `
            <div class="analogy-loading">

                <div class="loading-icon">
                    💡
                </div>

                <div>
                    ELIS is creating an analogy...
                </div>

                <div
                    style="
                        font-size:13px;
                        margin-top:6px;
                    "
                >
                    Creating a simple,
                    source-grounded comparison.
                </div>

            </div>
        `;

}


function renderAnalogy(result) {

    const mapping =
        Array.isArray(result.mapping)
            ? result.mapping
            : [];


    const mappingHtml =
        mapping.length > 0
            ? `
                <div class="section-heading">
                    🔗 How the analogy maps
                </div>

                <div class="mapping-list">

                    ${mapping.map(
                        item =>
                            `
                                <div class="mapping-item">

                                    <div class="mapping-label">
                                        Concept
                                    </div>

                                    <div class="mapping-value">
                                        ${escapeHtml(
                                            item.concept_part
                                            ||
                                            ""
                                        )}
                                    </div>

                                    <div
                                        class="mapping-label"
                                        style="margin-top:10px;"
                                    >
                                        Analogy
                                    </div>

                                    <div class="mapping-value">
                                        ${escapeHtml(
                                            item.analogy_part
                                            ||
                                            ""
                                        )}
                                    </div>

                                </div>
                            `
                    ).join("")}

                </div>
            `
            : "";


    analogyCard.innerHTML =
        `
            <div class="explanation-label">
                Selected Topic
            </div>

            <div class="analogy-title">
                ${escapeHtml(
                    result.concept
                    ||
                    selectedTopic.title
                )}
            </div>

            <div class="section-heading">
                💡 The Analogy
            </div>

            <div class="analogy-main">
                ${escapeHtml(
                    result.analogy
                    ||
                    "No analogy was returned."
                )}
            </div>

            ${mappingHtml}

            ${
                result.why_it_helps
                    ? `
                        <div class="section-heading">
                            🧠 Why this helps
                        </div>

                        <div class="example-box">
                            ${escapeHtml(
                                result.why_it_helps
                            )}
                        </div>
                    `
                    : ""
            }
        `;

}


function renderAnalogyError(
    message
) {

    analogyCard.innerHTML =
        `
            <div class="explanation-error">

                <strong>
                    We couldn't generate the analogy.
                </strong>

                <br><br>

                ${escapeHtml(message)}

            </div>
        `;

}


backFromAnalogyButton.addEventListener(
    "click",
    () => {

        showScreen(
            "learningScreen"
        );

    }
);


quizButton.addEventListener(
    "click",
    async () => {

        if (!currentDocumentId) {

            alert(
                "No processed document is available."
            );

            return;

        }


        if (selectedClassId === null) {

            alert(
                "Please select a learning level first."
            );

            return;

        }


        if (!selectedTopic) {

            alert(
                "Please select a topic first."
            );

            return;

        }


        showScreen(
            "quizScreen"
        );


        showQuizLoading();


        await generateDocumentQuiz();

    }
);


async function generateDocumentQuiz() {

    try {

        const response =
            await fetch(
                "/ai/quiz/document",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        document_id:
                            currentDocumentId,

                        class_id:
                            selectedClassId,

                        topic:
                            selectedTopic.title,

                        number_of_questions:
                            3

                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to generate the quiz."
            );

        }


        const quizData =
            data.quiz &&
            data.quiz.quiz
                ? data.quiz.quiz
                : data.quiz;


        currentQuiz =
            Array.isArray(
                quizData.questions
            )
                ? quizData.questions
                : [];


        if (currentQuiz.length === 0) {

            throw new Error(
                "No quiz questions were returned."
            );

        }


        currentQuizIndex = 0;

        quizAnswers = [];

        selectedQuizAnswer = null;

        quizAnswerLocked = false;


        renderQuizQuestion();


    } catch (error) {

        console.error(
            "Quiz error:",
            error
        );


        renderQuizError(
            error.message ||
            "Something went wrong while generating the quiz."
        );

    }

}


function showQuizLoading() {

    quizCard.innerHTML = `
        <div class="quiz-loading">

            <div
                style="
                    font-size:32px;
                    margin-bottom:10px;
                "
            >
                📝
            </div>

            <div>
                ELIS is preparing your quiz...
            </div>

            <div
                style="
                    font-size:13px;
                    margin-top:6px;
                "
            >
                Creating questions for your selected topic.
            </div>

        </div>
    `;

}


function renderQuizQuestion() {

    const question =
        currentQuiz[
            currentQuizIndex
        ];


    selectedQuizAnswer = null;

    quizAnswerLocked = false;


    const optionsHtml =
        question.options
            .map(
                (
                    option,
                    index
                ) =>
                    `
                        <button
                            class="quiz-option"
                            type="button"
                            data-option-index="${index}"
                        >
                            <strong>
                                ${String.fromCharCode(
                                    65 + index
                                )}.
                            </strong>

                            ${escapeHtml(option)}

                        </button>
                    `
            )
            .join("");


    quizCard.innerHTML = `
        <div class="quiz-progress">
            Question
            ${currentQuizIndex + 1}
            of
            ${currentQuiz.length}
        </div>

        <div class="explanation-label">
            Selected Topic
        </div>

        <div
            class="quiz-progress"
            style="margin-bottom:18px;"
        >
            ${escapeHtml(
                selectedTopic.title
            )}
        </div>

        <div class="quiz-question">
            ${escapeHtml(
                question.question
            )}
        </div>

        <div
            class="quiz-options"
            id="quizOptions"
        >
            ${optionsHtml}
        </div>

        <div id="quizFeedback"></div>

        <div class="quiz-controls">

            <button
                class="quiz-button"
                id="quizNextButton"
                type="button"
                disabled
            >
                ${
                    currentQuizIndex ===
                    currentQuiz.length - 1

                        ? "Finish Quiz"

                        : "Next Question →"
                }
            </button>

        </div>
    `;


    document
        .querySelectorAll(
            ".quiz-option"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        selectQuizOption(
                            button
                        )
                );

            }
        );


    document
        .getElementById(
            "quizNextButton"
        )
        .addEventListener(
            "click",
            handleQuizNext
        );

}


async function selectQuizOption(
    button
) {

    if (quizAnswerLocked) {
        return;
    }


    quizAnswerLocked = true;


    const optionIndex =
        Number(
            button.dataset.optionIndex
        );


    selectedQuizAnswer =
        currentQuiz[
            currentQuizIndex
        ].options[
            optionIndex
        ];


    const question =
        currentQuiz[
            currentQuizIndex
        ];


    document
        .querySelectorAll(
            ".quiz-option"
        )
        .forEach(
            optionButton => {

                optionButton.disabled =
                    true;

            }
        );


    let evaluation = null;


    try {

        const response =
            await fetch(
                "/quiz/evaluate",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            selected_answer:
                                selectedQuizAnswer,

                            correct_answer:
                                question.correct_answer

                        })
                }
            );


        evaluation =
            await response.json();


    } catch (error) {

        console.error(
            "Quiz evaluation error:",
            error
        );

    }


    const correct =
        evaluation &&
        typeof evaluation.is_correct === "boolean"

            ? evaluation.is_correct

            : selectedQuizAnswer ===
              question.correct_answer;


    button.classList.add(
        correct
            ? "correct"
            : "incorrect"
    );


    if (!correct) {

        document
            .querySelectorAll(
                ".quiz-option"
            )
            .forEach(
                optionButton => {

                    const index =
                        Number(
                            optionButton
                                .dataset
                                .optionIndex
                        );


                    if (
                        question.options[index] ===
                        question.correct_answer
                    ) {

                        optionButton.classList.add(
                            "correct"
                        );

                    }

                }
            );

    }


    quizAnswers[
        currentQuizIndex
    ] = {

        question:
            question.question,

        selected_answer:
            selectedQuizAnswer,

        correct_answer:
            question.correct_answer,

        is_correct:
            correct

    };


    const feedback =
        document.getElementById(
            "quizFeedback"
        );


    feedback.innerHTML = `

        <div class="quiz-feedback">

            <strong>
                ${
                    correct
                        ? "✅ Correct!"
                        : "❌ Not quite."
                }
            </strong>

            <br>

            ${escapeHtml(
                question.explanation ||
                (
                    correct
                        ? "Good job!"
                        : `The correct answer is: ${question.correct_answer}`
                )
            )}

        </div>

    `;


    document
        .getElementById(
            "quizNextButton"
        )
        .disabled = false;

}


async function handleQuizNext() {

    if (!quizAnswerLocked) {
        return;
    }


    if (
        currentQuizIndex <
        currentQuiz.length - 1
    ) {

        currentQuizIndex += 1;

        renderQuizQuestion();

        return;

    }


    await finishQuiz();

}


async function finishQuiz() {

    try {

        const response =
            await fetch(
                "/quiz/score",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            answers:
                                quizAnswers
                        })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to calculate quiz score."
            );

        }


        await calculateAndRenderMastery(

            data.score ??
            data.correct_answers ??
            0,

            data.total ??
            data.total_questions ??
            currentQuiz.length

        );


    } catch (error) {

        console.error(
            "Quiz scoring error:",
            error
        );


        const correctCount =
            quizAnswers.filter(
                answer =>
                    answer &&
                    answer.is_correct
            ).length;


        await calculateAndRenderMastery(
            correctCount,
            currentQuiz.length
        );

    }

}


async function calculateAndRenderMastery(
    score,
    total
) {

    try {

        const response =
            await fetch(
                "/mastery",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            score:
                                score,

                            total:
                                total

                        })
                }
            );


        const mastery =
            await response.json();


        if (!response.ok) {

            throw new Error(
                mastery.detail
                ||
                "Failed to calculate mastery."
            );

        }


        renderMastery(
            mastery
        );


    } catch (error) {

        console.error(
            "Mastery error:",
            error
        );


        const percentage =
            total > 0
                ? Math.round(
                    (score / total) * 100
                )
                : 0;


        let status =
            "Needs Practice";


        let message =
            "Review the learning material and try again.";


        if (percentage >= 70) {

            status =
                "Strong";


            message =
                "You have a strong understanding of this topic.";

        } else if (
            percentage >= 40
        ) {

            status =
                "Developing";


            message =
                "You are making progress. A little more practice can help.";

        }


        renderMastery({

            score:
                score,

            total:
                total,

            percentage:
                percentage,

            status:
                status,

            message:
                message

        });

    }

}


function renderMastery(
    result
) {

    quizCard.innerHTML = `

        <div class="quiz-score">

            <div class="explanation-label">
                🎯 Mastery Result
            </div>

            <div
                class="quiz-score-number"
            >
                ${result.score}
                /
                ${result.total}
            </div>

            <div
                class="mastery-percentage"
            >
                ${result.percentage}%
            </div>

            <div
                class="mastery-status"
            >
                ${escapeHtml(
                    result.status
                )}
            </div>

            <p
                class="mastery-message"
            >
                ${escapeHtml(
                    result.message
                )}
            </p>

            <p>
                Your mastery of

                <strong>
                    ${escapeHtml(
                        selectedTopic.title
                    )}
                </strong>

                has been measured from this quiz.
            </p>

            <div
                class="quiz-controls"
                style="justify-content:center;"
            >

                <button
                    class="quiz-button"
                    id="quizBackToLearningButton"
                    type="button"
                >
                    Back to Learning
                </button>

            </div>

        </div>

    `;


    document
        .getElementById(
            "quizBackToLearningButton"
        )
        .addEventListener(
            "click",
            () =>
                showScreen(
                    "learningScreen"
                )
        );

}


function renderQuizError(
    message
) {

    quizCard.innerHTML = `

        <div class="explanation-error">

            <strong>
                We couldn't generate the quiz.
            </strong>

            <br><br>

            ${escapeHtml(message)}

        </div>

    `;

}


backFromQuizButton.addEventListener(
    "click",
    () => {

        showScreen(
            "learningScreen"
        );

    }
);



uploadCard.addEventListener(
    "dragover",
    event => {

        event.preventDefault();


        uploadCard.classList.add(
            "dragover"
        );

    }
);


uploadCard.addEventListener(
    "dragleave",
    () => {

        uploadCard.classList.remove(
            "dragover"
        );

    }
);


uploadCard.addEventListener(
    "drop",
    event => {

        event.preventDefault();


        uploadCard.classList.remove(
            "dragover"
        );


        const file =
            event
                .dataTransfer
                .files[0];


        if (!file) {
            return;
        }


        handleFile(file);

    }
);



function showStatus(
    message,
    type
) {

    status.textContent =
        message;


    status.className =
        "status visible " +
        type;

}


function clearStatus() {

    status.textContent = "";


    status.className =
        "status";

}



function formatFileSize(
    bytes
) {

    if (bytes < 1024) {

        return bytes + " B";

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return (
            (
                bytes / 1024
            ).toFixed(1)
            +
            " KB"
        );

    }


    return (
        (
            bytes /
            (1024 * 1024)
        ).toFixed(2)
        +
        " MB"
    );

}




function escapeHtml(
    value
) {

    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}