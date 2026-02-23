export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-red-600 border-r-teal-500 animate-spin"></div>
      </div>
      <p className="text-gray-600 font-medium">Searching for food information...</p>
    </div>
  );
}
