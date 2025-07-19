from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from app.models import User, InterviewSession
from app.ai_services import AIServices
from app.utils import extract_text_from_file, preprocess_resume_text
import os
from pathlib import Path
import logging

# Initialize the blueprint for the main section
main = Blueprint('main', __name__)
ai = AIServices()

# Home Route
@main.route('/')
def index():
    return render_template('index.html')

# Candidate Dashboard Route (accessible without login)
@main.route('/candidate-dashboard')
def candidate_dashboard():
    return render_template('candidate_dashboard.html')

@main.route('/recruiter-dashboard')
def recruiter_dashboard():
    return render_template('recruiter_dashboard.html')

@main.route('/interview-prep')
def interview_prep():
    raw_questions = session.get('generated_questions', '')
    questions = raw_questions.split('\n') if isinstance(raw_questions, str) else []
    return render_template('interview_prep.html', questions=questions)

# Upload Resume Route
@main.route('/upload-resume', methods=['POST'])
def upload_resume():
    try:
        file = request.files.get('resume')
        if not file or file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('main.candidate_dashboard'))

        ext = file.filename.split('.')[-1].lower()
        if ext not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('Invalid file type', 'error')
            return redirect(url_for('main.candidate_dashboard'))

        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        upload_dir.mkdir(exist_ok=True)

        filepath = upload_dir / file.filename
        file.save(filepath)

        resume_text = extract_text_from_file(filepath)
        processed_text = preprocess_resume_text(resume_text)
        questions = ai.generate_questions_from_resume(processed_text)

        session['resume_text'] = processed_text
        session['generated_questions'] = questions

        return render_template('interview_prep.html', questions=questions.split('\n'))

    except Exception as e:
        logging.error(f"Upload error: {str(e)}")
        flash('Upload failed. Please try again.', 'error')
        return redirect(url_for('main.candidate_dashboard'))

# Practice Interview Route
@main.route('/practice-interview', methods=['GET', 'POST'])
def practice_interview():
    if request.method == 'POST':
        try:
            question = request.form.get('question', '').strip()
            answer = request.form.get('answer', '').strip()

            if not question or not answer:
                return jsonify({'error': 'Question and answer required'}), 400

            evaluation = ai.evaluate_answer(question, answer)
            sentiment = ai.analyze_sentiment(answer)

            return jsonify({
                'evaluation': evaluation,
                'sentiment': sentiment
            })

        except Exception as e:
            current_app.logger.error(f"Evaluation error: {str(e)}")
            return jsonify({'error': 'Evaluation failed'}), 500

    questions = session.get('generated_questions', '').split('\n')
    return render_template('practice_interview.html', questions=questions)

# Analyze Answer Route
@main.route('/analyze-answer', methods=['POST'])
def analyze_answer():
    data = request.get_json()
    question = data.get('question')
    answer = data.get('answer')

    evaluation = ai.evaluate_answer(question, answer)
    sentiment = ai.analyze_sentiment(answer)

    return jsonify({
        'evaluation': evaluation,
        'sentiment': sentiment
    })

@main.route('/conduct-interview', methods=['POST'])
def conduct_interview():
    candidate_id = request.form.get('candidate_id')
    job_description = request.form.get('job_description')

    candidate = User.get(candidate_id)
    questions = ai.generate_questions_from_resume(
        candidate.resume_text,
        job_description
    )

    return render_template('conduct_interview.html',
                           questions=questions,
                           candidate=candidate)

# Evaluate Candidate Route
@main.route('/evaluate-candidate', methods=['POST'])
def evaluate_candidate():
    responses = request.get_json()

    overall_evaluation = ""
    scores = {
        'technical': 0,
        'communication': 0,
        'relevance': 0,
        'confidence': 0
    }
    count = 0

    for qa in responses:
        evaluation = ai.evaluate_answer(qa['question'], qa['answer'])
        overall_evaluation += f"Question: {qa['question']}\nAnswer: {qa['answer']}\nEvaluation: {evaluation}\n\n"

        if "Relevance to question" in evaluation:
            scores['relevance'] += int(evaluation.split("Relevance to question")[1].split(")")[0].split("-")[-1].strip())
        if "Technical accuracy" in evaluation:
            scores['technical'] += int(evaluation.split("Technical accuracy")[1].split(")")[0].split("-")[-1].strip())
        if "Clarity and structure" in evaluation:
            scores['communication'] += int(evaluation.split("Clarity and structure")[1].split(")")[0].split("-")[-1].strip())
        if "Confidence indicators" in evaluation:
            scores['confidence'] += int(evaluation.split("Confidence indicators")[1].split(")")[0].split("-")[-1].strip())

        count += 1

    for key in scores:
        scores[key] = round(scores[key] / count, 1) if count > 0 else 0

    return jsonify({
        'detailed_evaluation': overall_evaluation,
        'scores': scores
    })
