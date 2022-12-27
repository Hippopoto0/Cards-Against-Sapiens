
import create from 'zustand'

interface CardsState {
    commitedCards: {[clientID: string]: string}
    prompt: string,
    answers: Array<string>
    setPrompt: (cardText: string) => void
    setAnswers: (cards: Array<string>) => void
    setCommitedCards: (cards: {clientID: string, cardText: string}) => void
}

export const useCards = create<CardsState>()((set) => ({
    commitedCards: {clientID: "", cardText: ""},
    prompt: "",
    answers: [],
    setPrompt: (cardText) => set((state) => ({ prompt: cardText })),
    setAnswers: (cards) => set((state) => ({ answers: cards })),
    setCommitedCards: (cards) => set((state) => ({ commitedCards: cards})),
}))

interface BearState {
  bears: number
  increase: (by: number) => void
}

const useBearStore = create<BearState>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}))