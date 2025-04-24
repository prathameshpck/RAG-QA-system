import React, { useState } from 'react';
import ChatWindow from './components/ChatWindow';
import MessageInput from './components/MessageInput';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;

    // Add user message to state
    const newMessages = [...messages, { text: userMessage, type: 'user' }];
    setMessages(newMessages);
    setIsLoading(true);

    // Convert to OpenAI-compatible message format
    const formattedMessages = newMessages.map((msg) => ({
      role: msg.type === 'user' ? 'user' : 'assistant',
      content: msg.text
    }));

    // Add placeholder for streaming bot message
    setMessages((prev) => [...prev, { text: '', type: 'bot' }]);

    try {
      const response = await fetch('http://localhost:8000/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          model: "neuralmagic/Llama-2-7b-chat-quantized.w8a8",
          messages: formattedMessages,
          stream: true,
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        // Parse each line starting with 'data:'
        const lines = chunk.split('\n').filter(line => line.startsWith('data:'));
        for (const line of lines) {
          const data = line.replace(/^data:\s*/, '');
          if (data === '[DONE]') continue;

          const json = JSON.parse(data);
          const delta = json.choices?.[0]?.delta?.content;
          if (delta) {
            accumulated += delta;

            // Replace the last bot message with the streaming one
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = { text: accumulated, type: 'bot' };
              return updated;
            });
          }
        }
      }
    } catch (err) {
      console.error('Streaming error:', err);
      setMessages((prev) => [
        ...prev,
        { text: 'Error during streaming response.', type: 'bot' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.appContainer}>
      <h1 style={styles.header}>ChatGPT UI</h1>
      <ChatWindow messages={messages} isLoading={isLoading} />
      <MessageInput onSend={handleSendMessage} />
    </div>
  );
};

const styles = {
  appContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: '#121212',
    color: '#FFFFFF',
  },
  header: {
    marginBottom: '20px',
    fontSize: '24px',
  },
};

export default App;
