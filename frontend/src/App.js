import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Leaderboard from './components/Leaderboard';
import PipelineDetails from './components/PipelineDetails';
import ExecutionPage from './components/ExecutionPage';
import Navigation from './components/Navigation';

function App() {
  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #2c3e50 0%, #34495e 50%, #3d566e 100%)',
      color: '#f5f5f5'
    }}>
      <Navigation />
      <Routes>
        <Route path="/" element={<Leaderboard />} />
        <Route path="/pipeline/:pipelineName" element={<PipelineDetails />} />
        <Route path="/execute" element={<ExecutionPage />} />
      </Routes>
    </div>
  );
}

export default App;