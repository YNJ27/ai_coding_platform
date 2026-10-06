import Editor from '@monaco-editor/react'
import { Braces, ChevronDown, MoreHorizontal } from 'lucide-react'

function CodeEditor({ file, value, onChange, onSave, saveMessage }) {
  const handleEditorMount = (editor, monaco) => {
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      onSave?.()
    })
  }

  return (
    <section className="editor-pane">
      <div className="editor-tabs"><div className="editor-tab active"><Braces size={14} />{file.name}{file.modified && <span className="tab-dot" />}</div><button className="editor-more" aria-label="More editor actions"><MoreHorizontal size={16} /></button></div>
      <div className="editor-breadcrumb"><span>src</span><ChevronDown size={12} /><strong>{file.name}</strong></div>
      <div className="monaco-wrap">
        <Editor height="100%" language={file.language} theme="vs-dark" value={value} onChange={onChange} onMount={handleEditorMount} options={{ minimap: { enabled: true }, lineNumbers: 'on', fontSize: 14, lineHeight: 24, padding: { top: 18 }, smoothScrolling: true, scrollBeyondLastLine: false, renderLineHighlight: 'all', fontFamily: 'JetBrains Mono, Consolas, monospace', automaticLayout: true }} />
      </div>
      <div className="editor-status"><span>Ln 8, Col 23</span><span>Spaces: 4</span><span>UTF-8</span><span>{file.language === 'python' ? 'Python' : 'JSON'}</span>{saveMessage && <span>{saveMessage}</span>}</div>
    </section>
  )
}

export default CodeEditor
