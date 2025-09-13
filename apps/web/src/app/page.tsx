export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI English Learning App
          </h1>
          <p className="text-lg text-gray-600 mb-8">
            AI-powered English learning application
          </p>
          <div className="card max-w-md mx-auto">
            <h2 className="text-xl font-semibold mb-4">Welcome!</h2>
            <p className="text-gray-600 mb-6">
              This is the MVP version of the AI English Learning App.
            </p>
            <button className="btn btn-primary w-full">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
