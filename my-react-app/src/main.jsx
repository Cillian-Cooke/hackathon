import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';

// Simple styling to improve the look slightly
const containerStyle = {
    maxWidth: '800px',
    margin: '20px auto',
    padding: '20px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
};

const messageAreaStyle = {
    border: '1px solid #e0e0e0',
    padding: '15px',
    height: '400px',
    overflowY: 'auto',
    marginBottom: '15px',
    borderRadius: '4px',
    backgroundColor: '#f9f9f9',
};

const inputGroupStyle = {
    display: 'flex',
    gap: '10px',
};

const SimpleDnDApp = () => {
    // Initial message to prompt the DM to start the scene
    const [messages, setMessages] = useState([
        { role: "assistant", content: "Welcome, Adventurer! Type a message to the Dungeon Master to begin your journey." },
    ]);
    const [inputText, setInputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (e) => {
        // Prevent form submit behavior if button is inside a form
        if (e) e.preventDefault(); 
        if (!inputText.trim() || isLoading) return;

        // 1. Add user message to history
        const userMessage = inputText.trim();
        const newMessages = [...messages, { role: "user", content: userMessage }];
        setMessages(newMessages);

        // 2. Clear input and set loading state
        setInputText("");
        setIsLoading(true);

        const payload = { input: userMessage, campaign_name: "web_campaign" };

        try {
            // 3. API Call to FastAPI
            const response = await fetch("http://127.0.0.1:8000/api/message", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                // Handle non-200 responses (e.g., 500 server error)
                throw new Error(`Server returned status ${response.status}`);
            }

            const data = await response.json();
            
            // 4. Add DM response to history
            setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
            
        } catch (err) {
            // 5. Display any fetch or network error
            console.error("API Error:", err);
            setMessages(prev => [...prev, { role: "assistant", content: `❌ Error communicating with DM server: ${err.message}. Check your terminal!` }]);
        } finally {
            // 6. Reset loading state
            setIsLoading(false);
        }
    };

    return (
        <div style={containerStyle}>
            <h1>🐉 Dungeon Master CLI (Web)</h1>
            <div style={messageAreaStyle}>
                {messages.map((msg, i) => (
                    <div key={i} style={{ 
                        marginBottom: '10px', 
                        padding: '8px', 
                        borderRadius: '4px',
                        backgroundColor: msg.role === 'user' ? '#e6f7ff' : '#fff0e6',
                        borderLeft: `3px solid ${msg.role === 'user' ? '#1890ff' : '#fa8c16'}`
                    }}>
                        <strong style={{ color: msg.role === 'user' ? '#1890ff' : '#fa8c16' }}>
                            {msg.role === 'user' ? 'YOU' : 'DM'}
                        </strong>: {msg.content}
                    </div>
                ))}
                {isLoading && (
                    <div style={{ marginTop: '10px', color: '#1890ff' }}>
                        <em>DM is thinking...</em>
                    </div>
                )}
            </div>

            <form onSubmit={sendMessage} style={inputGroupStyle}>
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={isLoading ? "Waiting for DM..." : "Enter your action..."}
                    disabled={isLoading}
                    style={{ flex: 1, padding: '10px', fontSize: '16px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <button 
                    type="submit"
                    disabled={isLoading || !inputText.trim()}
                    style={{ padding: '10px 20px', fontSize: '16px', borderRadius: '4px', cursor: isLoading ? 'not-allowed' : 'pointer' }}
                >
                    {isLoading ? 'Sending...' : 'Send'}
                </button>
            </form>
        </div>
    );
};

const container = document.getElementById('app');
const root = createRoot(container);
root.render(<SimpleDnDApp />);