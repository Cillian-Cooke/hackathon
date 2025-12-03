import React, { useState, useEffect, useRef } from 'react';
import { createRoot } from 'react-dom/client';
import { BsSun, BsMoonFill } from 'react-icons/bs';
// 👈 IMPORTANT: Ensure your CSS file is imported here!
import './style.css'; 

// --- SHARED CONSTANTS (Only colors needed for inline button backgrounds) ---
const BUTTON_SUMMARY = '#52c41a'; 
const BUTTON_STATUS = '#13c2c2'; 
const BUTTON_RESET = '#ff4d4f'; 
const BUTTON_SEND = '#647DE5'; 
// -------------------------------------------------------------------------

const SimpleDnDApp = () => {
    // State for dark mode (defaulting to true/dark)
    const [isDarkMode, setIsDarkMode] = useState(true);
    const [messages, setMessages] = useState([]); 
    const [inputText, setInputText] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    
    const CAMPAIGN_NAME = "web_campaign"; 

    // --- NEW: Ref for auto-scrolling ---
    const messageEndRef = useRef(null);

    const scrollToBottom = () => {
        if (messageEndRef.current) {
            messageEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    };

    // Scroll on every message or loading state change (when DM types)
    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    // --- Toggle Function ---
    const toggleDarkMode = () => {
        setIsDarkMode(prev => !prev);
    };

    // --- EFFECT: Trigger DM intro on mount and set body class for theme ---
    useEffect(() => {
        // Set the body class to control the global theme based on state
        document.body.className = isDarkMode ? '' : 'light-mode';

        if (messages.length === 0 && !isLoading) {
            sendInitialPrompt();
        }
        
        // Cleanup function to restore body class
        return () => {
            document.body.className = '';
        };
    }, [isDarkMode]); 

    // --- Reset Campaign Handler ---
    const handleReset = async () => {
        if (!window.confirm("Are you sure you want to reset the entire story and character? This action cannot be undone.")) {
            return;
        }

        setIsLoading(true);
        setMessages([{ role: "assistant", content: "⚙️ Attempting to reset campaign..." }]);

        try {
            const response = await fetch("http://127.0.0.1:8000/api/reset", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ campaign_name: CAMPAIGN_NAME }),
            });

            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }

            setMessages([]);
            setInputText("");
            sendInitialPrompt(); 
        } catch (err) {
            console.error("Reset API Error:", err);
            setMessages(prev => [...prev, { role: "assistant", content: `❌ Reset Error: ${err.message}. Check your terminal!` }]);
            setIsLoading(false);
        }
    };

    // --- sendInitialPrompt ---
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
            setMessages([{ role: "assistant", content: `❌ Initialization Error: ${err.message}. Check your terminal!` }]);
        } finally {
            setIsLoading(false);
        }
    };

    // --- sendMessage and sendMetaCommand ---
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
            setMessages(prev => [...prev, { role: "assistant", content: `❌ Error communicating with DM server: ${err.message}. Check your terminal!` }]);
        } finally {
            setIsLoading(false);
        }
    };
    
    const sendMetaCommand = (command) => {
        if (isLoading) return; 
        sendMessage(null, command);
    };


    return (
        <div className="dnd-container">
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px'}}>
                <h1 style={{margin: 0}}>
                    🐉 Dungeon Master CLI (Web)
                </h1>
                
                {/* --- DARK MODE SLIDER TOGGLE --- */}
                <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                    {/* The active icon uses the send button color, otherwise it inherits text color */}
                    <BsMoonFill color={isDarkMode ? BUTTON_SEND : 'var(--text-color)'} size={20} />
                    <label className="switch">
                        <input 
                            type="checkbox" 
                            checked={!isDarkMode} 
                            onChange={toggleDarkMode} 
                        />
                        <span className="slider" />
                    </label>
                    <BsSun color={!isDarkMode ? BUTTON_SEND : 'var(--text-color)'} size={20} />
                </div>
                {/* --- END DARK MODE SLIDER --- */}
                
            </div>
            
            <div className="message-area">
                {messages.map((msg, i) => (
                    <div 
                        key={i} 
                        className={`message-bubble ${msg.role === 'user' ? 'msg-user' : 'msg-dm'}`}
                    >
                        <strong className={msg.role === 'user' ? 'role-user' : 'role-dm'}>
                            {msg.role === 'user' ? 'YOU' : 'DM'}
                        </strong>: {msg.content}
                    </div>
                ))}

                {isLoading && (
                    <div style={{ marginTop: '10px', color: 'var(--user-msg-border)' }}>
                        <em>DM is thinking...</em>
                    </div>
                )}

                {/* 👇 NEW: Auto-scroll anchor */}
                <div ref={messageEndRef} />
            </div>

            {/* --- BUTTONS SECTION --- */}
            <div className="meta-buttons">
                <div style={{ display: 'flex', gap: '10px' }}>
                    <button 
                        onClick={() => sendMetaCommand('summary')}
                        disabled={isLoading}
                        className="rounded-btn"
                        style={{ backgroundColor: BUTTON_SUMMARY, color: 'white', border: 'none' }}
                    >
                        📖 Summary of Story
                    </button>
                    <button 
                        onClick={() => sendMetaCommand('status')}
                        disabled={isLoading}
                        className="rounded-btn"
                        style={{ backgroundColor: BUTTON_STATUS, color: 'white', border: 'none' }}
                    >
                        👤 Player Status
                    </button>
                </div>
                
                {/* --- RESET BUTTON --- */}
                <button 
                    onClick={handleReset}
                    disabled={isLoading}
                    className="rounded-btn"
                    style={{ backgroundColor: BUTTON_RESET, color: 'white', border: 'none' }}
                >
                    🔥 Reset Campaign
                </button>
            </div>
            {/* --- END BUTTONS SECTION --- */}

            <form onSubmit={sendMessage} className="input-group">
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={isLoading ? "Waiting for DM..." : "Enter your action..."}
                    disabled={isLoading}
                    className="input-field"
                />
                <button 
                    type="submit"
                    disabled={isLoading || !inputText.trim()}
                    className="rounded-btn"
                    style={{ backgroundColor: BUTTON_SEND, color: 'white', border: 'none' }}
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
