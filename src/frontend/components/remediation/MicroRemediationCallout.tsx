import React from 'react';

export interface MicroRemediationCalloutProps {
  isOpen: boolean;
  failureMode: 'PREREQUISITE_GAP' | 'RULE_MISCONCEPTION' | 'TRANSLATION_GAP' | 'EXECUTION_SLIP' | 'TRANSFER_GAP' | string;
  rootConceptNodeId: string;
  explanation: string;
  scaffoldMessage: string;
  actionLabel: string;
  actionType: 'RETRY_WITH_STEP_PROMPT' | 'SIGN_CHECK_CALLOUT' | 'PREREQUISITE_REROUTE' | string;
  onActionClick: () => void;
  onDismiss: () => void;
}

export const MicroRemediationCallout: React.FC<MicroRemediationCalloutProps> = ({
  isOpen,
  failureMode,
  rootConceptNodeId,
  explanation,
  scaffoldMessage,
  actionLabel,
  actionType,
  onActionClick,
  onDismiss,
}) => {
  if (!isOpen) return null;

  const getBadgeStyle = (mode: string) => {
    switch (mode) {
      case 'PREREQUISITE_GAP':
        return { bg: '#fee2e2', text: '#991b1b', label: 'Prerequisite Concept' };
      case 'RULE_MISCONCEPTION':
        return { bg: '#fef3c7', text: '#92400e', label: 'Algebraic Rule Check' };
      case 'EXECUTION_SLIP':
        return { bg: '#e0e7ff', text: '#3730a3', label: 'Calculation Check' };
      default:
        return { bg: '#f3f4f6', text: '#374151', label: 'Hint' };
    }
  };

  const badge = getBadgeStyle(failureMode);

  return (
    <div
      role="region"
      aria-label="Targeted Math Feedback"
      style={{
        marginTop: '12px',
        padding: '16px',
        borderRadius: '8px',
        border: '1px solid #cbd5e1',
        backgroundColor: '#ffffff',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
        fontFamily: 'Noto Sans, Lato, -apple-system, sans-serif',
        maxWidth: '560px',
        transition: 'all 0.2s ease-in-out',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span
            style={{
              fontSize: '11px',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              padding: '3px 8px',
              borderRadius: '999px',
              backgroundColor: badge.bg,
              color: badge.text,
            }}
          >
            {badge.label}
          </span>
          <span style={{ fontSize: '12px', color: '#64748b' }}>
            ID: {rootConceptNodeId}
          </span>
        </div>
        <button
          onClick={onDismiss}
          aria-label="Close diagnostic callout"
          style={{
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            fontSize: '16px',
            lineHeight: 1,
            padding: '2px 6px',
          }}
        >
          &times;
        </button>
      </div>

      <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#1e293b', fontWeight: 600 }}>
        {explanation}
      </p>

      <div
        style={{
          padding: '10px 12px',
          backgroundColor: '#f8fafc',
          borderRadius: '6px',
          borderLeft: '4px solid #1865f2',
          marginBottom: '12px',
        }}
      >
        <p style={{ margin: 0, fontSize: '13px', color: '#334155', fontStyle: 'italic' }}>
          💡 {scaffoldMessage}
        </p>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
        <button
          onClick={onDismiss}
          style={{
            padding: '6px 12px',
            fontSize: '13px',
            borderRadius: '6px',
            border: '1px solid #cbd5e1',
            backgroundColor: '#ffffff',
            color: '#475569',
            cursor: 'pointer',
          }}
        >
          Dismiss
        </button>
        <button
          onClick={onActionClick}
          style={{
            padding: '6px 14px',
            fontSize: '13px',
            fontWeight: 600,
            borderRadius: '6px',
            border: 'none',
            backgroundColor: '#1865f2',
            color: '#ffffff',
            cursor: 'pointer',
            boxShadow: '0 2px 4px rgba(24, 101, 242, 0.25)',
          }}
        >
          {actionLabel}
        </button>
      </div>
    </div>
  );
};
