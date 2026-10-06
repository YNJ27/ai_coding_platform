import { Filter, Search, SlidersHorizontal } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import Header from '../components/Header'
import ProblemCard from '../components/ProblemCard'
import { fetchProblems } from '../services/api'

const difficultyOptions = ['All', 'Easy', 'Medium', 'Hard']

function Problems() {
  const [query, setQuery] = useState('')
  const [difficulty, setDifficulty] = useState('All')
  const [problems, setProblems] = useState([])
  const [error, setError] = useState('')
  useEffect(() => {
    fetchProblems()
      .then((items) => setProblems(items.map((problem) => ({ ...problem, difficulty: problem.difficulty[0].toUpperCase() + problem.difficulty.slice(1), description: problem.description ?? '' }))))
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : 'Unable to load problems.'))
  }, [])
  const visibleProblems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()
    return problems.filter((problem) => {
      const matchesDifficulty = difficulty === 'All' || problem.difficulty === difficulty
      const matchesQuery = `${problem.title} ${problem.description}`.toLowerCase().includes(normalizedQuery)
      return matchesDifficulty && matchesQuery
    })
  }, [difficulty, problems, query])

  return (
    <div className="app-shell problems-page">
      <Header />
      <main className="problems-content">
        <section className="problems-hero">
          <div>
            <span className="eyebrow">THE PRACTICE ROOM <span className="eyebrow-line" /></span>
            <h1>Sharpen your<br /><em>thinking.</em></h1>
            <p>Small problems. Deep understanding.<br />Build the instincts that make good code feel inevitable.</p>
          </div>
          <div className="hero-stat"><span className="stat-number">{problems.length}</span><span>challenges<br />to explore</span></div>
        </section>

        <section className="problem-list-section" aria-labelledby="problem-list-title">
          <div className="section-heading">
            <div><span className="section-kicker">CURATED CHALLENGES</span><h2 id="problem-list-title">Choose your next problem</h2></div>
            <span className="count-label">{visibleProblems.length} of {problems.length} problems</span>
          </div>
          <div className="problem-toolbar">
            <label className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search problems..." /></label>
            <div className="filter-group"><SlidersHorizontal size={15} /><span>Difficulty</span>{difficultyOptions.map((level) => <button key={level} className={difficulty === level ? 'active' : ''} onClick={() => setDifficulty(level)}>{level}</button>)}</div>
            <button className="filter-button"><Filter size={15} /> Filters</button>
          </div>
          <div className="problem-table" role="table" aria-label="Coding problems">
            <div className="problem-table-header" role="row"><span role="columnheader">Problem</span><span role="columnheader">Difficulty</span><span role="columnheader">Action</span></div>
            <div className="problem-list">{visibleProblems.map((problem) => <ProblemCard problem={problem} key={problem.id} />)}</div>
            {error && <p className="no-problems">{error}</p>}
            {!error && visibleProblems.length === 0 && <p className="no-problems">No problems match your search.</p>}
          </div>
        </section>
      </main>
    </div>
  )
}

export default Problems
