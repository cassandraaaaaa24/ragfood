'use client';

interface ResultCardProps {
  result: {
    answer: string;
    context: string;
    sources: string[];
  };
  query: string;
}

export default function ResultCard({ result, query }: ResultCardProps) {
  return (
    <div className="space-y-6 animate-in fade-in-up">
      {/* Question */}
      <div className="card bg-gradient-to-r from-red-50 to-orange-50 border border-red-200">
        <h2 className="text-lg font-semibold text-gray-800">Your Question</h2>
        <p className="text-red-700 text-lg mt-2 font-medium">{query}</p>
      </div>

      {/* Answer */}
      <div className="card border border-teal-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Answer</h2>
        <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
          <p className="whitespace-pre-wrap text-base">{result.answer}</p>
        </div>
      </div>

      {/* Context */}
      {result.context && (
        <div className="card bg-gray-50 border border-gray-200">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">Context Used</h3>
          <p className="text-gray-600 text-sm leading-relaxed max-h-32 overflow-y-auto">
            {result.context}
          </p>
        </div>
      )}

      {/* Sources */}
      {result.sources.length > 0 && (
        <div className="card bg-blue-50 border border-blue-200">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">Sources</h3>
          <div className="flex flex-wrap gap-2">
            {result.sources.map((source, idx) => (
              <span
                key={idx}
                className="inline-block px-3 py-1 bg-blue-200 text-blue-800 text-sm rounded-full"
              >
                {source}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
