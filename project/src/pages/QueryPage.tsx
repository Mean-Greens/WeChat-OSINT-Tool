import React, { useState } from 'react';
import { Send } from 'lucide-react';
import { useWordListStore } from '../store/wordListStore';

export function QueryPage() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const words = useWordListStore((state) => state.words);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate LLM response
    setTimeout(() => {
      setResponse(`Sample response using words: ${words.join(', ')}`);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Query LLM</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Your Query
            </label>
            <textarea
              id="query"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query here..."
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? (
              'Processing...'
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Send Query
              </>
            )}
          </button>
        </form>

        {response && (
          <div className="mt-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">Response:</h2>
            <div className="bg-gray-50 rounded-md p-4">
              <p className="text-gray-700">{response}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}