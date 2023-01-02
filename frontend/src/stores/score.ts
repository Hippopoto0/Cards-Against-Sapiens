import create from "zustand"

interface ScoreState {
    score: number
    incrementScore: () => void
}

export const useScoreStore = create<ScoreState>()((set) => ({
    score: 0,
    incrementScore: () => set((state) => ({ score: state.score + 1 }))
}))

interface BearState {
  bears: number
  increase: (by: number) => void
}

const useBearStore = create<BearState>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}))