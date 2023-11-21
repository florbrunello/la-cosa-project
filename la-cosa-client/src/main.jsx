import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './app';

const domNode = document.getElementById("root");
const root = ReactDOM.createRoot(domNode);

root.render(
    <BrowserRouter>
        <App />
    </BrowserRouter>
)