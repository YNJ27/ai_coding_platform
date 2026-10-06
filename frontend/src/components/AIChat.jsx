import { Bot, Clock3, Send, Sparkles, UserRound } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { fetchChatHistory, sendChatMessage } from '../services/api'

const formatTime = (date) => new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

function AIChat({ sessionId, problemTitle, currentFile }) {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesContainerRef = useRef(null)

  useEffect(() => {
    if (!sessionId) return
    fetchChatHistory(sessionId)
      .then((history) => setMessages(history.map((item) => ({ ...item, timestamp: item.created_at }))))
      .catch(() => {})
  }, [sessionId])

  useEffect(() => {
    const container = messagesContainerRef.current
    if (container) container.scrollTop = container.scrollHeight
  }, [messages, isProcessing])

  const submitMessage = async (event) => {
    event?.preventDefault()
    const trimmedMessage = message.trim()
    if (!trimmedMessage || isProcessing) return

    const userMessage = { id: crypto.randomUUID(), role: 'user', content: trimmedMessage, timestamp: new Date().toISOString() }
    setMessages((current) => [...current, userMessage])
    setMessage('')
    setIsProcessing(true)

    try {
      const response = await sendChatMessage({ sessionId, message: trimmedMessage })
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: 'assistant', content: response.message, timestamp: new Date().toISOString() }])
    } catch (error) {
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: 'assistant', content: error instanceof Error ? error.message : 'I could not process that request. Please try again.', timestamp: new Date(), isError: true }])
    } finally {
      setIsProcessing(false)
    }
  }

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submitMessage(event)
    }
  }

  return (
    <section className="ai-chat" aria-label="AI coding assistant">
      <div className="ai-chat-header"><div className="ai-title"><span className="ai-icon"><Sparkles size={15} /></span><div><strong>AI Assist</strong><span>Context-aware coding help</span></div></div><span className="ai-context"><Clock3 size={12} /> {currentFile?.split('/').pop()}</span></div>
      <div className="ai-messages" ref={messagesContainerRef} aria-live="polite">
        {messages.length === 0 && <div className="chat-empty"><div className="chat-empty-icon"><Bot size={18} /></div><strong>Ask about your code</strong><p>I can help you understand {problemTitle}, debug issues, or explain how the current implementation works.</p></div>}
        {messages.map((item) => <div className={`chat-message ${item.role} ${item.isError ? 'is-error' : ''}`} key={item.id}><div className="message-avatar">{item.role === 'assistant' ? <Bot size={14} /> : <UserRound size={14} />}</div><div className="message-content"><p>{item.content}</p><time>{formatTime(item.timestamp)}</time></div></div>)}
        {isProcessing && <div className="chat-message assistant"><div className="message-avatar"><Bot size={14} /></div><div className="chat-loading"><span /><span /><span /></div></div>}
      </div>
      <form className="chat-composer" onSubmit={submitMessage}><textarea value={message} onChange={(event) => setMessage(event.target.value)} onKeyDown={handleKeyDown} placeholder="Ask about your code..." aria-label="Ask AI Assist" rows={2} disabled={isProcessing} /><button type="submit" aria-label="Send message" disabled={isProcessing || !message.trim()}><Send size={15} /></button><span className="composer-hint">Enter to send · Shift+Enter for a new line</span></form>
    </section>
  )
}

export default AIChat
