import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList, CartesianGrid } from 'recharts';

/**
 * WaterfallChart component for Causal Chain visualization
 * Shows how different factors contribute to a win probability or risk change
 */
const WaterfallChart = ({ data }) => {
  if (!data || data.length === 0) return <div className="text-gray-400 italic">No causal events to display.</div>;

  // Transform data for a proper waterfall visualization
  // In a real waterfall, each bar starts where the previous one ended.
  let cumulative = 50; // Base value (e.g., initial win probability)
  const preparedData = [{
    cause: 'Base',
    impact: 50,
    displayImpact: [0, 50],
    rawImpact: 50
  }];

  data.forEach((item) => {
    const start = cumulative;
    cumulative += item.impact;
    preparedData.push({
      cause: item.cause,
      impact: item.impact,
      displayImpact: [start, cumulative],
      rawImpact: item.impact
    });
  });

  preparedData.push({
    cause: 'Total',
    impact: cumulative,
    displayImpact: [0, cumulative],
    rawImpact: 0,
    isTotal: true
  });

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={preparedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
          <XAxis dataKey="cause" stroke="#9ca3af" fontSize={10} tick={{ fill: '#9ca3af' }} />
          <YAxis stroke="#9ca3af" fontSize={10} tick={{ fill: '#9ca3af' }} domain={[0, 100]} />
          <Tooltip 
            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-gray-800 p-3 rounded-lg border border-gray-700 shadow-xl">
                    <p className="font-bold text-white mb-1">{data.cause}</p>
                    <p className={`${data.rawImpact >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      Impact: {data.rawImpact > 0 ? '+' : ''}{data.rawImpact}%
                    </p>
                    <p className="text-gray-400 text-xs mt-1">Resulting WP: {data.displayImpact[1]}%</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="displayImpact" radius={[4, 4, 0, 0]}>
            {preparedData.map((entry, index) => {
              let color = '#3b82f6'; // Base/Total
              if (!entry.isTotal && entry.cause !== 'Base') {
                color = entry.impact >= 0 ? '#10b981' : '#ef4444';
              }
              if (entry.isTotal) color = '#636efa';
              return <Cell key={`cell-${index}`} fill={color} />;
            })}
            <LabelList 
              dataKey="rawImpact" 
              position="top" 
              content={(props) => {
                const { x, y, width, value, index } = props;
                if (index === 0 || index === preparedData.length - 1) return null;
                return (
                  <text x={x + width / 2} y={y - 10} fill={value >= 0 ? '#10b981' : '#ef4444'} fontSize={10} fontWeight="bold" textAnchor="middle">
                    {value > 0 ? '+' : ''}{value}%
                  </text>
                );
              }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WaterfallChart;
