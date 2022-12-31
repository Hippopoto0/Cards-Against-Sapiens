import create from "zustand";


interface usernameState {
    username: string
    setUsername: (text: string) => void
}

export const userUsernameStore = create<usernameState>()((set) => ({
    username: "",
    setUsername: (text) => set((state) => ({ username: text }))
}))

interface BearState {
  bears: number
  increase: (by: number) => void
}

const useBearStore = create<BearState>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}))