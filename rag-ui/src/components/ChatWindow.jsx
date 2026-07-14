import React, { useEffect, useRef } from 'react';

export default function ChatWindow({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={{ 
      flex: 1, 
      padding: '20px', 
      overflowY: 'auto', 
      backgroundColor: '#111827',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }}>
      {messages.length === 0 ? (
        <div style={{ color: '#6b7280', textAlign: 'center', marginTop: '140px', fontSize: '14px', padding: '0 20px' }}>
          ✨ Ask a question regarding policy definitions or procedures to run vector queries.
        </div>
      ) : (
        messages.map((msg, index) => (
          <div 
            key={index} 
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <div style={{
              maxWidth: '85%',
              padding: '10px 14px',
              borderRadius: '12px',
              fontSize: '14px',
              lineHeight: '1.5',
              backgroundColor: msg.role === 'user' ? '#38bdf8' : '#1f2937',
              color: '#fff',
              border: msg.role === 'user' ? 'none' : '1px solid rgba(255, 255, 255, 0.05)',
            }}>
              {msg.text}
            </div>
            {msg.sources && msg.sources.length > 0 && (
              <span style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px', padding: '0 4px' }}>
                📌 Sources: {msg.sources.join(', ')}
              </span>
            )}
          </div>
        ))
      )}
      <div ref={bottomRef} />
    </div>
  );
}