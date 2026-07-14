import React, { useState } from 'react';
import AdminUpload from './components/AdminUpload';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import { sendChatQuery } from './api';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);

  const handleSendMessage = async (text) => {
    const userMessage = { role: 'user', text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const data = await sendChatQuery(text);
      const assistantText = data.answer_context.join('\n') || "No reference context found for this query.";
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: assistantText, sources: data.sources }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: `❌ Error connecting to agent: ${err.message}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      margin: 0,
      padding: 0,
      boxSizing: 'border-box',
      minHeight: '100vh',
      backgroundColor: '#030712',
      backgroundImage: 'radial-gradient(circle at 50% 50%, #1e1b4b 0%, #030712 70%)',
      color: '#fff',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      overflowX: 'hidden'
    }}>
      {/* Premium Navbar */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '20px 60px',
        backgroundColor: 'rgba(3, 7, 18, 0.6)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '24px', fontWeight: 'bold', letterSpacing: '1px', color: '#38bdf8' }}>SAILS</span>
          <span style={{ fontSize: '14px', color: '#9ca3af', fontWeight: '300', marginTop: '4px' }}>Software</span>
        </div>
        <button style={{
          padding: '10px 24px',
          backgroundColor: '#fff',
          color: '#030712',
          border: 'none',
          borderRadius: '30px',
          fontWeight: '600',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}>
          Contact Us
        </button>
      </header>

      {/* Main Center Content Section */}
      <main style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px 20px',
        textAlign: 'center',
        zIndex: 1
      }}>
        <p style={{ color: '#9ca3af', fontSize: '16px', fontWeight: '500', marginBottom: '10px', letterSpacing: '0.5px' }}>
          Our Client's Success, Is Our Success.
        </p>
        
        <h1 style={{
          fontSize: '3.5rem',
          fontWeight: '800',
          margin: '0 0 10px 0',
          lineHeight: '1.2',
          maxWidth: '800px'
        }}>
          Your AI-Powered Partner 

          <span style={{ color: '#38bdf8' }}>in IT & Innovation</span>
        </h1>
        
        <p style={{ color: '#9ca3af', fontSize: '13px', fontWeight: '600', letterSpacing: '2px', marginBottom: '40px' }}>
          THINK TWICE, CODE ONCE.
        </p>

        {/* Upload Container placed beautifully in the Center */}
        <div style={{ width: '100%', maxWidth: '500px' }}>
          <AdminUpload />
        </div>

        {/* Footer Categories matching image context */}
        <div style={{
          display: 'flex',
          gap: '40px',
          marginTop: '60px',
          color: '#9ca3af',
          fontSize: '14px',
          fontWeight: '500'
        }}>
          <span>E-Commerce</span>
          <span>Fintech</span>
          <span>Healthcare</span>
          <span>Life Sciences</span>
        </div>
      </main>

      {/* FLOATING ACTION TRIGGER CHAT BUBBLE (Bottom Right) */}
      <button 
        onClick={() => setIsChatOpen(!isChatOpen)}
        style={{
          position: 'fixed',
          bottom: '30px',
          right: '30px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: '#38bdf8',
          color: '#fff',
          border: 'none',
          cursor: 'pointer',
          boxShadow: '0 8px 32px rgba(56, 189, 248, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          zIndex: 1000,
          transition: 'transform 0.2s ease'
        }}
      >
        {isChatOpen ? '✕' : '💬'}
      </button>

      {/* FLOATING RETRIEVAL AGENT DRAWER */}
      {isChatOpen && (
        <div style={{
          position: 'fixed',
          bottom: '105px',
          right: '30px',
          width: '400px',
          height: '550px',
          backgroundColor: '#1f2937',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.5)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          zIndex: 1000
        }}>
          <div style={{
            padding: '16px 20px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            backgroundColor: '#111827',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <span style={{ fontSize: '18px' }}>💬</span>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600', color: '#fff' }}>User Retrieval Agent</h3>
          </div>
          
          <ChatWindow messages={messages} />
          <ChatInput onSendMessage={handleSendMessage} disabled={loading} />
        </div>
      )}
    </div>
  );
}