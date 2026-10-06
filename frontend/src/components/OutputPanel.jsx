import { AlertCircle, CheckCircle2, Clock3, Copy, Trash2 } from 'lucide-react'

function OutputPanel({ result, isRunning, onClear }) {
  const hasError = result?.exitCode !== 0

  return (
    <section className="output-panel">
      <div className="output-header"><div className="output-heading"><span>OUTPUT</span>{result && <span className={hasError ? 'execution-status error' : 'execution-status success'}>{hasError ? 'Execution error' : 'Success'}</span>}</div><div className="output-tools">{result && <span><Clock3 size={13} /> {result.executionTime.toFixed(2)}s</span>}<button onClick={onClear} aria-label="Clear output"><Trash2 size={14} /></button></div></div>
      <div className="output-body">
        {isRunning && <div className="output-state running"><span className="spinner" /><strong>Running main.py...</strong><span>Preparing your execution</span></div>}
        {!isRunning && !result && <div className="output-state"><AlertCircle size={18} /><span>Run your code to see output here</span></div>}
        {!isRunning && result && <div className={`execution-result ${hasError ? 'has-error' : 'is-success'}`}>
          <div className="result-banner">{hasError ? <AlertCircle size={16} /> : <CheckCircle2 size={16} />}<strong>{hasError ? 'Execution failed' : 'Run completed successfully'}</strong><span>Exit code {result.exitCode}</span></div>
          {result.stdout && <div className="output-section"><div className="output-section-heading">stdout</div><pre className="terminal-output">{result.stdout}</pre><button className="copy-output" onClick={() => navigator.clipboard?.writeText(result.stdout)}><Copy size={13} /> Copy stdout</button></div>}
          {result.stderr && <div className="output-section error-section"><div className="output-section-heading">stderr / error</div><pre className="terminal-output">{result.stderr}</pre></div>}
        </div>}
      </div>
    </section>
  )
}

export default OutputPanel
