export function ChatLayout() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl flex-col gap-4 p-4 md:p-8">
      <header className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Chatbot</h1>
        <p className="text-sm text-slate-600">UI scaffold only. No chat logic yet.</p>
      </header>

      <section className="flex-1 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="h-[420px] overflow-y-auto rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-slate-500">
          Message area placeholder
        </div>
      </section>

      <footer className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Type your message..."
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 outline-none ring-0 focus:border-slate-400"
          />
          <button
            type="button"
            className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white"
          >
            Send
          </button>
        </div>
      </footer>
    </main>
  )
}
