# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "flask",
# ]
# ///

"""
Simple Quiz App Server

Run with: uv run quiz_app.py <quiz_file.json>

Example: uv run quiz_app.py python_quiz.json
"""

import json
import sys
from pathlib import Path
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

QUIZ_DATA = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz App</title>
    <style>
        * { box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        h1 {
            text-align: center;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 24px;
        }
        
        .quiz-container {
            background: white;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-bottom: 24px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
            border-radius: 4px;
        }
        
        .question-card { display: none; }
        .question-card.active { display: block; }
        
        .question-number {
            font-size: 14px;
            color: #888;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .question-text {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 24px;
            color: #2c3e50;
            line-height: 1.4;
        }
        
        .options {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .option {
            padding: 16px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            background: white;
            font-size: 16px;
        }
        
        .option:hover:not(.disabled) {
            border-color: #667eea;
            background: #f8f9ff;
        }
        
        .option.selected {
            border-color: #667eea;
            background: #f0f3ff;
        }
        
        .option.correct {
            border-color: #27ae60;
            background: #d5f4e6;
        }
        
        .option.incorrect {
            border-color: #e74c3c;
            background: #fdeaea;
        }
        
        .option.disabled { cursor: default; }
        
        .open-ended-input {
            width: 100%;
            padding: 16px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            outline: none;
            transition: all 0.2s;
        }
        
        .open-ended-input:focus {
            border-color: #667eea;
        }
        
        .open-ended-input.correct {
            border-color: #27ae60;
            background: #d5f4e6;
        }
        
        .open-ended-input.incorrect {
            border-color: #e74c3c;
            background: #fdeaea;
        }
        
        .feedback {
            margin-top: 16px;
            padding: 14px 18px;
            border-radius: 10px;
            font-weight: 500;
            display: none;
        }
        
        .feedback.correct {
            display: block;
            background: #d5f4e6;
            color: #1e8449;
        }
        
        .feedback.incorrect {
            display: block;
            background: #fdeaea;
            color: #c0392b;
        }
        
        .buttons {
            margin-top: 24px;
            display: flex;
            gap: 12px;
            justify-content: flex-end;
        }
        
        button {
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .btn-submit {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-submit:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-submit:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
        }
        
        .btn-next {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
        }
        
        .btn-next:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.4);
        }
        
        .results {
            text-align: center;
            display: none;
        }
        
        .results.active { display: block; }
        
        .score {
            font-size: 64px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 20px 0;
        }
        
        .score-label {
            font-size: 18px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .score-message {
            font-size: 24px;
            margin: 24px 0;
            color: #2c3e50;
        }
        
        .btn-restart {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            margin-top: 10px;
        }
        
        .btn-restart:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <h1>📝 Quiz Time</h1>
    
    <div class="quiz-container">
        <div class="progress-bar">
            <div class="progress-fill" id="progress"></div>
        </div>
        
        <div id="questions-container"></div>
        
        <div class="results" id="results">
            <p class="score-label">Your Score</p>
            <p class="score" id="final-score">0/0</p>
            <p class="score-message" id="score-message"></p>
            <button class="btn-restart" onclick="restartQuiz()">🔄 Try Again</button>
        </div>
    </div>

    <script>
        let quizData = [];
        let currentQuestion = 0;
        let score = 0;
        let answered = false;
        
        async function loadQuiz() {
            try {
                const response = await fetch('/api/quiz');
                quizData = await response.json();
                renderQuiz();
            } catch (error) {
                console.error('Error loading quiz:', error);
                document.getElementById('questions-container').innerHTML = 
                    '<p style="color: #e74c3c;">Error loading quiz data.</p>';
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function formatQuestion(text) {
            // Convert code in backticks to <code> tags
            return text.replace(/`([^`]+)`/g, '<code>$1</code>');
        }
        
        function renderQuiz() {
            const container = document.getElementById('questions-container');
            container.innerHTML = '';
            
            quizData.forEach((q, index) => {
                const card = document.createElement('div');
                card.className = 'question-card' + (index === 0 ? ' active' : '');
                card.id = 'question-' + index;
                
                let optionsHTML = '';
                if (q.type === 'multiple-choice') {
                    optionsHTML = '<div class="options">' + 
                        q.options.map((opt, i) => 
                            `<div class="option" data-index="${i}" onclick="selectOption(${index}, ${i})">${formatQuestion(escapeHtml(opt))}</div>`
                        ).join('') + '</div>';
                } else {
                    optionsHTML = `<input type="text" class="open-ended-input" id="input-${index}" 
                        placeholder="Type your answer..." 
                        onkeypress="if(event.key==='Enter')submitAnswer(${index})"
                        autocomplete="off">`;
                }
                
                card.innerHTML = `
                    <p class="question-number">Question ${index + 1} of ${quizData.length}</p>
                    <p class="question-text">${formatQuestion(escapeHtml(q.question))}</p>
                    ${optionsHTML}
                    <div class="feedback" id="feedback-${index}"></div>
                    <div class="buttons">
                        <button class="btn-submit" id="submit-${index}" onclick="submitAnswer(${index})">Submit</button>
                        <button class="btn-next" id="next-${index}" onclick="nextQuestion()" style="display:none">
                            ${index === quizData.length - 1 ? 'See Results →' : 'Next →'}
                        </button>
                    </div>
                `;
                
                container.appendChild(card);
            });
            
            updateProgress();
        }
        
        function selectOption(questionIndex, optionIndex) {
            if (answered) return;
            
            const card = document.getElementById('question-' + questionIndex);
            card.querySelectorAll('.option').forEach(opt => opt.classList.remove('selected'));
            card.querySelector(`[data-index="${optionIndex}"]`).classList.add('selected');
        }
        
        function submitAnswer(questionIndex) {
            if (answered) return;
            
            const q = quizData[questionIndex];
            const feedback = document.getElementById('feedback-' + questionIndex);
            const submitBtn = document.getElementById('submit-' + questionIndex);
            const nextBtn = document.getElementById('next-' + questionIndex);
            
            let isCorrect = false;
            
            if (q.type === 'multiple-choice') {
                const selected = document.querySelector('#question-' + questionIndex + ' .option.selected');
                if (!selected) {
                    alert('Please select an answer');
                    return;
                }
                const selectedIndex = parseInt(selected.dataset.index);
                isCorrect = selectedIndex === q.correctAnswer;
                
                document.querySelectorAll('#question-' + questionIndex + ' .option').forEach((opt, i) => {
                    opt.classList.add('disabled');
                    if (i === q.correctAnswer) {
                        opt.classList.add('correct');
                    } else if (i === selectedIndex && !isCorrect) {
                        opt.classList.add('incorrect');
                    }
                });
            } else {
                const input = document.getElementById('input-' + questionIndex);
                const userAnswer = input.value.trim().toLowerCase();
                
                if (!userAnswer) {
                    alert('Please enter an answer');
                    return;
                }
                
                isCorrect = q.acceptedAnswers.some(ans => 
                    ans.toLowerCase() === userAnswer
                );
                
                input.classList.add(isCorrect ? 'correct' : 'incorrect');
                input.disabled = true;
                
                if (!isCorrect) {
                    feedback.innerHTML = `✗ Incorrect.<br><small>Accepted: ${q.acceptedAnswers.join(', ')}</small>`;
                }
            }
            
            if (isCorrect) {
                score++;
                feedback.textContent = '✓ Correct!';
                feedback.className = 'feedback correct';
            } else if (q.type === 'multiple-choice') {
                feedback.textContent = '✗ Incorrect';
                feedback.className = 'feedback incorrect';
            } else {
                feedback.className = 'feedback incorrect';
            }
            
            answered = true;
            submitBtn.style.display = 'none';
            nextBtn.style.display = 'inline-block';
        }
        
        function nextQuestion() {
            answered = false;
            document.getElementById('question-' + currentQuestion).classList.remove('active');
            currentQuestion++;
            
            if (currentQuestion >= quizData.length) {
                showResults();
            } else {
                document.getElementById('question-' + currentQuestion).classList.add('active');
                updateProgress();
            }
        }
        
        function updateProgress() {
            const progress = (currentQuestion / quizData.length) * 100;
            document.getElementById('progress').style.width = progress + '%';
        }
        
        function showResults() {
            document.getElementById('questions-container').style.display = 'none';
            document.getElementById('results').classList.add('active');
            document.getElementById('final-score').textContent = score + '/' + quizData.length;
            document.getElementById('progress').style.width = '100%';
            
            const pct = (score / quizData.length) * 100;
            let msg = '';
            if (pct === 100) msg = '🎉 Perfect! Outstanding!';
            else if (pct >= 80) msg = '🌟 Great job!';
            else if (pct >= 60) msg = '👍 Good effort!';
            else if (pct >= 40) msg = '📚 Keep practicing!';
            else msg = '💪 Don\\'t give up!';
            
            document.getElementById('score-message').textContent = msg;
        }
        
        function restartQuiz() {
            currentQuestion = 0;
            score = 0;
            answered = false;
            document.getElementById('questions-container').style.display = 'block';
            document.getElementById('results').classList.remove('active');
            renderQuiz();
        }
        
        loadQuiz();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/quiz')
def get_quiz():
    return jsonify(QUIZ_DATA)

def main():
    global QUIZ_DATA
    
    if len(sys.argv) < 2:
        print("Usage: uv run quiz_app.py <quiz_file.json>")
        print("Example: uv run quiz_app.py python_quiz.json")
        sys.exit(1)
    
    quiz_file = sys.argv[1]
    quiz_path = Path(quiz_file)
    
    if not quiz_path.exists():
        print(f"Error: File '{quiz_file}' not found.")
        sys.exit(1)
    
    try:
        with open(quiz_path, 'r', encoding='utf-8') as f:
            QUIZ_DATA = json.load(f)
        print(f"✓ Loaded {len(QUIZ_DATA)} questions from '{quiz_file}'")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        sys.exit(1)
    
    print("\n🚀 Quiz Server running at http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    
    app.run(debug=False, port=5000)

if __name__ == '__main__':
    main()