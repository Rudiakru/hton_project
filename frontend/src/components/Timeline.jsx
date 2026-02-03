import React from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  ReferenceLine, 
  ReferenceArea,
  CartesianGrid
} from 'recharts';

const Timeline = ({ data, teamfights = [], onPointClick }) => {
  return (
    <div className="w-full h-full min-h-[300px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart 
          data={data} 
          onClick={(e) => {
            if (e && e.activePayload && onPointClick) {
              onPointClick(e.activePayload[0].payload);
            }
          }}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
          <XAxis dataKey="game_time" stroke="#9ca3af" fontSize={12} />
          <YAxis stroke="#9ca3af" fontSize={12} />
          
          {/* Background Zones for Risk Stages */}
          <ReferenceArea y1={0} y2={20} fill="#10b981" fillOpacity={0.05} />
          <ReferenceArea y1={20} y2={40} fill="#f59e0b" fillOpacity={0.05} />
          <ReferenceArea y1={40} y2={60} fill="#f97316" fillOpacity={0.05} />
          <ReferenceArea y1={60} y2={100} fill="#ef4444" fillOpacity={0.05} />

          {/* Teamfight Markers */}
          {teamfights.map((tf, idx) => (
            <ReferenceLine 
              key={idx}
              x={tf.start_time} 
              stroke={tf.won ? '#10B981' : '#EF4444'}
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ 
                value: 'TF', 
                position: 'top', 
                fill: tf.won ? '#10B981' : '#EF4444', 
                fontSize: 10,
                fontWeight: 'bold'
              }}
            />
          ))}

          <Tooltip 
            contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }}
            itemStyle={{ color: '#fff' }}
          />
          <Legend />
          
          <ReferenceLine y={0} stroke="#4b5563" strokeDasharray="3 3" />
          
          <Line 
            type="monotone" 
            dataKey="gold_diff" 
            stroke="#3b82f6" 
            strokeWidth={2} 
            dot={false}
            activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff' }}
            name="Gold Diff"
          />
          <Line 
            type="monotone" 
            dataKey="risk_score" 
            stroke="#ef4444" 
            strokeWidth={3} 
            dot={false}
            activeDot={{ r: 8, fill: '#ef4444', stroke: '#fff', cursor: 'pointer' }}
            name="Risk Score"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default Timeline;
