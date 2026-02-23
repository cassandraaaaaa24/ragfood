'use client';

import { useState } from 'react';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  disabled?: boolean;
}

export default function SearchBox({ onSearch, disabled = false }: SearchBoxProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSearch(input);
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-3 bg-white p-4 rounded-xl shadow-lg">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={disabled}
          placeholder="Ask me about any food... e.g., 'What is masala dosa?'"
          className="input-field flex-1"
          autoFocus
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="btn-primary"
        >
          {disabled ? 'Searching...' : 'Search'}
        </button>
      </div>
      <p className="text-gray-500 text-sm mt-3 text-center">
        Try asking about ingredients, cuisines, recipes, or dietary options
      </p>
    </form>
  );
}
