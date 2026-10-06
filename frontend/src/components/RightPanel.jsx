import { BookOpen, Bot, TerminalSquare } from 'lucide-react'
import { useState } from 'react'
import AIChat from './AIChat'
import OutputPanel from './OutputPanel'

const tabs = [
  { id: 'guide', label: 'Guide', icon: BookOpen },
  { id: 'output', label: 'Output', icon: TerminalSquare },
  { id: 'ai', label: 'AI Assist', icon: Bot },
]

function RightPanel({ sessionId, result, isRunning, onClear, problemTitle, currentFile }) {
  const [activeTab, setActiveTab] = useState('output')

  return (
    <aside className="right-panel">
      <div className="right-panel-tabs" role="tablist" aria-label="Workspace panels">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button key={id} className={activeTab === id ? 'active' : ''} onClick={() => setActiveTab(id)} role="tab" aria-selected={activeTab === id}>
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>
      <div className="right-panel-content">
        {activeTab === 'output' && <OutputPanel result={result} isRunning={isRunning} onClear={onClear} />}
        {activeTab === 'guide' && <div className="panel-placeholder"><BookOpen size={20} /><strong>Problem guide</strong><p>Read the prompt and examples here while you work through the solution.</p></div>}
        {activeTab === 'ai' && <AIChat sessionId={sessionId} problemTitle={problemTitle} currentFile={currentFile} />}
      </div>
    </aside>
  )
}

export default RightPanel
