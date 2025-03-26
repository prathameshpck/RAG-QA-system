import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';
import axios from 'axios';

const App = () => {
  const [messages, setMessages] = useState([]);

  // Function to handle sending messages
  const handleSendMessage = async (message) => {
    // Add user's message to the chat
    setMessages((prev) => [...prev, { text: message, type: 'user' }]);

    try {
      // Make an API call to your LLM endpoint
      const response = await axios.post('/v1/chat/completions', {
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
      // Enhanced error handling to always show the actual error message
      console.error('Error communicating with the LLM API:', error);

      let errorMessage = 'Unknown error occurred.';

      if (error.response) {
        // Server responded with a status code out of the 2xx range
        errorMessage = `Server Error (${error.response.status}): ${JSON.stringify(error.response.data)}`;
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = `No response from server. Possible network issue or server down.`;
      } else {
        // Something else caused the error
        errorMessage = `Error: ${error.message}`;
      }

      // Log the detailed error to the console
      console.error('Detailed error:', {
        message: error.message,
        response: error.response ? error.response.data : null,
        request: error.request ? error.request : null,
      });

      // Always return the actual error message to the chat
      setMessages((prev) => [
        ...prev,
        { text: errorMessage, type: 'bot' },
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
