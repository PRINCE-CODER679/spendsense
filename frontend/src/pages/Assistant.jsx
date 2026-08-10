import { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  User, 
  Send, 
  Sparkles, 
  RefreshCw, 
  HelpCircle, 
  ShieldAlert, 
  TrendingUp, 
  PieChart, 
  Wallet 
} from 'lucide-react';
import assistantService from '../services/assistantService';

const STARTER_QUESTIONS = [
  { text: 'Am I staying within my budget this month?', icon: Wallet },
  { text: 'Where am I spending the most money?', icon: PieChart },
  { text: 'Were any unusual transactions flagged recently?', icon: ShieldAlert },
  { text: 'What is my projected end-of-month spending?', icon: TrendingUp },
];

const Assistant = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your **SpendSense AI Financial Assistant**. I have analyzed your real-time financial data across income, expenses, budgets, forecasts, and anomalies.\n\nHow can I help you today?',
      source: 'system'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend) => {
    const query = textToSend || inputMessage.trim();
    if (!query || isLoading) return;

    const userMsg = { role: 'user', content: query };
    const updatedMessages = [...messages, userMsg];
    
    setMessages(updatedMessages);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Prepare history format
      const history = updatedMessages
        .filter(m => m.source !== 'system')
        .map(m => ({ role: m.role, content: m.content }));

      const res = await assistantService.sendMessage(query, history);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          source: res.source
        }
      ]);

      if (res.suggested_followups && res.suggested_followups.length > 0) {
        setSuggestedQuestions(res.suggested_followups);
      }
    } catch (err) {
      console.error('Failed to send assistant message:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ **Error:** Unable to connect to the assistant service. Please check your connection and try again.',
          source: 'error'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Chat reset. How else can I assist your financial planning?',
        source: 'system'
      }
    ]);
    setSuggestedQuestions([]);
  };

  const formatContent = (text) => {
    // Simple markdown formatter for bold, lists, and line breaks
    let formatted = text;
    
    // Bold **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italic *text*
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return formatted.split('\n').map((line, idx) => {
      if (line.startsWith('• ') || line.startsWith('- ')) {
        return (
          <li key={idx} className="ml-4 list-disc my-1" dangerouslySetInnerHTML={{ __html: line.substring(2) }} />
        );
      }
      return (
        <p key={idx} className={line.trim() === '' ? 'h-2' : 'my-1'} dangerouslySetInnerHTML={{ __html: line }} />
      );
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] max-w-6xl mx-auto">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl text-white shadow-md">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              AI Financial Assistant
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                <Sparkles className="w-3 h-3 mr-1 text-indigo-500" />
                Live Context
              </span>
            </h1>
            <p className="text-xs text-gray-500">Real-time insights powered by your SpendSense data</p>
          </div>
        </div>

        <button
          onClick={handleClearChat}
          className="flex items-center px-3 py-1.5 text-xs font-medium text-gray-600 hover:text-gray-900 bg-white border border-gray-200 hover:border-gray-300 rounded-lg shadow-sm transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Clear Chat
        </button>
      </div>

      {/* Main Chat Container */}
      <div className="flex-1 bg-white rounded-2xl border border-gray-200 shadow-sm flex flex-col overflow-hidden">
        
        {/* Messages Scroll Area */}
        <div className="flex-1 p-6 overflow-y-auto space-y-6 bg-gray-50/50">
          {messages.map((msg, index) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={index}
                className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}
              >
                {/* Avatar */}
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm ${
                    isUser
                      ? 'bg-slate-900 text-white'
                      : 'bg-gradient-to-tr from-indigo-600 to-purple-600 text-white'
                  }`}
                >
                  {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>

                {/* Message Bubble */}
                <div className={`max-w-[80%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`px-5 py-3.5 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      isUser
                        ? 'bg-indigo-600 text-white rounded-tr-none'
                        : 'bg-white text-gray-800 border border-gray-200/80 rounded-tl-none'
                    }`}
                  >
                    {formatContent(msg.content)}
                  </div>
                  
                  {msg.source && msg.source !== 'system' && !isUser && (
                    <span className="text-[10px] text-gray-400 mt-1 px-1 capitalize">
                      Source: {msg.source.replace('_', ' ')}
                    </span>
                  )}
                </div>
              </div>
            );
          })}

          {/* Loading Typing Indicator */}
          {isLoading && (
            <div className="flex items-start space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center shadow-sm">
                <Bot className="w-5 h-5 animate-pulse" />
              </div>
              <div className="bg-white border border-gray-200 px-5 py-4 rounded-2xl rounded-tl-none shadow-sm flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Starter Suggestions */}
        {messages.length <= 2 && !isLoading && (
          <div className="p-4 bg-white border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-500 mb-2 flex items-center">
              <HelpCircle className="w-3.5 h-3.5 mr-1 text-indigo-500" />
              Suggested Questions:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {STARTER_QUESTIONS.map((q, idx) => {
                const IconComponent = q.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(q.text)}
                    className="flex items-center p-2.5 text-left text-xs font-medium text-gray-700 bg-gray-50 hover:bg-indigo-50 hover:text-indigo-700 border border-gray-200 hover:border-indigo-200 rounded-xl transition-all group"
                  >
                    <IconComponent className="w-4 h-4 mr-2 text-gray-400 group-hover:text-indigo-600 flex-shrink-0" />
                    <span className="truncate">{q.text}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Input Bar */}
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask about your budgets, top expenses, forecast, or anomalies..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all disabled:opacity-60"
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              className="px-5 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl font-medium text-sm flex items-center space-x-2 shadow-sm transition-all flex-shrink-0"
            >
              <span>Send</span>
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Assistant;
