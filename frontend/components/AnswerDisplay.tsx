export default function AnswerDisplay({ answer, loading }: { answer: string, loading: boolean }) {
  if (loading) return <div>Loading...</div>;
  if (!answer) return null;
  return <div className="p-4 bg-gray-100 rounded mb-2"><strong>Answer:</strong> {answer}</div>;
}