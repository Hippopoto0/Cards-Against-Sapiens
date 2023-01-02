import React, { Fragment, useLayoutEffect, useState } from 'react'
import { MutatingDots } from 'react-loader-spinner'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { TbClipboard } from "react-icons/tb"

import { ws, clientID } from '../stores/webSocket'
import { Dialog, Transition } from '@headlessui/react'
import { userUsernameStore } from '../stores/username'

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

    const [isModalOpen, setModalOpen] = useState(false)
    
    const [searchParams, setSearchParams] = useSearchParams()
    const navigate = useNavigate()
    const roomID = searchParams.get("roomID")

    const [clientsInRoom, setClientsInRoom] = useState([])

    const { username, setUsername } = userUsernameStore((state) => ({ username: state.username, setUsername: state.setUsername }))
    // console.log("socket: " + ws.readyState)

    useLayoutEffect(() => {
        if (username == "") setModalOpen(true)
        // this will run if ws has already been established
        // ie if coming from main page

        
        // ws.readyState && ws.send(`add_to_waiting_room||${roomID}`)
        if (username != "") { ws.readyState && ws.send(`add_to_waiting_room||${JSON.stringify({"roomID": roomID, "username": username})}`) }

        ws.onmessage = (e: MessageEvent<String>) => {
            const [header, content] = e.data.split("||")

            // this runs if ws hadn't previously been established (direct from link)
            if (header === "receive_connection") {
                // ws.send(`add_to_waiting_room||${roomID}`)
                if (username != "") { ws.readyState && ws.send(`add_to_waiting_room||${JSON.stringify({"roomID": roomID, "username": username})}`) }
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
        <>
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
   <Transition appear show={isModalOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={() => { setModalOpen(false); setTimeout(() => {
          navigate("/")
        }, 200);}}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-60" />
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
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-secondary p-6 text-left align-middle shadow-xl transition-all flex flex-col items-center justify-center">
                  <Dialog.Title
                    as="h3"
                    className="text-2xl font-bold text-center leading-6 text-zinc-800"
                  >
                    Enter a Username
                  </Dialog.Title>
                  <input type="text" placeholder='Username' onChange={(e) => setUsername(e.target.value)} className=' rounded-md p-2 font-bold mt-8 outline-none focus:outline-2 focus:outline-zinc-3 00' />

                  <div className="mt-8 w-full flex">
                    <button 
                        onClick={() => { setModalOpen(false); setTimeout(() => {
          navigate("/")
        }, 200);}}
                        className='ml-auto font-bold px-6 py-3 rounded-md text-zinc-800 border-2 bg-secondary border-zinc-800 hover:brightness-95'
                    >
                        Menu
                    </button>
                   
                    <button 
                        onClick={() => {
                          setModalOpen(false)

                          if (username != "") { ws.readyState && ws.send(`add_to_waiting_room||${JSON.stringify({"roomID": roomID, "username": username})}`) }
                        }}
                        className='ml-4 font-bold px-6 py-3 rounded-md bg-zinc-800 text-gray-50 hover:brightness-125'
                    >
                        Join
                    </button>
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

export default Wait