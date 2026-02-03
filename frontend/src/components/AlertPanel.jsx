import React from 'react';
import { RISK_STAGES } from '../utils/constants';

const AlertPanel = ({ stage }) => {
  const currentStage = RISK_STAGES[stage] || RISK_STAGES.COMPETITIVE;

  return (
    <div className={`flex items-center p-4 rounded-lg border-l-4 ${currentStage.bg} ${currentStage.border} transition-all duration-500 animate-pulse`}>
      <div className="flex-shrink-0">
        {/* Icon based on stage */}
        <span className="text-2xl mr-3" role="img" aria-label="alert">
          {stage === 'CRITICAL' ? '🚨' : stage === 'VULNERABLE' ? '⚠️' : stage === 'WINNING' ? '✅' : '⚖️'}
        </span>
      </div>
      <div>
        <h3 className={`text-lg font-bold ${stage === 'CRITICAL' ? 'text-red-600' : 'text-white'}`}>
          {currentStage.label} - Macro Alert
        </h3>
        <p className="text-gray-300">
          {currentStage.message}
        </p>
      </div>
    </div>
  );
};

export default AlertPanel;
