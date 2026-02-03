import React from 'react';
import Dashboard from './components/Dashboard';
import DemoDashboard from './components/DemoDashboard';

function App() {
  // Vite exposes env via `import.meta.env.*` (only `VITE_` prefixed keys).
  // We also keep `REACT_APP_DEMO_MODE` for compatibility with earlier tooling/docs.
  const demoFlag = (
    import.meta.env?.VITE_DEMO_MODE ||
    import.meta.env?.VITE_REACT_APP_DEMO_MODE ||
    process.env.REACT_APP_DEMO_MODE ||
    ''
  );
  const isDemo = String(demoFlag).toLowerCase() === 'true';
  return (
    <div className="App">
      {isDemo ? <DemoDashboard /> : <Dashboard />}
    </div>
  );
}

export default App;
