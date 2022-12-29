import React, { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useNavigate } from "react-router-dom"
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function EnterRoom() {
    const [inputText, setInputText] = useState(" ")
    const codeInputEl = useRef<HTMLInputElement>(null)

    const [codeDigits, setCodeDigits] = useState(Array(4).fill(" ") as Array<string>)
    const [digitIndex, setDigitIndex] = useState(0)


    const navigate = useNavigate()

    useLayoutEffect(() => {
        codeInputEl.current?.focus()
    }, [])

    function decrementDigitIndex() {
        if (digitIndex == 0) return

        setDigitIndex(digitIndex - 1)
    }

    function incrementDigitIndex() {
        if (digitIndex == 3) return

        setDigitIndex(digitIndex + 1)
    }

    useEffect(() => {
        if (inputText.length == 0) {
            codeDigits[digitIndex] = " "
            setInputText(" ")

            decrementDigitIndex()
        }

        if (inputText.length > 1) {
            let val = inputText.replace(" ", "")

            let letter = val[0]

            if ("abcdefghijklmnopqrstuvwxyzABCDEFGGHIJKLMNOPQRSTUVWXYZ".includes(letter)) {

                codeDigits[digitIndex] = val[0]
                

                incrementDigitIndex()
            }
        }
        setInputText(" ")


    }, [inputText])

    function joinRoom() {
        let roomName = codeDigits.join("")

        toast.error("That room doesn't exist yet!")
        // navigate(`/game?roomID=${roomName.toUpperCase()}`)
    }

    function createRoomCode(): string {
        var result           = '';
        var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var charactersLength = characters.length;
        for ( var i = 0; i < 4; i++ ) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }

        return result;
    }

    return (
        <>
        <main className=' w-full h-screen bg-secondary text-black center flex-col'>
            <div className=' flex gap-4 text-5xl uppercase font-bold'>
                {codeDigits.map((letter, i) =>
                    <div key={i} className=" w-16 h-20 text-center flex flex-col items-center justify-end cursor-pointer select-none"
                        onClick={() => { setDigitIndex(i); codeInputEl.current?.focus()}}
                    >
                        { letter != " " ? <p> { letter } </p> : <p className=' text-zinc-600'> {"ROOM"[i]} </p> }
                        <div className={`mt-2 w-12 ${digitIndex == i ? "h-3" : "h-2"} bg-zinc-800 transition-all`}></div>
                    </div>
                )}
            </div>
            {/* {inputText} */}
            <button 
            onClick={() => joinRoom()}
            className='mt-20 font-bold px-8 py-3 rounded-md bg-zinc-800 text-gray-50 hover:brightness-125'>Join Room</button>
        <ToastContainer position='bottom-left' hideProgressBar newestOnTop />
        </main>
        <input ref={codeInputEl} value={inputText} onBlur={() => setDigitIndex(100000000)} onChange={(e) => setInputText((e.target as HTMLInputElement).value)} className='opacity-0 absolute top-0 left-0 pointer-events-none' type="text" />
        <button 
        onClick={() => navigate(`/wait?roomID=${createRoomCode()}`)}
        className='absolute bottom-4 right-4 font-bold px-8 py-3 rounded-md text-zinc-800 border-2 bg-secondary border-zinc-800 hover:brightness-95'>Create Room</button>
        </>
    )
}

export default EnterRoom