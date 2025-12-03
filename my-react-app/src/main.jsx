import React, { useState, useEffect } from 'react';
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

const metaButtonsStyle = {
    marginBottom: '10px',
    display: 'flex',
    gap: '10px',
    justifyContent: 'space-between', // Keeps reset button separate
};

const SimpleDnDApp = () => {
    const [messages, setMessages] = useState([]); 
    const [inputText, setInputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    
    // The fixed campaign name used by the web interface
    const CAMPAIGN_NAME = "web_campaign"; 

    // --- EFFECT: Trigger DM intro on mount ---
    useEffect(() => {
        if (messages.length === 0 && !isLoading) {
            sendInitialPrompt();
        }
    }, []); 

    // --- NEW: Reset Campaign Handler ---
    const handleReset = async () => {
        if (!window.confirm("Are you sure you want to reset the entire story and character? This action cannot be undone.")) {
            return;
        }

        setIsLoading(true);
        setMessages([{ role: "assistant", content: "⚙️ Attempting to reset campaign..." }]);

        try {
            // Call the new backend reset endpoint
            const response = await fetch("http://127.0.0.1:8000/api/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ campaign_name: CAMPAIGN_NAME }),
            });

            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }

            // Reset successful, clear state and start a new game
            setMessages([]);
            setInputText("");
            console.log("Campaign files deleted successfully.");
            
            // Re-run the initial prompt to start the new campaign
            sendInitialPrompt(); 

        } catch (err) {
            console.error("Reset API Error:", err);
            setMessages(prev => [...prev, { role: "assistant", content: `❌ Reset Error: ${err.message}. Check your terminal!` }]);
            setIsLoading(false);
        }
    };
    // ------------------------------------

    // --- Function: Handles the initial API call to start the game ---
    const sendInitialPrompt = async () => {
        setIsLoading(true);
        const initialPrompt = "Start the adventure with a short, setting-focused intro."; 
        const payload = { input: initialPrompt, campaign_name: CAMPAIGN_NAME, initial: true };

        try {
            const response = await fetch("http://127.0.0.1:8000/api/message", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }

            const data = await response.json();
            setMessages([{ role: "assistant", content: data.response }]);
            
        } catch (err) {
            console.error("Initial API Error:", err);
            setMessages([{ role: "assistant", content: `❌ Initialization Error: ${err.message}. Check your terminal!` }]);
        } finally {
            setIsLoading(false);
        }
    };

    // --- Central function to send messages (used by form submit and buttons) ---
    const sendMessage = async (e, metaCommand = null) => {
        const commandToSend = metaCommand || inputText.trim();
        
        if (e) e.preventDefault(); 
        
        if (!commandToSend || isLoading) return;

        const userMessage = commandToSend;
        const newMessages = [...messages, { role: "user", content: userMessage }];
        setMessages(newMessages);

        if (!metaCommand) {
            setInputText("");
        }

        setIsLoading(true);

        const payload = { input: userMessage, campaign_name: CAMPAIGN_NAME }; 

        try {
            const response = await fetch("http://127.0.0.1:8000/api/message", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }

            const data = await response.json();
            setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
            
        } catch (err) {
            console.error("API Error:", err);
            setMessages(prev => [...prev, { role: "assistant", content: `❌ Error communicating with DM server: ${err.message}. Check your terminal!` }]);
        } finally {
            setIsLoading(false);
        }
    };
    
    // --- Function to handle button clicks (sends automatically) ---
    const sendMetaCommand = (command) => {
        if (isLoading) return; 
        sendMessage(null, command);
    };


    return (
        <div style={containerStyle}>
            <h1 style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                🐉 Dungeon Master CLI (Web)
            </h1>
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

            {/* --- BUTTONS SECTION --- */}
            <div style={metaButtonsStyle}>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                        onClick={() => sendMetaCommand('summary')}
                        disabled={isLoading}
                        title="Send the 'summary' command to get a story recap"
                        style={{ 
                            padding: '10px 15px', 
                            fontSize: '14px', 
                            borderRadius: '4px', 
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            backgroundColor: '#52c41a', 
                            color: 'white',
                            border: 'none'
                        }}
                    >
                        📖 Summary of Story
                    </button>
                    <button 
                        onClick={() => sendMetaCommand('status')}
                        disabled={isLoading}
                        title="Send the 'status' command to view character details"
                        style={{ 
                            padding: '10px 15px', 
                            fontSize: '14px', 
                            borderRadius: '4px', 
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            backgroundColor: '#13c2c2', 
                            color: 'white',
                            border: 'none'
                        }}
                    >
                        👤 Player Status
                    </button>
                </div>
                
                {/* --- NEW RESET BUTTON --- */}
                <button 
                    onClick={handleReset}
                    disabled={isLoading}
                    title="Delete all campaign files and start a new story."
                    style={{ 
                        padding: '10px 15px', 
                        fontSize: '14px', 
                        borderRadius: '4px', 
                        cursor: isLoading ? 'not-allowed' : 'pointer',
                        backgroundColor: '#ff4d4f', // Red for destructive action
                        color: 'white',
                        border: 'none'
                    }}
                >
                    🔥 Reset Campaign
                </button>
                {/* --- END NEW RESET BUTTON --- */}

            </div>
            {/* --- END BUTTONS SECTION --- */}

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