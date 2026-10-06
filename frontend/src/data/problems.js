export const problems = [
  {
    id: 'battleship',
    title: 'Battleship',
    difficulty: 'Easy',
    description: 'Place ships on a grid and determine whether a fleet can fit without collisions.',
  },
  {
    id: 'inventory-packer',
    title: 'Inventory Packer',
    difficulty: 'Easy',
    description: 'Pack the highest-value combination of supplies into a limited crate.',
  },
  {
    id: 'spell-checker',
    title: 'Spell Checker',
    difficulty: 'Easy',
    description: 'Suggest the closest correction for each unknown word in a document.',
  },
  {
    id: 'card-game',
    title: 'Card Game',
    difficulty: 'Medium',
    description: 'Build a strategy that maximizes your score across a row of cards.',
  },
  {
    id: 'friend-recommender',
    title: 'Friend Recommender',
    difficulty: 'Medium',
    description: 'Rank new connections using shared interests and network distance.',
  },
]

export const getProblem = (id) => problems.find((problem) => problem.id === id) ?? problems[0]
