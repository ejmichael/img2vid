import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : ''

function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError("File is too large (max 5MB)")
        return
      }
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setError(null)
      setVideoUrl(null)
      setStatus(null)
    }
  }

  const handleGenerate = async () => {
    if (!file) return

    setLoading(true)
    setError(null)
    setVideoUrl(null)
    
    const formData = new FormData()
    formData.append('image', file)

    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, formData)
      setJobId(response.data.job_id)
      setStatus('queued')
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start generation")
      setLoading(false)
    }
  }

  useEffect(() => {
    let interval
    if (jobId && (status === 'queued' || status === 'processing')) {
      interval = setInterval(async () => {
        try {
          const response = await axios.get(`${API_BASE_URL}/status/${jobId}`)
          setStatus(response.data.status)
          if (response.data.status === 'done') {
            setVideoUrl(`${API_BASE_URL}${response.data.video_url}`)
            setLoading(false)
            setJobId(null)
          } else if (response.data.status === 'error') {
            setError(response.data.message || "An error occurred during generation")
            setLoading(false)
            setJobId(null)
          }
        } catch (err) {
          console.error("Polling error:", err)
        }
      }, 2000)
    }
    return () => clearInterval(interval)
  }, [jobId, status])

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center py-12 px-4">
      <header className="mb-12 text-center">
        <h1 className="text-5xl font-extrabold mb-4 bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
          AI Image Animator
        </h1>
        <p className="text-slate-400 text-lg">Convert any image into a breathtaking short video</p>
      </header>

      <main className="w-full max-w-2xl bg-slate-800 rounded-2xl p-8 shadow-2xl border border-slate-700">
        <div className="flex flex-col items-center gap-8">
          
          {/* Upload Section */}
          {!videoUrl && (
            <div className="w-full flex flex-col items-center">
              <label 
                className={`w-full h-64 border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-colors ${
                  preview ? 'border-purple-500 bg-purple-500/5' : 'border-slate-600 hover:border-slate-400'
                }`}
              >
                {preview ? (
                  <img src={preview} alt="Preview" className="h-full w-full object-contain rounded-lg p-2" />
                ) : (
                  <div className="text-center p-6">
                    <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.587-1.587a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className="mt-2 text-slate-400">Click to upload image (max 5MB)</p>
                  </div>
                )}
                <input type="file" className="hidden" onChange={handleFileChange} accept="image/png, image/jpeg" />
              </label>

              {file && !loading && !videoUrl && (
                <button
                  onClick={handleGenerate}
                  className="mt-6 px-10 py-4 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-full transition-all shadow-lg hover:shadow-purple-500/20 active:scale-95"
                >
                  Generate Video
                </button>
              )}
            </div>
          )}

          {/* Loading / Status State */}
          {loading && (
            <div className="flex flex-col items-center py-8">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-purple-500 mb-4"></div>
              <p className="text-xl font-medium text-purple-400 capitalize">{status}...</p>
              <p className="text-slate-500 mt-2">This may take a few moments</p>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="w-full p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-center">
              {error}
            </div>
          )}

          {/* Video Player Section */}
          {videoUrl && (
            <div className="w-full flex flex-col items-center">
              <div className="relative group w-full rounded-xl overflow-hidden bg-black shadow-inner">
                <video 
                  src={videoUrl} 
                  controls 
                  autoPlay 
                  loop 
                  className="w-full aspect-square md:aspect-video"
                />
              </div>
              <button
                onClick={() => {
                  setVideoUrl(null)
                  setFile(null)
                  setPreview(null)
                }}
                className="mt-8 text-slate-400 hover:text-white transition-colors"
              >
                Upload another image
              </button>
            </div>
          )}
        </div>
      </main>

      <footer className="mt-12 text-slate-500 text-sm">
        Built with FastAPI, Redis, and PyTorch
      </footer>
    </div>
  )
}

export default App
