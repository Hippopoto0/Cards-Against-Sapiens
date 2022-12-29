
import create from 'zustand'

interface CardsState {
    commitedCard: string,
    commitedCards: {[clientID: string]: string}
    prompt: string,
    answers: Array<string>
    setCommitedCard: (cardText: string) => void
    setPrompt: (cardText: string) => void
    setAnswers: (cards: Array<string>) => void
    pushToAnswers: (cardText: string) => void
    removeFromAnswers: (cardText: string) => void
    setCommitedCards: (cards: {clientID: string, cardText: string}) => void
}

export const useCards = create<CardsState>()((set, get) => ({
    commitedCard: "",
    commitedCards: {clientID: "", cardText: ""},
    prompt: "",
    answers: [],
    setCommitedCard: (cardText) => set((state) => ({ commitedCard: cardText })),
    setPrompt: (cardText) => set((state) => ({ prompt: cardText })),
    setAnswers: (cards) => set((state) => ({ answers: cards })),
    pushToAnswers: (cardText) => set((state) => ({ answers: [...state.answers, cardText] })),
    removeFromAnswers: (cardText) => {
      let newAnswers = get().answers.filter((text) => text != cardText)

      set((state) => ({ answers: newAnswers }))
    },
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