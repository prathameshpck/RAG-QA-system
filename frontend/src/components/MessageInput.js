import React, { useState } from 'react';

const MessageInput = ({ onSend }) => {
  const [message, setMessage] = useState('');

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      if (e.shiftKey) return; // Allow new line
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message);
    setMessage('');
  };

  return (
    <div style={styles.container}>
      <textarea
        style={styles.input}
        rows={2}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
      />
      <button style={styles.button} onClick={handleSend}>
        Send
      </button>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    gap: '10px',
    width: '60%',
    marginTop: '10px',
  },
  input: {
    flex: 1,
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '5px',
    backgroundColor: '#424242',
    color: '#FFFFFF',
    fontFamily: 'inherit',
    fontSize: '14px',
    resize: 'none'
  },
  button: {
    padding: '10px 16px',
    backgroundColor: '#1E88E5',
    color: '#FFFFFF',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
  },
};

export default MessageInput;
