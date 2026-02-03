import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

/**
 * CohesionChart component showing team spread over time
 */
const CohesionChart = ({ data }) => {
  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorCohesion" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
          <XAxis dataKey="game_time" stroke="#9ca3af" fontSize={10} />
          <YAxis stroke="#9ca3af" fontSize={10} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
          />
          <Area 
            type="monotone" 
            dataKey="cohesion_score" 
            stroke="#3b82f6" 
            fillOpacity={1} 
            fill="url(#colorCohesion)" 
            name="Cohesion Index"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CohesionChart;
