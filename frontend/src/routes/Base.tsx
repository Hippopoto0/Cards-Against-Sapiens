import { motion } from 'framer-motion'
import React, { useEffect, useLayoutEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useCards } from '../stores/cards'
import { clientID, ws } from '../stores/webSocket'

function App() {
  // const [ws, setWS] = useState<WebSocket>()
  // const [prompt, setPrompt] = useState("")
  // const [answers, setAnswers] = useState<string[]>([])

  const {prompt, answers, setPrompt, setAnswers, pushToAnswers, removeFromAnswers, commitedCard, setCommitedCard, setCommitedCards} = useCards((state) => ({answers: state.answers, prompt: state.prompt, setPrompt: state.setPrompt, setAnswers: state.setAnswers, pushToAnswers: state.pushToAnswers, removeFromAnswers: state.removeFromAnswers, commitedCard: state.commitedCard, setCommitedCard: state.setCommitedCard, setCommitedCards: state.setCommitedCards}))

  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()

  const roomID = searchParams.get("roomID")
  console.log("roomID: " + roomID)

  // const [client_id, setClient_id] = useState("")
  // const [ws, setWs] = useState<WebSocket>();
  // const client_id = Date.now().toString()

  

  useLayoutEffect(() => {
    ws.readyState && ws.send(`join_room||${roomID}`)

    console.log(clientID)
    ws.onmessage = (e: MessageEvent<String>) => {
      // console.log(e.data)
      let [header, content] = e.data.split("||")
      if (header === "receive_connection") {
        ws.send(`join_room||${roomID}`)
        console.log("clientid" + clientID)
      }
      if (header === "receive_room") {
        ws.send(`get_prompt||`)
        ws.send(`get_answers||`)
      }
      if (header === "receive_prompt") {
        setPrompt(content)
      }
      if (header === "receive_answers") {
        let result: string[] = []
        JSON.parse(content).forEach((element: any) => {
          result.push(element.text)
        });

        setAnswers(result)
      }
      if (header === "receive_goto_selection") {
        console.log("Gotta go lol")
        console.log(content)
        let cardData = JSON.parse(content)
        setCommitedCards(cardData)
        console.log(`commited card: ${commitedCard}`)
        removeFromAnswers(commitedCard)
        setCommitedCard("")

        navigate(`/select?roomID=${roomID}`)
      }
      if (header === "receive_extra_card") {
        let newCardText = JSON.parse(content).text

         pushToAnswers(newCardText)
      }
    }
  }, [commitedCard]) // reacts to commited card so it can see its change in state within the onmessage

  function commitCard(cardText: string) {
    console.log(clientID)

    setCommitedCard(cardText)

    ws.send(`commit_card||${cardText}`)
    
  }

  return (
    <main className=' w-full bg-secondary center overflow-x-hidden'>
      <div className='overflow-x-hidden flex items-center flex-col md:flex-row w-full xl:w-[1280px] h-screen bg-secondary overflow-y-scroll'>
        <section className='w-full md:w-80 center p-8'>
          <div className=' p-4 text-primary font-bold text-xl cursor-default select-none w-56 md:w-72 aspect-[3/5] bg-zinc-800 rounded-3xl shadow-lg'>
            { prompt }
          </div>
        </section>
        <section className='my-8 md:my-0 grid gap-y-10 md:gap-y-10 lg:gap-y-20 p-4 place-items-center grid-cols-2 grid-rows-5 md:grid-cols-4 md:grid-rows-3 w-full xs:w-4/5 sm:w-3/5 md:w-full h-auto lg:grid-cols-5 lg:grid-rows-2 flex-1'>
          {answers.map((cardText: string, i: number) => 
            <motion.div 
              key={i} 
              className='select-none p-2 text-sm font-semibold text-zinc-800 w-32 aspect-[3/4] bg-primary rounded-xl shadow-sm border-2 border-zinc-300 hover:cursor-pointer'
              onClick={() => commitCard(cardText)}
            >
              {cardText}
            </motion.div>
          )}
        </section>
      </div>
    </main>
  )
}

export default App