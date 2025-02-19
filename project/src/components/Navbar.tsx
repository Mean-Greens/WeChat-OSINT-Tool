import React from 'react';
import { NavLink } from 'react-router-dom';
import { MessageSquare, List } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex space-x-8">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  isActive
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`
              }
            >
              <MessageSquare className="w-5 h-5 mr-2" />
              Query LLM
            </NavLink>
            <NavLink
              to="/wordlist"
              className={({ isActive }) =>
                `flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                  isActive
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
                }`
              }
            >
              <List className="w-5 h-5 mr-2" />
              Word List
            </NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
}