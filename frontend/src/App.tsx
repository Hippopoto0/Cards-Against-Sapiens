import { motion } from 'framer-motion'
import React, { useLayoutEffect, useState } from 'react'

function App() {
  // const [ws, setWS] = useState<WebSocket>()
  const [prompt, setPrompt] = useState("")
  const [answers, setAnswers] = useState<string[]>([])
  let client_id = Date.now().toString()
  let ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`)

  useLayoutEffect(() => {
    ws.onmessage = (e: MessageEvent<String>) => {
      // console.log(e.data)
      let [header, content] = e.data.split("||")
      console.log(header)
      if (header === "receive_connection") {
        ws.send("get_prompt||")
        ws.send("get_answers||")
      }
      if (header === "receive_prompt") {
        console.log(content)
        setPrompt(content)
      }
      if (header === "receive_answers") {
        let result: string[] = []
        JSON.parse(content).forEach((element: any) => {
          result.push(element.text)
        });

        setAnswers(result)
        console.log(JSON.parse(content))
      }
    }
  }, [])

  return (
    <main className=' w-full bg-secondary center overflow-x-hidden'>
      <div className='overflow-x-hidden flex items-center flex-col md:flex-row w-full xl:w-[1280px] h-screen bg-secondary overflow-y-scroll'>
        <section className='w-full md:w-80 center p-8'>
          <div className=' p-4 text-primary font-bold text-xl cursor-default select-none w-56 md:w-72 aspect-[3/5] bg-zinc-900 rounded-3xl shadow-lg'>
            { prompt }
          </div>
        </section>
        <section className='my-8 md:my-0 grid gap-y-10 md:gap-y-10 lg:gap-y-20 p-4 place-items-center grid-cols-2 grid-rows-5 md:grid-cols-4 md:grid-rows-3 w-full xs:w-4/5 sm:w-3/5 md:w-full h-auto lg:grid-cols-5 lg:grid-rows-2 flex-1'>
          {answers.map((cardText: string, i: number) => 
            <motion.div 
              key={i} 
              className='select-none p-2 text-sm font-semibold text-zinc-800 w-32 aspect-[3/4] bg-primary rounded-xl shadow-md hover:cursor-pointer'
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