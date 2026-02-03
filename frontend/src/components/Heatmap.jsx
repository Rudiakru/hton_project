import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist';

const Heatmap = ({ data }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (chartRef.current && data) {
      const plotData = [{
        z: data,
        type: 'heatmap',
        colorscale: 'Viridis',
        showscale: true
      }];

      const layout = {
        title: 'Death Exposure Heatmap',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#fff' },
        xaxis: { title: 'Map X', gridcolor: '#374151' },
        yaxis: { title: 'Map Y', gridcolor: '#374151' },
        margin: { t: 40, b: 40, l: 40, r: 40 }
      };

      Plotly.newPlot(chartRef.current, plotData, layout, { responsive: true });
    }
  }, [data]);

  return <div ref={chartRef} className="w-full h-full min-h-[300px]" />;
};

export default Heatmap;
