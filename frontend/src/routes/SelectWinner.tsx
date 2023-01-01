import { motion } from 'framer-motion'
import React, { useEffect, useLayoutEffect } from 'react'
import { useCards } from '../stores/cards'
import anime from "animejs/lib/anime.es.js"
import { ws } from '../stores/webSocket'
import { useNavigate, useSearchParams } from 'react-router-dom'

function SelectWinner() {
    const {prompt, commitedCards, setCommitedCards} = useCards((state) => ({prompt: state.prompt, commitedCards: state.commitedCards, setCommitedCards: state.setCommitedCards}))
    const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const roomID = searchParams.get("roomID")

    useLayoutEffect(() => {
        ws.onmessage = (e: MessageEvent<string>) => {
            let [header, content] = e.data.split("||")

            if (header === "receive_winner") {
                console.log("winner is: " + content)
                ws.send("request_extra_card||")
                navigate("/game?roomID=" + roomID)
            }
        }
    }, [])

    useEffect(() => {
        anime({
            targets: [".anime-fade-children"],
            //   targets: '.staggering-easing-demo .el',
            translateY: [70, 0],
            opacity: [0, 1],
            duration: 1000,
            delay: anime.stagger(600, {easing: 'linear', start: 300}),
            easing: "easeOutElastic(1, 1)",
            // translateY: [70, 0],
            // opacity: [0, 1],
            // duration: 4000,
            // stagger: anime.stagger(200)
        })

    }, [])

    function commitCardPreference(id_of_preference: string) {
        ws.send(`add_score_to_card||${id_of_preference}`)
    } 
    
    return (
        <main className=' w-full bg-secondary center overflow-x-hidden'>
            <div className='overflow-x-hidden flex items-center flex-col md:flex-row w-full xl:w-[1280px] h-screen bg-secondary overflow-y-scroll'>
                <section className='w-full md:w-80 center p-8'>
                <div className=' p-4 text-primary font-bold text-xl cursor-default select-none w-56 md:w-72 aspect-[3/5] bg-zinc-800 rounded-3xl shadow-lg'>
                    { prompt }
                </div>
                </section>
                <section className=' my-8 md:my-0 grid gap-y-10 md:gap-y-10 lg:gap-y-20 p-4 place-items-center grid-cols-2 grid-rows-5 md:grid-cols-4 md:grid-rows-3 w-full xs:w-4/5 sm:w-3/5 md:w-full h-auto lg:grid-cols-5 lg:grid-rows-2 flex-1'>
                    {Object.keys(commitedCards).map((clientID, i) => {
                        let cardText = commitedCards[clientID]

                        return <div 
                            key={i} 
                            className='anime-fade-children select-none p-2 text-sm font-semibold text-zinc-800 w-32 aspect-[3/4] bg-primary rounded-xl shadow-sm border-2 border-zinc-300 hover:cursor-pointer'
                            onClick={() => commitCardPreference(clientID)}
                            >
                            {cardText}
                        </div>
                    })}
                </section>
            </div>
        </main>  
    )
}

export default SelectWinner