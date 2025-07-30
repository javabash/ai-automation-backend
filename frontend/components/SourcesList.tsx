
export default function SourcesList({ sources }: { sources: any[] }) {
  if (!sources?.length) return null;
  return (
    <div>
      <strong>Sources:</strong>
      <ul className="list-disc ml-6">
        {sources.map((src, idx) => (
          <li key={idx} className="mb-2">
            <div><b>{src.type}</b>{src.title ? `: ${src.title}` : ""}</div>
            <div className="text-sm text-gray-600">{src.snippet}</div>
            {src.url && <div><a href={src.url} className="text-blue-600" target="_blank" rel="noopener noreferrer">View Source</a></div>}
          </li>
        ))}
      </ul>
    </div>
  );
}
