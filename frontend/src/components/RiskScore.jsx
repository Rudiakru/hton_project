import React from 'react';

const RiskScore = ({ score, stage }) => {
  const getStageColor = (s) => {
    switch (s) {
      case 'WINNING': return 'text-green-500';
      case 'COMPETITIVE': return 'text-yellow-500';
      case 'VULNERABLE': return 'text-orange-500';
      case 'CRITICAL': return 'text-red-500';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-gray-800 rounded-lg border-b-4 border-red-600">
      <span className="text-sm uppercase tracking-widest text-gray-400">Current Risk Index</span>
      <span className={`text-6xl font-bold my-2 ${getStageColor(stage)}`}>{score}%</span>
      <span className={`text-xl font-semibold ${getStageColor(stage)}`}>{stage}</span>
    </div>
  );
};

export default RiskScore;
