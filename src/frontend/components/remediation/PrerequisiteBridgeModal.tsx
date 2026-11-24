import React, { useState } from 'react';

export interface PrerequisiteQuestion {
  id: string;
  prompt: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

export interface PrerequisiteBridgeModalProps {
  isOpen: boolean;
  conceptTitle: string;
  conceptNodeId: string;
  description: string;
  questions: PrerequisiteQuestion[];
  onComplete: (passed: boolean) => void;
  onCancel: () => void;
}

export const PrerequisiteBridgeModal: React.FC<PrerequisiteBridgeModalProps> = ({
  isOpen,
  conceptTitle,
  conceptNodeId,
  description,
  questions,
  onComplete,
  onCancel,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isAnswered, setIsAnswered] = useState<boolean>(false);
  const [score, setScore] = useState<number>(0);

  if (!isOpen) return null;

  const currentQ = questions[currentQuestionIndex] || {
    id: 'sample-1',
    prompt: 'Calculate: (-3) * (-4)',
    options: ['-12', '12', '-7', '7'],
    correctIndex: 1,
    explanation: 'A negative number multiplied by a negative number is always positive: (-3) * (-4) = 12.',
  };

  const handleSelectOption = (index: number) => {
    if (isAnswered) return;
    setSelectedOption(index);
  };

  const handleSubmitAnswer = () => {
    if (selectedOption === null || isAnswered) return;
    const correct = selectedOption === currentQ.correctIndex;
    setIsAnswered(true);
    if (correct) {
      setScore((prev) => prev + 1);
      setFeedback('Correct! ' + currentQ.explanation);
    } else {
      setFeedback('Not quite. ' + currentQ.explanation);
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex + 1 < questions.length) {
      setCurrentQuestionIndex((prev) => prev + 1);
      setSelectedOption(null);
      setIsAnswered(false);
      setFeedback(null);
    } else {
      // Completed all questions
      const passed = score + (selectedOption === currentQ.correctIndex ? 1 : 0) >= Math.ceil(questions.length * 0.7);
      onComplete(passed);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '16px',
        fontFamily: 'Noto Sans, Lato, -apple-system, sans-serif',
      }}
    >
      <div
        style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          maxWidth: '520px',
          width: '100%',
          padding: '24px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                color: '#2563eb',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              60-Second Prerequisite Bridge
            </span>
            <h2 style={{ margin: '4px 0 0 0', fontSize: '18px', color: '#0f172a' }}>{conceptTitle}</h2>
          </div>
          <span style={{ fontSize: '12px', color: '#64748b' }}>
            Question {currentQuestionIndex + 1} of {Math.max(questions.length, 1)}
          </span>
        </div>

        <p style={{ fontSize: '13px', color: '#475569', marginBottom: '16px' }}>{description}</p>

        <div
          style={{
            padding: '16px',
            backgroundColor: '#f8fafc',
            borderRadius: '8px',
            marginBottom: '16px',
            border: '1px solid #e2e8f0',
          }}
        >
          <p style={{ fontWeight: 600, fontSize: '15px', color: '#1e293b', margin: '0 0 12px 0' }}>
            {currentQ.prompt}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {currentQ.options.map((option, idx) => {
              const isSelected = selectedOption === idx;
              let borderCol = isSelected ? '#2563eb' : '#cbd5e1';
              let bgCol = isSelected ? '#eff6ff' : '#ffffff';

              if (isAnswered) {
                if (idx === currentQ.correctIndex) {
                  borderCol = '#16a34a';
                  bgCol = '#f0fdf4';
                } else if (isSelected) {
                  borderCol = '#dc2626';
                  bgCol = '#fef2f2';
                }
              }

              return (
                <button
                  key={idx}
                  onClick={() => handleSelectOption(idx)}
                  disabled={isAnswered}
                  style={{
                    padding: '10px 14px',
                    textAlign: 'left',
                    borderRadius: '6px',
                    border: `2px solid ${borderCol}`,
                    backgroundColor: bgCol,
                    fontSize: '14px',
                    color: '#1e293b',
                    cursor: isAnswered ? 'default' : 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {option}
                </button>
              );
            })}
          </div>
        </div>

        {feedback && (
          <div
            style={{
              padding: '10px 14px',
              borderRadius: '6px',
              backgroundColor: feedback.startsWith('Correct') ? '#f0fdf4' : '#fffbeb',
              border: `1px solid ${feedback.startsWith('Correct') ? '#86efac' : '#fde68a'}`,
              marginBottom: '16px',
              fontSize: '13px',
              color: feedback.startsWith('Correct') ? '#166534' : '#854d0e',
            }}
          >
            {feedback}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            onClick={onCancel}
            style={{
              padding: '8px 14px',
              border: 'none',
              background: 'none',
              color: '#64748b',
              fontSize: '13px',
              cursor: 'pointer',
            }}
          >
            Return to Exercise
          </button>

          {!isAnswered ? (
            <button
              onClick={handleSubmitAnswer}
              disabled={selectedOption === null}
              style={{
                padding: '8px 18px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: selectedOption !== null ? '#1865f2' : '#cbd5e1',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '14px',
                cursor: selectedOption !== null ? 'pointer' : 'not-allowed',
              }}
            >
              Check Answer
            </button>
          ) : (
            <button
              onClick={handleNext}
              style={{
                padding: '8px 18px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: '#16a34a',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '14px',
                cursor: 'pointer',
              }}
            >
              {currentQuestionIndex + 1 < questions.length ? 'Next Question' : 'Complete Bridge'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
