import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';

const App = () => {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (message) => {
    setMessages((prev) => [...prev, { text: message, type: 'user' }]);

    const response = await new Promise((resolve) =>
      setTimeout(() => resolve({ text: `You said: "${message}"` }), 1000)
    );

    setMessages((prev) => [...prev, { text: response.text, type: 'bot' }]);
  };

  return (
    <div style={{ maxWidth: '600px', margin: '20px auto', textAlign: 'center' }}>
      <h1>ChatGPT UI</h1>
      <ChatWindow messages={messages} />
      <MessageInput onSend={handleSendMessage} />
    </div>
  );
};

export default App;
