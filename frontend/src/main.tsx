import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import './index.css'
import Base from './routes/Base';
import EnterRoom from './routes/EnterRoom';
import { ToastContainer } from "react-toastify"
import SelectWinner from './routes/SelectWinner';
import Wait from './routes/Wait';
import Modal from './components/modal';

const router = createBrowserRouter([
  {
    path: "/",
    element: <EnterRoom />,
  },
  {
    path: "/game",
    element: <Base />,
  },
  {
    path: "/select",
    element: <SelectWinner />
  },
  {
    path: "/wait",
    element: <Wait />
  }
]);

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    {/* <App /> */}
    <RouterProvider router={router} />
    <Modal />
  </React.StrictMode>,
)
