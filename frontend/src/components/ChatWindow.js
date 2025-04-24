import React from 'react';

const ChatWindow = ({ messages, isLoading }) => {
  return (
    <div style={styles.container}>
      {messages.map((msg, index) => (
        <div
          key={index}
          style={{
            ...styles.message,
            alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
            backgroundColor: msg.type === 'user' ? '#1E88E5' : '#424242',
          }}
        >
          {msg.text}
        </div>
      ))}
      {isLoading && (
        <div style={{ ...styles.message, alignSelf: 'flex-start', backgroundColor: '#424242' }}>
          Loading...
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    padding: '20px',
    width: '70%',
    maxWidth: '900px',
    height: '65vh',
    border: '1px solid #333',
    borderRadius: '16px',
    backgroundColor: '#1E1E1E',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
    overflowY: 'auto',
    marginBottom: '1rem'
  },
  message: {
    maxWidth: '75%',
    padding: '12px 16px',
    borderRadius: '16px',
    fontSize: '15px',
    lineHeight: '1.4',
    color: '#EDEDED',
    fontFamily: 'system-ui, sans-serif'
  },
};

export default ChatWindow;
