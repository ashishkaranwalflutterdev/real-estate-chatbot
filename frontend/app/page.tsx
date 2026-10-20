'use client';

import React, { useState, useEffect, useRef } from 'react';

interface Citation {
  title: string;
  source: string;
  url: string;
  category: string;
}

interface Message {
  role: 'user' | 'bot';
  text: string;
  citations?: Citation[];
  modelUsed?: string;
}

const DEFAULT_QUESTIONS = [
  'What is AIDA in Oman and which brand partners are involved?',
  'What services and property types are offered on Wasalt?',
  'Tell me about Dar Global’s partnership with Automobili Lamborghini and Pagani.',
  'How does Wasalt ensure compliance with Saudi REGA Fal broker licensing?',
  'What are Dar Global’s latest financial results and GDV?',
];

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [prompts, setPrompts] = useState<string[]>(DEFAULT_QUESTIONS);
  const [serverStatus, setServerStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  const chatBottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    async function loadStats() {
      try {
        const base =
          process.env.NEXT_PUBLIC_API_URL ||
          (typeof window !== 'undefined' && window.location.port === '3000'
            ? 'http://localhost:8000'
            : '');
        const res = await fetch(`${base}/api/stats`);
        if (res.ok) {
          const data = await res.json();
          if (data.sample_prompts?.length) setPrompts(data.sample_prompts);
          setServerStatus('online');
        } else {
          setServerStatus('offline');
        }
      } catch {
        setServerStatus('offline');
      }
    }
    loadStats();
  }, []);

  const handleSend = async (customText?: string) => {
    const text = (customText || input).trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);

    try {
      const base =
        process.env.NEXT_PUBLIC_API_URL ||
        (typeof window !== 'undefined' && window.location.port === '3000'
          ? 'http://localhost:8000'
          : '');

      const res = await fetch(`${base}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) throw new Error(`HTTP error ${res.status}`);

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: data.reply || 'No response generated.',
          citations: data.citations || [],
          modelUsed: data.model_used,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'bot',
          text: `Error connecting to backend: ${err.message}. Please check if the API server is up.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderMessageContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      const parts = line.split(/(\*\*.*?\*\*)/g).map((seg, i) => {
        if (seg.startsWith('**') && seg.endsWith('**')) {
          return <strong key={i}>{seg.slice(2, -2)}</strong>;
        }
        return seg;
      });

      if (line.trim().startsWith('- ') || line.trim().startsWith('• ')) {
        return (
          <li key={idx} style={{ marginLeft: '16px' }}>
            {line.trim().replace(/^[-•]\s*/, '')}
          </li>
        );
      }

      if (line.trim().match(/^\d+\.\s/)) {
        return (
          <div key={idx} style={{ marginLeft: '8px', marginBottom: '4px' }}>
            {parts}
          </div>
        );
      }

      if (!line.trim()) {
        return <div key={idx} style={{ height: '6px' }} />;
      }

      return (
        <p key={idx} style={{ marginBottom: '6px' }}>
          {parts}
        </p>
      );
    });
  };

  return (
    <div className="app-container">
      <div className="bg-ambient" />

      {/* Header */}
      <header className="app-header">
        <div className="brand-section">
          <div className="brand-logo-badge">DG•W</div>
          <div className="brand-titles">
            <h1>Dar Global &amp; Wasalt AI</h1>
            <div className="brand-subtitle">
              <span>Grounded Real Estate Assistant</span>
              <span className="tag-pill tag-dar">Dar Global PLC</span>
              <span className="tag-pill tag-wasalt">Wasalt PropTech</span>
            </div>
          </div>
        </div>

        <div className="header-status">
          <div className="status-badge">
            <span
              className="pulse-dot"
              style={{
                backgroundColor: serverStatus === 'online' ? '#22c55e' : '#eab308',
                boxShadow:
                  serverStatus === 'online'
                    ? '0 0 8px #22c55e'
                    : '0 0 8px #eab308',
              }}
            />
            <span>{serverStatus === 'online' ? 'Grounded & Live' : 'Connecting...'}</span>
          </div>
        </div>
      </header>

      {/* Chat Window */}
      <main className="chat-window">
        <div className="messages-scroll">
          {messages.length === 0 ? (
            <div className="welcome-card">
              <div className="welcome-icon">🏛️</div>
              <h2 className="welcome-title">Verified Real Estate Intelligence</h2>
              <p className="welcome-desc">
                Ask anything about <strong>Dar Global</strong> (luxury international developments in
                Dubai, Oman, Qatar, Spain, Maldives) or <strong>Wasalt</strong> (Saudi PropTech
                portal, REGA Fal licensing, sales, rentals, and auctions). Every response is strictly
                grounded in official public documentation.
              </p>

              <div className="suggestions-grid">
                {prompts.map((q, i) => (
                  <button
                    key={i}
                    className="suggestion-chip"
                    onClick={() => handleSend(q)}
                  >
                    💬 {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, idx) => (
              <div key={idx} className={`message-row ${m.role}`}>
                <div className={`avatar ${m.role === 'user' ? 'user-avatar' : 'bot-avatar'}`}>
                  {m.role === 'user' ? 'YOU' : 'AI'}
                </div>
                <div className="message-bubble">
                  <div className="message-text">{renderMessageContent(m.text)}</div>

                  {m.citations && m.citations.length > 0 && (
                    <div className="citations-box">
                      <span className="citations-label">Sources</span>
                      <div className="citations-list">
                        {m.citations.map((c, i) => (
                          <a
                            key={i}
                            href={c.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="citation-pill"
                          >
                            🔗 {c.source}: {c.title}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}

                  {m.modelUsed && (
                    <div className="model-meta">
                      <span>Model: {m.modelUsed}</span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="message-row bot">
              <div className="avatar bot-avatar">AI</div>
              <div className="message-bubble">
                <div className="typing-dots">
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}
          <div ref={chatBottomRef} />
        </div>

        {/* Input Bar */}
        <div className="input-area">
          {messages.length > 0 && (
            <button className="btn-clear" onClick={() => setMessages([])} title="Clear chat">
              Clear
            </button>
          )}

          <textarea
            ref={inputRef}
            className="chat-input"
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about Dar Global projects, Wasalt listings, Fal licensing..."
            disabled={loading}
          />

          <button
            className="btn-send"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
          >
            <span>Send</span>
            <span>↗</span>
          </button>
        </div>
      </main>

      <footer className="app-footer">
        Powered by <a href="https://openrouter.ai" target="_blank" rel="noreferrer">OpenRouter</a> Free Models • Data from <a href="https://darglobal.co.uk" target="_blank" rel="noreferrer">darglobal.co.uk</a> &amp; <a href="https://wasalt.sa" target="_blank" rel="noreferrer">wasalt.sa</a>
      </footer>
    </div>
  );
}
