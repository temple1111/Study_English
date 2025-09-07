import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || ''; // Fallback for local development

function App() {
  const [name, setName] = useState('');
  const [level, setLevel] = useState('初級'); // Default value
  const [goal, setGoal] = useState('日常会話'); // Default value
  const [profileSetup, setProfileSetup] = useState(false);
  const [message, setMessage] = useState('');

  // Learning mode states
  const [currentWord, setCurrentWord] = useState('');
  const [currentOptions, setCurrentOptions] = useState([]); // New state for options
  const [selectedAnswer, setSelectedAnswer] = useState(''); // Changed from userAnswer
  const [feedback, setFeedback] = useState('');
  const [explanation, setExplanation] = useState('');
  const [score, setScore] = useState('');
  const [sessionFinished, setSessionFinished] = useState(false);
  const [blockchainPrompt, setBlockchainPrompt] = useState(false);
  const [blockchainData, setBlockchainData] = useState(null);
  const [finalAccuracy, setFinalAccuracy] = useState(0);

  // Options for select dropdowns
  const levelOptions = ['初級', '中級', '上級'];
  const goalOptions = ['日常会話', 'ビジネス英語', 'TOEIC 800点', '旅行'];

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${BACKEND_URL}/user/setup', { name, level, goal });
      setMessage(response.data.message);
      setProfileSetup(true);
    } catch (error) {
      setMessage('Error setting up profile: ' + (error.response?.data?.detail || error.message));
    }
  };

  const startLearningSession = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/learn/start', null, { params: { user_name: name } });
      setCurrentWord(response.data.word);
      setCurrentOptions(response.data.options); // Set options
      setFeedback('');
      setExplanation('');
      setSelectedAnswer(''); // Clear selected answer
      setScore('');
      setSessionFinished(false);
      setBlockchainPrompt(false);
      setBlockchainData(null);
      setFinalAccuracy(0);
    } catch (error) {
      setMessage('Error starting session: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (!selectedAnswer) {
      setMessage('解答を選択してください。');
      return;
    }
    try {
      const response = await axios.post(`${BACKEND_URL}/learn/submit_answer', {
        user_name: name,
        word: currentWord,
        user_answer: selectedAnswer, // Send selected answer
      });
      setFeedback(response.data.feedback);
      setExplanation(response.data.explanation);
      setScore(response.data.current_score);
      setSelectedAnswer(''); // Clear selected answer for next word

      if (response.data.session_finished) {
        setSessionFinished(true);
        setFinalAccuracy(response.data.final_accuracy);
        if (response.data.blockchain_record_prompt) {
          setBlockchainPrompt(true);
          setBlockchainData(response.data.blockchain_data);
        }
      } else {
        setCurrentWord(response.data.next_word);
        setCurrentOptions(response.data.next_options); // Set options for next word
      }
    } catch (error) {
      setMessage('Error submitting answer: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleRecordBlockchain = async () => {
    try {
      const response = await axios.post(`${BACKEND_URL}/blockchain/record_achievement', blockchainData);
      setMessage(response.data.message);
      setBlockchainPrompt(false);
    } catch (error) {
      setMessage('Error recording on blockchain: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (!profileSetup) {
    return (
      <div className="App">
        <header className="App-header">
          <h1>英単語学習アプリへようこそ！</h1>
          <p>まずはあなたのことを教えてください。</p>
          <form onSubmit={handleProfileSubmit}>
            <div>
              <label>
                お名前:
                <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
              </label>
            </div>
            <div>
              <label>
                英語レベル:
                <select value={level} onChange={(e) => setLevel(e.target.value)}>
                  {levelOptions.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>
            </div>
            <div>
              <label>
                学習目標:
                <select value={goal} onChange={(e) => setGoal(e.target.value)}>
                  {goalOptions.map((option) => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </label>
            </div>
            <button type="submit">プロフィールを設定</button>
          </form>
          {message && <p>{message}</p>}
        </header>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>学習モード</h1>
        <p>こんにちは、{name}さん！</p>
        <p>あなたの英語レベルは {level}、目標は {goal} ですね。</p>
        <p>これから一緒に頑張りましょう！</p>

        {!currentWord && !sessionFinished && (
          <button onClick={startLearningSession}>学習を開始する</button>
        )}

        {currentWord && !sessionFinished && (
          <div>
            <h2>単語: {currentWord}</h2>
            <form onSubmit={handleSubmitAnswer}>
              {currentOptions.map((option, index) => (
                <div key={index}>
                  <label>
                    <input
                      type="radio"
                      value={option}
                      checked={selectedAnswer === option}
                      onChange={(e) => setSelectedAnswer(e.target.value)}
                      required
                    />
                    {option}
                  </label>
                </div>
              ))}
              <button type="submit">回答を送信</button>
            </form>
            {feedback && <p>{feedback}</p>}
            {explanation && <p>解説: {explanation}</p>}
            {score && <p>現在のスコア: {score}</p>}
          </div>
        )}

        {sessionFinished && (
          <div>
            <h2>学習セッション終了！</h2>
            <p>最終正解率: {finalAccuracy.toFixed(2)}%</p>
            {blockchainPrompt && (
              <div>
                <p>素晴らしい！目標達成です！</p>
                <button onClick={handleRecordBlockchain}>学習成果をブロックチェーンに記録する</button>
              </div>
            )}
            <button onClick={startLearningSession}>もう一度学習する</button>
          </div>
        )}
        {message && <p>{message}</p>}
      </header>
    </div>
  );
}

export default App;