import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createRoot } from 'react-dom/client';
import { BsSun, BsMoonFill } from 'react-icons/bs';
import './style.css';

// =============================================================================
// Constants
// =============================================================================

const API_BASE_URL = 'http://127.0.0.1:8000/api';
const CAMPAIGN_NAME = 'web_campaign';

const THEME = {
  BUTTON_SUMMARY: '#52c41a',
  BUTTON_STATUS: '#13c2c2',
  BUTTON_RESET: '#ff4d4f',
  BUTTON_SEND: '#647DE5',
};

const META_COMMANDS = {
  SUMMARY: 'summary',
  STATUS: 'status',
};

// =============================================================================
// Custom Hooks
// =============================================================================

/**
 * Hook to manage auto-scrolling behavior for chat messages.
 */
const useAutoScroll = (dependencies) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, dependencies);

  return scrollRef;
};

/**
 * Hook to manage theme state and body class synchronization.
 */
const useTheme = (initialDarkMode = true) => {
  const [isDarkMode, setIsDarkMode] = useState(initialDarkMode);

  useEffect(() => {
    document.body.className = isDarkMode ? '' : 'light-mode';
    return () => { document.body.className = ''; };
  }, [isDarkMode]);

  const toggle = useCallback(() => setIsDarkMode((prev) => !prev), []);

  return { isDarkMode, toggle };
};

// =============================================================================
// API Service
// =============================================================================

const ApiService = {
  async sendMessage(input, isInitial = false) {
    const response = await fetch(`${API_BASE_URL}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input,
        campaign_name: CAMPAIGN_NAME,
        initial: isInitial,
      }),
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    return response.json();
  },

  async resetCampaign() {
    const response = await fetch(`${API_BASE_URL}/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ campaign_name: CAMPAIGN_NAME }),
    });

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    return response.json();
  },
};

// =============================================================================
// Sub-Components
// =============================================================================

const ThemeToggle = ({ isDarkMode, onToggle }) => (
  <div className="theme-toggle">
    <BsMoonFill
      color={isDarkMode ? THEME.BUTTON_SEND : 'var(--text-color)'}
      size={20}
    />
    <label className="switch">
      <input type="checkbox" checked={!isDarkMode} onChange={onToggle} />
      <span className="slider" />
    </label>
    <BsSun
      color={!isDarkMode ? THEME.BUTTON_SEND : 'var(--text-color)'}
      size={20}
    />
  </div>
);

const MessageBubble = ({ role, content }) => {
  const isUser = role === 'user';
  return (
    <div className={`message-bubble ${isUser ? 'msg-user' : 'msg-dm'}`}>
      <strong className={isUser ? 'role-user' : 'role-dm'}>
        {isUser ? 'YOU' : 'DM'}
      </strong>
      : {content}
    </div>
  );
};

const LoadingIndicator = () => (
  <div className="loading-indicator">
    <em>DM is thinking...</em>
  </div>
);

const ActionButton = ({ onClick, disabled, color, children }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    className="rounded-btn"
    style={{ backgroundColor: color, color: 'white', border: 'none' }}
  >
    {children}
  </button>
);

const MetaButtons = ({ onSummary, onStatus, onReset, isLoading }) => (
  <div className="meta-buttons">
    <div className="meta-buttons-left">
      <ActionButton
        onClick={onSummary}
        disabled={isLoading}
        color={THEME.BUTTON_SUMMARY}
      >
        📖 Summary of Story
      </ActionButton>
      <ActionButton
        onClick={onStatus}
        disabled={isLoading}
        color={THEME.BUTTON_STATUS}
      >
        👤 Player Status
      </ActionButton>
    </div>
    <ActionButton
      onClick={onReset}
      disabled={isLoading}
      color={THEME.BUTTON_RESET}
    >
      🔥 Reset Campaign
    </ActionButton>
  </div>
);

const ChatInput = ({ value, onChange, onSubmit, isLoading }) => {
  const isDisabled = isLoading || !value.trim();

  return (
    <form onSubmit={onSubmit} className="input-group">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={isLoading ? 'Waiting for DM...' : 'Enter your action...'}
        disabled={isLoading}
        className="input-field"
      />
      <ActionButton
        onClick={null}
        disabled={isDisabled}
        color={THEME.BUTTON_SEND}
      >
        {isLoading ? 'Sending...' : 'Send'}
      </ActionButton>
    </form>
  );
};

// =============================================================================
// Main Application Component
// =============================================================================

const DungeonMasterApp = () => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { isDarkMode, toggle: toggleTheme } = useTheme(true);
  const scrollAnchorRef = useAutoScroll([messages, isLoading]);

  /**
   * Appends a message to the chat history.
   */
  const appendMessage = useCallback((role, content) => {
    setMessages((prev) => [...prev, { role, content }]);
  }, []);

  /**
   * Displays an error message in the chat.
   */
  const showError = useCallback((context, error) => {
    appendMessage('assistant', `❌ ${context}: ${error.message}. Check your terminal!`);
  }, [appendMessage]);

  /**
   * Sends the initial prompt to start the adventure.
   */
  const initializeAdventure = useCallback(async () => {
    setIsLoading(true);

    try {
      const data = await ApiService.sendMessage(
        'Start the adventure with a short, setting-focused intro.',
        true
      );
      setMessages([{ role: 'assistant', content: data.response }]);
    } catch (error) {
      showError('Initialization Error', error);
    } finally {
      setIsLoading(false);
    }
  }, [showError]);

  /**
   * Sends a message or meta-command to the server.
   */
  const sendMessage = useCallback(async (event, metaCommand = null) => {
    event?.preventDefault();

    const messageContent = metaCommand || inputText.trim();
    if (!messageContent || isLoading) return;

    appendMessage('user', messageContent);
    if (!metaCommand) setInputText('');
    setIsLoading(true);

    try {
      const data = await ApiService.sendMessage(messageContent);
      appendMessage('assistant', data.response);
    } catch (error) {
      showError('Error communicating with DM server', error);
    } finally {
      setIsLoading(false);
    }
  }, [inputText, isLoading, appendMessage, showError]);

  /**
   * Handles campaign reset with user confirmation.
   */
  const handleReset = useCallback(async () => {
    const confirmed = window.confirm(
      'Are you sure you want to reset the entire story and character? This action cannot be undone.'
    );
    if (!confirmed) return;

    setIsLoading(true);
    setMessages([{ role: 'assistant', content: '⚙️ Attempting to reset campaign...' }]);

    try {
      await ApiService.resetCampaign();
      setMessages([]);
      setInputText('');
      initializeAdventure();
    } catch (error) {
      showError('Reset Error', error);
      setIsLoading(false);
    }
  }, [initializeAdventure, showError]);

  /**
   * Sends a meta-command (summary/status).
   */
  const sendMetaCommand = useCallback((command) => {
    if (!isLoading) sendMessage(null, command);
  }, [isLoading, sendMessage]);

  // Initialize adventure on mount
  useEffect(() => {
    if (messages.length === 0 && !isLoading) {
      initializeAdventure();
    }
  }, []);

  return (
    <div className="dnd-container">
      <header className="app-header">
        <h1>🐉 D&D Game (Web Client)</h1>
        <ThemeToggle isDarkMode={isDarkMode} onToggle={toggleTheme} />
      </header>

      <div className="message-area">
        {messages.map((msg, index) => (
          <MessageBubble key={index} role={msg.role} content={msg.content} />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={scrollAnchorRef} />
      </div>

      <MetaButtons
        onSummary={() => sendMetaCommand(META_COMMANDS.SUMMARY)}
        onStatus={() => sendMetaCommand(META_COMMANDS.STATUS)}
        onReset={handleReset}
        isLoading={isLoading}
      />

      <ChatInput
        value={inputText}
        onChange={setInputText}
        onSubmit={sendMessage}
        isLoading={isLoading}
      />
    </div>
  );
};

// =============================================================================
// Application Bootstrap
// =============================================================================

const container = document.getElementById('app');
const root = createRoot(container);
root.render(<DungeonMasterApp />);