import create from 'zustand'

export const clientID = Date.now().toString()
// export const ws = new WebSocket(`ws://localhost:8000/ws/${clientID}`)
export const ws = new WebSocket(`ws://cards-against-sapiens-server.onrender.com/ws/${clientID}`)

// interface WebSocketState {
//     ws: WebSocket,
//     clientID: string
// }

// let clientID = Date.now().toString()

// const useWebSocketStore = create<WebSocketState>()((set) => ({
//     ws: new WebSocket(`ws://localhost:8000/ws/${clientID}`),
//     clientID: clientID
// }))

interface BearState {
  bears: number
  increase: (by: number) => void
}

const useBearStore = create<BearState>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}))