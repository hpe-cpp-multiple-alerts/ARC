import React from "react";
import Dashboard from "./components/Dashboard";
import "./styles/Dashboard.css";
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import FeedbackPage from './components/FeedbackPage';

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/feedback/:graphId" element={<FeedbackPage />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
