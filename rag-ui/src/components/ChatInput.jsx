import React, { useState } from 'react';

export default function ChatInput({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} style={{ 
      display: 'flex', 
      padding: '12px', 
      borderTop: '1px solid rgba(255, 255, 255, 0.08)', 
      backgroundColor: '#111827' 
    }}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask internal policy questions..."
        disabled={disabled}
        style={{
          flex: 1,
          padding: '10px 14px',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backgroundColor: '#1f2937',
          color: '#fff',
          fontSize: '14px',
          outline: 'none',
        }}
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        style={{
          marginLeft: '8px',
          padding: '0 16px',
          backgroundColor: '#38bdf8',
          color: '#fff',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: '600',
          fontSize: '14px',
          opacity: disabled || !input.trim() ? 0.5 : 1
        }}
      >
        Send
      </button>
    </form>
  );
}