import { ChevronDown, ChevronRight, FileCode2, Folder, FolderOpen, GitBranch, Search } from 'lucide-react'
import { useState } from 'react'

function FileExplorer({ files, activeFile, onSelect, rootName = 'ARC LAB', folderName = 'src' }) {
  const [expandedFolders, setExpandedFolders] = useState({ [folderName]: true })
  const isExpanded = expandedFolders[folderName]
  const toggleFolder = (folder) => setExpandedFolders((current) => ({ ...current, [folder]: !current[folder] }))

  return (
    <aside className="file-explorer">
      <div className="panel-label"><span>Explorer</span><span className="explorer-actions"><Search size={15} /><span>...</span></span></div>
      <div className="workspace-folder"><ChevronDown size={14} /><FolderOpen size={15} className="folder-color" /><span>{rootName}</span></div>
      <div className="file-tree">
        <button className="tree-folder tree-folder-button" onClick={() => toggleFolder(folderName)} aria-expanded={isExpanded}>
          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />} {isExpanded ? <FolderOpen size={15} className="folder-color" /> : <Folder size={15} className="folder-color" />}<span>{folderName}</span>
        </button>
        {isExpanded && files.map((file) => <button key={file.path} className={`tree-file ${activeFile === file.path ? 'selected' : ''}`} onClick={() => onSelect(file.path)}><FileCode2 size={15} /><span>{file.name}</span>{file.modified && <i />}</button>)}
      </div>
      <div className="explorer-footer"><GitBranch size={14} /> main <span className="footer-spacer" /> 0↓ 0↑</div>
    </aside>
  )
}

export default FileExplorer
