export const RISK_STAGES = {
  WINNING: {
    label: 'WINNING',
    color: '#10B981',
    bg: 'bg-green-500/10',
    border: 'border-green-500',
    message: 'Maintain vision control, extend lead safely.'
  },
  COMPETITIVE: {
    label: 'COMPETITIVE',
    color: '#F59E0B',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500',
    message: 'Focus on objective setup, avoid risky plays.'
  },
  VULNERABLE: {
    label: 'VULNERABLE',
    color: '#F97316',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500',
    message: 'Vision score dropping - improve ward coverage.'
  },
  CRITICAL: {
    label: 'CRITICAL',
    color: '#EF4444',
    bg: 'bg-red-500/10',
    border: 'border-red-500',
    message: 'Spacing violations detected - regroup before next fight.'
  }
};

export const EVENT_IMPACTS = {
  dragon_lost: -6,
  baron_lost: -12,
  tower_lost: -3,
  death_carry: -4,
  death_support: -2,
  gold_swing_1k: -2
};
