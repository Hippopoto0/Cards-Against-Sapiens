import { motion } from 'framer-motion'
import React, { Fragment, useEffect, useLayoutEffect, useState } from 'react'
import { useCards } from '../stores/cards'
import anime from "animejs/lib/anime.es.js"
import { clientID, ws } from '../stores/webSocket'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useScoreStore } from '../stores/score'
import { Dialog, Transition } from '@headlessui/react'

function SelectWinner() {
    const {prompt, commitedCards, setCommitedCards} = useCards((state) => ({prompt: state.prompt, commitedCards: state.commitedCards, setCommitedCards: state.setCommitedCards}))
    const navigate = useNavigate()
    const [searchParams, setSearchParams] = useSearchParams()
    const roomID = searchParams.get("roomID")
    const { incrementScore } = useScoreStore((state) => ({ incrementScore: state.incrementScore }))

    const [preferredCard, setPreferredCard] = useState("")

    const [winnerCard, setWinnerCard] = useState("")
    const [winnerName, setWinnerName] = useState("")

    useLayoutEffect(() => {
        window.addEventListener("popstate", (e) => {
            e.preventDefault()

            navigate("/")
        })

        ws.onmessage = (e: MessageEvent<string>) => {
            let [header, content] = e.data.split("||")

            if (header === "receive_winner") {
                let winnerData = JSON.parse(content)

                let tempWinnerID = winnerData["client_id"]
                let tempWinnerUsername = winnerData["client_username"]
                let tempWinnerCardText = winnerData["client_card_text"]

                setWinnerCard(tempWinnerCardText)
                setWinnerName(tempWinnerUsername)

                console.log("winner is: " + tempWinnerUsername)
                if (tempWinnerID == clientID) incrementScore()

                ws.send("request_extra_card||")

                setTimeout(() => {
                    setWinnerName("")
                    setWinnerCard("")
                    
                    setTimeout(() => {
                        navigate("/game?roomID=" + roomID)
                    }, 200);
                }, 2000);

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

    function commitCardPreference(id_of_preference: string, textOfPreference: string) {
        if (preferredCard != "") return
        
        setPreferredCard(textOfPreference)

        ws.send(`add_score_to_card||${id_of_preference}`)
    } 
    
    return (
        <>
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
                            className={`anime-fade-children select-none p-2 text-sm font-semibold 
                            text-zinc-800 w-32 aspect-[3/4] bg-primary rounded-xl shadow-sm border-2 
                            border-zinc-300 hover:cursor-pointer transition-colors duration-500
                            ${preferredCard != "" && preferredCard != cardText ? "bg-zinc-400/50 text-zinc-800/30 hover:cursor-default" : ""}`}
                            onClick={() => commitCardPreference(clientID, cardText)}
                            >
                            {cardText}
                        </div>
                    })}
                </section>
            </div>
        </main> 
      <Transition appear show={winnerName != ""} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => {}}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-60 pointer-events-auto" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="relative w-full max-w-xs aspect-[3/4] transform overflow-hidden rounded-2xl bg-secondary p-6 text-left align-middle shadow-xl transition-all border-4 border-zinc-400">
                    <h1 className=' text-2xl font-bold'>{ winnerCard }</h1>

                    <div className='absolute bottom-0 left-0 h-12 w-full px-4 flex items-center justify-start bg-gradient-to-t from-zinc-200 to-transparent'>
                        <h1 className=' font-bold text-lg text-zinc-500'>{ winnerName }</h1>
                    </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>

        </>
    )
}

export default SelectWinner