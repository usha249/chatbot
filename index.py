import React, { useState, useEffect, useRef } from 'react';

// Main App component for the chatbot
const App = () => {
    // State to store chat messages, each with text and sender
    const [messages, setMessages] = useState([]);
    // State to store the current message being typed by the user
    const [inputMessage, setInputMessage] = useState('');
    // State to indicate if the bot is currently typing a response
    const [isTyping, setIsTyping] = useState(false);

    // Ref to automatically scroll to the latest message
    const messagesEndRef = useRef(null);

    // Effect to scroll to the bottom of the chat window when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    /**
     * Handles sending a message.
     * Adds the user's message to the chat and then calls the Gemini API for a bot response.
     */
    const sendMessage = async () => {
        if (inputMessage.trim() === '') return; // Don't send empty messages

        const userMessage = { text: inputMessage, sender: 'user' };
        setMessages(prevMessages => [...prevMessages, userMessage]); // Add user message
        setInputMessage(''); // Clear input field
        setIsTyping(true); // Show typing indicator

        try {
            // Prepare chat history for the Gemini API call
            // The API expects a specific format: { role: "user", parts: [{ text: "..." }] }
            // For this simple bot, we'll just send the current user message as the prompt.
            // For a more advanced bot, you'd send the full conversation history.
            let chatHistory = [];
            chatHistory.push({ role: "user", parts: [{ text: inputMessage }] });

            const payload = { contents: chatHistory };
            const apiKey = ""; // API key is handled by the Canvas environment for gemini-2.0-flash
            const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            // Check if the response contains valid content
            if (result.candidates && result.candidates.length > 0 &&
                result.candidates[0].content && result.candidates[0].content.parts &&
                result.candidates[0].content.parts.length > 0) {
                const botResponseText = result.candidates[0].content.parts[0].text;
                const botMessage = { text: botResponseText, sender: 'bot' };
                setMessages(prevMessages => [...prevMessages, botMessage]); // Add bot message
            } else {
                // Handle cases where the response structure is unexpected or content is missing
                console.error("Unexpected API response structure:", result);
                setMessages(prevMessages => [...prevMessages, { text: "Sorry, I couldn't get a response. Please try again.", sender: 'bot' }]);
            }
        } catch (error) {
            console.error("Error communicating with Gemini API:", error);
            setMessages(prevMessages => [...prevMessages, { text: "There was an error connecting to the bot. Please check your internet connection.", sender: 'bot' }]);
        } finally {
            setIsTyping(false); // Hide typing indicator
        }
    };

    // JSX for the chatbot UI
    return (
        <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4 font-sans antialiased">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md flex flex-col h-[80vh] overflow-hidden">
                {/* Chat Header */}
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-t-xl shadow-md flex items-center justify-between">
                    <h1 className="text-2xl font-bold">Usharani</h1> {/* Changed from "My Chatbot" to "Usharani" */}
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                </div>

                {/* Chat Messages Area */}
                <div className="flex-1 p-4 overflow-y-auto space-y-4">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[75%] p-3 rounded-lg shadow-sm ${
                                    msg.sender === 'user'
                                        ? 'bg-blue-500 text-white rounded-br-none'
                                        : 'bg-gray-200 text-gray-800 rounded-bl-none'
                                }`}
                            >
                                {msg.text}
                            </div>
                        </div>
                    ))}
                    {/* Typing indicator */}
                    {isTyping && (
                        <div className="flex justify-start">
                            <div className="max-w-[75%] p-3 rounded-lg shadow-sm bg-gray-200 text-gray-800 rounded-bl-none animate-pulse">
                                Bot is typing...
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} /> {/* Scroll target */}
                </div>

                {/* Message Input Area */}
                <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center space-x-3 rounded-b-xl">
                    <input
                        type="text"
                        className="flex-1 p-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
                        placeholder="Type your message..."
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter' && !isTyping) {
                                sendMessage();
                            }
                        }}
                        disabled={isTyping} // Disable input while bot is typing
                    />
                    <button
                        onClick={sendMessage}
                        className="bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled={isTyping || inputMessage.trim() === ''} // Disable button while typing or if input is empty
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default App;

                                    