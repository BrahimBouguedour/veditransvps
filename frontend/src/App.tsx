import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { 
  CloudArrowUpIcon, 
  GlobeAltIcon, 
  SparklesIcon, 
  VideoCameraIcon,
  LanguageIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

interface UploadState {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  error?: string
}

function App() {
  const [uploadState, setUploadState] = useState<UploadState>({
    status: 'idle',
    progress: 0
  })
  const [selectedLanguage, setSelectedLanguage] = useState('fr')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploadState({ status: 'uploading', progress: 0 })

    const formData = new FormData()
    formData.append('video_file', file)
    formData.append('translation_params', JSON.stringify({
      target_language: selectedLanguage,
      preserve_voice: true
    }))

    try {
      const response = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0
          setUploadState(prev => ({ ...prev, progress }))
        },
      })

      setUploadState({
        status: 'processing',
        progress: 100,
      })

      const taskId = response.data.task_id
      const statusInterval = setInterval(async () => {
        try {
          const statusResponse = await axios.get(`http://localhost:8000/api/status/${taskId}`)
          if (statusResponse.data.status === 'completed') {
            setUploadState({
              status: 'completed',
              progress: 100,
            })
            clearInterval(statusInterval)
          } else if (statusResponse.data.status === 'error') {
            setUploadState({
              status: 'error',
              progress: 0,
              error: statusResponse.data.error
            })
            clearInterval(statusInterval)
          }
        } catch (error) {
          setUploadState({
            status: 'error',
            progress: 0,
            error: 'Failed to check translation status'
          })
          clearInterval(statusInterval)
        }
      }, 2000)

    } catch (error: any) {
      setUploadState({
        status: 'error',
        progress: 0,
        error: error.response?.data?.detail || 'Failed to upload video'
      })
    }
  }, [selectedLanguage])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    maxFiles: 1,
    multiple: false,
    onDragEnter: () => {},
    onDragOver: () => {},
    onDragLeave: () => {}
  })

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 fixed w-full top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-1.5">
                  <GlobeAltIcon className="h-5 w-5 text-white" />
                </div>
                <span className="ml-2 text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-transparent bg-clip-text">
                  VidTranslate
                </span>
              </div>
              <div className="hidden md:flex space-x-8 ml-8">
                <a href="#features" className="text-sm text-gray-600 hover:text-blue-600">Features</a>
                <a href="#pricing" className="text-sm text-gray-600 hover:text-blue-600">Pricing</a>
                <a href="#about" className="text-sm text-gray-600 hover:text-blue-600">About</a>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="text-sm text-gray-600 hover:text-blue-600">Sign In</button>
              <button className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <div className="text-center max-w-3xl mx-auto pt-16 pb-12">
            <h1 className="text-5xl font-bold tracking-tight">
              <span className="block text-gray-900">Video Translation</span>
              <span className="block mt-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-transparent bg-clip-text">
                Made Simple
              </span>
            </h1>
            <p className="mt-6 text-lg text-gray-600 leading-relaxed">
              Transform your videos into any language while preserving the original voice.
              Fast, accurate, and powered by AI.
            </p>
            <div className="mt-8 flex justify-center space-x-4">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                Start Translating
              </button>
              <button className="bg-white text-gray-700 px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors">
                Watch Demo
              </button>
            </div>
          </div>

          {/* Features Grid */}
          <div className="mt-16 bg-white/50 backdrop-blur-sm rounded-2xl p-8 shadow-sm border border-gray-200">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="group hover:bg-blue-50 p-6 rounded-xl transition-colors">
                <div className="bg-blue-100 rounded-lg p-3 w-12 h-12 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                  <VideoCameraIcon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">Multiple Formats</h3>
                <p className="mt-2 text-gray-600">Support for all major video formats including MP4, AVI, MOV, and MKV.</p>
              </div>

              <div className="group hover:bg-blue-50 p-6 rounded-xl transition-colors">
                <div className="bg-blue-100 rounded-lg p-3 w-12 h-12 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                  <LanguageIcon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">100+ Languages</h3>
                <p className="mt-2 text-gray-600">Translate your content into any major language with high accuracy.</p>
              </div>

              <div className="group hover:bg-blue-50 p-6 rounded-xl transition-colors">
                <div className="bg-blue-100 rounded-lg p-3 w-12 h-12 flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                  <SparklesIcon className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">Voice Cloning</h3>
                <p className="mt-2 text-gray-600">Preserve the original voice characteristics in the translated audio.</p>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="mt-16 max-w-3xl mx-auto">
            <div
              {...getRootProps()}
              className={`
                p-8 border-2 border-dashed rounded-xl
                ${isDragActive 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-300 hover:border-blue-400'
                }
                transition-all duration-200 ease-in-out
                cursor-pointer
                bg-white/50 backdrop-blur-sm
              `}
            >
              <div className="text-center">
                <CloudArrowUpIcon
                  className={`mx-auto h-12 w-12 ${
                    isDragActive ? 'text-blue-500' : 'text-gray-400'
                  }`}
                  aria-hidden="true"
                />
                <div className="mt-4">
                  <input
                    type="file"
                    className="sr-only"
                    {...(getInputProps() as any)}
                  />
                  <p className="text-lg text-gray-700">
                    <span className="font-medium">Drop your video here</span> or{' '}
                    <span className="text-blue-500 hover:text-blue-600 font-medium">
                      click to browse
                    </span>
                  </p>
                  <p className="mt-2 text-sm text-gray-500">
                    Supports MP4, AVI, MOV, or MKV up to 100MB
                  </p>
                </div>
                
                {/* Language Selection */}
                <div className="mt-6 flex justify-center">
                  <div className="relative inline-block">
                    <select
                      className="appearance-none bg-white border border-gray-300 rounded-lg pl-4 pr-10 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                    >
                      <option value="fr">French</option>
                      <option value="es">Spanish</option>
                      <option value="de">German</option>
                      <option value="it">Italian</option>
                      <option value="ja">Japanese</option>
                    </select>
                    <ChevronDownIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Section */}
          {uploadState.status !== 'idle' && (
            <div className="mt-8 max-w-3xl mx-auto bg-white/50 backdrop-blur-sm rounded-xl p-6 border border-gray-200 shadow-sm">
              <div className="relative">
                <div className="overflow-hidden h-2 text-xs flex rounded-full bg-gray-100">
                  <div
                    style={{ width: `${uploadState.progress}%` }}
                    className={`
                      shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center
                      transition-all duration-500 ease-in-out
                      ${uploadState.status === 'error' ? 'bg-red-500' : 'bg-blue-500'}
                    `}
                  />
                </div>
              </div>
              <div className="mt-4 text-center">
                {uploadState.status === 'uploading' && (
                  <p className="text-lg text-gray-700">
                    Uploading... {uploadState.progress}%
                  </p>
                )}
                {uploadState.status === 'processing' && (
                  <p className="text-lg text-gray-700">
                    Processing your video...
                  </p>
                )}
                {uploadState.status === 'completed' && (
                  <p className="text-lg text-green-600 font-medium">
                    Translation completed successfully!
                  </p>
                )}
                {uploadState.status === 'error' && (
                  <p className="text-lg text-red-600">
                    Error: {uploadState.error}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-24 bg-white/80 backdrop-blur-md border-t border-gray-200">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Product</h3>
              <ul className="mt-4 space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Features</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Pricing</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">API</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Company</h3>
              <ul className="mt-4 space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">About</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Blog</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Careers</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Support</h3>
              <ul className="mt-4 space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Help Center</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Documentation</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Contact</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-900">Legal</h3>
              <ul className="mt-4 space-y-2">
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Privacy</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Terms</a></li>
                <li><a href="#" className="text-sm text-gray-600 hover:text-blue-600">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-500 text-center">
              © 2024 VidTranslate. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
