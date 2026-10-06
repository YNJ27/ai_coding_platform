import { Code2, Command, LayoutGrid, LogIn, Sparkles } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

function Header() {
  const location = useLocation()

  return (
    <header className="site-header">
      <Link className="brand" to="/">
        <span className="brand-mark"><Code2 size={17} strokeWidth={2.5} /></span>
        <span>arc<span className="brand-dot">.</span>lab</span>
      </Link>
      <nav className="main-nav" aria-label="Main navigation">
        <Link className={location.pathname === '/' ? 'active' : ''} to="/"><LayoutGrid size={15} /> Problems</Link>
        <a href="#workspace"><Command size={15} /> Playground</a>
      </nav>
      <div className="header-actions">
        <span className="status-pill"><span className="status-dot" /> Workspace online</span>
        <button className="icon-button" aria-label="AI assistant"><Sparkles size={17} /></button>
        <button className="profile-button" aria-label="Sign in"><LogIn size={15} /><span>Sign in</span></button>
      </div>
    </header>
  )
}

export default Header
