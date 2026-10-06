import { useEffect } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import CodingEnvironment from './pages/CodingEnvironment'
import Problems from './pages/Problems'
import { getOrCreateUserId } from './services/api'

function App() {
  useEffect(() => {
    getOrCreateUserId()
  }, [])

  return <BrowserRouter><Routes><Route path="/" element={<Problems />} /><Route path="/problems/:problemId" element={<CodingEnvironment />} /><Route path="*" element={<Navigate to="/" replace />} /></Routes></BrowserRouter>
}

export default App
