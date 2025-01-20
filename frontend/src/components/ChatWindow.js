import React from 'react';

const ChatWindow = ({ messages }) => (
  <div style={styles.container}>
    {messages.map((msg, index) => (
      <div
        key={index}
        style={{
          ...styles.message,
          alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
          backgroundColor: msg.type === 'user' ? '#DCF8C6' : '#F1F0F0',
        }}
      >
        {msg.text}
      </div>
    ))}
  </div>
);

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    padding: '10px',
    height: '400px',
    overflowY: 'auto',
    border: '1px solid #ccc',
    borderRadius: '5px',
    marginBottom: '10px',
  },
  message: {
    maxWidth: '70%',
    padding: '8px',
    borderRadius: '10px',
    fontSize: '14px',
  },
};

export default ChatWindow;
