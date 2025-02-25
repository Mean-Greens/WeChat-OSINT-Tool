import React, { useState, useEffect } from 'react';
import { Plus, X } from 'lucide-react';
import { useWordListStore } from '../store/wordListStore';

export function WordListPage() {
  const [newWord, setNewWord] = useState('');
  const { words, addWord, removeWord, fetchWords } = useWordListStore();

  useEffect(() => {
    fetchWords();
  }, [fetchWords]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newWord.trim()) {
      await addWord(newWord.trim());
      setNewWord('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Word List</h1>

        <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
          <input
            type="text"
            value={newWord}
            onChange={(e) => setNewWord(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add a new word..."
          />
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Word
          </button>
        </form>

        <div className="space-y-2">
          {words.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No words added yet</p>
          ) : (
            words.map((word) => (
              <div
                key={word}
                className="flex items-center justify-between bg-gray-50 px-4 py-2 rounded-md"
              >
                <span className="text-gray-700">{word}</span>
                <button
                  onClick={() => removeWord(word)}
                  className="text-gray-400 hover:text-red-500 focus:outline-none"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}