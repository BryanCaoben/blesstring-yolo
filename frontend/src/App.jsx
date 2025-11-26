import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout'
import DetectionPage from './pages/Detection'
import AnnotationPage from './pages/Annotation'
import TrainingPage from './pages/Training'
import ModelsPage from './pages/Models'
import './App.css'

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Navigate to="/detection" replace />} />
          <Route path="/detection" element={<DetectionPage />} />
          <Route path="/annotation" element={<AnnotationPage />} />
          <Route path="/training" element={<TrainingPage />} />
          <Route path="/models" element={<ModelsPage />} />
        </Routes>
      </AppLayout>
    </Router>
  )
}

export default App

