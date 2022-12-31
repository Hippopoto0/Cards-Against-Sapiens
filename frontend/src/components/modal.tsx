import { AnimatePresence, motion } from 'framer-motion'
import React from 'react'
import { userUsernameStore } from '../stores/username'
import create from 'zustand'

interface BearState {
  bears: number
  increase: (by: number) => void
}

const useBearStore = create<BearState>()((set) => ({
  bears: 0,
  increase: (by) => set((state) => ({ bears: state.bears + by })),
}))

interface ModalState {
    isOpen: boolean
    setOpen: (val: boolean) => void
}

export const useModalStore = create<ModalState>()((set) => ({
    isOpen: false,
    setOpen: (val) => set({ isOpen: val })
}))

function Modal() {
    const { username, setUsername } = userUsernameStore((state) => ({ username: state.username, setUsername: state.setUsername }))

    const { isOpen, setOpen } = useModalStore((state) => ({ isOpen: state.isOpen, setOpen: state.setOpen }))

    return (
        <AnimatePresence >
            { isOpen &&
            <>
            <motion.div
            key={"bg-div"} 
            initial={{ x: 200 }}
            animate={{ x: 0, opacity: "100%" }}
            exit={{ opacity: "0%" }}
            className=' absolute top-0 left-0 w-screen h-screen bg-zinc-900/80 '></motion.div>

            <motion.div 
            key="modal-div"
            initial={{ scale: 0.8, opacity: "0%" }}
            animate={{ scale: 1, opacity: "100%" }}
            exit={{ scale: 0.8, opacity: "0%" }}
            className=' absolute top-0 left-0 w-screen h-screen flex items-center justify-center'>
                <div className=' w-96 h-60 rounded-2xl bg-secondary p-4 flex flex-col items-center'>
                    <h1 className=' text-2xl  font-bold text-zinc-700'>Enter a Username</h1>

                    <input onChange={(e) => setUsername(e.target.value)} type="text" placeholder='Username' className='mt-10 p-2 rounded-xl border-2 border-zinc-300 font-bold text-md outline-none text-slate-700' />

                    <div className=' mt-auto w-full h-12 flex gap-4 items-center justify-end'>

                        <button 
                        onClick={() => {}}
                        className=' font-bold px-[calc(1rem-2px)] py-[calc(0.5rem-2px)] text-sm rounded-md text-zinc-800 border-2 bg-secondary border-zinc-800 hover:brightness-95'>
                            Cancel
                        </button>
                        <button 
                        onClick={() => setOpen(false)}
                        className='font-bold px-4 py-2 text-sm rounded-md bg-zinc-800 text-gray-50 hover:brightness-125'>
                            Join
                        </button>
                    </div>
                </div>
            </motion.div>
            </>
            }
        </AnimatePresence>
    )
}

export default Modal