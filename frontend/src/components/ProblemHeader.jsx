import { ArrowLeft, CircleHelp, Info, LogOut, Play } from 'lucide-react'
import { Link } from 'react-router-dom'

function ProblemHeader({ problem, onRun, isRunning }) {
  return (
    <div className="workspace-header">
      <div className="workspace-title">
        <Link className="back-link" to="/" aria-label="Back to problems"><ArrowLeft size={16} /></Link>
        <div><span className="workspace-kicker">Coding challenge</span><h1>{problem.title} <Info size={14} aria-label="Problem information" /></h1></div>
      </div>
      <div className="workspace-actions">
        <button className="run-button" onClick={onRun} disabled={isRunning}><Play size={14} fill="currentColor" /> {isRunning ? 'Running...' : 'Run Main'}</button>
        <Link className="exit-button" to="/"><LogOut size={14} /> Exit</Link>
        <button className="help-button" aria-label="Help"><CircleHelp size={17} /></button>
      </div>
    </div>
  )
}

export default ProblemHeader
