import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import CodeEditor from '../components/CodeEditor'
import FileExplorer from '../components/FileExplorer'
import ProblemHeader from '../components/ProblemHeader'
import RightPanel from '../components/RightPanel'
import { createCodingSession, fetchProblem, fetchSessionFiles, getOrCreateUserId, runCodingSession, saveSessionFile } from '../services/api'

function CodingEnvironment() {
  const { problemId } = useParams()
  const [problem, setProblem] = useState(null)
  const [activeFile, setActiveFile] = useState('')
  const [fileContents, setFileContents] = useState({})
  const [fileMetadata, setFileMetadata] = useState([])
  const [sessionId, setSessionId] = useState('')
  const [loadError, setLoadError] = useState('')
  const [result, setResult] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [saveMessage, setSaveMessage] = useState('')
  const activeFileData = useMemo(() => fileMetadata.find((file) => file.path === activeFile) ?? fileMetadata[0], [activeFile, fileMetadata])
  const files = fileMetadata.map((file) => ({ ...file, modified: fileContents[file.path] !== file.content }))

  useEffect(() => {
    if (!problemId) return
    fetchProblem(problemId)
      .then((item) => {
        setProblem({ ...item, difficulty: item.difficulty[0].toUpperCase() + item.difficulty.slice(1) })
        return createCodingSession({ userId: getOrCreateUserId(), problemId: item.id })
      })
      .then((session) => {
        setSessionId(session.session_id)
        return fetchSessionFiles(session.session_id)
      })
      .then((sessionFiles) => {
        const nextFiles = sessionFiles.map((file) => ({ ...file, name: file.path.split('/').pop(), modified: false }))
        setFileMetadata(nextFiles)
        setFileContents(Object.fromEntries(nextFiles.map((file) => [file.path, file.content])))
        setActiveFile(nextFiles[0]?.path ?? '')
      })
      .catch((error) => setLoadError(error instanceof Error ? error.message : 'Unable to open problem.'))
  }, [problemId])

  const handleSave = async () => {
    if (!sessionId) {
      setSaveMessage('Session is not connected.')
      return
    }
    try {
      await saveSessionFile({ sessionId, path: activeFile, content: fileContents[activeFile] ?? '' })
      setSaveMessage('Saved')
    } catch (error) {
      setSaveMessage(error instanceof Error ? error.message : 'Unable to save file.')
    }
  }

  const handleRun = async () => {
    if (isRunning) return
    setIsRunning(true)
    try {
      if (sessionId) {
        const execution = await runCodingSession(sessionId)
        setResult({
          stdout: execution.stdout,
          stderr: execution.stderr,
          exitCode: execution.status === 'passed' ? 0 : 1,
          executionTime: execution.execution_time_ms / 1000,
        })
      } else {
        setResult({ stdout: '', stderr: 'The coding session is still loading.', exitCode: 1, executionTime: 0 })
      }
    } catch (error) {
      setResult({ stdout: '', stderr: error instanceof Error ? error.message : 'Unable to run the program.', exitCode: 1, executionTime: 0 })
    } finally {
      setIsRunning(false)
    }
  }

  return (
    <div className="ide-shell">
      {loadError && <div className="no-problems">{loadError}</div>}
      {problem && <ProblemHeader problem={problem} onRun={handleRun} isRunning={isRunning} />}
      <div className="ide-layout">
        <FileExplorer files={files} activeFile={activeFile} onSelect={setActiveFile} rootName="BATTLESHIP" />
        {activeFileData && <CodeEditor file={{ ...activeFileData, modified: fileContents[activeFile] !== activeFileData.content }} value={fileContents[activeFile]} onChange={(value) => setFileContents((current) => ({ ...current, [activeFile]: value ?? '' }))} onSave={handleSave} saveMessage={saveMessage} />}
        {problem && <RightPanel sessionId={sessionId} result={result} isRunning={isRunning} onClear={() => setResult(null)} problemTitle={problem.title} currentFile={activeFile} />}
      </div>
    </div>
  )
}

export default CodingEnvironment
