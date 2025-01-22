import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import axios from 'axios'; // Axios for making API requests

const App = () => {
  const [messages, setMessages] = useState([]);

  // Function to handle sending messages
  const handleSendMessage = async (message) => {
    // Add user's message to the chat
    setMessages((prev) => [...prev, { text: message, type: 'user' }]);
  
    try {
      // Make an API call to your LLM endpoint
      const response = await axios.post('http://localhost:8000/v1/chat/completions', {
        model: "neuralmagic/Llama-2-7b-chat-quantized.w8a8",
        messages: [
          {
            role: "user",
            content: message // User's input message
          }
        ]
      }, {
        headers: {
          "Content-Type": "application/json"
        }
      });
  
      // Extract and add the assistant's response
      const botResponse = response.data.choices?.[0]?.message?.content || "No response from the model.";
      setMessages((prev) => [...prev, { text: botResponse, type: 'bot' }]);
    } catch (error) {
      console.error('Error communicating with the LLM API:', error);
      setMessages((prev) => [
        ...prev,
        { text: 'Sorry, there was an error fetching the response.', type: 'bot' },
      ]);
    }
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
