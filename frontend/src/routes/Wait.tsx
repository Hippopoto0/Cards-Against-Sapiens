import React, { useLayoutEffect, useState } from 'react'
import { MutatingDots } from 'react-loader-spinner'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { TbClipboard } from "react-icons/tb"

import { ws, clientID } from '../stores/webSocket'

function copyTextToClipboard(text: string) {
  var textArea = document.createElement("textarea");

  //
  // *** This styling is an extra step which is likely not required. ***
  //
  // Why is it here? To ensure:
  // 1. the element is able to have focus and selection.
  // 2. if the element was to flash render it has minimal visual impact.
  // 3. less flakyness with selection and copying which **might** occur if
  //    the textarea element is not visible.
  //
  // The likelihood is the element won't even render, not even a
  // flash, so some of these are just precautions. However in
  // Internet Explorer the element is visible whilst the popup
  // box asking the user for permission for the web page to
  // copy to the clipboard.
  //

  // Place in the top-left corner of screen regardless of scroll position.
  textArea.style.position = 'fixed';
  textArea.style.top = "0";
  textArea.style.left = "0";

  // Ensure it has a small width and height. Setting to 1px / 1em
  // doesn't work as this gives a negative w/h on some browsers.
  textArea.style.width = '2em';
  textArea.style.height = '2em';

  // We don't need padding, reducing the size if it does flash render.
  textArea.style.padding = "0";

  // Clean up any borders.
  textArea.style.border = 'none';
  textArea.style.outline = 'none';
  textArea.style.boxShadow = 'none';

  // Avoid flash of the white box if rendered for any reason.
  textArea.style.background = 'transparent';


  textArea.value = text;

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    var successful = document.execCommand('copy');
    var msg = successful ? 'successful' : 'unsuccessful';
    console.log('Copying text command was ' + msg);
  } catch (err) {
    console.log('Oops, unable to copy');
  }

  document.body.removeChild(textArea);
}

function Wait() {
    
    const [searchParams, setSearchParams] = useSearchParams()
    const navigate = useNavigate()
    const roomID = searchParams.get("roomID")

    const [clientsInRoom, setClientsInRoom] = useState([])
    // console.log("socket: " + ws.readyState)

    useLayoutEffect(() => {
        // this will run if ws has already been established
        // ie if coming from main page
        ws.readyState && ws.send(`add_to_waiting_room||${roomID}`)

        ws.onmessage = (e: MessageEvent<String>) => {
            const [header, content] = e.data.split("||")

            // this runs if ws hadn't previously been established (direct from link)
            if (header === "receive_connection") {
                ws.send(`add_to_waiting_room||${roomID}`)
            }

            if (header === "receive_waiting_players") {
                console.log("gotta get rid maybe: " + content)
                setClientsInRoom(JSON.parse(content))
            }

            if (header === "receive_goto_game") {
                navigate(`/game?roomID=${roomID}`)
            }
        }
    }, [])

    function startGotoGame() {
        ws.send("start_game_from_wait||")


    }

    return (
        <main className=' w-full h-screen bg-secondary center flex-col'>
            <div className=' flex gap-4 text-5xl uppercase font-bold'>
                {roomID?.split("").map((letter, i) =>
                    <div key={i} className=" w-16 h-20 text-center flex flex-col items-center justify-end select-none"
                    >
                        { letter != " " ? <p className=' text-zinc-800'> { letter } </p> : <p className=' text-zinc-600'> {"ROOM"[i]} </p> }
                        <div className={`mt-2 w-12 h-2 bg-zinc-800 transition-all`}></div>
                    </div>
                )}
            </div>

            <div className=' w-96 max-w-[80vw] flex flex-col items-center justify-start mt-5 mb-5'>
                <div className='mr-4 mb-4 relative flex items-center justify-center pb-2 pt-6'>
                    <div className=' absolute -right-20'>
                        <MutatingDots 
                            height="100"
                            width="100"
                            color="rgb(82,82,91)"
                            secondaryColor= 'rgb(82,82,91)'
                            radius='12.5'
                            ariaLabel="mutating-dots-loading"
                            wrapperStyle={{}}
                            wrapperClass=" scale-[40%] brightness-110"
                            visible={true}
                        />
                    </div>
                    <p className=' text-zinc-600 font-semibold select-none'>Waiting for Players</p>

                </div>
                <div className='p-4 w-full rounded-xl min-h-[12rem] bg-primary flex flex-col shadow-sm border-2 border-zinc-300'>
                    {clientsInRoom.map((clientName, i) => 
                        <h2 key={i} className="font-semibold text-zinc-700 select-none">{ clientName }</h2>
                    )}
                </div>
            </div>

            <div className=' flex gap-5 items-end justify-center'>
                <button 
                onClick={() => copyTextToClipboard(window.location.toString())}
                className='flex flex-row items-center justify-between font-bold px-[calc(2rem-2px)] py-[calc(0.75rem-2px)] rounded-md text-zinc-800 border-2 bg-secondary border-zinc-800 hover:brightness-95'>
                    Copy Link
                    <TbClipboard className=' translate-x-3 text-zinc-800' strokeWidth={3} />
                </button>
                <button 
                onClick={() => startGotoGame()}
                className='mt-5 font-bold px-8 py-3 rounded-md bg-zinc-800 text-gray-50 hover:brightness-125'>
                    Start Game
                </button>
            </div>
        </main>
    )
}

export default Wait