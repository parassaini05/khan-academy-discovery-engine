import React, { useState } from 'react';

export interface VisualScaleBalanceProps {
  initialLeftExpression?: string; // e.g. "3x + 4"
  initialRightExpression?: string; // e.g. "19"
  targetConstant?: number; // 4
  onBalancedStep?: (operation: string, value: number) => void;
}

export const VisualScaleBalance: React.FC<VisualScaleBalanceProps> = ({
  initialLeftExpression = '3x + 4',
  initialRightExpression = '19',
  targetConstant = 4,
  onBalancedStep,
}) => {
  const [leftValue, setLeftValue] = useState<number>(19);
  const [rightValue, setRightValue] = useState<number>(19);
  const [leftSubtracted, setLeftSubtracted] = useState<number>(0);
  const [rightSubtracted, setRightSubtracted] = useState<number>(0);
  const [message, setMessage] = useState<string>('The equation is currently balanced.');

  const handleSubtractFromLeft = () => {
    const newLeft = leftValue - targetConstant;
    const newSub = leftSubtracted + targetConstant;
    setLeftValue(newLeft);
    setLeftSubtracted(newSub);
    updateBalanceState(newLeft, rightValue);
  };

  const handleSubtractFromRight = () => {
    const newRight = rightValue - targetConstant;
    const newSub = rightSubtracted + targetConstant;
    setRightValue(newRight);
    setRightSubtracted(newSub);
    updateBalanceState(leftValue, newRight);
  };

  const updateBalanceState = (left: number, right: number) => {
    if (left === right) {
      setMessage('✅ Perfectly balanced! Whatever you subtract from one side, you subtracted from the other.');
      if (onBalancedStep) {
        onBalancedStep('SUBTRACT', targetConstant);
      }
    } else if (left < right) {
      setMessage('⚠️ Unbalanced! You subtracted from the left side, but forgot the right side.');
    } else {
      setMessage('⚠️ Unbalanced! You subtracted from the right side, but forgot the left side.');
    }
  };

  const handleReset = () => {
    setLeftValue(19);
    setRightValue(19);
    setLeftSubtracted(0);
    setRightSubtracted(0);
    setMessage('The equation is currently balanced.');
  };

  // Compute tilt angle (degrees)
  const diff = rightValue - leftValue;
  const tiltDeg = Math.max(-15, Math.min(15, diff * 1.5));

  return (
    <div
      style={{
        padding: '20px',
        backgroundColor: '#f8fafc',
        borderRadius: '10px',
        border: '1px solid #e2e8f0',
        fontFamily: 'Noto Sans, Lato, sans-serif',
        maxWidth: '540px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '13px', fontWeight: 700, color: '#334155', textTransform: 'uppercase' }}>
          Interactive Scale Balance Model
        </span>
        <button
          onClick={handleReset}
          style={{
            fontSize: '11px',
            color: '#64748b',
            background: 'none',
            border: 'none',
            textDecoration: 'underline',
            cursor: 'pointer',
          }}
        >
          Reset Balance
        </button>
      </div>

      {/* Visual Balance Scale SVG */}
      <div style={{ textAlign: 'center', margin: '20px 0' }}>
        <svg width="340" height="140" viewBox="0 0 340 140" style={{ overflow: 'visible' }}>
          {/* Fulcrum base */}
          <polygon points="170,90 150,130 190,130" fill="#64748b" />
          <line x1="120" y1="130" x2="220" y2="130" stroke="#475569" strokeWidth="4" />

          {/* Pivoting Balance Beam */}
          <g transform={`rotate(${tiltDeg}, 170, 90)`} style={{ transition: 'transform 0.3s ease' }}>
            <line x1="40" y1="90" x2="300" y2="90" stroke="#1e293b" strokeWidth="6" strokeLinecap="round" />
            <circle cx="170" cy="90" r="6" fill="#0f172a" />

            {/* Left Pan Strings & Pan */}
            <line x1="50" y1="90" x2="35" y2="120" stroke="#94a3b8" strokeWidth="2" />
            <line x1="50" y1="90" x2="65" y2="120" stroke="#94a3b8" strokeWidth="2" />
            <rect x="25" y="120" width="50" height="8" rx="3" fill="#3b82f6" />

            {/* Right Pan Strings & Pan */}
            <line x1="290" y1="90" x2="275" y2="120" stroke="#94a3b8" strokeWidth="2" />
            <line x1="290" y1="90" x2="305" y2="120" stroke="#94a3b8" strokeWidth="2" />
            <rect x="265" y="120" width="50" height="8" rx="3" fill="#3b82f6" />
          </g>
        </svg>
      </div>

      {/* Control Buttons for Operations */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '14px' }}>
        <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #cbd5e1' }}>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#1e293b' }}>Left Pan</div>
          <div style={{ fontSize: '15px', fontWeight: 700, color: '#2563eb', margin: '4px 0' }}>
            {leftSubtracted > 0 ? `3x + 4 - ${leftSubtracted}` : initialLeftExpression}
          </div>
          <button
            onClick={handleSubtractFromLeft}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '4px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#f1f5f9',
              cursor: 'pointer',
              marginTop: '4px',
            }}
          >
            Subtract {targetConstant}
          </button>
        </div>

        <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #cbd5e1' }}>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#1e293b' }}>Right Pan</div>
          <div style={{ fontSize: '15px', fontWeight: 700, color: '#2563eb', margin: '4px 0' }}>
            {rightSubtracted > 0 ? `19 - ${rightSubtracted}` : initialRightExpression}
          </div>
          <button
            onClick={handleSubtractFromRight}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              borderRadius: '4px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#f1f5f9',
              cursor: 'pointer',
              marginTop: '4px',
            }}
          >
            Subtract {targetConstant}
          </button>
        </div>
      </div>

      <div
        style={{
          padding: '10px 12px',
          borderRadius: '6px',
          backgroundColor: leftValue === rightValue ? '#f0fdf4' : '#fff7ed',
          border: `1px solid ${leftValue === rightValue ? '#86efac' : '#fdba74'}`,
          fontSize: '12px',
          color: leftValue === rightValue ? '#15803d' : '#9a3412',
          textAlign: 'center',
          fontWeight: 500,
        }}
      >
        {message}
      </div>
    </div>
  );
};
