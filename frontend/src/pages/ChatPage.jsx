import Chat from '../components/Chat'

export default function ChatPage({ messages, onSend, loading }) {
  return <Chat messages={messages} onSend={onSend} loading={loading} />
}
