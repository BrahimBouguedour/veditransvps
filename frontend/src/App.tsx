import { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import './App.css';

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ProcessingStep {
  id: number;
  label: string;
  status: 'waiting' | 'active' | 'completed' | 'error';
}

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('spanish');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [processingTime, setProcessingTime] = useState<number>(0);
  const [processingStartTime, setProcessingStartTime] = useState<number | null>(null);
  const AVERAGE_PROCESSING_TIME = 95; // Rounded from 94.547 seconds

  // Add processing time history for better estimates
  const [processingHistory, setProcessingHistory] = useState<number[]>([94.547, 96.969]);

  // Calculate dynamic average based on history
  const getAverageProcessingTime = () => {
    if (processingHistory.length === 0) return AVERAGE_PROCESSING_TIME;
    return Math.round(processingHistory.reduce((a, b) => a + b, 0) / processingHistory.length);
  };

  const [steps, setSteps] = useState<ProcessingStep[]>([
    { id: 1, label: 'Audio Extraction', status: 'waiting' },
    { id: 2, label: 'Transcription', status: 'waiting' },
    { id: 3, label: 'Translation', status: 'waiting' },
    { id: 4, label: 'Speech Generation', status: 'waiting' },
    { id: 5, label: 'Audio Merge', status: 'waiting' }
  ]);

  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<any>(null);
  const [mainResults, setMainResults] = useState<any>(null);
  const [stepTiming, setStepTiming] = useState<{[key: string]: number}>({});

  // Simplified language list
  const languages = [
    'Spanish',
    'French',
    'German',
    'Italian',
    'Portuguese',
    'Russian',
    'Japanese',
    'Korean',
    'Chinese',
    'Arabic'
  ];

  // Function to check if text is RTL
  const isRTL = (text: string): boolean => {
    const rtlRegex = /[\u0591-\u07FF\u200F\u202B\u202E\uFB1D-\uFDFD\uFE70-\uFEFC]/;
    return rtlRegex.test(text);
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please upload a valid video file');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov']
    },
    multiple: false
  });

  const updateStepStatus = (stepNumber: number, status: 'waiting' | 'active' | 'completed' | 'error') => {
    setCurrentStep(stepNumber);
    setSteps(prevSteps => 
      prevSteps.map(step => {
        if (step.id === stepNumber) {
          return { ...step, status };
        } else if (step.id < stepNumber) {
          return { ...step, status: 'completed' };
        }
        return step;
      })
    );
  };

  useEffect(() => {
    let timerInterval: NodeJS.Timeout | null = null;
    
    if (isProcessing && processingStartTime) {
      timerInterval = setInterval(() => {
        const currentTime = Date.now();
        const elapsedSeconds = Math.floor((currentTime - processingStartTime) / 1000);
        setProcessingTime(elapsedSeconds);
      }, 1000);
    } else if (!isProcessing) {
      if (timerInterval) clearInterval(timerInterval);
    }

    return () => {
      if (timerInterval) clearInterval(timerInterval);
    };
  }, [isProcessing, processingStartTime]);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getEstimatedTimeRemaining = (elapsedSeconds: number): string => {
    const avgTime = getAverageProcessingTime();
    const remainingSeconds = Math.max(0, avgTime - elapsedSeconds);
    return formatTime(remainingSeconds);
  };

  const getProgressPercentage = (elapsedSeconds: number): number => {
    return Math.min(100, (elapsedSeconds / AVERAGE_PROCESSING_TIME) * 100);
  };

  // Update processing history when a task completes successfully
  const updateProcessingHistory = (time: number) => {
    setProcessingHistory(prev => [...prev, time].slice(-5)); // Keep last 5 processing times
  };

  const handleDownload = (videoPath: string) => {
    console.log('Original video path:', videoPath);
    
    // Clean up the path - remove any backslashes and ensure proper formatting
    const cleanPath = videoPath.replace(/\\/g, '/');
    console.log('Cleaned path:', cleanPath);
    
    const encodedPath = encodeURIComponent(cleanPath);
    console.log('Encoded video path:', encodedPath);
    
    const downloadUrl = `${API_URL}/download/${encodedPath}`;
    console.log('Full download URL:', downloadUrl);
    
    // Create a temporary link and click it
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = cleanPath.split('/').pop() || 'translated_video.mp4';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(false);
    setProcessingStartTime(Date.now());
    setProcessingTime(0);

    const formData = new FormData();
    formData.append('video_file', selectedFile);
    formData.append('translation_params', JSON.stringify({
      target_language: selectedLanguage,
      preserve_voice: false
    }));

    try {
      updateStepStatus(1, 'active');
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            console.log('Upload progress:', progress);
          }
        }
      });

      if (response.data.task_id) {
        await pollTaskStatus(response.data.task_id);
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred during upload';
      setError(`Upload failed: ${errorMessage}`);
      setIsProcessing(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`${API_URL}/api/status/${taskId}`);
        const status = response.data.status;
        const currentStepInfo = response.data.current_step;
        const result = response.data.result;
        const stepTime = response.data.step_timing;

        console.log('Current step:', currentStepInfo);
        console.log('Processing status:', status);
        
        // Update step timing if available
        if (stepTime) {
          setStepTiming(stepTime);
        }

        // Update current step if available
        if (currentStepInfo) {
          const stepNumber = currentStepInfo.step_number;
          updateStepStatus(stepNumber, 'active');
        }

        // Check for completion
        if (status === 'completed' || result?.status === 'success') {
          clearInterval(pollInterval);
          setIsProcessing(false);
          setSuccess(true);
          updateStepStatus(5, 'completed');
          
          if (processingTime > 0) {
            updateProcessingHistory(processingTime);
          }

          // Set results and download URL
          if (result) {
            setMainResults({
              audio_extraction: {
                status: 'success',
                duration: result.audio_duration
              },
              transcription: {
                status: 'success',
                text: result.transcription?.text,
                text_length: result.transcription?.text?.length
              },
              translation: {
                status: 'success',
                original_text: result.transcription?.text,
                translated_text: result.translation,
                original_length: result.transcription?.text?.length,
                translated_length: result.translation?.length
              },
              speech_generation: {
                status: 'success',
                duration: result.audio_duration
              },
              audio_merge: {
                status: 'success',
                file_path: result.video_path,
                size: result.file_size
              }
            });
            setDownloadUrl(result.video_path);
          } else {
            setError('Video processing completed but no results available');
          }
        } 
        // Check for error
        else if (status === 'error' || result?.status === 'error') {
          clearInterval(pollInterval);
          const errorMsg = result?.error || response.data.error || 'Processing failed';
          setError(errorMsg);
          setIsProcessing(false);
          updateStepStatus(currentStep, 'error');
        }
      } catch (err: any) {
        console.error('Status check error:', err);
        clearInterval(pollInterval);
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to check processing status';
        setError(`Status check failed: ${errorMessage}`);
        setIsProcessing(false);
        updateStepStatus(currentStep, 'error');
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  };

  const handleTest = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(false);
    setTestResults(null);

    const formData = new FormData();
    formData.append('video_file', selectedFile);
    formData.append('translation_params', JSON.stringify({
      target_language: selectedLanguage,
      preserve_voice: false
    }));

    try {
      const response = await axios.post(`${API_URL}/api/test-process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Accept': 'application/json'
        }
      });

      setTestResults(response.data.test_results);
      setIsProcessing(false);
    } catch (err: any) {
      console.error('Test error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred during test';
      setError(`Test failed: ${errorMessage}`);
      setIsProcessing(false);
    }
  };

  const renderResults = (results: any, isTest: boolean = false) => {
    if (!results) return null;

    const audioMergeResult = results.audio_merge;
    const hasDownloadableVideo = audioMergeResult?.status === 'success' && audioMergeResult?.file_path;

    // Only show the download section if we have a video ready
    if (hasDownloadableVideo) {
  return (
        <div className="success-message">
          <h3>Video Processing Complete!</h3>
          <div className="final-download-section">
            <button
              className="download-button-large"
              onClick={() => handleDownload(audioMergeResult.file_path)}
            >
              Download Translated Video
              </button>
            <p className="download-info">Your translated video is ready!</p>
          </div>
        </div>
      );
    }

    return null;
  };

  const renderProcessingSteps = () => {
    return (
      <div className="processing-indicator">
        <div className="loading-spinner" />
        <div className="processing-stats">
          <div className="processing-time">Time Elapsed: {formatTime(processingTime)}</div>
          <div className="estimated-time">Estimated Time Remaining: {getEstimatedTimeRemaining(processingTime)}</div>
          <div className="progress-percentage">
            Progress: {Math.round(getProgressPercentage(processingTime))}%
          </div>
                </div>
        <div className="progress-steps">
          <div className="progress-line">
            <div
              className="progress-line-fill"
              style={{
                width: `${(currentStep / steps.length) * 100}%`
              }}
            />
          </div>
          {steps.map((step) => (
            <div key={step.id} className="progress-step">
              <div
                className={`step-number ${
                  step.id === currentStep
                    ? 'active'
                    : step.id < currentStep
                    ? 'completed'
                    : ''
                }`}
              >
                {step.id}
              </div>
              <div className="step-label">
                {step.label}
                {stepTiming[step.label.toLowerCase()] && (
                  <div className="step-timing">
                    {stepTiming[step.label.toLowerCase()].toFixed(2)}s
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
            </div>
    );
  };

  return (
    <div className="container">
      <header className="header">
        <h1>VediTrans</h1>
        <p>Smart Video Translation Platform - Transform Your Content Globally</p>
      </header>

      <div className="upload-section">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="upload-content">
            {isDragActive ? (
              <p>Drop the video here...</p>
            ) : (
              <>
                <svg
                  className="upload-icon"
                  width="64"
                  height="64"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p>Drag & drop a video file here, or click to select</p>
                {selectedFile && (
                  <p className="selected-file">Selected: {selectedFile.name}</p>
                )}
              </>
            )}
          </div>
        </div>

        <select
          className="language-select"
          value={selectedLanguage}
          onChange={(e) => setSelectedLanguage(e.target.value.toLowerCase())}
        >
          {languages.map((language) => (
            <option key={language.toLowerCase()} value={language.toLowerCase()}>
              {language}
            </option>
          ))}
        </select>

        <div className="button-group">
          <button
            className="test-button test-button-primary"
            onClick={handleTest}
            disabled={!selectedFile || isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Process Video'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {isProcessing && renderProcessingSteps()}
        {testResults && renderResults(testResults, true)}
      </div>
    </div>
  );
}

export default App;