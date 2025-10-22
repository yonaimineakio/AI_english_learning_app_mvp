"use client"

import { useCallback, useEffect, useRef, useState } from 'react'

interface UseAudioRecordingOptions {
  silenceThresholdSeconds?: number
  maxRecordingSeconds?: number
  minRecordingSeconds?: number
  silenceDbThreshold?: number
  onRecordingComplete?: (blob: Blob) => void
}

interface UseAudioRecordingReturn {
  isRecording: boolean
  isProcessing: boolean
  isAutoStopping: boolean
  audioBlob: Blob | null
  startRecording: () => Promise<void>
  stopRecording: (options?: { force?: boolean }) => void
  clearRecording: () => void
  error: string | null
  elapsedSeconds: number
  silenceDurationSeconds: number
  silenceThresholdSeconds: number
  maxRecordingSeconds: number
  minRecordingSeconds: number
}

const DEFAULT_DB_THRESHOLD = -45
const MIN_DECIBELS = -160
const DEFAULT_SAMPLE_RATE = 44100

const computeDecibels = (timeDomainData: Float32Array): number => {
  if (timeDomainData.length === 0) {
    return MIN_DECIBELS
  }

  let sumSquares = 0
  for (let i = 0; i < timeDomainData.length; i += 1) {
    const sample = timeDomainData[i]
    if (!Number.isFinite(sample)) continue
    sumSquares += sample * sample
  }

  const rms = Math.sqrt(sumSquares / timeDomainData.length)
  const minRms = 1e-8
  const db = 20 * Math.log10(Math.max(rms, minRms))
  if (!Number.isFinite(db)) {
    return MIN_DECIBELS
  }
  return Math.max(db, MIN_DECIBELS)
}

export function useAudioRecording(options: UseAudioRecordingOptions = {}): UseAudioRecordingReturn {
  const {
    silenceThresholdSeconds = 5,
    maxRecordingSeconds = 60,
    minRecordingSeconds = 1,
    silenceDbThreshold = DEFAULT_DB_THRESHOLD,
    onRecordingComplete,
  } = options

  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isAutoStopping, setIsAutoStopping] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [silenceDurationSeconds, setSilenceDurationSeconds] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const timeDomainDataRef = useRef<Float32Array | null>(null)
  const silenceTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const elapsedTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const isStoppingRef = useRef(false)
  const preRollBufferRef = useRef<Float32Array[]>([])
  const isPreRollingRef = useRef(false)

  const stopTimers = useCallback(() => {
    if (elapsedTimerRef.current) {
      clearInterval(elapsedTimerRef.current)
      elapsedTimerRef.current = null
    }
    if (silenceTimerRef.current) {
      clearInterval(silenceTimerRef.current)
      silenceTimerRef.current = null
    }
  }, [])

  const cleanupAudioProcessing = useCallback(() => {
    analyserRef.current?.disconnect()
    audioContextRef.current?.close().catch((err) => console.warn('Failed to close AudioContext', err))
    analyserRef.current = null
    audioContextRef.current = null
    timeDomainDataRef.current = null
    preRollBufferRef.current = []
    isPreRollingRef.current = false
  }, [])

  const stopRecording = useCallback(
    (stopOptions?: { force?: boolean }) => {
      if (!mediaRecorderRef.current || !isRecording || isStoppingRef.current) return

      const nowElapsed = elapsedSeconds
      if (!stopOptions?.force && nowElapsed < minRecordingSeconds) {
        return
      }

      isStoppingRef.current = true
      setIsProcessing(true)
      stopTimers()
      mediaRecorderRef.current.stop()
    },
    [elapsedSeconds, isRecording, minRecordingSeconds, stopTimers],
  )

  const analyseAudioLevel = useCallback(() => {
    if (!analyserRef.current || !timeDomainDataRef.current) return

    const timeDomainData = timeDomainDataRef.current as Float32Array
    analyserRef.current.getFloatTimeDomainData(timeDomainData as any)
    const decibels = computeDecibels(timeDomainData)

    setSilenceDurationSeconds((prev) => {
      const isSilent = decibels < silenceDbThreshold
      const nextValue = isSilent ? Number((prev + 0.2).toFixed(1)) : 0

      if (isSilent && nextValue >= silenceThresholdSeconds) {
        setIsAutoStopping(true)
        stopRecording({ force: true })
      }

      return nextValue
    })
  }, [silenceDbThreshold, silenceThresholdSeconds, stopRecording])

  const initializeAudioProcessing = useCallback((stream: MediaStream) => {
    try {
      const audioContext = new AudioContext({ sampleRate: DEFAULT_SAMPLE_RATE })
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 2048

      const timeDomainData = new Float32Array(analyser.fftSize)

      source.connect(analyser)

      audioContextRef.current = audioContext
      analyserRef.current = analyser
      timeDomainDataRef.current = timeDomainData as Float32Array
      
      // プリロール録音を開始
      startPreRollRecording(analyser, timeDomainData)
    } catch (err) {
      console.warn('Failed to initialize audio analyser', err)
    }
  }, [])

  const startPreRollRecording = useCallback((analyser: AnalyserNode, timeDomainData: Float32Array) => {
    isPreRollingRef.current = true
    preRollBufferRef.current = []
    
    const preRollInterval = setInterval(() => {
      if (!isPreRollingRef.current) {
        clearInterval(preRollInterval)
        return
      }
      
      analyser.getFloatTimeDomainData(timeDomainData as any)
      const bufferCopy = new Float32Array(timeDomainData.length)
      bufferCopy.set(timeDomainData)
      preRollBufferRef.current.push(bufferCopy)
      
      // プリロールバッファのサイズを制限（約1秒分）
      if (preRollBufferRef.current.length > 20) {
        preRollBufferRef.current.shift()
      }
    }, 50)
  }, [])

  const startTimers = useCallback(() => {
    stopTimers()

    elapsedTimerRef.current = setInterval(() => {
      setElapsedSeconds((prev) => {
        const nextValue = prev + 0.1
        if (nextValue >= maxRecordingSeconds) {
          setIsAutoStopping(true)
          stopRecording({ force: true })
          return maxRecordingSeconds
        }
        return Number(nextValue.toFixed(1))
      })
    }, 100)

    silenceTimerRef.current = setInterval(() => {
      analyseAudioLevel()
    }, 200)
  }, [analyseAudioLevel, maxRecordingSeconds, stopRecording, stopTimers])

  const startRecording = useCallback(async () => {
    try {
      setError(null)

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('このブラウザは音声録音をサポートしていません')
      }

      if (!window.MediaRecorder) {
        throw new Error('このブラウザはMediaRecorderをサポートしていません')
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: DEFAULT_SAMPLE_RATE,
        },
      })

      let mimeType = 'audio/webm;codecs=opus'
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'audio/webm'
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = 'audio/mp4'
          if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = ''
          }
        }
      }

      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)

      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        // プリロール録音を停止
        isPreRollingRef.current = false
        
        const recordedBlob = new Blob(audioChunksRef.current, { type: mimeType || 'audio/webm' })
        setAudioBlob(recordedBlob)
        setIsProcessing(false)
        setIsRecording(false)
        setIsAutoStopping(false)
        setSilenceDurationSeconds(0)
        setElapsedSeconds(0)
        cleanupAudioProcessing()
        isStoppingRef.current = false

        // Call the recording complete callback if provided
        if (onRecordingComplete) {
          onRecordingComplete(recordedBlob)
        }

        stream.getTracks().forEach((track) => track.stop())
      }

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event)
        setError('録音中にエラーが発生しました')
        setIsRecording(false)
        cleanupAudioProcessing()
        stopTimers()
      }

      // プリロール録音を停止してから実際の録音を開始
      isPreRollingRef.current = false
      
      mediaRecorder.start(50)
      setIsRecording(true)
      setIsProcessing(false)
      setAudioBlob(null)
      setElapsedSeconds(0)
      setSilenceDurationSeconds(0)
      setIsAutoStopping(false)
      initializeAudioProcessing(stream)
      startTimers()
    } catch (err) {
      console.error('Failed to start recording:', err)
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('マイクへのアクセスが拒否されました。ブラウザの設定でマイクの許可を有効にしてください。')
        } else if (err.name === 'NotFoundError') {
          setError('マイクが見つかりません。マイクが接続されているか確認してください。')
        } else if (err.name === 'NotSupportedError') {
          setError('このブラウザは音声録音をサポートしていません。')
        } else {
          setError(err.message)
        }
      } else {
        setError('録音の開始に失敗しました')
      }
    }
  }, [initializeAudioProcessing, startTimers, cleanupAudioProcessing, stopTimers])

  const clearRecording = useCallback(() => {
    setAudioBlob(null)
    setError(null)
    setIsProcessing(false)
    setIsAutoStopping(false)
    setElapsedSeconds(0)
    setSilenceDurationSeconds(0)
    audioChunksRef.current = []
    stopTimers()
    cleanupAudioProcessing()
  }, [cleanupAudioProcessing, stopTimers])

  const cleanupOnUnmount = useCallback(() => {
    stopTimers()
    cleanupAudioProcessing()
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
  }, [cleanupAudioProcessing, stopTimers])

  useEffect(() => {
    return () => {
      cleanupOnUnmount()
    }
  }, [cleanupOnUnmount])

  return {
    isRecording,
    isProcessing,
    isAutoStopping,
    audioBlob,
    startRecording,
    stopRecording,
    clearRecording,
    error,
    elapsedSeconds,
    silenceDurationSeconds,
    silenceThresholdSeconds,
    maxRecordingSeconds,
    minRecordingSeconds,
  }
}
