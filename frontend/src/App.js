import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Leaderboard from './components/Leaderboard';
import PipelineDetails from './components/PipelineDetails';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Leaderboard />} />
      <Route path="/pipeline/:pipelineName" element={<PipelineDetails />} />
    </Routes>
  );
}

export default App;