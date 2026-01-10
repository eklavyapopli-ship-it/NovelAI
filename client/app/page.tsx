'use client';

import { useState, useEffect } from 'react';

export default function NovelAI() {
  const [message, setMessage] = useState('');
  const [answer, setAnswer] = useState('');
  const [jobId, setJobId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const sendMessage = async () => {
    if (!message.trim()) return;

    setLoading(true);
    setAnswer('');
    setError('');

    try {
      const res = await fetch(
        `http://0.0.0.0:8000/chat?query=${encodeURIComponent(message)}`,
        { method: 'POST' }
      );

      const data = await res.json();
      setJobId(data.job_id);
    } catch (err: any) {
      setError('The archive failed to respond.');
      setLoading(false);
    }
  };

useEffect(() => {
  if (!jobId) return;

  const ws = new WebSocket('ws://0.0.0.0:8000/job-status');

  ws.onopen = () => {
    ws.send(jobId); // send job_id to backend
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.status === 'finished') {
      setAnswer(data.result);
      setLoading(false);
      ws.close();
    }

    if (data.status === 'failed') {
      setError('The archive failed to respond.');
      setLoading(false);
      ws.close();
    }
  };

  ws.onerror = () => {
    setError('WebSocket connection error.');
    setLoading(false);
    ws.close();
  };

  return () => {
    ws.close();
  };
}, [jobId]);


  return (
    <main className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-black text-zinc-200 flex items-center justify-center px-6">
      <div className="max-w-4xl w-full bg-zinc-950/80 backdrop-blur border border-zinc-800 rounded-2xl shadow-2xl p-8 space-y-6">

        {/* Header */}
        <header className="text-center space-y-2">
          <h1 className='text-6xl text-center font-serif text-amber-400'>LIBRIS </h1>
          <h1 className="text-4xl font-serif tracking-wide text-amber-400">
           The Omniscient Novel AI
          </h1>
          <p className="text-sm text-zinc-400 italic">
            Keeper of plots, prose, characters, and forgotten stories
          </p>
        </header>

        {/* Input */}
        <div className="space-y-3">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask about a novel, character arc, trope, or hidden meaning..."
            className="w-full h-36 bg-zinc-900 text-zinc-100 border border-zinc-700 rounded-xl p-4 resize-none focus:outline-none focus:ring-2 focus:ring-amber-500"
          />

          <button
            onClick={sendMessage}
            disabled={loading}
            className="w-full py-3 rounded-xl bg-amber-600 hover:bg-amber-700 disabled:bg-zinc-700 text-black font-semibold tracking-wide transition"
          >
            {loading ? 'Consulting the Archive…' : 'Ask the Archive'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="text-red-400 text-sm text-center">
            {error}
          </div>
        )}

        {/* Answer */}
        {answer && (
          <section className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 leading-relaxed">
            <h2 className="text-amber-400 font-serif text-lg mb-3">
              The Archive Responds
            </h2>
            <p className="whitespace-pre-wrap text-zinc-200">
              {answer}
            </p>
          </section>
        )}
      </div>
    </main>
  );
}
