const Workspace = () => {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <aside style={{ width: 260 }}>ConversationList</aside>
      <main style={{ flex: 1 }}>ChatArea</main>
      <aside style={{ width: 400 }}>PreviewPanel</aside>
    </div>
  )
}

export default Workspace
