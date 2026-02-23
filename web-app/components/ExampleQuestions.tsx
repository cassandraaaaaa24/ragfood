'use client';

interface ExampleQuestionsProps {
  onSelectQuestion: (question: string) => void;
  disabled?: boolean;
}

const exampleQuestions = [
  '🥘 Which Indian dish uses chickpeas?',
  '🍜 What is masala dosa made of?',
  '🔥 What is japchae?',
  '🥗 Which foods are high in protein?',
  '🌏 Tell me about Singaporean food',
  '🌱 What vegan options are available?',
  '🍲 What foods can be grilled?',
  '🍯 What dessert is made from milk and soaked in syrup?',
];

export default function ExampleQuestions({
  onSelectQuestion,
  disabled = false,
}: ExampleQuestionsProps) {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          How can I help you today?
        </h2>
        <p className="text-gray-600">
          Try asking one of these questions or ask your own
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {exampleQuestions.map((question, idx) => (
          <button
            key={idx}
            onClick={() => {
              const cleanQuestion = question.replace(/^[🥘🍜🔥🥗🌏🌱🍲🍯]\s+/, '');
              onSelectQuestion(cleanQuestion);
            }}
            disabled={disabled}
            className="card text-left hover:shadow-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <p className="text-gray-800 font-medium">{question}</p>
          </button>
        ))}
      </div>

      <div className="mt-12 p-6 bg-blue-50 rounded-xl border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">💡 How it works</h3>
        <p className="text-blue-800 text-sm leading-relaxed">
          This app uses AI (Groq) and vector search (Upstash) to find relevant food information
          from a comprehensive dataset. Your questions are matched against thousands of food records
          to provide accurate, contextual answers.
        </p>
      </div>
    </div>
  );
}
