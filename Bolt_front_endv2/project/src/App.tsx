import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryPage } from './pages/QueryPage';
import { WordListPage } from './pages/WordListPage';
import { Navbar } from './components/Navbar';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <Navbar />
        <main className="py-8">
          <Routes>
            <Route path="/" element={<QueryPage />} />
            <Route path="/wordlist" element={<WordListPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;