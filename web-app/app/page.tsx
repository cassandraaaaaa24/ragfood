'use client';

import { useState } from 'react';
import SearchBox from '@/components/SearchBox';
import ResultCard from '@/components/ResultCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import ExampleQuestions from '@/components/ExampleQuestions';

interface SearchResult {
  answer: string;
  context: string;
  sources: string[];
}

export default function Home() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setError('Please enter a question');
      return;
    }

    setQuery(searchQuery);
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-orange-50 to-teal-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-6 sm:px-6">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl font-bold bg-gradient-to-r from-red-600 to-teal-500 bg-clip-text text-transparent">
              🍜 RAG Food
            </h1>
            <p className="text-gray-600 mt-2">
              Ask questions about foods from around the world
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        {/* Search Box */}
        <div className="mb-12">
          <SearchBox onSearch={handleSearch} disabled={loading} />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <p className="font-semibold">Error: {error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <LoadingSpinner />
          </div>
        )}

        {/* Results */}
        {result && !loading && (
          <div className="space-y-6">
            <ResultCard result={result} query={query} />
          </div>
        )}

        {/* Example Questions */}
        {!result && !loading && !error && (
          <ExampleQuestions onSelectQuestion={handleSearch} disabled={loading} />
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white mt-16 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <p className="text-gray-400">
            Powered by Groq + Upstash Vector + Next.js
          </p>
          <p className="text-gray-500 mt-2 text-sm">
            Explore recipes and facts about foods from Indian, Korean, Taiwanese, Filipino, and Singaporean cuisines.
          </p>
        </div>
      </footer>
    </main>
  );
}
