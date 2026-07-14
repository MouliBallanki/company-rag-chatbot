import React, { useState } from 'react';
import { uploadFiles } from '../api';

export default function AdminUpload() {
  const [files, setFiles] = useState([]);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setStatus({ type: 'error', message: 'Please select at least one file.' });
      return;
    }

    setLoading(true);
    setStatus({ type: 'info', message: 'Uploading documents...' });
    try {
      const result = await uploadFiles(files);
      setStatus({ type: 'success', message: result.message });
      setFiles([]);
    } catch (err) {
      setStatus({ type: 'error', message: err.message || 'Upload failed.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      padding: '30px',
      backgroundColor: 'rgba(255, 255, 255, 0.03)',
      backdropFilter: 'blur(16px)',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      borderRadius: '16px',
      boxShadow: '0 4px 30px rgba(0, 0, 0, 0.4)',
      textAlign: 'left'
    }}>
      <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '600', color: '#fff' }}>📋 Corporate Knowledge Ingestion</h3>
      <p style={{ color: '#9ca3af', fontSize: '13px', margin: '0 0 20px 0', lineHeight: '1.4' }}>
        Select or drop HR files, compliance sheets, or guides to index them inside the localized agent vector database.
      </p>
      
      <form onSubmit={handleUpload}>
        <div style={{
          border: '2px dashed rgba(255, 255, 255, 0.15)',
          borderRadius: '8px',
          padding: '20px',
          textAlign: 'center',
          backgroundColor: 'rgba(0, 0, 0, 0.2)',
          marginBottom: '20px',
          cursor: 'pointer'
        }}>
          <input 
            type="file" 
            multiple 
            onChange={handleFileChange} 
            style={{ color: '#9ca3af', fontSize: '14px', width: '100%' }}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#38bdf8',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            fontWeight: '600',
            fontSize: '14px',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s',
            boxShadow: '0 4px 12px rgba(56, 189, 248, 0.2)'
          }}
        >
          {loading ? 'Ingesting Documents...' : 'Process & Index Files'}
        </button>
      </form>

      {status.message && (
        <div style={{
          marginTop: '15px',
          padding: '10px 12px',
          borderRadius: '6px',
          fontSize: '13px',
          backgroundColor: status.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : status.type === 'error' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(56, 189, 248, 0.15)',
          color: status.type === 'success' ? '#34d399' : status.type === 'error' ? '#f87171' : '#38bdf8',
          border: `1px solid ${status.type === 'success' ? 'rgba(16, 185, 129, 0.3)' : status.type === 'error' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(56, 189, 248, 0.3)'}`
        }}>
          {status.message}
        </div>
      )}
    </div>
  );
}