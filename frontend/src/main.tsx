import React from 'react'
import ReactDOM from 'react-dom/client'
import { Shell } from './shell/Shell'
import './design-tokens.css'
import './styles-v1.1.css'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Shell />
  </React.StrictMode>
)
