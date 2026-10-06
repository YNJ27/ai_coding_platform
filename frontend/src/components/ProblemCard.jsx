import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'

function ProblemCard({ problem }) {
  return (
    <article className="problem-card">
      <div className="problem-cell">
        <h3>{problem.title}</h3>
        <p>{problem.description}</p>
      </div>
      <div className={`difficulty-cell difficulty-${problem.difficulty.toLowerCase()}`}>
        {problem.difficulty}
      </div>
      <div className="action-cell">
        <Link className="solve-button" to={`/problems/${problem.id}`}>
          Solve
          <ArrowUpRight size={15} />
        </Link>
      </div>
    </article>
  )
}

export default ProblemCard
